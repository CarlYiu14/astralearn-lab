import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps.auth import get_current_user
from app.deps.course_access import require_course_faculty, require_course_member
from app.models import LessonQuiz, LessonSection, LessonUnit, User
from app.schemas.lesson import (
    LessonCompileRequest,
    LessonCompileResponse,
    LessonDetail,
    LessonQuizOut,
    LessonSectionOut,
    LessonSummary,
)
from app.services.audit_service import write_audit
from app.services.async_jobs import enqueue_lesson_compile
from app.services.lesson_compiler import compile_lesson_unit
from app.services.lesson_publish import publish_lesson, unpublish_lesson

router = APIRouter(tags=["lessons"])


@router.post("/courses/{course_id}/lessons/compile", response_model=LessonCompileResponse)
def compile_lesson(
    course_id: uuid.UUID,
    payload: LessonCompileRequest,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> LessonCompileResponse:
    require_course_faculty(db, course_id=course_id, user=current)

    if payload.run_async:
        job_id = enqueue_lesson_compile(
            db,
            course_id=course_id,
            document_id=payload.source_document_id,
            target_audience=payload.target_audience,
        )
        write_audit(
            db,
            action="lesson.compile",
            actor_user_id=current.id,
            course_id=course_id,
            resource_type="async_job",
            resource_id=job_id,
            detail={"mode": "async", "document_id": str(payload.source_document_id)},
            request=request,
        )
        db.commit()
        return LessonCompileResponse(mode="async", job_id=job_id)

    try:
        lesson_id = compile_lesson_unit(
            db,
            course_id=course_id,
            document_id=payload.source_document_id,
            target_audience=payload.target_audience,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    write_audit(
        db,
        action="lesson.compile",
        actor_user_id=current.id,
        course_id=course_id,
        resource_type="lesson_unit",
        resource_id=lesson_id,
        detail={"mode": "sync", "document_id": str(payload.source_document_id)},
        request=request,
    )
    db.commit()
    return LessonCompileResponse(mode="sync", lesson_unit_id=lesson_id)


@router.get("/courses/{course_id}/lessons", response_model=list[LessonSummary])
def list_lessons(
    course_id: uuid.UUID,
    lesson_status: str | None = Query(default=None, alias="status", description="draft | published | all"),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[LessonUnit]:
    if lesson_status is not None and lesson_status not in {"draft", "published", "all"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="status must be draft, published, or all")

    member = require_course_member(db, course_id=course_id, user=current)

    effective_status = lesson_status
    if member.role == "student":
        if lesson_status in (None, "published"):
            effective_status = "published"
        elif lesson_status in {"all", "draft"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students may only list published lessons",
            )

    stmt = select(LessonUnit).where(LessonUnit.course_id == course_id)
    if effective_status in {"draft", "published"}:
        stmt = stmt.where(LessonUnit.status == effective_status)

    return list(db.execute(stmt.order_by(LessonUnit.created_at.desc())).scalars().all())


@router.post("/courses/{course_id}/lessons/{lesson_id}/publish", response_model=LessonSummary)
def publish_lesson_endpoint(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> LessonUnit:
    require_course_faculty(db, course_id=course_id, user=current)
    try:
        lesson = publish_lesson(db, course_id=course_id, lesson_id=lesson_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    write_audit(
        db,
        action="lesson.publish",
        actor_user_id=current.id,
        course_id=course_id,
        resource_type="lesson_unit",
        resource_id=lesson.id,
        request=request,
    )
    db.commit()
    return lesson


@router.post("/courses/{course_id}/lessons/{lesson_id}/unpublish", response_model=LessonSummary)
def unpublish_lesson_endpoint(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> LessonUnit:
    require_course_faculty(db, course_id=course_id, user=current)
    try:
        lesson = unpublish_lesson(db, course_id=course_id, lesson_id=lesson_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    write_audit(
        db,
        action="lesson.unpublish",
        actor_user_id=current.id,
        course_id=course_id,
        resource_type="lesson_unit",
        resource_id=lesson.id,
        request=request,
    )
    db.commit()
    return lesson


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_model=LessonDetail)
def get_lesson(
    course_id: uuid.UUID, lesson_id: uuid.UUID, db: Session = Depends(get_db), current: User = Depends(get_current_user)
) -> LessonDetail:
    member = require_course_member(db, course_id=course_id, user=current)

    lesson = db.get(LessonUnit, lesson_id)
    if lesson is None or lesson.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    if lesson.status != "published" and member.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Published lessons only for student role",
        )

    sections = (
        db.execute(
            select(LessonSection)
            .where(LessonSection.lesson_unit_id == lesson_id)
            .order_by(LessonSection.order_no, LessonSection.id)
        )
        .scalars()
        .all()
    )
    quizzes = db.execute(select(LessonQuiz).where(LessonQuiz.lesson_unit_id == lesson_id)).scalars().all()

    return LessonDetail(
        lesson=LessonSummary.model_validate(lesson),
        sections=[LessonSectionOut.model_validate(s) for s in sections],
        quizzes=[LessonQuizOut.model_validate(q) for q in quizzes],
    )
