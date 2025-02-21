from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import yaml
import asyncio
import logging
import sys

app = FastAPI()

# CORS setup - allowing all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store the generated YAML config file
CONFIG_FILE_PATH = "promptfooconfig.yaml"

# Configure logging with maximum detail
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],  # Ensures logs are printed immediately
)

def log_info(message):
    """Logs an info message with ✅ emoji"""
    logging.info(f"✅ {message}")
    print(f"✅ {message}", flush=True)

def log_error(message):
    """Logs an error message with ❌ emoji"""
    logging.error(f"❌ {message}")
    print(f"❌ {message}", flush=True)

def model_exists(model_name):
    """
    Checks if the model is already available in Ollama.
    Returns True if the model exists, False otherwise.
    """
    try:
        list_command = "docker exec -it ollama ollama list"
        log_info(f"Checking if model '{model_name}' exists with command: {list_command}")

        process = subprocess.Popen(
            list_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            log_error(f"Error checking models: {stderr.decode()}")
            return False

        models_available = stdout.decode()
        log_info(f"Available models:\n{models_available}")

        return model_name in models_available

    except Exception as e:
        log_error(f"Failed to check model existence: {str(e)}")
        return False

@app.post("/generate-config/")
async def generate_config(data: dict):
    """
    Generate the `promptfooconfig.yaml` dynamically from user input and pull the model if needed.
    """
    model_name = data["model"]
    dataset = data["dataset"]
    prompt = data["prompt"] + " ensure to return the output only in JSON format"

    log_info(f"Received request to generate config for model: {model_name}")

    # Check if model exists before pulling
    if model_exists(model_name):
        log_info(f"Model '{model_name}' already exists. Skipping pull.")
    else:
        log_info(f"Model '{model_name}' not found. Pulling model...")

        try:
            model_pull_command = f"docker exec -it ollama ollama pull {model_name}"
            log_info(f"Pulling model using command: {model_pull_command}")

            process = subprocess.Popen(
                model_pull_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                log_error(f"Error pulling model: {stderr.decode()}")
                return {"message": "Error pulling model", "error": stderr.decode()}

            log_info(f"Model pulled successfully: {stdout.decode()}")

        except Exception as e:
            log_error(f"Failed to pull model: {str(e)}")
            return {"message": "Error pulling model", "error": str(e)}

    # Generate YAML config
    config_data = {
        "prompts": [prompt],
        "providers": [f"ollama:{model_name}"],
        "tests": dataset,
        "defaultTest": {
            "options": {
                "provider": {
                    "text": {
                        "id": f"ollama:{model_name}"
                    }
                }
            }
        }
    }

    with open(CONFIG_FILE_PATH, "w") as f:
        yaml.dump(config_data, f)

    log_info(f"Generated YAML config saved to {CONFIG_FILE_PATH}")
    return {"message": "Config file generated successfully"}

@app.post("/run-eval/")
async def run_eval():
    """
    REST API endpoint to run `promptfoo eval` followed by `promptfoo view`.
    Runs `promptfoo view` in the background to prevent blocking.
    """
    try:
        log_info("Starting `promptfoo eval` process...")
        eval_process = await asyncio.create_subprocess_shell(
            "promptfoo eval",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        eval_stdout, eval_stderr = await eval_process.communicate()

        log_info(f"Evaluation output:\n{eval_stdout.decode()}")

        # Start `promptfoo view` in the background
        log_info("Starting `promptfoo view` process in the background...")
        subprocess.Popen(
            ["promptfoo", "view"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Ensures FastAPI does not block
        )

        log_info("Promptfoo view started successfully!")

        return {
            "message": "Evaluation completed successfully, and view is running in the background.",
            "eval_output": eval_stdout.decode() if eval_stdout else "",
        }

    except Exception as e:
        log_error(f"Error during execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Run the server when executing the script directly
if __name__ == "__main__":
    import uvicorn
    log_info("Starting FastAPI server on port 7100")
    uvicorn.run(app, host="0.0.0.0", port=7100)
