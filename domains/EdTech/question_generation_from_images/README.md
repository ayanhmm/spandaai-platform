# Image-to-Question Generator API  

## Overview  

The **Image-to-Question Generator API** is a powerful tool that automatically generates academic questions from uploaded images. It supports both **numerical problem-solving questions** (requiring calculations) and **theoretical/conceptual questions** (requiring analysis and reasoning). The API allows fine-grained control over question difficulty, cognitive complexity, and subject domain.  

### Key Features  

✅ **Generate Questions from Images** – Extract questions directly from diagrams, graphs, or text-based images.  
✅ **Customizable Question Types** – Choose between **numerical** (math-based) or **theoretical** (concept-based) questions.  
✅ **Difficulty Control** – Adjust question complexity with `easy`, `medium`, `hard`, or `master` difficulty levels.  
✅ **Cognitive Complexity** – Set Bloom’s taxonomy levels (`remember`, `understand`, `apply`, `analyze`, `evaluate`, `create`).  
✅ **Domain-Specific Questions** – Specify a subject (e.g., "physics," "biochemistry") for tailored questions.  
✅ **Real-Time Streaming** – Get questions as they are generated via **Server-Sent Events (SSE)**.  
✅ **Batch Generation** – Request multiple questions at once (1-15 per request).  

---

## API Endpoints  

### 1. **Generate Questions (Synchronous)**  
**`POST /generate-questions`**  
Generate a set of questions from an uploaded image in a single response.  

#### Request Parameters:  
| Parameter | Type | Description | Default |  
|-----------|------|-------------|---------|  
| `image` | `File` (PNG/JPEG) | Image to analyze | **Required** |  
| `num_questions` | `int` | Number of questions (1-15) | `5` |  
| `question_types` | `List[str]` | Question styles (optional) | `None` |  
| `difficulty` | `str` | `"easy"`, `"medium"`, `"hard"`, `"master"` | `"master"` |  
| `domain` | `str` | Subject domain (e.g., "physics") | `None` |  
| `user_instructions` | `str` | Custom instructions for generation | `None` |  
| `cognitive_level` | `str` | Bloom’s level (`"analyze"`, `"evaluate"`, etc.) | `"analyze"` |  
| `numerical` | `bool` | If `True`, generates math-based questions | `True` |  

#### Example Response:  
```json
{
  "questions": [
    "Calculate the force required to move the object in the diagram, given the coefficient of friction μ = 0.4.",
    "Explain the thermodynamic principle illustrated in the graph."
  ],
  "analysis": "The image shows a free-body diagram with forces acting on an object on an inclined plane.",
  "stats": {
    "requested": 5,
    "generated": 2,
    "difficulty": "master",
    "cognitive_level": "analyze",
    "domain": "physics",
    "question_type": "numerical"
  }
}
```

---

### 2. **Stream Questions (Real-Time SSE)**  
**`POST /stream-questions`**  
Streams questions as they are generated, useful for large batches or real-time applications.  

#### Response Format (Server-Sent Events):  
- `analysis_complete` – Image analysis is done.  
- `question_generated` – A new question is available.  
- `generation_complete` – All questions are generated.  
- `error` – If processing fails.  

#### Example SSE Output:  
```plaintext
event: analysis_complete  
data: {"analysis": "The image depicts a chemical reaction diagram..."}  

event: question_generated  
data: {"question_number": 1, "question": "What is the rate-limiting step in this reaction?"}  

event: generation_complete  
data: {"stats": {"requested": 3, "generated": 3, ...}}  
```

---

### 3. **Health Check**  
**`GET /health`**  
Check if the API is running.  

#### Response:  
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "service": "Question Generator API"
}
```

---

## Usage Examples  

### Python (Using `requests`)  
```python
import requests

url = "http://localhost:8014/generate-questions"
files = {"image": open("diagram.png", "rb")}
params = {
    "num_questions": 3,
    "difficulty": "hard",
    "domain": "biology",
    "cognitive_level": "evaluate",
    "numerical": False
}

response = requests.post(url, files=files, data=params)
print(response.json())
```

### JavaScript (Fetch API)  
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8014/stream-questions', {
  method: 'POST',
  body: formData,
  headers: { 'Accept': 'text/event-stream' }
}).then(async (response) => {
  const reader = response.body.getReader();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    console.log(new TextDecoder().decode(value));
  }
});
```

---

## Error Handling  

| Status Code | Error | Description |  
|------------|-------|-------------|  
| `400` | Bad Request | Invalid image or missing parameters. |  
| `422` | Validation Error | Invalid `difficulty` or `num_questions`. |  
| `500` | Server Error | Internal processing failure. |  

---

## Setup & Deployment  

Enable virtual environment.
Create .env file and install dependencies

1. **Install Dependencies**:  
   ```sh
   pip install -e .
   ```

2. **Run the API**:  
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8014
   ```

3. **Environment Variables**:  
   - `HOST` (default: `0.0.0.0`)  
   - `PORT` (default: `8014`)  


Or use Docker


**Run the App**:  
   ```sh
   docker compose up
   ```

---

## License  
MIT License. Free for academic and commercial use.  

**GitHub Repo**: [Link] (if applicable)  

--- 

This API is ideal for:  
- **Educational apps** (automated quiz generation)  
- **Research tools** (data extraction from scientific images)  
- **E-learning platforms** (dynamic question banks)  

For questions, contact [Your Email].