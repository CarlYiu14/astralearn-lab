from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CourseMember

ROLE_ORDER = {"student": 1, "instructor": 2, "owner": 3}


def role_at_least(role: str, minimum: str) -> bool:
    return ROLE_ORDER.get(role, 0) >= ROLE_ORDER[minimum]


def get_membership(db: Session, *, course_id: uuid.UUID, user_id: uuid.UUID) -> CourseMember | None:
    return db.execute(
        select(CourseMember).where(CourseMember.course_id == course_id, CourseMember.user_id == user_id)
    ).scalar_one_or_none()
