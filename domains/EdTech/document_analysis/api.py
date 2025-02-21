from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from document_analysis import analysis_algorithms
from document_analysis.spanda_types import QueryRequestThesisAndRubric

import uvicorn
import asyncio

app = FastAPI()

@app.websocket("/api/ws/document_analysis")
async def websocket_document(websocket: WebSocket):
    document_analyzer = analysis_algorithms.DocumentAnalyzer()
    
    try:
        await websocket.accept()
        
        # Receive and process the initial data
        data = await websocket.receive_json()
        request = QueryRequestThesisAndRubric(**data)
        
        process_task = asyncio.create_task(
            document_analyzer.process_Document(websocket, request)
        )
        
        # Wait for either the processing to complete or a disconnect
        try:
            await process_task
        except WebSocketDisconnect:
            # Cancel the processing task if websocket disconnects
            process_task.cancel()
            document_analyzer.handle_disconnect()
            print("WebSocket disconnected during processing")
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            if not document_analyzer.is_connection_closed:
                await document_analyzer.safe_send(websocket, {
                    "type": "error",
                    "data": {"message": str(e)}
                })
            
    except WebSocketDisconnect:
        print("WebSocket disconnected during setup")
        await document_analyzer.handle_disconnect()
    except Exception as e:
        print(f"Error in main handler: {str(e)}")
        if not document_analyzer.is_connection_closed:
            await document_analyzer.safe_send(websocket, {
                "type": "error",
                "data": {"message": str(e)}
            })
    finally:
        if not document_analyzer.is_connection_closed:
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
