from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from document_analysis import analysis_algorithms
from document_analysis.spanda_types import QueryRequestThesisAndRubric

import uvicorn
import asyncio

app = FastAPI()

@app.websocket("/api/ws/dissertation_analysis")
async def websocket_dissertation(websocket: WebSocket):
    """
    WebSocket Endpoint: /api/ws/dissertation_analysis

    This endpoint enables real-time dissertation analysis. Please check API documentation for details.

    Workflow:
    1. Accepts a WebSocket connection.
    2. Receives JSON with a rubric, dissertation details, and optional feedback.
    3. Processes the dissertation asynchronously.
    4. Streams real-time progress and analysis results.
    5. Handles errors and disconnections gracefully.

    Usage:
    1. Connect to ws://<host>:9000/api/ws/dissertation_analysis.
    2. Send a JSON payload.
    3. Receive step-by-step analysis updates.

    Returns:
    - None (Communication via WebSocket messages).
    """
    dissertation_analyzer = analysis_algorithms.DocumentAnalyzer()
    
    try:
        await websocket.accept()
        
        # Receive and process the initial data
        data = await websocket.receive_json()
        request = QueryRequestThesisAndRubric(**data)
        
        # Create a task for processing the dissertation
        process_task = asyncio.create_task(
            dissertation_analyzer.process_Document(websocket, request)
        )
        
        # Wait for either the processing to complete or a disconnect
        try:
            await process_task
        except WebSocketDisconnect:
            # Cancel the processing task if websocket disconnects
            process_task.cancel()
            dissertation_analyzer.handle_disconnect()
            print("WebSocket disconnected during processing")
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            if not dissertation_analyzer.is_connection_closed:
                await dissertation_analyzer.safe_send(websocket, {
                    "type": "error",
                    "data": {"message": str(e)}
                })
            
    except WebSocketDisconnect:
        print("WebSocket disconnected during setup")
        await dissertation_analyzer.handle_disconnect()
    except Exception as e:
        print(f"Error in main handler: {str(e)}")
        if not dissertation_analyzer.is_connection_closed:
            await dissertation_analyzer.safe_send(websocket, {
                "type": "error",
                "data": {"message": str(e)}
            })
    finally:
        if not dissertation_analyzer.is_connection_closed:
            await websocket.close()


@app.post("/analyze")
async def analyze_document(request: QueryRequestThesisAndRubric):
    """Non-streaming endpoint to analyze a document."""
    document_analyzer = analysis_algorithms.DocumentAnalyzer()
    result = await document_analyzer.process_Document(None, request, streaming=False)
    return result


# Main function to start the FastAPI server
def main():
    uvicorn.run(app, host="0.0.0.0", port=9000)


if __name__ == "__main__":
    main()
