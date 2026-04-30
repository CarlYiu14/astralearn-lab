from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class RetrievedChunk:
    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    extra: dict[str, Any]


def retrieve_chunks_for_course(
    db: Session, *, course_id: uuid.UUID, query_embedding: list[float], top_k: int
) -> list[RetrievedChunk]:
    vec_literal = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
    sql = text(
        """
        SELECT
            dc.id,
            dc.document_id,
            dc.chunk_index,
            dc.content,
            dc.metadata AS chunk_metadata
        FROM document_chunks dc
        INNER JOIN course_documents cd ON cd.id = dc.document_id
        WHERE cd.course_id = CAST(:course_id AS uuid)
          AND dc.embedding IS NOT NULL
        ORDER BY dc.embedding <=> CAST(:qvec AS vector)
        LIMIT :top_k
        """
    )
    rows = db.execute(
        sql, {"course_id": str(course_id), "qvec": vec_literal, "top_k": top_k}
    ).mappings().all()

    out: list[RetrievedChunk] = []
    for row in rows:
        meta = row["chunk_metadata"]
        if meta is None:
            meta = {}
        if not isinstance(meta, dict):
            meta = dict(meta)
        out.append(
            RetrievedChunk(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=int(row["chunk_index"]),
                content=str(row["content"]),
                extra=meta,
            )
        )
    return out
