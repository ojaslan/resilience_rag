from pydantic import BaseModel, field_validator
from typing import List, Optional


class AgentResponse(BaseModel):
    answer: str
    sources: List[str] = []
    confidence: float = 1.0
    chaos_active: bool = False
    guardrail_triggered: bool = False
    guardrail_reason: Optional[str] = None

    @field_validator("answer")
    @classmethod
    def answer_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Answer must not be empty.")
        return v

    @field_validator("confidence")
    @classmethod
    def confidence_range(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0 and 1.")
        return v


class UserQuery(BaseModel):
    query: str
    session_id: str = "default"

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Query must not be empty.")
        return v
