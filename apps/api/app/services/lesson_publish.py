from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import LessonSection, LessonUnit


def publish_lesson(db: Session, *, course_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonUnit:
    lesson = db.get(LessonUnit, lesson_id)
    if lesson is None or lesson.course_id != course_id:
        raise ValueError("Lesson not found")

    section_count = db.scalar(
        select(func.count()).select_from(LessonSection).where(LessonSection.lesson_unit_id == lesson_id)
    )
    if int(section_count or 0) < 1:
        raise ValueError("Lesson must contain at least one section before publishing")

    lesson.status = "published"
    lesson.published_at = datetime.now(timezone.utc)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def unpublish_lesson(db: Session, *, course_id: uuid.UUID, lesson_id: uuid.UUID) -> LessonUnit:
    lesson = db.get(LessonUnit, lesson_id)
    if lesson is None or lesson.course_id != course_id:
        raise ValueError("Lesson not found")

    lesson.status = "draft"
    lesson.published_at = None
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson
