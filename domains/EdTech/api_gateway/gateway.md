# Comprehensive Kong API Gateway Endpoint Documentation for EdTech domain

## Introduction

This document outlines all endpoints exposed through the Kong API Gateway for the educational document analysis system. The system provides services for dissertation analysis, data preprocessing, educational AI agents, and question generation.

## Base URL
```
http://<host>:8090
```

---

# 1. Document Analysis Service
Base path: `/api`

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
Base path: `/api`

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

---

# 3. Data Processing Service
Base path: `/api`

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

### Process PDF
```
POST /api/process-pdf
```

**Purpose:** Extracts text content and analyzes embedded images from PDF documents to enable further analysis.

**Detailed Description:** This comprehensive PDF processing endpoint performs multiple operations: text extraction from all pages, detection and analysis of embedded images, and basic structure recognition. The service uses OCR when necessary for scanned documents. For each embedded image, the system generates a descriptive analysis and records positioning information. This endpoint is essential for working with academic PDFs, research papers, and formal documentation where both textual and visual information must be processed.

#### Input Format
```
Form Data:
- file: PDF file
```

#### Output Format
```json
{
    "text": "string",
    "pages": "number",
    "images": [
        {
            "page": "number",
            "description": "string",
            "dimensions": {
                "width": "number",
                "height": "number"
            }
        }
    ]
}
```

### Process DOCX
```
POST /api/process-docx
```

**Purpose:** Extracts text, embedded images, and metadata from Microsoft Word documents for analysis.

**Detailed Description:** This endpoint specializes in parsing Microsoft Word (.docx) files to extract their content and structure. It retrieves plain text while preserving paragraph breaks and section divisions, extracts and analyzes embedded images, and captures document metadata including authorship information and revision history. The comprehensive processing enables downstream analysis systems to work with formal documents while maintaining awareness of their original formatting and context.

#### Input Format
```
Form Data:
- file: DOCX file
```

#### Output Format
```json
{
    "text": "string",
    "images": [
        {
            "description": "string",
            "location": "string"
        }
    ],
    "metadata": {
        "author": "string",
        "created": "string",
        "modified": "string"
    }
}
```

## 3.4 Health Check
```
GET /api/health
```

**Purpose:** Monitors the operational status of the data processing service for system health monitoring.

**Detailed Description:** This endpoint provides real-time information about the operational status of the data processing service. It returns basic health metrics including a status indicator (typically "up" or "down"), the current software version, and system uptime in seconds. This endpoint is essential for monitoring systems, load balancers, and operational dashboards to verify service availability and perform automated health checks.

#### Output Format
```json
{
    "status": "string",
    "version": "string",
    "uptime": "number"
}
```

---

# 4. QA Generation Service
Base path: `/api`

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