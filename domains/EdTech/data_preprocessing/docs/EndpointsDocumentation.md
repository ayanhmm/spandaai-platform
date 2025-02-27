# Data Preprocessing API Documentation

This document provides detailed information about the Data Preprocessing API endpoints, including request parameters, response formats, and usage examples.

# Data Preprocessing API Endpoints

## 1. Health Check

**Endpoint:**  
`GET /api/health`

**Description:**  
Checks if the API service is running properly.

---

## 2. Text Chunking

**Endpoint:**  
`POST /api/chunk-text`

**Description:**  
Splits input text into semantic chunks using LangChain's RecursiveCharacterTextSplitter.

---

## 3. Get First N Words

**Endpoint:**  
`POST /api/first-n-words`

**Description:**  
Extracts the first N words from the provided text.

---

## 4. Resize Image

**Endpoint:**  
`POST /api/resize-image`

**Description:**  
Resizes an uploaded image while maintaining its aspect ratio.

---

## 5. Process Images in Batch

**Endpoint:**  
`POST /api/process-images-batch`

**Description:**  
Processes multiple images in batches for analysis.

---

## 6. Process PDF Document

**Endpoint:**  
`POST /api/process-pdf`

**Description:**  
Extracts text and analyzes embedded images from a PDF file.

---

## 7. Process DOCX Document

**Endpoint:**  
`POST /api/process-docx`

**Description:**  
Extracts text and analyzes embedded images from a DOCX file.

---

## 8. Extract Text and Analyze Images from File

**Endpoint:**  
`POST /api/extract_text_from_file_and_analyze_images`

**Description:**  
Automatically routes to the appropriate handler based on file type (PDF or DOCX) to process and analyze the document.

---

## Base URL

```
http://[server-address]:9001
```

## Endpoints

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


## Limitations and Considerations

1. **File Size Limits**: The API may have limitations on maximum file sizes for uploaded documents and images.

2. **Processing Time**: Document processing operations, especially for large files with many images, may take considerable time.

3. **Supported Formats**:
   - Document processing is limited to PDF and DOCX formats
   - Image processing supports common formats (JPEG, PNG, etc.)

4. **Batch Processing**: When using the batch image processing endpoint, consider memory constraints when setting the batch size for large numbers of images.

5. **Rate Limiting**: The API may implement rate limiting to prevent abuse. Check HTTP response headers for rate limit information.

This documentation covers all the available endpoints in the Data Preprocessing API, providing the necessary information to integrate and use each feature effectively.