# Education and Technology AI Agents API Documentation

The Education and Technology AI Agents API is built with FastAPI and provides several endpoints for processing, analyzing, and summarizing documents. The API extracts key elements such as author name, topic, and educational degree information (if available), while also offering tools to score a document based on defined criteria.

## Base URL

The server runs on:  
**Host:** `0.0.0.0`  
**Port:** `9002`

For example, if you are running locally, your base URL might be:  
```
http://localhost:9002
```

---

## Endpoints Overview

1. [Pre-Analysis](#1-pre-analysis)
2. [Process Chunks](#2-process-chunks)
3. [Summarize & Analyze](#3-summarize--analyze)
4. [Extract Author Name](#4-extract-author-name)
5. [Extract Topic](#5-extract-topic)
6. [Extract Degree](#6-extract-degree)
7. [Scoring](#7-scoring)
8. [Initial Processing](#8-initial-processing)

---

## 1. Pre-Analysis

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

## 2. Process Chunks

**Endpoint:**  
`POST /api/process-chunks`

**Description:**  
Processes the document text in smaller chunks (batches) to perform summarization or other processing tasks.

**Request Model:**  
- **ProcessChunksRequest**
  - `chunks` (List[string]): List of text chunks.
  - `system_prompt` (string): The prompt that will guide the processing (e.g., “Summarize the following text…”).
  - `batch_size` (integer, optional): Number of chunks to process in one batch (default is 5).

**Example Request:**
```json
{
  "chunks": [
    "Chunk 1 text...",
    "Chunk 2 text...",
    "Chunk 3 text..."
  ],
  "system_prompt": "Please summarize the following text.",
  "batch_size": 3
}
```

**Response:**  
A JSON list of strings where each element is the processed output (e.g., summary) corresponding to each chunk.

**Example Response:**
```json
[
  "Summary for Chunk 1",
  "Summary for Chunk 2",
  "Summary for Chunk 3"
]
```

---

## 3. Summarize & Analyze

**Endpoint:**  
`POST /api/summarize-analyze`

**Description:**  
Takes the entire document text, summarizes it, and provides an analysis.

**Request Model:**  
- **ThesisText** (renamed here to represent general document text)
  - `text` (string): The full text of the document.

**Example Request:**
```json
{
  "text": "Complete document text here..."
}
```

**Response Model:**  
- **SummaryResponse**
  - `summary` (string): The summarized analysis of the document.

**Example Response:**
```json
{
  "summary": "The document examines the interplay between advanced algorithms and healthcare outcomes..."
}
```

---

## 4. Extract Author Name

**Endpoint:**  
`POST /api/extract-name`

**Description:**  
Extracts the author’s or originator's name from the provided document text.

**Request Model:**  
- **ThesisText**
  - `text` (string): The document text containing the author's name.

**Example Request:**
```json
{
  "text": "This document by Jane Doe explores advanced machine learning techniques..."
}
```

**Response:**  
A JSON object with the key:
- `name` (string): The extracted author or originator name.

**Example Response:**
```json
{
  "name": "Jane Doe"
}
```

---

## 5. Extract Topic

**Endpoint:**  
`POST /api/extract-topic`

**Description:**  
Extracts the main topic of the document from the provided text.

**Request Model:**  
- **ThesisText**
  - `text` (string): The document text from which to extract the topic.

**Example Request:**
```json
{
  "text": "The study focuses on renewable energy sources and their sustainability..."
}
```

**Response:**  
A JSON object with the key:
- `topic` (string): The extracted topic.

**Example Response:**
```json
{
  "topic": "Renewable Energy and Sustainability"
}
```

---

## 6. Extract Degree

**Endpoint:**  
`POST /api/extract-degree`

**Description:**  
Extracts the degree information from the document text. This endpoint is particularly useful when analyzing educational documents where degree information is mentioned.

**Request Model:**  
- **ThesisText**
  - `text` (string): The document text containing degree information.

**Example Request:**
```json
{
  "text": "A document submitted for the degree of Master of Science in Computer Science..."
}
```

**Response:**  
A JSON object with the key:
- `degree` (string): The extracted degree.

**Example Response:**
```json
{
  "degree": "Master of Science in Computer Science"
}
```

---

## 7. Scoring

**Endpoint:**  
`POST /api/scoring`

**Description:**  
Scores a document based on an analysis, specified criteria, guidelines for scoring, and provided feedback.

**Request Model:**  
- **ScoringRequest**
  - `analysis` (string): The analysis text of the document.
  - `criteria` (string): The criteria on which the document is to be evaluated.
  - `score_guidelines` (string): Guidelines for scoring.
  - `criteria_guidelines` (string): Guidelines explaining each criteria.
  - `feedback` (string): Feedback for improvements.

**Example Request:**
```json
{
    "analysis": "Analysis of document",
    "criteria": "Knowledge Coverage",
    "score_guidelines": "Score in a range of 0 to 3",
    "criteria_guidelines": "Guidelines for criteria - eg. Please look into deapth of knowledge more.",
    "feedback": "Feedback provided"
}
```

**Response Model:**  
- **ScoringResponse**
  - `score` (string): The calculated score (e.g., "85/100").

**Example Response:**
```json
{
  "score": "85/100"
}
```

---

## 8. Initial Processing

**Endpoint:**  
`POST /api/process-initial`

**Description:**  
Processes the document text to perform an initial analysis, extracting key elements such as author name, topic, and degree information (if applicable).

**Request Model:**  
- **ThesisText**
  - `text` (string): The complete document text.

**Example Request:**
```json
{
  "text": "This document by John Doe for the PhD program in Computer Science explores..."
}
```

**Response Model:**  
- **InitialAnalysisResponse**
  - `degree` (string): The extracted degree.
  - `name` (string): The extracted author or originator name.
  - `topic` (string): The extracted document topic.

**Example Response:**
```json
{
  "degree": "PhD",
  "name": "John Doe",
  "topic": "Artificial Intelligence and Society"
}
```

---

## Running the Server

To start the FastAPI server, ensure that all dependencies are installed and run:
```bash
uvicorn your_module_name:app --host 0.0.0.0 --port 9002
```
Replace `your_module_name` with the name of the Python file (without the `.py` extension).

---

## Error Handling

For any unexpected errors during processing, the API returns an HTTP 500 status with a JSON detail message. For example:
```json
{
  "detail": "Failed to pre-analyze document"
}
```

---