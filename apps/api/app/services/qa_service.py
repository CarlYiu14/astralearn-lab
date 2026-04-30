from __future__ import annotations

import json
import uuid
from typing import Any, Literal

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Course
from app.schemas.qa import Citation, CourseQAResponse
from app.services.embeddings import embed_texts
from app.services.retrieval import RetrievedChunk, retrieve_chunks_for_course


def _openai_key_present() -> bool:
    return bool(settings.openai_api_key and settings.openai_api_key.strip())


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    lines: list[str] = []
    for ch in chunks:
        lines.append(
            f"CHUNK_ID={ch.id}\nDOCUMENT_ID={ch.document_id}\nINDEX={ch.chunk_index}\nTEXT:\n{ch.content}\n---"
        )
    return "\n".join(lines)


def _validate_citations(citations: list[dict[str, Any]], allowed: set[uuid.UUID]) -> list[Citation]:
    out: list[Citation] = []
    for raw in citations:
        try:
            cid = uuid.UUID(str(raw["chunk_id"]))
            did = uuid.UUID(str(raw["document_id"]))
            quote = str(raw.get("quote", "")).strip()
        except (KeyError, ValueError, TypeError):
            continue
        if cid not in allowed:
            continue
        if len(quote) > 500:
            quote = quote[:500]
        out.append(Citation(chunk_id=cid, document_id=did, quote=quote))
    return out


def _llm_answer(*, question: str, chunks: list[RetrievedChunk]) -> tuple[str, list[Citation], Literal["high", "medium", "low"]]:
    from openai import OpenAI

    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured")

    client = OpenAI(api_key=api_key)
    system = (
        "You answer using ONLY the provided course chunks. "
        "Return STRICT JSON with keys: answer (string), citations (array of objects with "
        "chunk_id, document_id, quote), confidence (one of: high, medium, low). "
        "Every factual claim in answer must be supported by at least one citation quote copied from chunks. "
        "If chunks are insufficient, set confidence to low and explain what is missing."
    )
    user = f"QUESTION:\n{question}\n\nCONTEXT:\n{_build_context_block(chunks)}"

    completion = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw = completion.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON") from exc
    answer = str(data.get("answer", "")).strip()
    conf_raw = str(data.get("confidence", "low")).strip().lower()
    if conf_raw not in {"high", "medium", "low"}:
        conf: Literal["high", "medium", "low"] = "low"
    else:
        conf = conf_raw  # type: ignore[assignment]

    allowed = {c.id for c in chunks}
    citations = _validate_citations(list(data.get("citations") or []), allowed)
    return answer, citations, conf


def run_course_qa(db: Session, *, course_id: uuid.UUID, question: str, top_k: int) -> CourseQAResponse:
    course = db.get(Course, course_id)
    if course is None:
        raise ValueError("Course not found")

    qvec = embed_texts([question], stable_keys=[f"qa:{course_id}:{question[:200]}"])[0]
    chunks = retrieve_chunks_for_course(db, course_id=course_id, query_embedding=qvec, top_k=top_k)
    if not chunks:
        raise ValueError("No indexed chunks found for this course. Upload and process documents first.")

    allowed_ids = [c.id for c in chunks]

    if _openai_key_present():
        answer, citations, confidence = _llm_answer(question=question, chunks=chunks)
        return CourseQAResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            mode="llm",
            retrieved_chunk_ids=allowed_ids,
        )

    head = chunks[0]
    excerpt = head.content.strip()
    if len(excerpt) > 900:
        excerpt = excerpt[:900].rstrip() + "…"

    answer = (
        "OpenAI is not configured (missing OPENAI_API_KEY), so this is an extractive preview:\n\n" + excerpt
    )
    citations = [
        Citation(
            chunk_id=head.id,
            document_id=head.document_id,
            quote=(head.content[:400].strip() + ("…" if len(head.content) > 400 else "")),
        )
    ]
    return CourseQAResponse(
        answer=answer,
        citations=citations,
        confidence="low",
        mode="extractive",
        retrieved_chunk_ids=allowed_ids,
    )
