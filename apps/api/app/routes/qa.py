import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps.auth import get_current_user
from app.deps.course_access import require_course_member
from app.models import User
from app.schemas.qa import CourseQARequest, CourseQAResponse
from app.services.qa_service import run_course_qa

router = APIRouter(tags=["qa"])


@router.post("/courses/{course_id}/qa", response_model=CourseQAResponse)
def course_qa(
    course_id: uuid.UUID,
    payload: CourseQARequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> CourseQAResponse:
    require_course_member(db, course_id=course_id, user=current)
    try:
        return run_course_qa(db, course_id=course_id, question=payload.question, top_k=payload.top_k)
    except ValueError as exc:
        msg = str(exc)
        if msg == "Course not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from exc
