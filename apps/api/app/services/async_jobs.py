from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AsyncJob
from app.services.lesson_compiler import compile_lesson_unit


def enqueue_lesson_compile(
    db: Session, *, course_id: uuid.UUID, document_id: uuid.UUID, target_audience: str | None
) -> uuid.UUID:
    job = AsyncJob(
        id=uuid.uuid4(),
        course_id=course_id,
        job_type="lesson_compile",
        payload={"source_document_id": str(document_id), "target_audience": target_audience},
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job.id


def process_next_async_job(db: Session) -> bool:
    job = db.execute(
        select(AsyncJob)
        .where(AsyncJob.status == "pending")
        .order_by(AsyncJob.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    ).scalar_one_or_none()
    if job is None:
        return False

    job.status = "running"
    db.flush()

    try:
        if job.course_id is None:
            raise ValueError("Job is missing course_id")

        if job.job_type == "lesson_compile":
            document_id = uuid.UUID(str(job.payload.get("source_document_id")))
            audience = job.payload.get("target_audience")
            if audience is not None and not isinstance(audience, str):
                audience = str(audience)

            lesson_id = compile_lesson_unit(
                db,
                course_id=job.course_id,
                document_id=document_id,
                target_audience=audience,
                persist_commit=False,
            )

            job.status = "succeeded"
            job.result = {"lesson_unit_id": str(lesson_id)}
            job.error_message = None
        else:
            job.status = "failed"
            job.error_message = f"Unsupported job_type={job.job_type}"
    except Exception as exc:  # noqa: BLE001
        job.status = "failed"
        job.error_message = str(exc)[:4000]

    db.commit()
    return True
