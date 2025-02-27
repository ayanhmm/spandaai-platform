# Comprehensive Kong API Gateway Endpoint Documentation for EdTech domain

## Introduction

This document outlines all endpoints exposed through the Kong API Gateway for the educational document analysis system. The system provides services for dissertation analysis, data preprocessing, educational AI agents, and question generation.

## Base URL
```
http://<host>:8090
```

---

# 1. Document Analysis Service

## 1.1 Real-time Analysis (WebSocket)
```
WS /api/ws/dissertation_analysis
```

**Purpose:** Enables real-time analysis of dissertations with streaming updates on analysis progress. This WebSocket endpoint establishes a persistent connection that allows the client to receive incremental updates as the analysis progresses, providing transparency into the analysis process.

**Detailed Description:** When connecting to this WebSocket endpoint, the client must send an initial message containing the dissertation content and rubric information. The service will then begin analyzing the dissertation section by section, streaming progress updates and partial results as they become available. This real-time approach is particularly valuable for long documents where full analysis may take considerable time.

### Input Format
```json
{
    "rubric": {
        "<section_name>": {
            "criteria_explanation": "string",
            "score_explanation": "string",
            "criteria_output": "string"
        }
    },
    "pre_analysis": {
        "degree": "string",
        "name": "string",
        "topic": "string",
        "pre_analyzed_summary": "string"
    },
    "feedback": "string"
}
```

### Stream Responses
```json
// Progress Update
{
    "type": "progress",
    "data": {
        "message": "string",
        "percentage": "number",
        "section": "string"
    }
}

// Final Result
{
    "type": "result",
    "data": {
        "analysis": {
            "<section_name>": {
                "score": "number",
                "comments": "string",
                "recommendations": "string"
            }
        }
    }
}

// Error
{
    "type": "error",
    "data": {
        "message": "string",
        "code": "string"
    }
}
```

## 1.2 Document Analysis (REST)
```
POST /analyze
```

**Purpose:** Performs complete dissertation analysis in a single synchronous request, evaluating the document against provided criteria and returning detailed feedback.

**Detailed Description:** This endpoint accepts a dissertation document along with a rubric containing specific evaluation criteria. The service performs a comprehensive analysis of the entire document, applying the provided rubric to evaluate each section. Unlike the WebSocket endpoint, this REST endpoint processes the entire analysis in a single request-response cycle, making it suitable for smaller documents or when real-time updates aren't necessary.

### Input Format
```json
{
    "rubric": {
        "<section_name>": {
            "criteria_explanation": "string",
            "score_explanation": "string",
            "criteria_output": "string"
        }
    },
    "pre_analysis": {
        "degree": "string",
        "name": "string",
        "topic": "string",
        "pre_analyzed_summary": "string"
    },
    "feedback": "string"
}
```

### Output Format
```json
{
    "status": "success",
    "analysis": {
        "<section_name>": {
            "score": "number",
            "comments": "string",
            "recommendations": "string"
        }
    },
    "overall_score": "number",
    "summary": "string"
}
```

---

# 2. Educational AI Agents Service

## 2.1 Process Chunks
```
POST /api/process-chunks
```

**Purpose:** Processes large dissertation text in manageable chunks for parallel analysis, improving scalability for lengthy documents.

**Detailed Description:** This endpoint takes a long document that has been pre-divided into chunks and processes each chunk independently using AI analysis. The system prompt parameter guides the AI's behavior for each chunk. The batch size parameter controls parallel processing capacity. This approach enables efficient analysis of very large documents that might exceed token limits of AI models or would be inefficient to process as a single unit.

### Input Format
```json
{
    "chunks": ["string"],
    "system_prompt": "string",
    "batch_size": "number"
}
```

### Output Format
```json
{
    "processed_chunks": [
        {
            "chunk_id": "number",
            "analysis": "string",
            "key_points": ["string"]
        }
    ]
}
```

## 2.2 Summarize and Analyze
```
POST /api/summarize-analyze
```

**Purpose:** Generates concise summaries and in-depth analysis of text content, focusing on key points and insights.

**Detailed Description:** This endpoint takes raw text content and performs two key operations: summarization and analysis. The summarization condenses the input text while preserving essential information. The analysis component examines the content for key insights, arguments, patterns, or issues. The analysis_type parameter allows clients to specify what kind of analysis is desired (e.g., critical, thematic, structural).

### Input Format
```json
{
    "text": "string",
    "analysis_type": "string"
}
```

### Output Format
```json
{
    "summary": "string",
    "analysis": "string",
    "key_points": ["string"]
}
```

## 2.3 Information Extraction Endpoints

### Extract Name
```
POST /api/extract-name
```

**Purpose:** Extracts and identifies the author's name from dissertation text using NLP techniques.

**Detailed Description:** This specialized endpoint uses natural language processing to locate and extract the author's name from dissertation text. It can handle various document formats and conventions for displaying author information. The confidence score indicates how certain the system is about the extracted name. This endpoint is particularly useful for automating document management systems where author attribution is important.

#### Input Format
```json
{
    "text": "string"
}
```

#### Output Format
```json
{
    "name": "string",
    "confidence": "number"
}
```

### Extract Topic
```
POST /api/extract-topic
```

**Purpose:** Analyzes dissertation content to identify the main topic, subtopics, and relevant keywords.

**Detailed Description:** This endpoint performs semantic analysis on the text to determine its central topic and hierarchical structure of subtopics. Using NLP and thematic analysis techniques, it identifies the primary subject matter as well as subsidiary themes. The keywords list provides searchable terms that characterize the document's focus. This information is valuable for document classification, search indexing, and content recommendation systems.

#### Input Format
```json
{
    "text": "string"
}
```

#### Output Format
```json
{
    "main_topic": "string",
    "subtopics": ["string"],
    "keywords": ["string"]
}
```

### Extract Degree
```
POST /api/extract-degree
```

**Purpose:** Identifies and extracts degree information, field of study, and institution details from academic documents.

**Detailed Description:** This endpoint specializes in recognizing academic credentials within text. It can identify degree types (e.g., Ph.D., Master's, Bachelor's), fields of study, and the awarding institutions. This information is extracted using a combination of pattern matching and contextual analysis. The endpoint is particularly useful for academic document processing systems and credential verification workflows.

#### Input Format
```json
{
    "text": "string"
}
```

#### Output Format
```json
{
    "degree": "string",
    "field": "string",
    "institution": "string"
}
```

## 2.4 Scoring
```
POST /api/scoring
```

**Purpose:** Evaluates dissertation content against specific criteria to generate quantitative scores and qualitative feedback.

**Detailed Description:** This endpoint implements a customizable scoring system that applies weighted criteria to analyze academic content. Each criterion can be assigned different weights to reflect its importance in the overall assessment. The service provides both numerical scores and detailed written feedback for each criterion, along with specific recommendations for improvement. This endpoint is particularly valuable for automated grading systems, dissertation committees, and educational assessment tools.

### Input Format
```json
{
    "analysis": "string",
    "criteria": {
        "<criterion_name>": {
            "description": "string",
            "weight": "number"
        }
    },
    "score_guidelines": "string",
    "criteria_guidelines": "string",
    "feedback": "string"
}
```

### Output Format
```json
{
    "overall_score": "number",
    "criterion_scores": {
        "<criterion_name>": {
            "score": "number",
            "feedback": "string"
        }
    },
    "recommendations": ["string"]
}
```

## 2.5 Pre-Analysis

**Endpoint:**  
`POST /api/pre_analyze`

**Description:**  
Processes an entire document to extract key elements (degree, name, topic) and returns a pre-analyzed summary based on the document’s topic.

**Request Model:**  
- **QueryRequestDocument**  
  - `document` (string): The full text of the document.

**Example Request:**
```json
{
  "document": "Full document text goes here..."
}
```

**Response:**  
A JSON object with the following keys:
- `degree` (string): Extracted degree information (if applicable).
- `name` (string): Extracted author or originator name.
- `topic` (string): Extracted document topic.
- `pre_analyzed_summary` (string): A summary analysis of the document.

**Example Response:**
```json
{
  "degree": "PhD",
  "name": "John Doe",
  "topic": "Artificial Intelligence in Healthcare",
  "pre_analyzed_summary": "This document explores the impact of AI on healthcare systems by..."
}
```

---

# 3. Data Processing Service

## 3.1 Text Processing

### Chunk Text
```
POST /api/chunk-text
```

**Purpose:** Splits long text documents into semantically meaningful chunks to facilitate efficient processing and analysis.

**Detailed Description:** This endpoint implements an intelligent text segmentation algorithm that divides large documents into smaller, processable chunks. Rather than simple character or word count-based splitting, the service attempts to preserve semantic units like paragraphs, sections, or coherent ideas. The chunk_size parameter controls the approximate size of each chunk, while overlap allows for context preservation between adjacent chunks. This is essential for downstream NLP tasks that have token limits or benefit from parallel processing.

#### Input Format
```json
{
    "text": "string",
    "chunk_size": "number",
    "overlap": "number"
}
```

#### Output Format
```json
{
    "chunks": [
        {
            "text": "string",
            "length": "number",
            "index": "number"
        }
    ]
}
```

### First N Words
```
POST /api/first-n-words
```

**Purpose:** Extracts a specified number of words from the beginning of a text, useful for generating previews or summaries.

**Detailed Description:** This utility endpoint extracts the first N words from a given text while maintaining sentence integrity when possible. It's designed for creating document previews, introductory snippets, or sampling content. The service ensures that the extraction doesn't break in the middle of words and provides an accurate word count in the output. This functionality is particularly useful for content management systems, search result displays, and document indexing.

#### Input Format
```json
{
    "text": "string",
    "n_words": "number"
}
```

#### Output Format
```json
{
    "text": "string",
    "word_count": "number"
}
```

## 3.2 Image Processing

### Resize Image
```
POST /api/resize-image
```

**Purpose:** Resizes images while preserving aspect ratio and maintaining visual quality for use in analysis and documentation.

**Detailed Description:** This endpoint provides intelligent image resizing capabilities that respect aspect ratio constraints. It accepts min_size and max_size parameters to ensure the resulting image falls within appropriate dimensional boundaries. The service applies high-quality interpolation algorithms to maintain image clarity during resizing. This functionality is particularly important for normalizing images for machine learning models, optimizing storage requirements, or preparing images for consistent display in reports.

#### Input Format
```
Form Data:
- file: Image file
- max_size: number
- min_size: number
```

#### Output Format
```
Binary image data with Content-Type header
```

### Process Images Batch
```
POST /api/process-images-batch
```

**Purpose:** Processes multiple images in a single request, applying consistent transformations across a batch of files.

**Detailed Description:** This endpoint enables bulk processing of multiple images, applying the same transformations and optimizations to each. The batch_size parameter controls how many images are processed concurrently. For each processed image, the service returns metadata including the processed file location and dimensions. This capability is crucial for efficiently handling document sets with multiple images, such as illustrated reports, textbooks, or multi-page scanned documents.

#### Input Format
```
Form Data:
- files[]: Array of image files
- batch_size: number
```

#### Output Format
```json
{
    "results": [
        {
            "filename": "string",
            "processed_url": "string",
            "dimensions": {
                "width": "number",
                "height": "number"
            }
        }
    ]
}
```

## 3.3 Document Processing

### Health Check

Check if the API service is running properly.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Text Chunking

Split text into semantic chunks using LangChain's RecursiveCharacterTextSplitter.

**Endpoint:** `POST /api/chunk-text`

**Request Body:**
```json
{
  "text": "Your long text content goes here...",
  "chunk_size": 1000
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| text | string | Yes | - | Input text to be chunked |
| chunk_size | integer | No | 1000 | Target size for each chunk in words |

**Response:**
```json
{
  "chunks": [
    ["First chunk of text...", 987],
    ["Second chunk of text...", 1024],
    ["Third chunk of text...", 856]
  ]
}
```

**Example Request:**
```json
{
  "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
  "chunk_size": 10
}
```

**Example Response:**
```json
{
  "chunks": [
    ["Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do", 12],
    ["eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim", 11],
    ["ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip", 12],
    ["ex ea commodo consequat.", 4]
  ]
}
```

---

### Get First N Words

Extract the first N words from a given text.

**Endpoint:** `POST /api/first-n-words`

**Request Body:**
```json
{
  "text": "Your text content goes here...",
  "n_words": 50
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| text | string | Yes | - | Input text |
| n_words | integer | Yes | - | Number of words to extract |

**Response:**
```json
{
  "text": "First 50 words from the input text..."
}
```

**Example Request:**
```json
{
  "text": "The quick brown fox jumps over the lazy dog. This is a sample sentence to test the API endpoint.",
  "n_words": 5
}
```

**Example Response:**
```json
{
  "text": "The quick brown fox jumps"
}
```

---

### Resize Image

Resize an uploaded image while maintaining aspect ratio.

**Endpoint:** `POST /api/resize-image`

**Request:**
- Form data with the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file | file | Yes | - | Image file to resize |
| max_size | integer | No | 800 | Maximum allowed dimension |
| min_size | integer | No | 70 | Minimum allowed dimension |

**Response:**
- The resized image bytes with appropriate content type

**Example Request:**
```
POST /api/resize-image HTTP/1.1
Host: localhost:9001
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="example.jpg"
Content-Type: image/jpeg

[Binary image data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="max_size"

600
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="min_size"

100
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Example Response:**
- Binary image data with the appropriate content type (e.g., image/jpeg)

---

### Process Images in Batch

Process multiple images in batches for analysis.

**Endpoint:** `POST /api/process-images-batch`

**Request:**
- Form data with the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| files | array of files | Yes | - | List of image files |
| batch_size | integer | No | 5 | Number of images to process in each batch |

**Response:**
```json
{
  "analysis_results": {
    "0": "Analysis result for first image",
    "1": "Analysis result for second image",
    "2": "Analysis result for third image"
  }
}
```

**Example Request:**
```
POST /api/process-images-batch HTTP/1.1
Host: localhost:9001
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="files"; filename="image1.jpg"
Content-Type: image/jpeg

[Binary image data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="files"; filename="image2.jpg"
Content-Type: image/jpeg

[Binary image data]
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="batch_size"

2
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Example Response:**
```json
{
  "analysis_results": {
    "0": "Image contains: landscape with mountains and trees",
    "1": "Image contains: portrait of a person wearing glasses"
  }
}
```

---

### Process PDF Document

Process a PDF file, extracting text and analyzing embedded images.

**Endpoint:** `POST /api/process-pdf`

**Request:**
- Form data with the following parameter:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file | file | Yes | - | PDF file to process |

**Response:**
```json
{
  "text_and_image_analysis": "Combined text extraction and image analysis results from the PDF"
}
```

**Example Request:**
```
POST /api/process-pdf HTTP/1.1
Host: localhost:9001
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

[Binary PDF data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Example Response:**
```json
{
  "text_and_image_analysis": "Document Title: Annual Report\nContents:\n1. Executive Summary\n2. Financial Results\n...\nImage Analysis:\nPage 1: Contains company logo and header\nPage 3: Contains chart showing quarterly profits\n..."
}
```

---

### Process DOCX Document

Process a DOCX file, extracting text and analyzing embedded images.

**Endpoint:** `POST /api/process-docx`

**Request:**
- Form data with the following parameter:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file | file | Yes | - | DOCX file to process |

**Response:**
```json
{
  "text_and_image_analysis": "Combined text extraction and image analysis results from the DOCX"
}
```

**Example Request:**
```
POST /api/process-docx HTTP/1.1
Host: localhost:9001
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="report.docx"
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document

[Binary DOCX data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Example Response:**
```json
{
  "text_and_image_analysis": "Document Title: Project Proposal\nContents:\nIntroduction: This document outlines the proposed implementation...\n\nImage Analysis:\nPage 2: Organization chart showing team structure\nPage 5: Timeline diagram showing project milestones\n..."
}
```

---

### Extract Text and Analyze Images from File

This endpoint serves as a general-purpose document processor that automatically routes to the appropriate handler based on file type.

**Endpoint:** `POST /api/extract_text_from_file_and_analyze_images`

**Request:**
- Form data with the following parameter:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file | file | Yes | - | PDF or DOCX file to process |

**Response:**
- For PDF files, the response format matches the `/api/process-pdf` endpoint
- For DOCX files, the response format matches the `/api/process-docx` endpoint

**Example Request:**
```
POST /api/extract_text_from_file_and_analyze_images HTTP/1.1
Host: localhost:9001
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

[Binary PDF data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Example Response:**
```json
{
  "text_and_image_analysis": "Document Analysis:\n\nText Content:\nThis document contains information about...\n\nImage Analysis:\n- Page 1: Company logo detected\n- Page 2: Graph showing quarterly sales data\n- Page 3: Product illustration with labeled components\n..."
}
```

---

# 4. QA Generation Service

## 4.1 Generate Questions
```
POST /api/questions_generation
```

**Purpose:** Creates customized educational questions based on provided topics and parameters for assessment and learning purposes.

**Detailed Description:** This sophisticated question generation endpoint creates educational assessment items tailored to specific requirements. It supports multiple question formats (multiple choice, true/false, fill-in-the-blank, short answer, and essay) across different difficulty levels. The service can generate contextually relevant questions by analyzing provided context material. For multiple-choice questions, it creates plausible distractors along with the correct answer. The endpoint also provides explanations for correct answers to facilitate learning. This capability is valuable for educators creating assessments, learning platforms that offer practice questions, and automated tutoring systems.

### Input Format
```json
{
    "topic": "string",
    "difficulty": "string", // "easy" | "medium" | "hard"
    "type_of_question": "string", // "multiple_choice" | "true_false" | "fill_blanks" | "short_answer" | "essay"
    "no_of_questions": "number",
    "context": "string",
    "no_of_options": "number", // for multiple choice
    "numericality": "string",
    "few_shot": "string"
}
```

### Output Format
```json
{
    "preamble": "string",
    "questions": [
        {
            "id": "string",
            "question": "string",
            "type": "string",
            "difficulty": "string",
            "options": ["string"], // for multiple choice
            "correct_answer": "string",
            "explanation": "string"
        }
    ],
    "metadata": {
        "total_questions": "number",
        "difficulty_distribution": {
            "easy": "number",
            "medium": "number",
            "hard": "number"
        }
    }
}
```

## 4.2 Generate Answers
```
POST /api/answers_generation
```

**Purpose:** Creates model answers for educational questions with detailed explanations to assist in learning and assessment.

**Detailed Description:** This endpoint produces high-quality model answers for educational questions. Given a question, its type, and optional context, the service generates a comprehensive answer that incorporates domain knowledge and educational best practices. The response includes not only the direct answer but also a detailed explanation of the reasoning process, which makes it valuable for learning purposes. The confidence score indicates the system's certainty about the generated answer. Related concepts help learners understand connections to other topics. This endpoint is particularly useful for automated tutoring systems, self-assessment tools, and content creation for educational materials.

### Input Format
```json
{
    "question": "string",
    "type_of_question": "string",
    "context": "string",
    "no_of_options": "number"
}
```

### Output Format
```json
{
    "answer": "string",
    "explanation": "string",
    "confidence": "number",
    "related_concepts": ["string"]
}
```

## 4.3 File Ingestion
```
POST /api/ingest_files
```

**Purpose:** Processes uploaded educational materials to automatically generate relevant questions and answers from content.

**Detailed Description:** This endpoint handles the ingestion and analysis of educational content files (PDFs, DOCXs, etc.) to automatically generate appropriate assessment questions. The service associates all generated content with a course ID for organizational purposes. For each file, it performs content extraction, topic identification, and intelligent question generation based on the material. The response includes detailed processing results for each file, including any errors encountered. This batch processing capability is essential for educators and content creators who need to quickly transform existing materials into interactive assessment content.

### Input Format
```
Form Data:
- courseid: string
- files[]: Array of files
```

### Output Format
```json
{
    "results": [
        {
            "filename": "string",
            "status": "string",
            "processed": "boolean",
            "question_count": "number",
            "error": "string"
        }
    ],
    "summary": {
        "total_files": "number",
        "successful": "number",
        "failed": "number"
    }
}
```