# Detailed Kong API Gateway Endpoint Documentation

## Base URL
```
http://<host>:8090
```

# 1. Dissertation Analysis Service
Base path: `/dissertation`

## 1.1 Real-time Analysis (WebSocket)
```
WS /dissertation/ws/dissertation_analysis
```

**Purpose:** Enables real-time analysis of dissertations with streaming updates on analysis progress.

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
POST /dissertation/analyze
```

**Purpose:** Performs complete dissertation analysis in a single request.

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

## 1.3 Process Chunks
```
POST /dissertation/process-chunks
```

**Purpose:** Processes dissertation text in manageable chunks for analysis.

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

## 1.4 Information Extraction Endpoints

### Extract Name
```
POST /dissertation/extract-name
```

**Purpose:** Extracts author's name from dissertation.

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
POST /dissertation/extract-topic
```

**Purpose:** Extracts dissertation's main topic and subtopics.

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
POST /dissertation/extract-degree
```

**Purpose:** Extracts degree information from dissertation.

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

## 1.5 Scoring
```
POST /dissertation/scoring
```

**Purpose:** Evaluates dissertation against provided criteria.

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

# 2. Data Preprocessing Service
Base path: `/preprocess`

## 2.1 Text Processing

### Chunk Text
```
POST /preprocess/chunk-text
```

**Purpose:** Splits text into semantic chunks for processing.

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
POST /preprocess/first-n-words
```

**Purpose:** Extracts specified number of words from beginning of text.

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

## 2.2 Image Processing

### Resize Image
```
POST /preprocess/resize-image
```

**Purpose:** Resizes images while maintaining aspect ratio.

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
POST /preprocess/process-images-batch
```

**Purpose:** Processes multiple images in batch.

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

## 2.3 Document Processing

### Process PDF
```
POST /preprocess/process-pdf
```

**Purpose:** Extracts text and analyzes images from PDF.

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
POST /preprocess/process-docx
```

**Purpose:** Extracts text and analyzes images from DOCX.

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

# 3. Question Generation Service
Base path: `/questions`

## 3.1 Generate Questions
```
POST /questions/generate
```

**Purpose:** Generates questions based on provided topic and parameters.

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

## 3.2 Generate Answers
```
POST /questions/answers
```

**Purpose:** Generates answers for provided questions.

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

## 3.3 File Ingestion
```
POST /questions/ingest-files
```

**Purpose:** Processes uploaded files for question generation.

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