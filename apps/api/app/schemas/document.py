import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    status: str
    file_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentProcessRequest(BaseModel):
    mode: str = Field(default="sync", pattern="^sync$")
    reprocess: bool = Field(default=True)


class DocumentProcessResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    status: str
    chunk_count: int
    char_count: int
