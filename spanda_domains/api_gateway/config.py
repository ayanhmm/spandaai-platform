import os

# Configuration
class Config:
    DATA_PROCESSING_URL = os.getenv("DATA_PROCESSING_URL", "http://localhost:9001")
    EDU_AI_AGENTS_URL = os.getenv("EDU_AI_AGENTS_URL", "http://localhost:9002")
    GATEWAY_PORT = int(os.getenv("PORT", "8090"))
    DOCUMENT_ANALYSIS_URL = os.getenv("DOCUMENT_ANALYSIS_URL", "http://localhost:9000")