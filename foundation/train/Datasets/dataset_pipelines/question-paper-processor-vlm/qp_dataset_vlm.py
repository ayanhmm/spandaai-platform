import os
import csv
import json
import hashlib
import asyncio
import logging
import fitz  # PyMuPDF
import httpx
import tempfile
import shutil
import subprocess
from pathlib import Path
from tqdm import tqdm
from enum import Enum
from typing import Optional, AsyncGenerator, Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qp_dataset.log'),
        logging.StreamHandler()
    ]
)

class CancellationToken:
    def __init__(self):
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

class ModelType(Enum):
    OCR = "OCR"  # For OCR and LaTeX conversion
    EXTRACTION = "EXTRACTION"  # For information extraction
    TOPIC = "TOPIC"  # For topic inference

class EnvConfig:
    def __init__(self):
        # VLLM Configuration
        self.vllm_urls = {
            ModelType.OCR: os.getenv("VLLM_URL_FOR_OCR"),
            ModelType.EXTRACTION: os.getenv("VLLM_URL_FOR_EXTRACTION"),
            ModelType.TOPIC: os.getenv("VLLM_URL_FOR_TOPIC"),
        }
        self.vllm_models = {
            ModelType.OCR: os.getenv("VLLM_MODEL_FOR_OCR"),
            ModelType.EXTRACTION: os.getenv("VLLM_MODEL_FOR_EXTRACTION"),
            ModelType.TOPIC: os.getenv("VLLM_MODEL_FOR_TOPIC"),
        }
        
        # Ollama Configuration
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_models = {
            ModelType.OCR: os.getenv("OLLAMA_MODEL_FOR_OCR", "llama3.2"),
            ModelType.EXTRACTION: os.getenv("OLLAMA_MODEL_FOR_EXTRACTION", "llama3.2"),
            ModelType.TOPIC: os.getenv("OLLAMA_MODEL_FOR_TOPIC", "llama3.2"),
        }
    
    def is_vllm_available(self, model_type: ModelType) -> bool:
        """Check if VLLM is configured and available for specific model type"""
        return bool(self.vllm_urls.get(model_type) and self.vllm_models.get(model_type))
    
    def is_ollama_available(self, model_type: ModelType) -> bool:
        """Check if Ollama is configured and available for specific model type"""
        return bool(self.ollama_url and self.ollama_models.get(model_type))
    
    def get_model_and_url(self, model_type: ModelType) -> tuple[Optional[str], Optional[str]]:
        """Get the appropriate model and URL based on availability"""
        # First try VLLM
        if self.is_vllm_available(model_type):
            return self.vllm_models[model_type], self.vllm_urls[model_type]
        # Then try Ollama
        elif self.is_ollama_available(model_type):
            return self.ollama_models[model_type], self.ollama_url
        return None, None

async def invoke_llm(
    system_prompt: str,
    user_prompt: str,
    model_type: ModelType,
    config: Optional[EnvConfig] = None
) -> dict:
    """
    Unified interface for invoking LLM models. Automatically chooses between VLLM and Ollama
    based on availability, with priority given to VLLM.
    """
    if config is None:
        config = EnvConfig()
    
    model, url = config.get_model_and_url(model_type)
    
    if not model or not url:
        return {"error": f"No LLM service available for model type {model_type.value}"}
    
    if config.is_vllm_available(model_type):
        return await invoke_llm_vllm(system_prompt, user_prompt, model, url)
    else:
        return await invoke_llm_ollama(system_prompt, user_prompt, model, url)

async def invoke_llm_vllm(
    system_prompt: str, 
    user_prompt: str, 
    model: str,
    url: str,
    temperature: float = 0.2,  # Lower temperature for more deterministic outputs
    top_p: float = 0.9,
    top_k: int = 10,
) -> dict:
    """Invoke VLLM with specified parameters"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=None)
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                ai_msg = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {"answer": ai_msg}
            else:
                logging.error(f"VLLM Error: {response.status_code} - {response.text}")
                return {"error": response.text}
    
    except Exception as e:
        logging.error(f"VLLM error occurred: {str(e)}")
        return {"error": str(e)}

async def invoke_llm_ollama(
    system_prompt: str, 
    user_prompt: str, 
    model: str,
    url: str,
) -> dict:
    """Invoke Ollama with specified parameters"""
    prompt = f"""
{system_prompt}

{user_prompt}
"""
    payload = {
        "prompt": prompt,
        "model": model,
        "options": {
            "top_k": 10,
            "top_p": 0.9,
            "temperature": 0.2,  # Lower temperature for more deterministic outputs
            "num_ctx": 8192  # Increased context window for longer documents
        },
        "stream": False
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{url}/api/generate", json=payload, timeout=None)
            
            if response.status_code == 200:
                response_data = json.loads(response.content)
                ai_msg = response_data.get('response', '')
                return {"answer": ai_msg}
            else:
                logging.error(f"Ollama Error: {response.status_code} - {response.text}")
                return {"error": response.text}
    except Exception as e:
        logging.error(f"Ollama error occurred: {str(e)}")
        return {"error": str(e)}

def generate_document_id(file_path: str) -> str:
    """Generates a unique identifier for a document based on its file path."""
    return hashlib.sha256(file_path.encode()).hexdigest()[:8]

async def extract_text_with_latex(pdf_content: str, config: EnvConfig) -> str:
    """
    Use LLM to extract text from PDF content and convert mathematical equations to LaTeX
    """
    system_prompt = """
    You are an expert OCR and LaTeX conversion system specialized in academic and scientific documents, particularly question papers. Your primary task is to accurately convert mathematical notation to LaTeX.

    SPECIFIC INSTRUCTIONS:
    1. Preserve the original structure of the document including question numbers, sections, and formatting
    2. Convert ALL mathematical expressions to proper LaTeX syntax
    3. Pay special attention to:
       - Fractions (convert to \\frac{numerator}{denominator})
       - Square roots (convert to \\sqrt{expression})
       - Superscripts and subscripts (use ^ and _ notation)
       - Greek letters (α → \\alpha, β → \\beta, etc.)
       - Mathematical operators (× → \\times, ÷ → \\div, etc.)
       - Special characters (≤ → \\leq, ≥ → \\geq, ≠ → \\neq, etc.)
       - Powers with base 10 (10⁶ → 10^6)

    CONVERSION EXAMPLES:
    - "3x² + 4y = 7" → "3x^2 + 4y = 7"
    - "a/b + c" → "\\frac{a}{b} + c"
    - "√(x²+y²)" → "\\sqrt{x^2 + y^2}"
    - "∫₀¹ f(x)dx" → "\\int_{0}^{1} f(x)dx"
    - "α + β = γ" → "\\alpha + \\beta = \\gamma"
    - "100MB/minute" → "100\\text{MB/minute}"

    For inline equations, enclose them in $ symbols: $equation here$
    For display equations, enclose them in $$ symbols: $$equation here$$
    
    Ensure that you capture the complete mathematical meaning in every equation.
    """
    
    user_prompt = f"""
    Below is the raw text content extracted from a PDF question paper. 
    Please clean up the text and convert any mathematical equations to LaTeX format:
    
    {pdf_content}
    
    Mathematical expressions should be enclosed in $ symbols for inline math and $$ symbols for display math.
    """
    
    result = await invoke_llm(system_prompt, user_prompt, ModelType.OCR, config)
    if "error" in result:
        logging.error(f"Error in OCR processing: {result['error']}")
        return pdf_content  # Return original content if error occurs
    
    return result["answer"]

async def extract_course_info(text_content: str, config: EnvConfig) -> dict:
    """
    Uses LLM to extract course information from the text content
    """
    system_prompt = """
    You are an expert information extraction system. Your task is to extract and structure key course information 
    from an academic document. Extract the following fields:
    - Course No/Code
    - Course Title
    
    Return ONLY a valid JSON object with these fields. If any field cannot be found, use "Unknown" as the value.
    """
    
    user_prompt = f"""
    Extract the course information from the following text content:
    
    {text_content[:3000]}  # Using first part of document only to focus on header info
    
    Return the information in this format:
    {{
        "course_no": "course code or number here",
        "course_title": "course title here"
    }}
    """
    
    result = await invoke_llm(system_prompt, user_prompt, ModelType.EXTRACTION, config)
    if "error" in result:
        logging.error(f"Error extracting course info: {result['error']}")
        return {"course_no": "Unknown_Course_No", "course_title": "Unknown_Course_Title"}
    
    try:
        # Try to parse the LLM response as JSON
        json_str = result["answer"]
        # Find JSON object in the response if there's surrounding text
        json_start = json_str.find('{')
        json_end = json_str.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = json_str[json_start:json_end]
        
        course_info = json.loads(json_str)
        return {
            "course_no": course_info.get("course_no", "Unknown_Course_No"),
            "course_title": course_info.get("course_title", "Unknown_Course_Title")
        }
    except json.JSONDecodeError as e:
        logging.error(f"JSON parse error in course info: {e}, Response: {result['answer']}")
        return {"course_no": "Unknown_Course_No", "course_title": "Unknown_Course_Title"}

async def extract_questions(text_content: str, config: EnvConfig) -> list:
    """
    Uses LLM to extract questions from the text content with improved JSON handling
    """
    system_prompt = """
    You are an expert question extraction system for academic exam papers. Your task is to accurately identify and extract ONLY the questions as they appear in the original document, without adding any solutions, answers, or additional content.

    CRITICAL EXTRACTION RULES:
    1. Extract ONLY what appears in the original text - NEVER add any content that isn't present.
    2. DO NOT solve any equations or mathematical expressions.
    3. DO NOT complete any calculations that are left incomplete in the original.
    4. DO NOT provide any answers whatsoever.
    5. DO NOT generate any content - you are ONLY extracting existing content.
    6. PRESERVE the original text EXACTLY as it appears, including any incomplete equations.
    7. If an equation appears as "Find x when..." then leave it EXACTLY that way - DON'T solve for x.
    8. If a value is missing in the original, DO NOT fill it in.

    ABOUT MATH CONTENT:
    1. Convert mathematical expressions to LaTeX, but ONLY represent what's visibly in the text.
    2. NEVER add equality signs (=) or results that aren't in the original text.
    3. NEVER use \\approx or any other symbol to provide approximate answers.
    4. If an equation is left unsolved in the original, DO NOT solve it or complete it.
    5. TREAT all mathematical expressions as literal text to be preserved, not as problems to be solved.

    CRITICAL JSON FORMATTING REQUIREMENTS:
    - You MUST produce valid, parseable JSON.
    - For ALL LaTeX expressions, DOUBLE escape backslashes. Example: "\\\\alpha" not "\\alpha"
    - Do NOT include any control characters (ASCII < 32) except for normal whitespace.
    - Do NOT include any markdown formatting like ```json or ``` around your response.
    - Return ONLY the JSON array with no explanatory text before or after.

    YOUR ONLY ROLE IS TO ACCURATELY EXTRACT AND CONVERT THE ORIGINAL TEXT TO JSON FORMAT - NOT TO GENERATE ANSWERS.
    """
   
    user_prompt = f"""
    Extract all questions from the following exam paper content EXACTLY as they appear:
   
    {text_content}
   
    Return the information as a JSON array like this:
    [
        {{
            "question_number": "Q.1",
            "question_text": "Full question text with any equations in LaTeX (properly escaped for JSON)",
            "marks": "10"
        }},
        ...
    ]
   
    CRITICAL REMINDERS:
    1. Extract ONLY what appears in the original document - DO NOT add any new content.
    2. DO NOT solve any equations or complete any calculations.
    3. DO NOT generate answers to the questions.
    4. PRESERVE the questions exactly as they appear, even if they contain incomplete expressions.
    5. If a question asks to "Find x" or "Calculate y" - DO NOT provide x or y.
    6. For LaTeX expressions, use double backslashes: e.g., "\\\\alpha" not "\\alpha"
    7. Ensure the output is valid JSON with properly escaped characters.
    """
   
    result = await invoke_llm(system_prompt, user_prompt, ModelType.EXTRACTION, config)
    if "error" in result:
        logging.error(f"Error extracting questions: {result['error']}")
        return []
    
    # Multiple parsing attempts with progressively more aggressive fixes
    parsing_attempts = [
        # Attempt 1: Try direct JSON parsing
        lambda resp: json.loads(resp.strip()),
        
        # Attempt 2: Try with json5 (more permissive parser)
        lambda resp: json5.loads(resp.strip()),
        
        # Attempt 3: Try to extract just the JSON array
        lambda resp: json.loads(resp[resp.find('['):resp.rfind(']')+1].strip()),
        
        # Attempt 4: Apply manual fixes then parse
        lambda resp: json.loads(manual_json_fix(resp)),
        
        # Attempt 5: Manual object extraction as last resort
        lambda resp: extract_questions_as_objects(resp)
    ]
    
    response_text = result["answer"]
    
    # Try each parsing method
    for attempt_num, parser in enumerate(parsing_attempts, 1):
        try:
            questions = parser(response_text)
            logging.info(f"Successfully parsed questions using method {attempt_num}")
            return questions
        except Exception as e:
            if attempt_num < len(parsing_attempts):
                logging.warning(f"Parsing attempt {attempt_num} failed: {e}")
            else:
                logging.error(f"All parsing attempts failed: {e}")
    
    # If all attempts fail, return empty list
    return []

def extract_questions_as_objects(raw_response: str) -> list:
    """
    Fallback method to extract question objects from raw LLM output when JSON parsing fails.
    Uses pattern matching to identify and extract question objects manually.
    """
    questions = []
    # Look for question objects in the text
    import re
    # Find all text that looks like question objects
    # This regex looks for patterns like {"question_number": "Q.1", ...}
    question_pattern = r'{\s*"question_number"\s*:\s*"[^"]+"\s*,\s*"question_text"\s*:\s*"[^"]*(?:\\.[^"]*)*"\s*,\s*"marks"\s*:\s*"[^"]*"\s*}'
    
    # Find all matches
    matches = re.findall(question_pattern, raw_response, re.DOTALL)
    
    for match in matches:
        try:
            # Extract the question number
            q_num_match = re.search(r'"question_number"\s*:\s*"([^"]+)"', match)
            q_text_match = re.search(r'"question_text"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', match, re.DOTALL)
            marks_match = re.search(r'"marks"\s*:\s*"([^"]*)"', match)
            
            if q_num_match and q_text_match:
                q_num = q_num_match.group(1)
                q_text = q_text_match.group(1)
                marks = marks_match.group(1) if marks_match else ""
                
                # Sanitize text (remove problematic escapes)
                q_text = q_text.replace('\\\\', '\\')  # Handle double escaped backslashes
                
                questions.append({
                    "question_number": q_num,
                    "question_text": q_text,
                    "marks": marks
                })
        except Exception as e:
            logging.warning(f"Failed to extract question: {e}")
            continue
    
    if not questions:
        # As a last resort, try to manually find question blocks by numbered patterns
        question_blocks = re.split(r'(?:\n|^)(?:Q\.\s*\d+|\d+\.|\(Q\d+\))\s*', raw_response)
        if len(question_blocks) > 1:  # Skip the first split which is usually empty
            for i, block in enumerate(question_blocks[1:], 1):
                if block.strip():
                    questions.append({
                        "question_number": f"Q.{i}",
                        "question_text": block.strip(),
                        "marks": ""
                    })
    
    return questions

def preprocess_llm_json_response(response_text: str) -> str:
    """
    Pre-process an LLM response to improve JSON parsing chances
    """
    # Remove markdown code blocks
    response_text = response_text.replace('```json', '').replace('```', '')
    
    # Find JSON content
    import re
    json_match = re.search(r'(\[\s*\{.*\}\s*\])', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(1)
    
    # Normalize control characters
    response_text = ''.join(ch if ord(ch) >= 32 or ch in '\n\r\t' else ' ' for ch in response_text)
    
    # Fix LaTeX escape sequences in a safer way
    def normalize_latex(match):
        content = match.group(1)
        # First standardize to single backslashes
        content = re.sub(r'\\{2,}', r'\\', content)
        # Then double them all for JSON
        content = content.replace('\\', '\\\\')
        return f'"{content}"'
    
    # Process all string literals
    response_text = re.sub(r'"([^"]*(?:\\.[^"]*)*)"', normalize_latex, response_text)
    
    return response_text
            
def manual_json_fix(json_str: str) -> str:
    """
    More robust JSON repair for LLM-generated JSON with LaTeX content
    """
    # Remove code block markers
    json_str = json_str.replace('```json', '').replace('```', '')
    
    # Try to extract just the JSON array
    import re
    array_match = re.search(r'\[\s*{.+}\s*\]', json_str, re.DOTALL)
    if array_match:
        json_str = array_match.group(0)
    
    # Handle control characters
    json_str = ''.join(ch for ch in json_str if ord(ch) >= 32 or ch in '\n\r\t')
    
    # Fix common LaTeX escaping issues
    def fix_latex_escapes(match):
        latex = match.group(1)
        # First standardize all backslashes to be single
        latex = re.sub(r'\\{2,}', r'\\', latex)
        # Then double escape all of them for JSON
        latex = latex.replace('\\', '\\\\')
        return f'"{latex}"'
    
    # Find all strings in the JSON and process them
    processed_str = re.sub(r'"((?:[^"\\]|\\.)*)(?:\\\\)*"', fix_latex_escapes, json_str)
    
    # Fix other JSON syntax issues
    processed_str = processed_str.replace('"{', '{').replace('}"', '}')
    processed_str = processed_str.replace('\\"', '"')
    processed_str = processed_str.replace('"\\\\', '"\\')
    processed_str = processed_str.replace('\\\\"', '\\"')
    
    # Fix quotes
    processed_str = processed_str.replace('"', '"').replace('"', '"')
    
    return processed_str

async def infer_topic_name(question_text: str, course_title: str, config: EnvConfig) -> str:
    """
    Infers the topic name for a question based on the course title and question text.
    """
    system_prompt = """
    You are an expert in academic curriculum classification for university courses. Your task is to infer the precise topic or subject area of a given exam question based on its content and the course context.

    GUIDELINES FOR TOPIC IDENTIFICATION:
    1. Analyze the technical vocabulary, concepts, and problem domain in the question
    2. Consider the broader course context (course title, code, level)
    3. Identify the specific subfield or knowledge area being tested
    4. Be precise - use standard terminology from the academic discipline
    5. For complex questions covering multiple aspects, identify the primary topic

    For example:
    - Instead of just "Mathematics", specify "Differential Equations"
    - Instead of just "Computer Science", specify "Database Indexing"
    - Instead of just "Physics", specify "Electromagnetic Induction"

    Based on your analysis, provide ONLY the specific topic name as a standard discipline term - no explanations or additional text.
    """
    
    user_prompt = f"""
    Based on the following question from the course titled '{course_title}', 
    what specific topic does this question cover?
    
    Question: {question_text}
    
    Return ONLY the topic name as a single word or short phrase.
    """
    
    result = await invoke_llm(system_prompt, user_prompt, ModelType.TOPIC, config)
    if "error" in result:
        logging.error(f"Error inferring topic: {result['error']}")
        return "Unknown_Topic"
    
    # Clean up the response - take first line only as topic
    topic = result["answer"].strip().split('\n')[0]
    return topic

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

def write_json_safely(data: Dict[str, Any], output_file: str):
    """
    Writes data to JSON with proper UTF-8 encoding and error handling.
    """
    try:
        # Process any LaTeX in the data
        processed_data = sanitize_json_data(data)
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(processed_data, jsonfile, ensure_ascii=False, indent=2)
        logging.info(f"✅ Data successfully written to {output_file}")
    except Exception as e:
        logging.error(f"Error writing JSON: {str(e)}", exc_info=True)
        raise

def sanitize_latex_for_json(text: str) -> str:
    """
    Prepare LaTeX text for JSON serialization by properly escaping backslashes
    """
    # Double escape any backslashes
    return text.replace('\\', '\\\\')

def sanitize_json_data(data):
    """
    Recursively process all string values in a data structure to safely handle LaTeX
    """
    if isinstance(data, str):
        return sanitize_latex_for_json(data)
    elif isinstance(data, dict):
        return {k: sanitize_json_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json_data(item) for item in data]
    else:
        return data

async def process_text_files(input_dir: str, output_file: str, config: EnvConfig):
    """
    Processes all text files in the input directory and saves the extracted data as a JSON file.
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

    dataset = []
    file_results = {}

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

            document_id = generate_document_id(file_path)
            
            # Process with LLM for OCR and LaTeX conversion
            processed_text = await extract_text_with_latex(text_content, config)
            
            # Extract course information
            course_info = await extract_course_info(processed_text, config)
            
            # Extract questions
            questions = await extract_questions(processed_text, config)
            
            logging.info(f"Extracted {len(questions)} questions from {os.path.basename(file_path)}")
            
            file_result = {
                "document_id": document_id,
                "filename": os.path.basename(file_path),
                "course_info": course_info,
                "questions": []
            }
            
            # Process each question
            for question in questions:
                topic_name = await infer_topic_name(
                    question["question_text"], course_info["course_title"], config
                )
                
                question_item = {
                    "question_number": question["question_number"],
                    "question_text": question["question_text"],
                    "marks": question["marks"],
                    "topic": topic_name,
                    "course_no": course_info["course_no"],
                    "course_title": course_info["course_title"]
                }
                
                # Add to file result
                file_result["questions"].append(question_item)
                
                # Add to dataset for fine-tuning
                instruction = (
                    f"Act as an expert in question generation. "
                    f"When you find the course titled '{course_info['course_title']}' "
                    f"with course number '{course_info['course_no']}', "
                    f"generate a new question related to the topic '{topic_name}'. "
                    f"The new question should be similar in style and complexity to the following example, "
                    f"but it must not repeat the same question: "
                    f"Ensure the generated question aligns with the course content and topic."
                )

                input_text = (
                    f"Generate a question for the course id '{course_info['course_no']}', "
                    f"course name '{course_info['course_title']}' under the topic '{topic_name}' "
                    f"appropriate for marks {question['marks']}"
                )
                
                dataset.append({
                    "instruction": instruction,
                    "input": input_text,
                    "question": question["question_text"],
                    "course_no": course_info["course_no"],
                    "course_title": course_info["course_title"],
                    "marks": question["marks"],
                    "topic": topic_name,
                    "metadata_tag": document_id
                })
            
            # Save individual file results
            file_output = os.path.join(os.path.dirname(output_file), f"file_{document_id}.json")
            write_json_safely(file_result, file_output)
            file_results[document_id] = file_result

        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}", exc_info=True)

    if dataset:
        # Save combined dataset as JSON
        output_data = {
            "dataset": dataset,
            "file_results": file_results
        }
        write_json_safely(output_data, output_file)
        
        # Also save as CSV for compatibility
        csv_output = os.path.splitext(output_file)[0] + ".csv"
        fieldnames = ["instruction", "input", "question", "course_no", "course_title", "marks", "topic", "metadata_tag"]
        with open(csv_output, 'w', encoding='utf-8-sig', newline='', errors='replace') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in dataset:
                writer.writerow({k: item.get(k, "") for k in fieldnames})
        logging.info(f"✅ Data also written to CSV: {csv_output}")
    else:
        logging.warning("❌ No valid data extracted from input files. No files generated.")

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
            # For other document types (DOCX, PPTX), use LibreOffice
            elif file_extension in ['.docx', '.pptx', '.doc', '.html', '.htm', '.md']:
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

async def test_llm_connection(config: EnvConfig) -> bool:
    """Test LLM connection before processing"""
    for model_type in [ModelType.OCR, ModelType.EXTRACTION, ModelType.TOPIC]:
        model, url = config.get_model_and_url(model_type)
        if not model or not url:
            logging.warning(f"No model/URL configured for {model_type.value}")
            continue

        try:
            if url.endswith('/api/generate'):
                base_url = url.replace('/api/generate', '')
            else:
                base_url = url
                
            async with httpx.AsyncClient() as session:
                # Just a simple GET to see if the service is up
                response = await session.get(base_url, timeout=5)
                if response.status_code == 200:
                    logging.info(f"✅ Connection test successful for {model_type.value}")
                    return True
                else:
                    logging.error(f"Connection test failed for {model_type.value}: HTTP {response.status_code}")
        except Exception as e:
            logging.error(f"Connection test error for {model_type.value}: {str(e)}")
    
    return False

async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "question_papers")
    output_dir = os.path.join(script_dir, "final_stack")
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created input directory: {input_dir}")
        print("Please add question papers to this directory and run the script again.")
        return
    
    # Initialize configuration
    config = EnvConfig()
    
    # Test LLM connection
    connection_ok = await test_llm_connection(config)
    if not connection_ok:
        print("⚠️ Warning: Could not connect to LLM service. Check your configuration.")
        if input("Continue anyway? (y/n): ").lower() != 'y':
            return
    
    # Process documents to PDF and text
    os.makedirs(output_dir, exist_ok=True)
    process_directory(input_dir, output_dir)

    # Process text files with LLM
    text_input_dir = os.path.join(output_dir, "text_converted")
    output_file = os.path.join(output_dir, "fine_tuning_dataset.json")
    
    logging.info(f"Starting processing with the following configuration:")
    logging.info(f"Input directory: {text_input_dir}")
    logging.info(f"Output file: {output_file}")
    
    if not os.path.exists(text_input_dir) or not os.path.isdir(text_input_dir):
        logging.error(f"Directory not found: {text_input_dir}")
        return

    await process_text_files(text_input_dir, output_file, config)
    print("✅ Processing complete!")

if __name__ == "__main__":
    asyncio.run(main())