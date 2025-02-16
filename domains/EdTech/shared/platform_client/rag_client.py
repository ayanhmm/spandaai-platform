import os
import httpx
from dotenv import load_dotenv
import base64
import json
import aiohttp

# Load environment variables from .env file
load_dotenv()

VERBA_URL = os.getenv("VERBA_URL", "http://localhost:8000")  # Default if not set
VERBA_API_ENDPOINT = f"{VERBA_URL}/api/import_file"


async def send_file_to_verba(file_bytes, filename, credentials, rag_config, labels=[]):
    """
    Prepare and send the file payload to the Verba API.
    """
    UNSUPPORTED_EXTENSIONS = ("exe", "bin", "dll")
    base_filename = os.path.splitext(filename)[0]
    file_extension = os.path.splitext(filename)[1][1:]

    if file_extension.lower() in UNSUPPORTED_EXTENSIONS:
        return {"filename": filename, "status": "unsupported"}

    # Validate file content
    if not file_bytes or len(file_bytes) == 0:
        return {"filename": filename, "status": "error", "error": "File is empty or invalid"}

    try:
        encoded_file = base64.b64encode(file_bytes).decode("utf-8")
    except Exception as e:
        return {"filename": filename, "status": "error", "error": f"Base64 encoding failed: {str(e)}"}

    # Prepare metadata
    metadata = {"keywords": []}

    # File data
    file_data = {
        "fileID": f"{base_filename}.{file_extension}",
        "filename": f"{base_filename}.{file_extension}",
        "extension": file_extension,
        "status_report": {},
        "source": "",
        "isURL": False,
        "overwrite": False,
        "content": encoded_file,
        "metadata": json.dumps(metadata),
        "file_size": len(file_bytes),
        "status": "READY",
        "rag_config": rag_config,
        "labels": labels,
    }

    # Payload
    payload = {
        "fileID": f"{base_filename}.{file_extension}",
        "file_data": file_data,
        "credentials": credentials,
        "rag_config": rag_config,
        "total": 1,
        "order": 1,
        "chunk": json.dumps(file_data),
        "isLastChunk": True,
    }

    # Send to Verba API
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(VERBA_API_ENDPOINT, json=payload, headers={"Content-Type": "application/json"}) as response:
                response_text = await response.text()
                if response.status == 200:
                    return {"filename": filename, "status": "success", "response": response_text}
                else:
                    return {"filename": filename, "status": "failed", "response": response_text}
        except Exception as e:
            return {"filename": filename, "status": "error", "error": str(e)}


async def  call_spanda_retrieve(payload):
    url = f"{VERBA_URL}/api/query"
    request_data = payload
   
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, json=request_data)
        # Check if the response was successful
        if response.status_code == 200:
            is_response_relevant = response.json()
            print(is_response_relevant) 
            return is_response_relevant
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        