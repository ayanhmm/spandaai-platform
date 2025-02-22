# 🌟 **Question Paper Processor**

**Question Paper Processor** is a powerful Python-based tool that automates the extraction, processing, and transformation of question papers into structured datasets. It supports multiple document formats (PDF, DOCX, PPTX, HTML, Markdown) and leverages advanced libraries and APIs for text processing, spelling correction, and topic inference.

---

## 📌 **Table of Contents**

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Expected Output](#expected-output)
6. [Directory Structure](#directory-structure)
7. [Dependencies](#dependencies)

---

## 🔍 **Overview**

The **Question Paper Processor** automates:
- 📄 **Multi-format conversion**: Converts DOCX, PPTX, HTML, and Markdown into PDFs.
- 📝 **Text extraction**: Extracts text from PDFs while maintaining structure.
- 🏷 **Metadata identification**: Extracts course information (Course No., Course Title) and question details.
- 🔍 **Spelling correction**: Uses an LLM API to fix spelling errors in extracted text.
- 📚 **Topic inference**: Predicts topic names based on course title and question text.
- 📊 **Structured dataset generation**: Creates a well-organized CSV dataset containing all extracted details.

This tool is perfect for educators, researchers, and institutions aiming to convert unstructured question papers into structured datasets for **LLM FineTuning**.

---

## 🚀 **Features**

✅ **Multi-format Support** – Processes PDF, DOCX, PPTX, HTML, and Markdown files.

✅ **Text Extraction** – Extracts clean, structured text from documents.

✅ **Spelling Correction** – Uses an LLM API to correct text errors.

✅ **Topic Inference** – Automatically infers topic names for questions.

✅ **Dataset Generation** – Outputs a structured CSV ready for machine learning.

✅ **Error Handling** – Robust error handling and logging for debugging.

---

## ⚙️ **Installation**

### **Prerequisites**
1. 🐍 **Python 3.10**: Ensure Python 3.10 is installed.
2. 🔧 **System Dependencies**: `LibreOffice` and `wkhtmltopdf` for document conversion.

### **Installation Steps**

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/question-paper-processor.git
   cd question-paper-processor
   ```

2. Run the installation script:
   ```bash
   chmod +x installation.sh
   ./installation.sh
   ```

   This script will:
   - Verify Python 3.10 installation.
   - Install system dependencies (`LibreOffice`, `wkhtmltopdf`).
   - Set up a Python virtual environment.
   - Install Python dependencies from `requirements.txt`.

3. Verify installation:
   ```bash
   source venv/bin/activate
   pip list
   ```
---

## 🛠 **Usage**

### **Step 1: Place Input Files**
Place your question paper files (PDF, DOCX, PPTX, HTML, Markdown) in the `question_papers` directory.

### **Step 2: Configure the Tool**
- Update `api_url` and `model_name` in `qp_dataset.py` if using a custom LLM API.
- Ensure the LLM API server is running.

### **Step 3: Run the Script**
```bash
python qp_dataset.py
```

### **Step 4: View Output**
- Processed text files → `final_stack/text_converted/`
- Final dataset → `fine_tuning_dataset.csv`

---

## 📊 **Expected Output**

### **Intermediate Files**
📂 **PDF Files** – Converted from DOCX, PPTX, HTML, Markdown → `final_stack/pdf_converted/`

📂 **Text Files** – Extracted text from PDFs → `final_stack/text_converted/`

### **Final Dataset: `fine_tuning_dataset.csv`**
| Field          | Description                                          |
|---------------|--------------------------------------------------|
| `instruction`  | Instruction for generating similar questions.    |
| `input`        | Context input for question generation.           |
| `question`     | Extracted question text.                        |
| `course_no`    | Course number (e.g., CS101).                     |
| `course_title` | Course title (e.g., Introduction to AI).        |
| `marks`        | Marks allocated to the question.                |
| `topic`        | Inferred topic of the question.                 |
| `metadata_tag` | Unique document identifier.                     |

🔹 **Example Row:**
```csv
instruction,input,question,course_no,course_title,marks,topic,metadata_tag
"Generate a question for CS101...", "What is the time complexity of binary search?", "CS101", "Algorithms", "10", "Binary Search", "a1b2c3d4"
```

📜 **Logs** → Stored in `qp_dataset.log` for debugging.

---

## 📂 **Directory Structure**
```
question-paper-processor/
├── installation.sh          # Installation script
├── requirements.txt         # Python dependencies
├── qp_dataset.py            # Main processing script
├── question_papers/         # Input question papers directory
├── final_stack/             # Output directory
│   ├── pdf_converted/       # Converted PDFs
│   └── text_converted/      # Extracted text files
└── fine_tuning_dataset.csv  # Final dataset
```

---

## 📦 **Dependencies**

### **System Dependencies**
- 🖥 **LibreOffice** – Converts DOCX, PPTX to PDF.
- 🌐 **wkhtmltopdf** – Converts HTML, Markdown to PDF.

### **Python Libraries**
- `tqdm` – Progress tracking.
- `PyMuPDF` – PDF text extraction.
- `python-docx` – DOCX file processing.
- `python-pptx` – PPTX file processing.
- `beautifulsoup4` – HTML parsing.
- `markdown` – Converts Markdown to HTML.
- `aiohttp` – Asynchronous API requests.

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

🚀 **Happy Processing!** 🎉

