import os
import shlex
import logging
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import docker

# Load configuration from file if available, otherwise use defaults
config_path = "config.yaml"
if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
else:
    # Default configuration
    config = {
        "docker": {
            "image_name": "vllm/vllm-openai:latest",
            "app_network": "app_network",
            "platform_network": "platform_network",
            "gpu_runtime": "nvidia"
        }
    }

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create a Docker client
client = docker.from_env()

# Define a Pydantic model for input validation
class StartVLLMRequest(BaseModel):
    hf_token: str = Field(..., min_length=1, description="Hugging Face Hub token")
    model_name: str = Field(..., min_length=1, description="Name of the model to run")
    command: str = Field(default="", description="Additional command arguments")

@app.post("/start-vllm")
def start_vllm_container(request: StartVLLMRequest):
    hf_token = request.hf_token
    model_name = request.model_name
    command = request.command
    # Use the part after the last '/' as the container name
    container_name = model_name.split("/")[-1]

    logger.info(f"Starting vLLM container for model: {model_name} (container name: {container_name})")

    # Build the command list for the container
    command_list = ["--model", model_name]
    if command:
        try:
            extra_args = shlex.split(command)
            command_list.extend(extra_args)
            logger.info(f"Parsed additional command arguments: {extra_args}")
        except Exception as e:
            logger.error(f"Error parsing command arguments: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid command format: {str(e)}")
    
    try:
        # Run the container using the Docker SDK
        container = client.containers.run(
            image=config["docker"]["image_name"],
            name=container_name,
            detach=True,
            runtime=config["docker"]["gpu_runtime"],
            environment={"HUGGING_FACE_HUB_TOKEN": hf_token},
            ports={"8000/tcp": 7000},
            volumes={
                os.path.expanduser("~") + "/.cache/huggingface": {
                    "bind": "/root/.cache/huggingface",
                    "mode": "rw"
                }
            },
            ipc_mode="host",
            network=config["docker"]["app_network"],
            command=command_list
        )
        logger.info(f"Container started with ID: {container.id}")

        # Attach the container to the platform network
        platform_network = config["docker"]["platform_network"]
        try:
            network_obj = client.networks.get(platform_network)
            network_obj.connect(container)
            logger.info(f"Container {container_name} attached to network: {platform_network}")
        except docker.errors.NotFound:
            logger.error(f"Platform network {platform_network} not found.")
            raise HTTPException(status_code=500, detail=f"Platform network {platform_network} not found.")
        except Exception as e:
            logger.error(f"Error attaching container to platform network: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error attaching container to platform network: {str(e)}")
        
        return {
            "message": "vLLM container started and attached to platform network successfully",
            "container_id": container.id
        }
    except docker.errors.APIError as e:
        logger.error(f"Docker API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/stop-vllm")
def stop_vllm_container(model_name: str):
    # Use the last part of the model name as the container name
    container_name = model_name.split("/")[-1]
    logger.info(f"Received request to stop container: {container_name}")
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
        logger.info(f"Container {container_name} stopped and removed successfully")
        return {"message": f"vLLM container {container_name} stopped and removed successfully"}
    except docker.errors.NotFound:
        logger.error(f"Container {container_name} not found")
        raise HTTPException(status_code=404, detail=f"Container {container_name} not found")
    except docker.errors.APIError as e:
        logger.error(f"Docker API error while stopping/removing container: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/status-vllm")
def status_vllm_container(model_name: str):
    container_name = model_name.split("/")[-1]
    logger.info(f"Checking status of container: {container_name}")
    try:
        container = client.containers.get(container_name)
        return {"container_id": container.id, "status": container.status}
    except docker.errors.NotFound:
        logger.error(f"Container {container_name} not found")
        raise HTTPException(status_code=404, detail=f"Container {container_name} not found")
    except Exception as e:
        logger.error(f"Error retrieving container status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI server starting up")
    # Cleanup orphaned containers matching our naming convention
    for container in client.containers.list(all=True):
        if container.name.startswith("vllm"):
            try:
                container.remove(force=True)
                logger.info(f"Removed orphaned container: {container.name}")
            except Exception as e:
                logger.error(f"Error removing container {container.name}: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("FastAPI server shutting down")
    # Stop all running vLLM containers gracefully
    for container in client.containers.list():
        if container.name.startswith("vllm"):
            try:
                container.stop()
                logger.info(f"Stopped container during shutdown: {container.name}")
            except Exception as e:
                logger.error(f"Error stopping container {container.name}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on port 7500")
    uvicorn.run(app, host="0.0.0.0", port=7500)
