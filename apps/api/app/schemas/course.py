import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CourseCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    code: str | None = Field(default=None, max_length=50)
    term: str | None = Field(default=None, max_length=50)
    description: str | None = None


class CourseResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    code: str | None
    term: str | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
