from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    actor_user_id: uuid.UUID | None
    action: str
    course_id: uuid.UUID | None
    resource_type: str | None
    resource_id: uuid.UUID | None
    detail: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
