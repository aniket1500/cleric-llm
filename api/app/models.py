from pydantic import BaseModel
from typing import List, Optional

class DocumentSubmission(BaseModel):
    question: str
    documents: List[str]

class GetQuestionAndFactsResponse(BaseModel):
    question: str
    facts: Optional[List[str]] = None  # Use None as the default value to avoid issues when no facts are available
    status: str

