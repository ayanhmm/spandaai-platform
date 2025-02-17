from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from face_analysis import facial_analysis as ed
import os
import uvicorn

app = FastAPI()

# Endpoint to process video
@app.post("/process-video")
async def process_video_endpoint(file: UploadFile, batch_size: int = Form(10), output_fps: int = Form(4)):
    tempin = 'media/input/tempfile.mp4'
    try:
        with open(tempin, 'wb') as f:
            content = await file.read()
            f.write(content)
        out = ed.process_video(tempin, batch_size=batch_size, output_fps=output_fps)
        os.remove(tempin)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Endpoint to calculate direction json from complete faces json
@app.post("/direction-from-json")
async def direction_from_json_endpoint(data):
    try:
        return ed.direction_from_json(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Endpoint to calculate attention levels from directions json
@app.post("/attention-from-direction")
async def attention_from_direction_endpoint(data, t1: int = Form(2000), t2: int = Form(4000), thresh: float = Form(0.7)):
    try:
        return ed.attention_from_direction(data, t1, t2, thresh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Endpoint to execute complete pipeline from input video to attention levels dict
@app.post("/attention_pipeline")
async def attention_pipeline_endpoint(file: UploadFile, batch_size: int = Form(10), output_fps: int = Form(4),
                                      t1: int = Form(2000), t2: int = Form(4000), thresh: float = Form(0.7)):
    tempin = 'media/input/tempfile.mp4'
    try:
        with open(tempin, 'wb') as f:
            content = await file.read()
            f.write(content)
        out = ed.frontend_pipeline(tempin, batch_size=batch_size, output_fps=output_fps, t1=t1, t2=t2, attention_threshold=thresh)
        os.remove(tempin)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Main function to start the FastAPI server
def main():
    uvicorn.run(app, host="0.0.0.0", port=9005)


if __name__ == "__main__":
    main()
