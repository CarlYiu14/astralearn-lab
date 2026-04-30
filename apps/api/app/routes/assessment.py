import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps.auth import get_current_user
from app.deps.course_access import require_course_member
from app.models import AssessmentSession, Course, User
from app.schemas.assessment import (
    AssessmentSessionCreateRequest,
    AssessmentSessionCreateResponse,
    NextQuestionResponse,
    QuestionPublic,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.assessment_service import pick_next_question, record_attempt, start_practice_session

router = APIRouter(tags=["assessment"])


def _assert_session_actor(session: AssessmentSession, user: User) -> None:
    if session.user_id is None or session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This practice session does not belong to the current user",
        )


@router.post("/courses/{course_id}/assessment/sessions", response_model=AssessmentSessionCreateResponse)
def create_session(
    course_id: uuid.UUID,
    payload: AssessmentSessionCreateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> AssessmentSessionCreateResponse:
    _ = payload
    require_course_member(db, course_id=course_id, user=current)

    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    try:
        session_id = start_practice_session(db, course_id=course_id, user_id=current.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AssessmentSessionCreateResponse(session_id=session_id)


@router.post("/courses/{course_id}/assessment/sessions/{session_id}/next-question", response_model=NextQuestionResponse)
def next_question(
    course_id: uuid.UUID,
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> NextQuestionResponse:
    require_course_member(db, course_id=course_id, user=current)

    session = db.get(AssessmentSession, session_id)
    if session is None or session.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    _assert_session_actor(session, current)

    try:
        question, target = pick_next_question(db, course_id=course_id, session_id=session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.refresh(session)
    theta = float(session.ability_theta or 0.0)

    if question is None:
        return NextQuestionResponse(question=None, target_difficulty=target, ability_theta=theta)

    public = QuestionPublic.model_validate(question)
    return NextQuestionResponse(question=public, target_difficulty=target, ability_theta=theta)


@router.post("/courses/{course_id}/assessment/sessions/{session_id}/submit", response_model=SubmitAnswerResponse)
def submit_answer(
    course_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> SubmitAnswerResponse:
    require_course_member(db, course_id=course_id, user=current)

    session = db.get(AssessmentSession, session_id)
    if session is None or session.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    _assert_session_actor(session, current)

    try:
        result = record_attempt(
            db,
            course_id=course_id,
            session_id=session_id,
            question_id=payload.question_id,
            user_answer=payload.user_answer,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return SubmitAnswerResponse(
        is_correct=result["is_correct"],
        score=result["score"],
        q_type=result["q_type"],
        ability_theta=result["ability_theta"],
    )
