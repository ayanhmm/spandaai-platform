# Question Generation API Documentation

## Base URL
The service runs on port 9004.

## Health Check
### GET /
Check if the service is running.

**Response**
```json
{
    "message": "Hello! This is the advanced question/answer generation microservice! Running successfully!"
}
```

## Question Generation
### POST /api/questions_generation
Generate questions based on a given topic and parameters.

**Request Body**
```json
{
    "topic": string,
    "difficulty": string,
    "type_of_question": string,
    "no_of_questions": integer,
    "context": string (optional),
    "no_of_options": integer (optional),
    "numericality": string,
    "few_shot": string (optional)
}
```

**Supported Question Types**
- Multiple choice questions
- True/false
- Fill in the blanks
- Short answer
- Essay

**Response**
```json
{
    "preamble": string,
    "questions": array,
    "metadata": object
}
```

**Error Responses**
- 400: Unsupported question type
- 500: Internal server error

## Answer Generation
### POST /api/answers_generation
Generate answers for given questions.

**Request Body**
```json
{
    "question": string,
    "type_of_question": string,
    "context": string (optional),
    "no_of_options": integer (optional)
}
```

**Response**
```json
{
    "questions": array,
    "metadata": {
        "total_questions": integer
    }
}
```

## File Ingestion
### POST /api/ingest_files/
Upload and process multiple files.

**Request Parameters**
- Form Data:
  - `courseid`: string (required)
  - `files`: array of files (required)

**Constraints**
- Maximum file size: 10GB (10000 * 1024 * 1024 bytes)

**Response**
```json
{
    "results": [
        {
            "filename": string,
            "status": string,
            "error": string (optional)
        }
    ]
}
```

**Error Responses**
- 413: File size exceeds limit
- 500: Internal server error

## Important Notes

1. **CORS Configuration**
   - The API allows requests from all origins (`*`)
   - Supports all methods and headers
   - Allows credentials

2. **File Size Limits**
   - Maximum file size is enforced at 10GB
   - Larger files will receive a 413 status code

3. **Authentication**
   - Credentials are required for certain operations
   - Uses a predefined credentials configuration

4. **RAG Configuration**
   - Supports different RAG (Retrieval-Augmented Generation) configurations for:
     - Question generation
     - File ingestion
     - Answer generation

5. **Error Handling**
   - All endpoints return appropriate HTTP status codes
   - Error messages are included in the response body
   - File processing errors are reported per file in batch operations

## Data Models

### QueryRequest
```python
{
    "topic": str,
    "difficulty": str,
    "type_of_question": str,
    "no_of_questions": int,
    "context": Optional[str],
    "no_of_options": Optional[int],
    "numericality": str,
    "few_shot": Optional[str]
}
```

### QuestionRequest
```python
{
    "question": str,
    "type_of_question": str,
    "context": Optional[str],
    "no_of_options": Optional[int]
}
```