import os
import re
import csv
import json
import hashlib
from pathlib import Path
from tqdm import tqdm
import aiohttp
import asyncio
import logging
import fitz  # PyMuPDF
import docx
import pptx
from bs4 import BeautifulSoup
import markdown
import tempfile
import shutil
import subprocess
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qp_dataset.log'),
        logging.StreamHandler()
    ]
)

def generate_document_id(file_path: str) -> str:
    """Generates a unique identifier for a document based on its file path."""
    return hashlib.sha256(file_path.encode()).hexdigest()[:8]

def clean_text(text: str) -> str:
    """
    Cleans text by replacing problematic characters and ensuring compatibility.
    """
    if not text:
        return " "
    # Replace problematic characters with spaces or remove them
    return re.sub(r'[\x00-\x1F\x7F]', ' ', text).strip()

def write_csv_safely(rows: list, output_file: str, fieldnames: list):
    """
    Writes data to CSV with proper UTF-8 encoding and error handling.
    """
    try:
        # Add BOM for Excel compatibility
        with open(output_file, 'w', encoding='utf-8-sig', newline='', errors='replace') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                # Clean each field in the row
                cleaned_row = {
                    key: clean_text(value)
                    for key, value in row.items()
                }
                writer.writerow(cleaned_row)

        logging.info(f"✅ Data successfully written to {output_file}")

    except Exception as e:
        logging.error(f"Error writing CSV: {str(e)}", exc_info=True)
        raise

def extract_course_info(text_content: str) -> dict:
    """
    Extracts Course No and Course Title from the text content.
    Handles multiple course codes and limits Page 1 parsing to first few lines.
    """
    course_no = "Unknown_Course_No"
    course_title = "Unknown_Course_Title"

    lines = text_content.splitlines()

    if "Course No." in text_content:
        course_no_match = re.search(r"Course No\.\s*:\s*(.+)", text_content, re.IGNORECASE)
        course_title_match = re.search(r"Course Title\s*:\s*(.+)", text_content, re.IGNORECASE)

        if course_no_match:
            course_no = course_no_match.group(1).strip()
        if course_title_match:
            course_title = course_title_match.group(1).strip()
    else:
        # Look for course info in first few lines after "Page 1:"
        page_1_index = -1
        for i, line in enumerate(lines):
            if "Page 1:" in line:
                page_1_index = i
                break

        if page_1_index != -1:
            # Check next 3 lines after "Page 1:" for course information
            search_text = "\n".join(lines[page_1_index:page_1_index + 4])
            page_1_match = re.search(r"Page 1:\s*(.+?)\s+([A-Z]{3,}\d{3}[A-Z0-9/]*)", search_text, re.IGNORECASE | re.DOTALL)

            if page_1_match:
                course_title = page_1_match.group(1).strip()
                # Extract all course codes
                course_codes = re.findall(r'[A-Z]{3,}\d{3}[A-Z0-9]*', page_1_match.group(2))
                course_no = "/".join(course_codes) if course_codes else "Unknown_Course_No"

    return {"course_no": course_no, "course_title": course_title}

def extract_questions(text_content: str) -> list:
    """
    Extracts questions from the text content using regex.
    Handles questions ending with marks in square brackets [ ] or parentheses ( ).
    Excludes "no of questions" and "no of pages" entries.
    """
    # First, remove any lines containing "no of questions" or "no of pages"
    lines = text_content.splitlines()
    filtered_lines = [
        line for line in lines
        if not re.search(r'no\.?\s+of\s+questions|no\.?\s+of\s+pages', line, re.IGNORECASE)
    ]
    filtered_text = "\n".join(filtered_lines)

    # Enhanced regex to capture questions with marks in square brackets or parentheses
    question_pattern = re.compile(
        r"(Q\.\d+(?:\s*\(.*?\))?.*?)\s*(?:\[(\d+)\]|\((\d+)\))",  # Matches both [marks] and (marks)
        re.DOTALL
    )
    matches = question_pattern.finditer(filtered_text)

    questions = []
    for match in matches:
        question_number = match.group(1).strip()
        question_text = match.group(1).strip()
        marks = match.group(2) or match.group(3)  # Use whichever group is matched ([ ] or ( ))

        questions.append({
            "question_number": question_number,
            "question_text": question_text,
            "marks": marks
        })

    return questions

async def correct_spelling(text: str, api_url: str, model_name: str) -> str:
    """
    Corrects spelling mistakes in the text using an LLM.
    """
    try:
        if not text.strip():
            logging.warning("Skipping spelling correction: Input text is empty.")
            return text

        prompt = (
            f"Correct any spelling mistakes in the following text without changing its structure:\n\n{text}"
        )

        timeout = aiohttp.ClientTimeout(total=300)   # 5 minutes timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False  # Set to non-streaming mode
            }
            headers = {"Content-Type": "application/json"}

            logging.debug(f"Making API request to {api_url}/api/generate")

            async with session.post(f"{api_url}/api/generate", json=data, headers=headers) as response:
                if response.status != 200:
                    logging.error(f"API Error: HTTP {response.status}")
                    return text

                try:
                    response_json = await response.json()
                    corrected_text = response_json.get('response', '')
                    if corrected_text:
                        logging.info(f"Successfully corrected text. First 100 chars: {corrected_text[:100]}...")
                        return corrected_text.strip()
                    else:
                        logging.warning("API returned empty response")
                        return text

                except json.JSONDecodeError as e:
                    logging.error(f"JSON Decode Error: {e}")
                    return text

    except Exception as e:
        logging.error(f"Unexpected error in correct_spelling: {str(e)}")
        return text

async def infer_topic_name(question_text: str, course_title: str, api_url: str, model_name: str) -> str:
    """
    Infers the topic name for a question based on the course title and question text.
    """
    try:
        prompt = (
            f"Infer the topic name for the following question from the course titled '{course_title}':\n\n{question_text}\n\n"
            f"PLEASE OUTPUT ONLY THE TOPIC AND NOTHING ELSE"
        )

        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            data = {"model": model_name, "prompt": prompt}
            headers = {"Accept": "application/x-ndjson", "Content-Type": "application/json"}

            async with session.post(f"{api_url}/api/generate", json=data, headers=headers) as response:
                if response.status != 200:
                    logging.error(f"Error inferring topic name: HTTP {response.status}, {await response.text()}")
                    return "Unknown_Topic"

                collected_text = ""
                async for line in response.content:
                    if line.strip():
                        try:
                            obj = json.loads(line)
                            collected_text += obj.get("response", "")
                            if obj.get("done", False):
                                break
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON Decode Error while inferring topic: {e}")

                if collected_text.strip():
                    return collected_text.strip().capitalize()

    except Exception as e:
        logging.error(f"Error inferring topic name: {str(e)}", exc_info=True)

    return "Unknown_Topic"

async def process_text_files(input_dir: str, output_file: str, api_url: str, model_name: str):
    """
    Processes all text files in the input directory and saves the extracted data as a CSV file.
    """
    supported_extensions = [".txt"]
    files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if os.path.splitext(f)[1].lower() in supported_extensions
    ]

    if not files:
        logging.warning("No supported files found in the 'text_converted' directory.")
        return

    csv_rows = []

    logging.info(f"Processing {len(files)} files...")
    for file_path in tqdm(files, desc="Processing Files", unit="file"):
        try:
            # Read file with error handling
            try:
                with open(file_path, "r", encoding="utf-8", errors='replace') as f:
                    text_content = f.read()
            except UnicodeError:
                # Fallback to latin-1 if UTF-8 fails
                with open(file_path, "r", encoding="latin-1", errors='replace') as f:
                    text_content = f.read()

            corrected_text = await correct_spelling(text_content, api_url, model_name)
            course_info = extract_course_info(corrected_text)
            questions = extract_questions(corrected_text)
            document_id = generate_document_id(file_path)

            for question in questions:
                topic_name = await infer_topic_name(
                    question["question_text"], course_info["course_title"], api_url, model_name
                )

                instruction = (
                    f"Act as an expert in question generation. "
                    f"When you find the course titled '{course_info['course_title']}' "
                    f"with course number '{course_info['course_no']}', "
                    f"generate a new question related to the topic '{topic_name}'. "
                    f"The new question should be similar in style and complexity to the following example, "
                    f"but it must not repeat the same question: "
                    f"'{question['question_text']}'. "
                    f"Ensure the generated question aligns with the course content and topic."
                )

                input_text = (
                    f"Generate a question for the course id '{course_info['course_no']}', "
                    f"course name '{course_info['course_title']}' under the topic '{topic_name}' "
                    f"appropriate for marks {question['marks']}"
                )

                csv_rows.append({
                    "instruction": instruction,
                    "input": input_text,
                    "question": question["question_text"],
                    "course_no": course_info["course_no"],
                    "course_title": course_info["course_title"],
                    "marks": question["marks"],
                    "topic": topic_name,
                    "metadata_tag": document_id
                })

        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}", exc_info=True)

    if csv_rows:
        fieldnames = ["instruction", "input", "question", "course_no", "course_title", "marks", "topic", "metadata_tag"]
        write_csv_safely(csv_rows, output_file, fieldnames)
    else:
        logging.warning("❌ No valid data extracted from input files. No CSV file generated.")

class DocumentToPDFConverter:
    """Converts various document formats to PDF using LibreOffice"""
    def __init__(self):
        # Check if LibreOffice is installed
        try:
            subprocess.run(['which', 'libreoffice'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("LibreOffice not found. Please install it using:")
            print("sudo apt-get install libreoffice")
            raise

    def convert_to_pdf_libreoffice(self, input_path: str, output_dir: str) -> Optional[str]:
        """Convert document to PDF using LibreOffice"""
        try:
            # Create temporary directory for conversion
            with tempfile.TemporaryDirectory() as temp_dir:
                # Use LibreOffice to convert the document
                subprocess.run([
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', temp_dir,
                    input_path
                ], check=True, capture_output=True)
                # Get the output PDF path
                pdf_filename = Path(input_path).stem + '.pdf'
                temp_pdf_path = os.path.join(temp_dir, pdf_filename)
                if os.path.exists(temp_pdf_path):
                    output_path = os.path.join(output_dir, pdf_filename)
                    shutil.move(temp_pdf_path, output_path)
                    return output_path
            return None
        except Exception as e:
            print(f"Error converting to PDF: {str(e)}")
            return None

    def convert_html_to_pdf(self, input_path: str, output_path: str) -> bool:
        """Convert HTML to PDF using wkhtmltopdf"""
        try:
            # Check if wkhtmltopdf is installed
            if not shutil.which('wkhtmltopdf'):
                print("wkhtmltopdf not found. Please install it using:")
                print("sudo apt-get install wkhtmltopdf")
                return False
            subprocess.run(['wkhtmltopdf', input_path, output_path],
                         check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Error converting HTML to PDF: {str(e)}")
            return False

    def convert_markdown_to_pdf(self, input_path: str, output_path: str) -> bool:
        """Convert Markdown to PDF via HTML using wkhtmltopdf"""
        try:
            # First convert Markdown to HTML
            with open(input_path, 'r', encoding='utf-8') as md_file:
                md_content = md_file.read()
            html_content = markdown.markdown(md_content)
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as temp_html:
                temp_html.write(html_content)
                temp_html_path = temp_html.name
            # Convert HTML to PDF
            result = self.convert_html_to_pdf(temp_html_path, output_path)
            # Clean up temporary file
            os.unlink(temp_html_path)
            return result
        except Exception as e:
            print(f"Error converting Markdown to PDF: {str(e)}")
            return False

class PDFToTextConverter:
    """Converts PDF to text using PyMuPDF"""
    def convert_pdf_to_text(self, pdf_path: str) -> str:
        """Extract text from PDF with improved formatting"""
        try:
            text_content = []
            with fitz.open(pdf_path) as doc:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    # Get page text with blocks for better structure preservation
                    blocks = page.get_text("blocks")
                    # Sort blocks by vertical position then horizontal
                    blocks.sort(key=lambda b: (b[1], b[0]))
                    page_text = "\n".join(block[4] for block in blocks if block[4].strip())
                    if page_text.strip():
                        text_content.append(f"Page {page_num + 1}:\n{page_text}")
            return '\n\n'.join(text_content)
        except Exception as e:
            raise Exception(f"Error converting PDF to text: {str(e)}")

def process_directory(input_dir: str, output_dir: str):
    """Process all documents by converting to PDF first, then to text"""
    # Create output directories
    pdf_dir = os.path.join(output_dir, "pdf_converted")
    text_dir = os.path.join(output_dir, "text_converted")
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(text_dir, exist_ok=True)
    # Initialize converters
    pdf_converter = DocumentToPDFConverter()
    text_converter = PDFToTextConverter()
    # Process all files
    files = os.listdir(input_dir)
    print(f"Found {len(files)} files to process...")
    for file in tqdm(files, desc="Converting Documents"):
        input_path = os.path.join(input_dir, file)
        file_extension = Path(file).suffix.lower()
        file_name = Path(file).stem
        # Define output paths
        pdf_path = os.path.join(pdf_dir, f"{file_name}.pdf")
        text_path = os.path.join(text_dir, f"{file_name}.txt")
        try:
            # If file is already PDF, just copy it
            if file_extension == '.pdf':
                shutil.copy2(input_path, pdf_path)
            # For HTML and Markdown, use specific converters
            elif file_extension in ['.html', '.htm']:
                if not pdf_converter.convert_html_to_pdf(input_path, pdf_path):
                    continue
            elif file_extension == '.md':
                if not pdf_converter.convert_markdown_to_pdf(input_path, pdf_path):
                    continue
            # For other document types (DOCX, PPTX), use LibreOffice
            elif file_extension in ['.docx', '.pptx']:
                pdf_result = pdf_converter.convert_to_pdf_libreoffice(input_path, pdf_dir)
                if not pdf_result:
                    continue
            else:
                print(f"Unsupported file format: {file}")
                continue
            # Convert PDF to text
            text_content = text_converter.convert_pdf_to_text(pdf_path)
            # Save text content
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"✅ Processed: {file}")
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")

async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "question_papers")
    output_dir = os.path.join(script_dir, "final_stack")
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found: {input_dir}")
        return
    process_directory(input_dir, output_dir)

    # Process text files after conversion
    text_input_dir = os.path.join(output_dir, "text_converted")
    output_file = "fine_tuning_dataset.csv"
    api_url = "http://localhost:11434"
    model_name = "llama3.2"  # If using different Model change it here

    logging.info(f"Starting processing with the following configuration:")
    logging.info(f"Input directory: {text_input_dir}")
    logging.info(f"Output file: {output_file}")
    logging.info(f"API URL: {api_url}")
    logging.info(f"Model name: {model_name}")

    if not os.path.exists(text_input_dir) or not os.path.isdir(text_input_dir):
        logging.error(f"Directory not found: {text_input_dir}")
        return

    # Test API connection before processing
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    logging.error(f"API test failed: HTTP {response.status}")
                    return
                logging.info("API connection test successful")
    except Exception as e:
        logging.error(f"Could not connect to API: {str(e)}")
        return

    await process_text_files(text_input_dir, output_file, api_url, model_name)

if __name__ == "__main__":
    asyncio.run(main())