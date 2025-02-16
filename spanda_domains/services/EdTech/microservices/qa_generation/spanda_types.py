from typing import Optional
from pydantic import BaseModel

# take file as an input in a new class and use it with Prajwal's API

class QueryRequest(BaseModel):
    topic: str
    difficulty: str
    type_of_question: str
    no_of_questions: int
    context: Optional[str] = None
    no_of_options: Optional[int] = None
    numericality:str
    few_shot: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str
    type_of_question: str
    context: Optional[str] = None  
    no_of_options: Optional[int] = None
