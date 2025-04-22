

---

# ✨📚 **Question Paper Processor** – *Powering the Future of Fine-Tuned LLMs*

Transform raw, unstructured academic question papers into beautifully structured, machine-readable datasets tailored for **Large Language Model (LLM) fine-tuning**.  
Whether you're an **AI researcher**, **educator**, or **institutional innovator**, the **Question Paper Processor** is your all-in-one pipeline to supercharge curriculum-specific LLMs.

---

## 📘 **Table of Contents**
1. [🔍 Overview](#-overview)  
2. [🚀 Features](#-features)  
3. [⚙️ Installation](#-installation)  
4. [🛠 Usage](#-usage)  
5. [📊 Expected Output](#-expected-output)  
6. [📂 Directory Structure](#-directory-structure)  
7. [📦 Dependencies](#-dependencies)  
8. [🤖 LLM Configuration](#-llm-configuration)

---

## 🔍 **Overview**

The **Question Paper Processor** is an intelligent, end-to-end system that:
- 📄 Converts DOCX, PPTX, HTML, and Markdown files into PDFs.
- 🧠 Extracts clean, structured text from PDFs — including complex mathematical notation (converted to LaTeX).
- 🧾 Automatically detects metadata (Course No., Course Title, Marks).
- 🧮 Converts equations into accurate LaTeX syntax.
- 🧠 Uses **LLMs** to infer the **topic** for every question.
- 📊 Outputs pristine, ready-to-train datasets in **CSV** and **JSON** formats — perfectly formatted for **LLM fine-tuning**.

---

## 🚀 **Features**

✨ **Multi-Format Support** – Seamlessly processes DOCX, PPTX, HTML, Markdown, and PDF files.

🧠 **LLM-Powered Intelligence** – Uses vision and instruction models to extract structure, infer topics, and detect metadata.

📐 **LaTeX-Enhanced Output** – Ensures math expressions are LaTeX-ready for accurate rendering and training.

🎯 **High-Quality Dataset Creation** – Outputs optimized datasets with `instruction`, `input`, `question`, `marks`, `topics`, and more.

🛠 **Robust Error Handling** – Logs all operations in detail, helping you debug and iterate quickly.

🌐 **Dual Backend Support** – Compatible with both **Ollama** and **VLLM** backends for flexible model orchestration.

---

## ⚙️ **Installation**

### 🧾 Prerequisites
1. 🐍 **Python 3.10**: Ensure Python 3.10 is installed.
2. 🔧 **System Dependencies**: `LibreOffice` and `wkhtmltopdf` for document conversion.

### 📥 Install Steps

```bash
# 1. Clone the repository
git clone git@github.com:spandaai/spandaai-platform.git
cd spandaai-platform/domains/EdTech/training/Datasets/dataset_pipelines/question_paper_processor_vlm
 ```

```bash
# 2. Run the installation script
chmod +x installation.sh
./installation.sh
 ```
  This script will:
   - Verify Python 3.10 installation.
   - Install system dependencies (`LibreOffice`, `wkhtmltopdf`).
   - Set up a Python virtual environment.
   - Install Python dependencies from `requirements.txt`.

```bash
# 3. Activate your environment
source venv/bin/activate
pip list  # Confirm packages are installed
```

---

## 🛠 **Usage**

### 📁 Step 1: Add Your Files
Place all question paper files (`.pdf`, `.docx`, `.pptx`, `.html`, `.md`) in the `question_papers/` folder.

### ⚙️ Step 2: Set Environment Variables
Update `.env` to choose between **Ollama** (default) or **VLLM**.

```env
# Default: Ollama (locally running)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL_FOR_OCR=llama3.2-vision
OLLAMA_MODEL_FOR_EXTRACTION=llama3.2-vision
OLLAMA_MODEL_FOR_TOPIC=llama3.2-vision

# Option: Uncomment to use VLLM
# VLLM_URL_FOR_OCR=http://vllmnemotrontext:8001/v1/chat/completions
# VLLM_MODEL_FOR_OCR=AMead10/Llama-3.2-3B-Instruct-AWQ
```

Ensure your chosen LLM server is up and models are pulled.

### ▶️ Step 3: Run the Script

```bash
python qp_dataset_vlm.py
```

### 🔎 Step 4: Explore Outputs
- Extracted text → `final_stack/text_converted/`
- Final datasets → `fine_tuning_dataset.csv`, `fine_tuning_dataset.json`
- Logs → `qp_dataset.log`

---

### **Intermediate Files**
📂 **PDF Files** – Converted from DOCX, PPTX, HTML, Markdown → `final_stack/pdf_converted/`

📂 **Text Files** – Extracted text from PDFs → `final_stack/text_converted/`

---


## 📊 **Expected Output**

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



### 🧾 Sample CSV Output
| instruction               | input                                           | question                                       | course_no | course_title         | marks | topic           | metadata_tag |
|---------------------------|--------------------------------------------------|------------------------------------------------|-----------|-----------------------|-------|------------------|---------------|
| Act as an expert in question generation...    | Generate a question for the course id...   | What is the time complexity of binary search? | CS101     | Algorithms            | 10    | Binary Search    | a1b2c3d4      |

### 📁 Intermediate Artifacts
- ✅ `final_stack/pdf_converted/` → All input files converted to PDF.
- ✅ `final_stack/text_converted/` → Cleaned & structured text output.
- ✅ `qp_dataset.log` → Detailed execution log for full transparency.

---

## 📂 **Directory Structure**
```
question-paper-processor/
├── installation.sh               # One-step setup
├── requirements.txt              # Python dependencies
├── qp_dataset.py                 # Core processing logic
├── .env                          # LLM configuration file
├── question_papers/              # Input files
├── final_stack/                  # All generated outputs
│   ├── pdf_converted/            # PDFs from input formats
│   ├── text_converted/           # Extracted text files
├── fine_tuning_dataset.csv       # Final dataset for training
├── fine_tuning_dataset.json      # Same dataset in JSON format
└── qp_dataset.log                # Logs for all pipeline steps
```

---

## 📦 **Dependencies**

### 🖥 System
- 🖥 **LibreOffice** – Converts DOCX, PPTX to PDF.
- 🌐 **wkhtmltopdf** – Converts HTML, Markdown to PDF.

### 🐍 Python
Install with:

```bash
pip install -r requirements.txt
```

Key packages:
- `PyMuPDF` – PDF parsing.
- `tqdm` – Beautiful progress bars.
- `httpx` – Async LLM calls.
- `dotenv`, `json5`, `logging`, `asyncio` – Environment management, logging, and async magic.

---

## 🤖 **LLM Configuration**

### 🔧 Ollama (Default)
- Local URL: `http://localhost:11434`
- Models used: `llama3.2-vision`
```bash
ollama pull llama3.2-vision
```

### 🔄 Switch to VLLM
Update `.env`:
```env
VLLM_URL_FOR_OCR=http://vllmnemotrontext:8001/v1/chat/completions
VLLM_MODEL_FOR_OCR=AMead10/Llama-3.2-3B-Instruct-AWQ
```

💡 **Auto-Fallback Logic** – If both are configured, **VLLM is prioritized**. If neither is running, the script exits with a warning.

---

🎓 **Train Smarter. Fine-Tune Faster. Build Better.**  
With **Question Paper Processor**, your LLMs learn from the best: real academic content, cleanly structured and semantically enriched.

---

🔥 **Ready to revolutionize how your LLM learns?**  
**Let’s process some papers!** 🧠📄

---