from __future__ import annotations

import json
import re
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import CourseDocument, DocumentChunk, LessonQuiz, LessonSection, LessonUnit


def _openai_key_present() -> bool:
    return bool(settings.openai_api_key and settings.openai_api_key.strip())


def _load_document_corpus(db: Session, *, course_id: uuid.UUID, document_id: uuid.UUID) -> tuple[CourseDocument, str]:
    doc = db.get(CourseDocument, document_id)
    if doc is None or doc.course_id != course_id:
        raise ValueError("Document not found for this course")

    rows = db.execute(
        select(DocumentChunk.content)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).scalars().all()
    corpus = "\n\n".join(rows)
    if not corpus.strip():
        raise ValueError("Document has no indexed chunks yet. Process the document first.")
    return doc, corpus


def _normalize_section_type(value: str) -> str:
    v = value.strip().lower()
    allowed = {"objective", "explanation", "example", "summary", "checkpoint"}
    return v if v in allowed else "explanation"


def _heuristic_compile(*, document_title: str, corpus: str, audience: str | None) -> dict[str, Any]:
    parts = [p.strip() for p in re.split(r"\n{2,}", corpus) if p.strip()]
    head = parts[0][:1200] if parts else corpus[:1200]
    tail = parts[-1][:1200] if len(parts) > 1 else corpus[-1200:]

    audience_line = f"This module targets: {audience}.\n\n" if audience else ""
    sections: list[dict[str, Any]] = [
        {
            "type": "objective",
            "content": audience_line + "By the end of this micro-module, you should be able to recall the core claims in the source excerpt.",
        },
        {"type": "explanation", "content": f"### Source overview\n{head}"},
        {"type": "summary", "content": f"### Takeaways\n{tail}"},
    ]
    quiz = [
        {
            "question": "In one sentence, what is the primary focus of the opening excerpt?",
            "options": None,
            "answer_key": head.split("\n", maxsplit=1)[0].strip()[:200],
            "rationale": "This checks whether you anchored on the first explicit claim in the excerpt.",
        }
    ]
    return {
        "title": f"Micro-lesson: {document_title}",
        "bloom_level": "understand",
        "sections": sections,
        "quiz": quiz,
    }


def _llm_compile(*, document_title: str, corpus: str, audience: str | None) -> dict[str, Any]:
    from openai import OpenAI

    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured")

    client = OpenAI(api_key=api_key)
    audience_line = f"Audience: {audience}\n" if audience else ""
    system = (
        "You compile a compact micro-lesson from source text. Return STRICT JSON with keys: "
        "title, bloom_level, sections, quiz. "
        "sections is an array of {type, content} where type is one of objective|explanation|example|summary|checkpoint. "
        "content is markdown. "
        "quiz is an array (1-3 items) of {question, options, answer_key, rationale}. "
        "If options is not applicable, set it to null and use a short text answer_key."
    )
    user = f"{audience_line}DOCUMENT_TITLE:\n{document_title}\n\nSOURCE_TEXT:\n{corpus[:120000]}\n"

    completion = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.25,
    )
    raw = completion.choices[0].message.content or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON") from exc


def _persist_lesson(
    db: Session, *, course_id: uuid.UUID, document_id: uuid.UUID, payload: dict[str, Any], persist_commit: bool = True
) -> uuid.UUID:
    title = str(payload.get("title") or "Compiled lesson").strip()[:255]
    bloom = str(payload.get("bloom_level") or "").strip()[:40] or None

    lesson = LessonUnit(
        id=uuid.uuid4(),
        course_id=course_id,
        source_document_id=document_id,
        title=title,
        bloom_level=bloom,
        status="draft",
    )
    db.add(lesson)
    db.flush()

    sections = list(payload.get("sections") or [])
    for idx, sec in enumerate(sections):
        if not isinstance(sec, dict):
            continue
        st = _normalize_section_type(str(sec.get("type", "explanation")))
        content = str(sec.get("content", "")).strip()
        if not content:
            continue
        db.add(LessonSection(lesson_unit_id=lesson.id, section_type=st, order_no=idx, content_md=content))

    quizzes = list(payload.get("quiz") or [])
    for item in quizzes[:3]:
        if not isinstance(item, dict):
            continue
        q = str(item.get("question", "")).strip()
        if not q:
            continue
        answer_key = str(item.get("answer_key", "")).strip()
        if not answer_key:
            continue
        options = item.get("options")
        if options is not None and not isinstance(options, (list, dict)):
            options = None
        rationale = item.get("rationale")
        rationale_str = str(rationale).strip() if rationale is not None else None
        db.add(
            LessonQuiz(
                lesson_unit_id=lesson.id,
                question=q,
                options=options if isinstance(options, (list, dict)) or options is None else None,
                answer_key=answer_key,
                rationale=rationale_str,
            )
        )

    if persist_commit:
        db.commit()
    else:
        db.flush()
    db.refresh(lesson)
    return lesson.id


def compile_lesson_unit(
    db: Session,
    *,
    course_id: uuid.UUID,
    document_id: uuid.UUID,
    target_audience: str | None,
    persist_commit: bool = True,
) -> uuid.UUID:
    doc, corpus = _load_document_corpus(db, course_id=course_id, document_id=document_id)

    if _openai_key_present():
        payload = _llm_compile(document_title=doc.title, corpus=corpus, audience=target_audience)
    else:
        payload = _heuristic_compile(document_title=doc.title, corpus=corpus, audience=target_audience)

    if not isinstance(payload.get("sections"), list) or len(payload["sections"]) == 0:
        raise ValueError("Lesson compiler produced no sections")

    return _persist_lesson(
        db, course_id=course_id, document_id=document_id, payload=payload, persist_commit=persist_commit
    )
