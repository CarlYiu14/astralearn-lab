from __future__ import annotations

import math
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AssessmentSession, Attempt, CourseDocument, DocumentChunk, QuestionBank


def _normalize_answer(value: str) -> str:
    return " ".join(value.strip().lower().split())


def seed_questions_from_chunks(db: Session, *, course_id: uuid.UUID, min_count: int = 6) -> int:
    existing = db.scalar(select(func.count()).select_from(QuestionBank).where(QuestionBank.course_id == course_id))
    if existing is None:
        existing = 0
    if int(existing) >= min_count:
        return int(existing)

    needed = min_count - int(existing)
    stmt = (
        select(DocumentChunk.id, DocumentChunk.content)
        .join(CourseDocument, CourseDocument.id == DocumentChunk.document_id)
        .where(CourseDocument.course_id == course_id)
        .where(CourseDocument.status == "ready")
        .order_by(func.random())
        .limit(max(1, needed))
    )
    rows = db.execute(stmt).all()
    if not rows:
        raise ValueError("No indexed chunks available to seed questions for this course.")

    created = 0
    for rank, (chunk_id, content) in enumerate(rows):
        text = str(content).strip()
        first_line = text.split("\n", maxsplit=1)[0].strip()
        answer_key = first_line[:200] if first_line else text[:80]
        prompt = (
            "Answer with the exact opening line of the excerpt (case and spacing are normalized for grading).\n\n"
            f"EXCERPT:\n{text[:900]}"
        )
        db.add(
            QuestionBank(
                id=uuid.uuid4(),
                course_id=course_id,
                difficulty=max(1, min(5, 2 + (rank % 3))),
                q_type="short_answer",
                prompt=prompt,
                answer_key=answer_key,
                options=None,
                extra={"source_chunk_id": str(chunk_id)},
            )
        )
        created += 1

    db.commit()
    return int(existing) + created


def start_practice_session(db: Session, *, course_id: uuid.UUID, user_id: uuid.UUID | None) -> uuid.UUID:
    seed_questions_from_chunks(db, course_id=course_id, min_count=6)
    session = AssessmentSession(id=uuid.uuid4(), course_id=course_id, user_id=user_id, mode="practice", state="active")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session.id


def _attempted_question_ids(db: Session, *, session_id: uuid.UUID) -> set[uuid.UUID]:
    rows = db.execute(select(Attempt.question_id).where(Attempt.session_id == session_id)).scalars().all()
    return set(rows)


def _pick_target_difficulty(db: Session, *, session_id: uuid.UUID) -> int:
    last = db.execute(
        select(Attempt.is_correct, QuestionBank.difficulty)
        .join(QuestionBank, QuestionBank.id == Attempt.question_id)
        .where(Attempt.session_id == session_id)
        .order_by(Attempt.created_at.desc())
        .limit(1)
    ).first()
    if last is None:
        return 2
    was_correct, prev_diff = last
    prev = int(prev_diff)
    if was_correct:
        return min(5, prev + 1)
    return max(1, prev - 1)


def pick_next_question(db: Session, *, course_id: uuid.UUID, session_id: uuid.UUID) -> tuple[QuestionBank | None, int]:
    session = db.get(AssessmentSession, session_id)
    if session is None or session.course_id != course_id or session.state != "active":
        raise ValueError("Session not found")

    attempted = _attempted_question_ids(db, session_id=session_id)
    target = _pick_target_difficulty(db, session_id=session_id)

    base = select(QuestionBank).where(QuestionBank.course_id == course_id)
    if attempted:
        base = base.where(~QuestionBank.id.in_(attempted))

    q = db.execute(base.where(QuestionBank.difficulty == target).order_by(func.random()).limit(1)).scalar_one_or_none()
    if q is not None:
        return q, target
    q2 = db.execute(base.order_by(func.random()).limit(1)).scalar_one_or_none()
    return q2, target


def grade_answer(*, question: QuestionBank, user_answer: str) -> tuple[bool, float]:
    if question.q_type == "mcq":
        expected = _normalize_answer(question.answer_key)
        got = _normalize_answer(user_answer)
        return got == expected, 1.0 if got == expected else 0.0

    expected = _normalize_answer(question.answer_key)
    got = _normalize_answer(user_answer)
    ok = got == expected
    return ok, 1.0 if ok else 0.0


def _update_session_ability_theta(session: AssessmentSession, *, question: QuestionBank, is_correct: bool) -> float:
    """Online 1PL-style update: treat difficulty as a fixed item parameter b on a compact scale."""
    theta = float(session.ability_theta or 0.0)
    b = (int(question.difficulty) - 3) * 0.35
    eta = 0.45
    y = 1.0 if is_correct else 0.0
    p = 1.0 / (1.0 + math.exp(-(theta - b)))
    theta_next = theta + eta * (y - p)
    theta_next = max(-3.0, min(3.0, theta_next))
    session.ability_theta = theta_next
    return theta_next


def record_attempt(
    db: Session, *, course_id: uuid.UUID, session_id: uuid.UUID, question_id: uuid.UUID, user_answer: str
) -> dict[str, Any]:
    session = db.get(AssessmentSession, session_id)
    if session is None or session.course_id != course_id:
        raise ValueError("Session not found")

    question = db.get(QuestionBank, question_id)
    if question is None or question.course_id != course_id:
        raise ValueError("Question not found")

    ok, score = grade_answer(question=question, user_answer=user_answer)
    theta_next = _update_session_ability_theta(session, question=question, is_correct=ok)
    attempt = Attempt(
        id=uuid.uuid4(),
        session_id=session_id,
        question_id=question_id,
        user_answer=user_answer,
        is_correct=ok,
        score=score,
    )
    db.add(attempt)
    db.add(session)
    db.commit()
    return {"is_correct": ok, "score": score, "q_type": question.q_type, "ability_theta": theta_next}
