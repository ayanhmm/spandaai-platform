from fastapi import FastAPI, UploadFile, HTTPException, Request, File, Form
from fastapi.responses import Response, JSONResponse
from typing import List, Optional, Dict, Any
import httpx
import logging
import uvicorn
from datetime import datetime
from functools import wraps
import asyncio
from spanda_domains.api_gateway.spanda_types import *
from spanda_domains.api_gateway.config import Config
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import aiohttp

# Load environment variables and configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTTPClientManager:
    def __init__(self):
        self.clients: Dict[str, httpx.AsyncClient] = {}

    async def get_client(self, base_url: str, timeout: Optional[float] = 30.0) -> httpx.AsyncClient:
        if base_url not in self.clients:
            self.clients[base_url] = httpx.AsyncClient(
                base_url=base_url,
                timeout=timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self.clients[base_url]

    async def close_all(self):
        for client in self.clients.values():
            await client.aclose()

# Initialize client manager
client_manager = HTTPClientManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    logger.info("Starting up API Gateway...")
    yield
    # Shutdown: Cleanup resources
    logger.info("Shutting down API Gateway...")
    await client_manager.close_all()

# FastAPI app initialization with lifespan
app = FastAPI(
    title="API Gateway",
    description="API Gateway for Data Processing Services",
    version="1.0.0",
    lifespan=lifespan
)

class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class RequestMetrics:
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    def get_duration(self) -> float:
        return (datetime.utcnow() - self.start_time).total_seconds()

async def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """Retry a coroutine with exponential backoff."""
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= 2
    
    raise last_exception

def log_request():
    """Decorator for logging request details and timing."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            metrics = RequestMetrics()
            endpoint = func.__name__
            
            try:
                result = await func(*args, **kwargs)
                logger.info(
                    f"Request to {endpoint} completed successfully "
                    f"in {metrics.get_duration():.2f}s"
                )
                return result
            except Exception as e:
                logger.error(
                    f"Request to {endpoint} failed after {metrics.get_duration():.2f}s: {str(e)}"
                )
                raise
        return wrapper
    return decorator


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

async def make_request(
    url: str,
    method: str = "POST",
    data: Optional[dict] = None,
    files: Optional[dict] = None,
    params: Optional[dict] = None,
    timeout: Optional[float] = 30.0
) -> Any:
    client = await client_manager.get_client(url, timeout)
    
    async def request_with_retry():
        response = await client.request(
            method=method,
            url=url,
            json=data,
            files=files,
            params=params
        )
        response.raise_for_status()
        return response

    try:
        response = await retry_with_backoff(request_with_retry)
        return response
    except httpx.TimeoutException as e:
        logger.error(f"Request timeout to {url}: {e}")
        raise HTTPException(status_code=504, detail="Request timed out")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error from {url}: {e}")
        raise HTTPException(
            status_code=e.response.status_code if hasattr(e, 'response') else 500,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in request to {url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Text processing endpoints
@app.post("/gateway/chunk-text", response_model=ChunkTextResponse)
@log_request()
async def gateway_chunk_text(request: TextChunkRequest):
    response = await make_request(
        f"{Config.DATA_PROCESSING_URL}/api/chunk-text",
        data=request.dict()
    )
    return response.json()

@app.post("/gateway/first-n-words", response_model=FirstWordsResponse)
@log_request()
async def gateway_first_n_words(request: FirstWordsRequest):
    response = await make_request(
        f"{Config.DATA_PROCESSING_URL}/api/first-n-words",
        data=request.dict()
    )
    return response.json()

# Image processing endpoints
@app.post("/gateway/resize-image")
@log_request()
async def gateway_resize_image(
    file: UploadFile,
    max_size: Optional[int] = 800,
    min_size: Optional[int] = 70
):
    files = {"file": (file.filename, await file.read(), file.content_type)}
    response = await make_request(
        f"{Config.DATA_PROCESSING_URL}/api/resize-image",
        files=files,
        params={"max_size": max_size, "min_size": min_size}
    )
    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", file.content_type)
    )

@app.post("/gateway/process-images-batch", response_model=ImageProcessingResponse)
@log_request()
async def gateway_process_images_batch(
    files: List[UploadFile],
    batch_size: Optional[int] = 5
):
    files_dict = {
        f"files": (f.filename, await f.read(), f.content_type)
        for f in files
    }
    response = await make_request(
        f"{Config.DATA_PROCESSING_URL}/api/process-images-batch",
        files=files_dict,
        params={"batch_size": batch_size}
    )
    return response.json()

# Document processing endpoints
@app.post("/gateway/process-pdf", response_model=DocumentAnalysisResponse)
@log_request()
async def gateway_process_pdf(file: UploadFile):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    files = {"file": (file.filename, await file.read(), file.content_type)}
    response = await make_request(
        f"{Config.DATA_PROCESSING_URL}/api/process-pdf",
        files=files
    )
    return response.json()

@app.post("/gateway/process-docx", response_model=DocumentAnalysisResponse)
@log_request()
async def gateway_process_docx(file: UploadFile):
    if not file.filename.lower().endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX")
    
    files = {"file": (file.filename, await file.read(), file.content_type)}
    response = await make_request(
        f"{Config.DATA_PROCESSING_URL}/api/process-docx",
        files=files
    )
    return response.json()

# Analysis endpoints
@app.post("/analyze")
@log_request()
async def analyze(request: Request):
    body = await request.json()
    response = await make_request(
        f"{Config.DOCUMENT_ANALYSIS_URL}/analyze",
        data=body,
        timeout=None  # No timeout for analysis requests
    )
    return response.json()

# AI agent endpoints
@app.post("/api/process-chunks")
@log_request()
async def process_chunks_gateway(request: ProcessChunksRequest):
    response = await make_request(
        f"{Config.EDU_AI_AGENTS_URL}/api/process-chunks",
        data=request.dict()
    )
    return response.json()

@app.post("/api/summarize-analyze")
@log_request()
async def summarize_analyze_gateway(request: DocumentText):
    response = await make_request(
        f"{Config.EDU_AI_AGENTS_URL}/api/summarize-analyze",
        data=request.dict()
    )
    return response.json()

@app.post("/api/extract-name")
@log_request()
async def extract_name_gateway(request: DocumentText):
    response = await make_request(
        f"{Config.EDU_AI_AGENTS_URL}/api/extract-name",
        data=request.dict()
    )
    return response.json()

@app.post("/api/extract-topic")
@log_request()
async def extract_topic_gateway(request: DocumentText):
    response = await make_request(
        f"{Config.EDU_AI_AGENTS_URL}/api/extract-topic",
        data=request.dict()
    )
    return response.json()

@app.post("/api/extract-degree")
@log_request()
async def extract_degree_gateway(request: DocumentText):
    response = await make_request(
        f"{Config.EDU_AI_AGENTS_URL}/api/extract-degree",
        data=request.dict()
    )
    return response.json()

@app.post("/api/scoring")
@log_request()
async def scoring_gateway(request: ScoringRequest):
    response = await make_request(
        f"{Config.EDU_AI_AGENTS_URL}/api/scoring",
        data=request.dict()
    )
    return response.json()

# Health check endpoint
@app.get("/gateway/health")
@log_request()
async def gateway_health_check():
    try:
        response = await make_request(
            f"{Config.DATA_PROCESSING_URL}/api/health",
            method="GET"
        )
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "data_processing_service": response.json()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "data_processing_service": "unavailable"
        }

# QA Generation endpoints
@app.post("/gateway/questions-generation")
@log_request()
async def gateway_questions_generation(query_request: QueryRequest):
    """
    Gateway endpoint for generating questions based on given context and topic.
    """
    try:
        response = await make_request(
            f"{Config.QA_GENERATION_URL}/api/questions_generation",
            data=query_request.dict(exclude_none=True),
            timeout=None  # Disable timeout
        )
        return response.json()
    except Exception as e:
        logger.error(f"Error in questions generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Questions generation service error: {str(e)}"
        )

@app.post("/gateway/answers-generation")
@log_request()
async def gateway_answers_generation(question_request: QuestionRequest):
    """
    Gateway endpoint for generating answers based on given questions and context.
    """
    try:
        response = await make_request(
            f"{Config.QA_GENERATION_URL}/api/answers_generation",
            data=question_request.dict(exclude_none=True),
            timeout=None  # Disable timeout
        )
        return response.json()
    except Exception as e:
        logger.error(f"Error in answers generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Answers generation service error: {str(e)}"
        )

@app.post("/gateway/ingest-files")
@log_request()
async def gateway_ingest_files(
    courseid: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Gateway endpoint for ingesting files to Verba.
    """
    try:
        # Use aiohttp to create a proper multipart request
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field("courseid", courseid)

            for file in files:
                form_data.add_field(
                    "files", 
                    await file.read(), 
                    filename=file.filename,
                    content_type=file.content_type
                )

            async with session.post(
                f"{Config.QA_GENERATION_URL}/api/ingest_files/",
                data=form_data
            ) as response:
                return await response.json()

    except Exception as e:
        logger.error(f"Error in file ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File ingestion service error: {str(e)}"
        )

def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=Config.GATEWAY_PORT
    )

if __name__ == "__main__":
    main()