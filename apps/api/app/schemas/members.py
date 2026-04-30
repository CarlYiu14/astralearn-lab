from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class CourseMemberInviteRequest(BaseModel):
    email: EmailStr
    role: str = Field(description="student | instructor")


class CourseMemberOut(BaseModel):
    user_id: uuid.UUID
    email: str
    name: str | None
    role: str
