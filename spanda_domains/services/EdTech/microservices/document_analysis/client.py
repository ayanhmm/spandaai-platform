import requests
from typing import Dict
from pydantic import BaseModel

class RubricCriteria(BaseModel):
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
    feedback: str = None

# Define the request payload
data = QueryRequestThesisAndRubric(
    rubric={
        "Clarity": RubricCriteria(
            criteria_explanation="How clear is the thesis statement?",
            score_explanation="A well-defined thesis should be concise and clear.",
            criteria_output="The thesis statement is clearly defined."
        )
    },
    pre_analysis=PreAnalysis(
        degree="Masters",
        name="John Doe",
        topic="AI in Healthcare",
        pre_analyzed_summary="The thesis explores the impact of AI in medical diagnostics."
    ),
    feedback="Great structure but needs more examples."
)

# Send request to API Gateway
url = "http://localhost:8090/analyze"
response = requests.post(url, json=data.dict())

# Print response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
