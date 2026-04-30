import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID | None
    job_type: str
    status: str
    payload: dict[str, Any]
    result: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
