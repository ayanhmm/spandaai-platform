# API Gateway Documentation

## Overview
The API Gateway service provides a unified interface for data processing, document analysis, and AI agent services. It handles text processing, image processing, document analysis, and educational AI services.

## Base URLs
- Data Processing Service: `{Config.DATA_PROCESSING_URL}`
- Document Analysis Service: `{Config.DOCUMENT_ANALYSIS_URL}`
- Educational AI Agents Service: `{Config.EDU_AI_AGENTS_URL}`

## Authentication
Authentication details should be configured in the Config class.

## Common Response Codes
- 200: Successful operation
- 400: Bad request / Invalid input
- 404: Resource not found
- 500: Internal server error
- 504: Gateway timeout

## Text Processing Endpoints

### Chunk Text
```http
POST /gateway/chunk-text
```

Splits text into manageable chunks.

**Request Body (TextChunkRequest)**
```json
{
  "text": "string",
  "chunk_size": 1000  // optional, default: 1000
}
```

**Response (ChunkTextResponse)**
```json
{
  "chunks": [
    ["string", 0],
    ["string", 1]
  ]
}
```

### First N Words
```http
POST /gateway/first-n-words
```

Extracts the first N words from a text.

**Request Body (FirstWordsRequest)**
```json
{
  "text": "string",
  "n_words": 0
}
```

**Response (FirstWordsResponse)**
```json
{
  "text": "string"
}
```

## Image Processing Endpoints

### Resize Image
```http
POST /gateway/resize-image
```

Resizes an image according to specified dimensions.

**Parameters**
- `file`: UploadFile (required)
- `max_size`: int (optional, default: 800)
- `min_size`: int (optional, default: 70)

**Response**
- Binary image data with appropriate content-type header

### Process Images Batch
```http
POST /gateway/process-images-batch
```

Processes multiple images in a batch.

**Parameters**
- `files`: List[UploadFile] (required)
- `batch_size`: int (optional, default: 5)

**Response (ImageProcessingResponse)**
```json
{
  "analysis_results": {
    "0": "string",
    "1": "string"
  }
}
```

## Document Processing Endpoints

### Process PDF
```http
POST /gateway/process-pdf
```

Analyzes a PDF document.

**Parameters**
- `file`: UploadFile (must be PDF)

**Response (DocumentAnalysisResponse)**
```json
{
  "text_and_image_analysis": "string"
}
```

### Process DOCX
```http
POST /gateway/process-docx
```

Analyzes a DOCX document.

**Parameters**
- `file`: UploadFile (must be DOCX)

**Response (DocumentAnalysisResponse)**
```json
{
  "text_and_image_analysis": "string"
}
```

## AI Analysis Endpoints

### Analyze
```http
POST /analyze
```

Performs document analysis with no timeout limit.

**Request Body**
- Raw JSON payload

**Response**
- Analysis results as JSON

## Educational AI Agent Endpoints

### Process Chunks
```http
POST /api/process-chunks
```

Processes text chunks with AI analysis.

**Request Body (ProcessChunksRequest)**
```json
{
  "chunks": ["string"],
  "system_prompt": "string",
  "batch_size": 5
}
```

### Summarize and Analyze
```http
POST /api/summarize-analyze
```

Generates summary and analysis of document text.

**Request Body (documentText)**
```json
{
  "text": "string"
}
```

### Extract Name
```http
POST /api/extract-name
```

Extracts author name from document text.

**Request Body (documentText)**
```json
{
  "text": "string"
}
```

### Extract Topic
```http
POST /api/extract-topic
```

Extracts document topic.

**Request Body (documentText)**
```json
{
  "text": "string"
}
```

### Extract Degree
```http
POST /api/extract-degree
```

Extracts degree information from document.

**Request Body (documentText)**
```json
{
  "text": "string"
}
```

### Scoring
```http
POST /api/scoring
```

Performs document scoring based on criteria.

**Request Body (ScoringRequest)**
```json
{
  "analysis": "string",
  "criteria": "string",
  "score_guidelines": "string",
  "criteria_guidelines": "string",
  "feedback": "string"
}
```

### Process Initial
```http
POST /api/process-initial
```

Performs initial document processing.

**Request Body (documentText)**
```json
{
  "text": "string"
}
```

## Health Check

### Gateway Health
```http
GET /gateway/health
```

Checks the health status of the gateway and its services.

**Response**
```json
{
  "status": "string",
  "timestamp": "string",
  "data_processing_service": "string"
}
```

## Data Models

### RubricCriteria
```typescript
{
  criteria_explanation: string
  score_explanation: string
  criteria_output: string
}
```

### PreAnalysis
```typescript
{
  degree: string
  name: string
  topic: string
  pre_analyzed_summary: string
}
```

### Error Response
```json
{
  "error": "string",
  "detail": "string",
  "timestamp": "string"
}
```

## Error Handling
- All endpoints include automatic retry with exponential backoff
- Request timing metrics are logged
- Detailed error messages are provided in responses
- Timeout handling is implemented for all requests except analysis endpoints

## Performance Considerations
- Connection pooling is implemented
- Request retries with exponential backoff
- Configurable timeouts per endpoint
- Resource cleanup on shutdown
- Batch processing available for multiple files

## Monitoring
- Request duration logging
- Error tracking
- Health check endpoint for service status
- Detailed logging of request lifecycle