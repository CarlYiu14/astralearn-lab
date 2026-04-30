from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Course, CourseMember, User
from app.services.membership import get_membership, role_at_least


def get_course_or_404(db: Session, course_id: uuid.UUID) -> Course:
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


def require_course_member(db: Session, *, course_id: uuid.UUID, user: User) -> CourseMember:
    _ = get_course_or_404(db, course_id)
    member = get_membership(db, course_id=course_id, user_id=user.id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this course")
    return member


def require_course_faculty(db: Session, *, course_id: uuid.UUID, user: User) -> CourseMember:
    member = require_course_member(db, course_id=course_id, user=user)
    if not role_at_least(member.role, "instructor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or owner role required for this action",
        )
    return member
