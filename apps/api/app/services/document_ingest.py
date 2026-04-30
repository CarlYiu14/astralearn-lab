from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import DocumentChunk, CourseDocument
from app.services.embeddings import embed_texts


@dataclass(frozen=True)
class IngestResult:
    chunk_count: int
    char_count: int


def _read_text(file_path: Path) -> str:
    # Day 3 focuses on .txt; PDF/Office ingestion comes later.
    if file_path.suffix.lower() not in {".txt", ".md"}:
        msg = f"Unsupported file type: {file_path.suffix or '(no extension)'}"
        raise ValueError(msg)
    return file_path.read_text(encoding="utf-8", errors="replace")


def _chunk_text(text: str, *, max_chars: int = 2000) -> list[str]:
    text = re.sub(r"\r\n", "\n", text).strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0

    for p in paragraphs:
        if not buf:
            buf = [p]
            buf_len = len(p)
            continue

        if buf_len + 2 + len(p) > max_chars:
            chunks.append("\n\n".join(buf))
            buf = [p]
            buf_len = len(p)
        else:
            buf.append(p)
            buf_len += 2 + len(p)

    if buf:
        chunks.append("\n\n".join(buf))

    # If a single paragraph is larger than max_chars, hard-split.
    final: list[str] = []
    for chunk in chunks:
        if len(chunk) <= max_chars:
            final.append(chunk)
            continue
        for i in range(0, len(chunk), max_chars):
            final.append(chunk[i : i + max_chars])

    return final


def process_document_to_chunks(db: Session, document: CourseDocument) -> IngestResult:
    # Idempotent: wipe prior derived chunks before recompute.
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))

    document.status = "processing"
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        file_path = Path(document.file_path)
        text = _read_text(file_path)
        parts = _chunk_text(text)
        if not parts:
            document.status = "failed"
            db.add(document)
            db.commit()
            raise ValueError("Document is empty or could not be chunked")

        stable_keys = [f"{document.id}:{idx}:{len(part)}" for idx, part in enumerate(parts)]
        vectors = embed_texts(parts, stable_keys=stable_keys)
        if len(vectors) != len(parts):
            raise RuntimeError("Embedding provider returned an unexpected vector count")

        for idx, (part, vec) in enumerate(zip(parts, vectors, strict=True)):
            db.add(
                DocumentChunk(
                    document_id=document.id,  # type: ignore[arg-type]
                    chunk_index=idx,
                    content=part,
                    embedding=vec,
                    extra={"source_path": str(file_path.name), "chars": len(part)},
                )
            )

        document.status = "ready"
        db.add(document)
        db.commit()

        return IngestResult(chunk_count=len(parts), char_count=len(text))
    except Exception:
        document.status = "failed"
        db.add(document)
        db.commit()
        raise


def build_storage_path(*, course_id: uuid.UUID, document_id: uuid.UUID, original_name: str) -> Path:
    base = Path(settings.storage_dir) / "uploads" / str(course_id)
    base.mkdir(parents=True, exist_ok=True)
    safe_name = os.path.basename(original_name) or "upload.bin"
    return base / f"{document_id}_{safe_name}"


def ensure_parent_exists(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
