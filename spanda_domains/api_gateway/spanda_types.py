from typing import List, Optional, Dict, Tuple
from typing_extensions import TypedDict
from pydantic import BaseModel

# Pydantic models
class ChunkTextResponse(BaseModel):
    chunks: List[Tuple[str, int]]

class TextChunkRequest(BaseModel):
    text: str
    chunk_size: Optional[int] = 1000

class FirstWordsRequest(BaseModel):
    text: str
    n_words: int

class FirstWordsResponse(BaseModel):
    text: str

class ImageProcessingResponse(BaseModel):
    analysis_results: Dict[int, str]

class DocumentAnalysisResponse(BaseModel):
    text_and_image_analysis: str

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str

# Pydantic models
class RubricCriteria(TypedDict):
    criteria_explanation: str
    score_explanation: str
    criteria_output: str

class PreAnalysis(BaseModel):
    degree: str
    name: str
    topic: str
    pre_analyzed_summary: str

class QueryRequestThesisAndRubric(BaseModel):
    rubric: Dict[str, RubricCriteria]
    pre_analysis: PreAnalysis
    feedback: Optional[str] = None

class ThesisText(BaseModel):
    text: str

class ProcessChunksRequest(BaseModel):
    chunks: List[str]
    system_prompt: str
    batch_size: int = 5

class DissertationRequest(BaseModel):
    rubric: dict
    dissertation: str
    feedback: str = None
    
class ScoringRequest(BaseModel):
    analysis: str
    criteria: str
    score_guidelines: str
    criteria_guidelines: str
    feedback: str
