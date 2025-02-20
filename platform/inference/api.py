from fastapi import FastAPI, HTTPException
import subprocess
import os
import shlex
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/start-vllm")
def start_vllm_container(hf_token: str, model_name: str, command: str = ""):
    logger.info(f"Received request to start vLLM container with model: {model_name}")
    
    # Log the base configuration
    logger.info("Setting up base docker command configuration")
    docker_run_command = [
        "docker", "run", "-d",
        "--name", f"{model_name.split('/')[-1]}",  # Extract only the part after the last '/'
        "--gpus", "all",
        "--env", f"HUGGING_FACE_HUB_TOKEN={hf_token}",
        "-p", "8001:8000",
        "-v", os.path.expanduser("~") + "/.cache/huggingface:/root/.cache/huggingface",
        "--ipc", "host",
        "--network", "app_network",
        "vllm/vllm-openai:latest",
        "--model", model_name
    ]
    # Parse and add additional command arguments
    if command:
        logger.info(f"Parsing additional command arguments: {command}")
        try:
            extra_args = shlex.split(command)
            docker_run_command.extend(extra_args)
            logger.debug(f"Complete docker command after adding extra args: {' '.join(docker_run_command)}")
        except Exception as e:
            logger.error(f"Failed to parse additional command arguments: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid command format: {str(e)}")
    
    # Run the container
    logger.info("Attempting to start docker container")
    logger.info(f"Running Docker command: {docker_run_command}")
    try:
        result = subprocess.run(docker_run_command, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Container start failed with error: {result.stderr.strip()}")
            raise HTTPException(status_code=500, detail=f"Failed to start container: {result.stderr.strip()}")
        
        container_id = result.stdout.strip()
        logger.info(f"Container started successfully with ID: {container_id}")
    except Exception as e:
        logger.error(f"Unexpected error while starting container: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error while starting container: {str(e)}")

    # Attach the container to platform_network
    logger.info("Attempting to attach container to platform_network")
    attach_command = [
        "docker", "network", "connect", "platform_network", container_id
    ]
    
    try:
        attach_result = subprocess.run(attach_command, capture_output=True, text=True)
        if attach_result.returncode != 0:
            logger.error(f"Network attachment failed: {attach_result.stderr.strip()}")
            raise HTTPException(
                status_code=500, 
                detail=f"Container started but failed to attach to platform_network: {attach_result.stderr.strip()}"
            )
        logger.info("Successfully attached container to platform_network")
    except Exception as e:
        logger.error(f"Unexpected error while attaching to network: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error while attaching to network: {str(e)}")

    logger.info("Container deployment completed successfully")
    return {
        "message": "vllm container started and attached to platform_network successfully",
        "container_id": container_id
    }

@app.post("/stop-vllm")
def stop_vllm_container(model_name: str):
    """
    Stops and deletes the vLLM container with the given model name.
    Assumes that the container was started with its name set to the model name.
    """
    logger.info(f"Received request to stop vLLM container with model name: {model_name}")
    
    # Stop the container
    stop_command = ["docker", "stop", model_name]

    logger.info(f"Running Docker command to stop container: {' '.join(stop_command)}")
    stop_command_str = " ".join(stop_command)
    logger.info(f"Stop command: {stop_command_str}")
    try:
        stop_result = subprocess.run(stop_command, capture_output=True, text=True)
        if stop_result.returncode != 0:
            error_message = stop_result.stderr.strip()
            logger.error(f"Failed to stop container: {error_message}")
            raise HTTPException(status_code=500, detail=f"Failed to stop container: {error_message}")
    except Exception as e:
        logger.error(f"Unexpected error while stopping container: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error while stopping container: {str(e)}")
    
    # Remove the container
    rm_command = ["docker", "rm", model_name]
    logger.info(f"Running Docker command to remove container: {' '.join(rm_command)}")
    try:
        rm_result = subprocess.run(rm_command, capture_output=True, text=True)
        if rm_result.returncode != 0:
            error_message = rm_result.stderr.strip()
            logger.error(f"Failed to remove container: {error_message}")
            raise HTTPException(status_code=500, detail=f"Failed to remove container: {error_message}")
    except Exception as e:
        logger.error(f"Unexpected error while removing container: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error while removing container: {str(e)}")
    
    logger.info(f"Container with model name '{model_name}' stopped and removed successfully")
    return {"message": f"vLLM container with model name '{model_name}' stopped and removed successfully"}

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI server starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI server shutting down")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on port 7500")
    uvicorn.run(app, host="0.0.0.0", port=7500)