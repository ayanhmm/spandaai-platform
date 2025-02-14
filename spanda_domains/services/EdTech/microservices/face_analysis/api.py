from spanda_domains.services.EdTech.microservices.face_analysis.facial_analysis import *
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Tuple
import tempfile
import os
import shutil
from config import config
import uvicorn
from pathlib import Path

app = FastAPI(
    title="Attention Detection API",
    description="API for processing videos and detecting attention/engagement",
    version="1.0.0"
)

# Pydantic models for request/response
class HeadPose(BaseModel):
    pitch: float
    yaw: float
    roll: float

class Face(BaseModel):
    box: List[float]
    score: float
    head_pose: HeadPose
    focused: bool

class FrameResult(BaseModel):
    time: float
    faces: List[Face]

class AttentionSpans(BaseModel):
    focused: List[Tuple[float, float]]
    mostly_focused: List[Tuple[float, float]]
    partially_focused: List[Tuple[float, float]]
    unfocused: List[Tuple[float, float]]

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Tuple
import tempfile
import os
import json
import shutil
from pathlib import Path
import uuid

app = FastAPI(
    title="Attention Detection API",
    description="API for processing videos and detecting attention/engagement",
    version="1.0.0"
)

def create_temp_file(suffix='.mp4'):
    """Create a temporary file with a unique name"""
    temp_dir = tempfile.gettempdir()
    unique_filename = f"video_{uuid.uuid4().hex}{suffix}"
    return os.path.join(temp_dir, unique_filename)

@app.post("/process-video/")
async def api_process_video(
    video: UploadFile = File(...),
    output_video: bool = Form(False)
):
    """
    Process a video file and return engagement results.
    Optionally save processed video with annotations.
    """
    try:
        print(f"Received video: {video.filename}")
        print(f"Output video requested: {output_video}")
        
        # Create temporary files with unique names
        input_path = create_temp_file('.mp4')
        output_path = create_temp_file('_output.mp4') if output_video else None
        
        print(f"Input path: {input_path}")
        if output_path:
            print(f"Output path: {output_path}")
        
        try:
            # Save uploaded video
            print("Saving uploaded video...")
            with open(input_path, 'wb') as buffer:
                content = await video.read()  # Read the entire file
                buffer.write(content)
            
            print("Processing video...")
            # Process video
            results = process_video(
                input_video=input_path,
                output_video=output_path
            )
            
            # If output video was requested and exists, prepare it for download
            if output_video and output_path and os.path.exists(output_path):
                return FileResponse(
                    output_path,
                    media_type="video/mp4",
                    filename="processed_video.mp4",
                    background=None  # Ensure synchronous response
                )
            
            return results
            
        finally:
            # Cleanup temporary files
            print("Cleaning up temporary files...")
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except Exception as e:
                    print(f"Error removing input file: {e}")
            
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception as e:
                    print(f"Error removing output file: {e}")
            
    except Exception as e:
        print(f"Error in api_process_video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/focus-detection/", response_model=List[Dict])
async def api_focus_detection(batch_face_object: List[Dict]):
    """
    Detect focus in a batch of face objects.
    """
    try:
        return focus_detection(batch_face_object)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/direction-from-json/")
async def api_direction_from_json(json_data: List[FrameResult]):
    """
    Extract direction information from engagement results.
    """
    try:
        return direction_from_json(json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/attention-from-direction/", response_model=AttentionSpans)
async def api_attention_from_direction(
    data_source: Union[str, List[FrameResult]],
    t1: Optional[int] = config.attention.t1,
    t2: Optional[int] = config.attention.t2,
    attention_threshold: Optional[float] = config.attention.attention_threshold
):
    """
    Compute attention spans from direction data.
    """
    try:
        return attention_from_direction(data_source, t1, t2, attention_threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/frontend-pipeline/", response_model=AttentionSpans)
async def api_frontend_pipeline(
    video: UploadFile = File(...),
    output_video: bool = False
):
    """
    Complete pipeline for video processing and attention analysis.
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded video
            input_path = os.path.join(temp_dir, "input.mp4")
            output_path = os.path.join(temp_dir, "output.mp4") if output_video else None
            
            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(video.file, buffer)
            
            # Run pipeline
            results = frontend_pipeline(
                input_path,
                output_path,
                config.video.batch_size,
                config.video.output_fps,
                config.attention.t1,
                config.attention.t2,
                config.attention.attention_threshold
            )
            
            # If output video was requested, prepare it for download
            if output_video and os.path.exists(output_path):
                return FileResponse(
                    output_path,
                    media_type="video/mp4",
                    filename="processed_video.mp4"
                )
            
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "config": {
        "video": config.video.__dict__,
        "model": config.model.__dict__,
        "attention": config.attention.__dict__
    }}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9003)