# API Documentation: Dissertation Analysis Service

## Overview
This FastAPI service provides real-time and non-streaming endpoints for dissertation analysis. It includes WebSocket-based live processing and a traditional HTTP-based analysis endpoint.

## Base URL
```
http://<host>:9000
```

---

## WebSocket Endpoint
### **Dissertation Analysis WebSocket**
**Endpoint:**
```
/ws/dissertation_analysis
```
**Method:** WebSocket

### **Description**
This WebSocket endpoint enables real-time dissertation analysis. Clients can connect, send dissertation details, and receive step-by-step feedback on the analysis progress.

### **Workflow**
1. Establish a WebSocket connection.
2. Send a JSON payload with rubric and dissertation details.
3. Receive real-time analysis updates.
4. Handle disconnection or errors gracefully.

### **Request Format**
```json
{
    "rubric": {
        "Introduction": {
            "criteria_explanation": "Evaluates clarity of introduction.",
            "score_explanation": "Scores from 1-5 based on clarity.",
            "criteria_output": "Well-defined introduction."
        }
    },
    "pre_analysis": {
        "degree": "PhD",
        "name": "John Doe",
        "topic": "AI in Education",
        "pre_analyzed_summary": "The study focuses on AI's impact on education."
    },
    "feedback": "Please ensure clarity in the introduction."
}
```

### **Response Format**
The server streams real-time JSON responses, such as:
```json
{
    "type": "progress",
    "data": {"message": "Analyzing introduction section..."}
}
```
```json
{
    "type": "result",
    "data": {"message": "Analysis completed successfully."}
}
```

### **Error Handling**
- If an error occurs, the server sends:
```json
{
    "type": "error",
    "data": {"message": "An error occurred during analysis."}
}
```

---

## REST API Endpoint
### **Analyze Document**
**Endpoint:**
```
/analyze
```
**Method:** POST

### **Description**
This endpoint allows clients to perform non-streaming dissertation analysis via a standard HTTP request.

### **Request Format**
Note: The pre_analyzed_summary could just be the document text itself. Or if the document is very long, use Spanda.AI's summarization service and that could be the input instead!

```json
{
    "rubric": {
        "Introduction": {
            "criteria_explanation": "Evaluates clarity of introduction.",
            "score_explanation": "Scores from 1-5 based on clarity.",
            "criteria_output": "Well-defined introduction."
        }
    },
    "pre_analysis": {
        "degree": "PhD",
        "name": "John Doe",
        "topic": "AI in Education",
        "pre_analyzed_summary": "The study focuses on AI's impact on education."
    },
    "feedback": "Please ensure clarity in the introduction."
}
```

### **Response Format**
```json
{
    "status": "success",
    "message": "Document analyzed successfully.",
    "analysis": {
        "Introduction": {
            "score": 4,
            "comments": "Clear and well-articulated introduction."
        }
    }
}
```

### **Error Handling**
If an error occurs, the response format will be:
```json
{
    "status": "error",
    "message": "Invalid input data."
}
```

---

## WebSocket Handling
### **Events**
| Event Type  | Description |
|------------|-------------|
| `progress` | Provides updates on different analysis stages. |
| `result`   | Sends final analysis output. |
| `error`    | Reports issues encountered during processing. |

### **Disconnection Handling**
- If the client disconnects, the processing stops.
- If the server detects a closed connection, it stops streaming updates.

---

## Notes
- WebSocket clients should handle reconnect logic in case of disconnection.
- Ensure JSON payloads match the expected format to avoid errors.
- The WebSocket-based endpoint is ideal for real-time feedback, while the REST endpoint is best for batch processing.

