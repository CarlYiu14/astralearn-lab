import uuid
from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    quote: str = Field(max_length=500)


class CourseQARequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=8, ge=1, le=24)


class CourseQAResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: Literal["high", "medium", "low"]
    mode: Literal["llm", "extractive"]
    retrieved_chunk_ids: list[uuid.UUID]
