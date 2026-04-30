import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AssessmentSessionCreateRequest(BaseModel):
    """Body optional; session is always bound to the authenticated user."""

    model_config = ConfigDict(extra="ignore")


class AssessmentSessionCreateResponse(BaseModel):
    session_id: uuid.UUID


class QuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: uuid.UUID
    difficulty: int
    q_type: str
    prompt: str
    options: Any | None = None


class NextQuestionResponse(BaseModel):
    question: QuestionPublic | None
    target_difficulty: int
    ability_theta: float


class SubmitAnswerRequest(BaseModel):
    question_id: uuid.UUID
    user_answer: str = Field(min_length=1, max_length=8000)


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    score: float
    q_type: str
    ability_theta: float
