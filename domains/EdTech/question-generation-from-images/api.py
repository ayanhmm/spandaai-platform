from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
from generate_from_image import generate_educational_questions, stream_educational_questions
import logging
import uvicorn
from pydantic import BaseModel
import os

app = FastAPI(
    title="Graduate-Level Question Generator API",
    description="API for generating master's level questions from images with cognitive complexity control",
    version="2.1.0",
    docs_url="/docs",
    redoc_url=None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuestionRequest(BaseModel):
    num_questions: int = 5
    question_types: Optional[List[str]] = None
    difficulty: str = "master"
    domain: Optional[str] = None
    user_instructions: str = '',
    custom_prompt: Optional[str] = None
    use_default_prompt: bool = True
    cognitive_level: str = "analyze"
    numerical: bool = True

@app.post("/generate-questions", response_model=Dict)
async def generate_questions(
    image: UploadFile = File(...),
    num_questions: int = Form(...),
    question_types: Optional[List[str]] = None,
    difficulty: str = Form("master"),
    domain: Optional[str] = None,
    user_instructions: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    use_default_prompt: bool = Form(True),
    cognitive_level: str = "analyze",
    numerical: bool = Form(True)
):
    """
    Generate graduate-level questions from images with precise academic controls.
    
    Parameters:
    - image: Image file to analyze (required)
    - num_questions: Number of questions (1-15, default 5)
    - question_types: Question styles ["conceptual","applied","critical evaluation"]
    - difficulty: "easy", "medium", "hard", or "master" (default)
    - domain: Academic discipline ("biochemistry", "physics", etc.)
    - custom_prompt: Custom instructions for image analysis
    - use_default_prompt: Use default prompt if no custom provided (default True)
    - cognitive_level: Bloom's level ("remember" to "create")
    
    Returns:
    {
        "questions": [list of generated questions],
        "analysis": "image description",
        "stats": {
            "requested": int,
            "generated": int,
            "difficulty": str,
            "cognitive_level": str,
            "domain": str
        }
    }
    """
    try:
        # Validate parameters
        if not 1 <= num_questions <= 15:
            raise HTTPException(
                status_code=422,
                detail="Number of questions must be between 1 and 15"
            )

        valid_difficulties = ["easy", "medium", "hard", "master"]
        if difficulty.lower() not in valid_difficulties:
            raise HTTPException(
                status_code=422,
                detail=f"Difficulty must be one of: {', '.join(valid_difficulties)}"
            )

        # Validate image
        image_data = await image.read()

        # Generate questions
        result = await generate_educational_questions(
            image_data=image_data,
            num_questions=num_questions,
            question_types=question_types,
            difficulty=difficulty,
            domain=domain,
            user_instructions=user_instructions,
            use_default_prompt=use_default_prompt,
            cognitive_level=cognitive_level,
            numerical=numerical
        )

        if "error" in result:
            logger.error(f"Generation failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during question generation"
        )


@app.post("/stream-questions")
async def stream_questions(
    image: UploadFile = File(..., description="Image file (PNG/JPEG) for question generation"),
    num_questions: int = 5,
    question_types: Optional[List[str]] = None,
    difficulty: str = "master",
    domain: Optional[str] = None,
    user_instructions: Optional[str] = None,
    use_default_prompt: bool = True,
    cognitive_level: str = "analyze",
    numerical: bool = True
):
    """
    Stream graduate-level questions as they're generated from the uploaded image.
    
    Results are streamed as Server-Sent Events (SSE) in the following format:
    - event: analysis_complete - Image analysis is completed
    - event: question_generated - A new question has been generated
    - event: generation_complete - All questions have been generated
    - event: error - An error occurred during processing
    """
    try:
        # Validate parameters
        if not 1 <= num_questions <= 15:
            raise HTTPException(
                status_code=422,
                detail="Number of questions must be between 1 and 15"
            )

        valid_difficulties = ["easy", "medium", "hard", "master"]
        if difficulty not in valid_difficulties:
            raise HTTPException(
                status_code=422,
                detail=f"Difficulty must be one of: {', '.join(valid_difficulties)}"
            )

        # Read image data
        image_data = await image.read()
        
        # Set headers needed for proper SSE handling
        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked"
        }
        
        # Return a streaming response with appropriate headers
        return StreamingResponse(
            stream_educational_questions(
                image_data=image_data,
                num_questions=num_questions,
                question_types=question_types,
                difficulty=difficulty,
                domain=domain,
                user_instructions=user_instructions,
                use_default_prompt=use_default_prompt,
                cognitive_level=cognitive_level,
                numerical=numerical
            ),
            media_type="text/event-stream",
            headers=headers
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during question generation"
        )
    
@app.get("/health")
async def health_check():
    """Service health endpoint"""
    return {
        "status": "healthy",
        "version": app.version,
        "service": app.title
    }

def main():
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8014)),
        log_level="info"
    )

if __name__ == "__main__":
    main()