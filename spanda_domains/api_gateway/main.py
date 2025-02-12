from spanda_domains.api_gateway.spanda_types import *
from spanda_domains.api_gateway.config import Config

from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from typing import List, Optional
import httpx
import logging
import uvicorn
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="API Gateway",
    description="API Gateway for Data Processing Services",
    version="1.0.0"
)

# HTTP client
async def get_http_client():
    return httpx.AsyncClient(
        base_url=Config.DATA_PROCESSING_URL,
        timeout=30.0
    )

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_response = ErrorResponse(
        error=exc.__class__.__name__,
        detail=str(exc),
        timestamp=datetime.utcnow().isoformat()
    )
    
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
    else:
        status_code = 500
        logger.error(f"Unexpected error: {exc}")
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.dict()
    )

@app.post("/gateway/chunk-text", response_model=ChunkTextResponse)
async def gateway_chunk_text(request: TextChunkRequest):
    async with await get_http_client() as client:
        try:
            response = await client.post("/api/chunk-text", json=request.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error in chunk_text gateway: {e}")
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail=str(e))

@app.post("/gateway/first-n-words", response_model=FirstWordsResponse)
async def gateway_first_n_words(request: FirstWordsRequest):
    async with await get_http_client() as client:
        try:
            response = await client.post("/api/first-n-words", json=request.dict())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error in first_n_words gateway: {e}")
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail=str(e))

@app.post("/gateway/resize-image")
async def gateway_resize_image(
    file: UploadFile,
    max_size: Optional[int] = 800,
    min_size: Optional[int] = 70
):
    async with await get_http_client() as client:
        try:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            params = {"max_size": max_size, "min_size": min_size}
            response = await client.post("/api/resize-image", files=files, params=params)
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", file.content_type)
            )
        except httpx.HTTPError as e:
            logger.error(f"Error in resize_image gateway: {e}")
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail=str(e))

@app.post("/gateway/process-images-batch", response_model=ImageProcessingResponse)
async def gateway_process_images_batch(
    files: List[UploadFile],
    batch_size: Optional[int] = 5
):
    async with await get_http_client() as client:
        try:
            files_dict = {
                f"files": (f.filename, await f.read(), f.content_type)
                for f in files
            }
            response = await client.post(
                "/api/process-images-batch",
                files=files_dict,
                params={"batch_size": batch_size}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error in process_images_batch gateway: {e}")
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail=str(e))

@app.post("/gateway/process-pdf", response_model=DocumentAnalysisResponse)
async def gateway_process_pdf(file: UploadFile):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    async with await get_http_client() as client:
        try:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post("/api/process-pdf", files=files)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error in process_pdf gateway: {e}")
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail=str(e))

@app.post("/gateway/process-docx", response_model=DocumentAnalysisResponse)
async def gateway_process_docx(file: UploadFile):
    if not file.filename.lower().endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX")
    
    async with await get_http_client() as client:
        try:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post("/api/process-docx", files=files)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error in process_docx gateway: {e}")
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500,
                              detail=str(e))

@app.get("/gateway/health")
async def gateway_health_check():
    async with await get_http_client() as client:
        try:
            response = await client.get("/api/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "data_processing_service": response.json()
            }
        except httpx.HTTPError as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "data_processing_service": "unavailable"
            }


# HTTP Client with Infinite Timeout
async def forward_request_analysis(target_url: str, request: Request):
    async with httpx.AsyncClient(timeout=None) as client:  # No timeout
        body = await request.json()
        response = await client.post(target_url, json=body)
        return response.json()

@app.post("/analyze")
async def analyze(request: Request):
    return await forward_request_analysis(f"{Config.DOCUMENT_ANALYSIS_URL}/analyze", request)

# Route handlers
@app.post("/api/process-chunks")
async def process_chunks_gateway(request: ProcessChunksRequest):
    return await forward_request("/api/process-chunks", request.dict())

@app.post("/api/summarize-analyze")
async def summarize_analyze_gateway(request: ThesisText):
    return await forward_request("/api/summarize-analyze", request.dict())

@app.post("/api/extract-name")
async def extract_name_gateway(request: ThesisText):
    return await forward_request("/api/extract-name", request.dict())

@app.post("/api/extract-topic")
async def extract_topic_gateway(request: ThesisText):
    return await forward_request("/api/extract-topic", request.dict())

@app.post("/api/extract-degree")
async def extract_degree_gateway(request: ThesisText):
    return await forward_request("/api/extract-degree", request.dict())

@app.post("/api/scoring")
async def scoring_gateway(request: ScoringRequest):
    return await forward_request("/api/scoring", request.dict())

@app.post("/api/process-initial")
async def process_initial_gateway(request: ThesisText):
    return await forward_request("/api/process-initial", request.dict())

# Helper function for making requests
async def forward_request(endpoint: str, data: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{Config.EDU_AI_AGENTS_URL}{endpoint}",
                json=data,
                timeout=30
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Config.GATEWAY_PORT
    )

if __name__ == "__main__":
    main()