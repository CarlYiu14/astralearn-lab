import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class LessonCompileRequest(BaseModel):
    source_document_id: uuid.UUID
    run_async: bool = False
    target_audience: str | None = Field(default=None, max_length=500)


class LessonCompileResponse(BaseModel):
    mode: Literal["sync", "async"]
    lesson_unit_id: uuid.UUID | None = None
    job_id: uuid.UUID | None = None


class LessonSummary(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    source_document_id: uuid.UUID
    title: str
    bloom_level: str | None
    status: str
    published_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LessonSectionOut(BaseModel):
    id: uuid.UUID
    section_type: str
    order_no: int
    content_md: str

    model_config = {"from_attributes": True}


class LessonQuizOut(BaseModel):
    id: uuid.UUID
    question: str
    options: Any | None
    rationale: str | None

    model_config = {"from_attributes": True}


class LessonDetail(BaseModel):
    lesson: LessonSummary
    sections: list[LessonSectionOut]
    quizzes: list[LessonQuizOut]
