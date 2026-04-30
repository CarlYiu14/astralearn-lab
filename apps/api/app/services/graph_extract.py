from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import ConceptEdge, ConceptNode, Course, CourseDocument, DocumentChunk


def _openai_key_present() -> bool:
    return bool(settings.openai_api_key and settings.openai_api_key.strip())


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return (value[:120] if value else "concept") or "concept"


def sample_course_corpus(db: Session, *, course_id: uuid.UUID, max_chunks: int) -> tuple[str, int]:
    stmt = (
        select(DocumentChunk.content, CourseDocument.title)
        .join(CourseDocument, CourseDocument.id == DocumentChunk.document_id)
        .where(CourseDocument.course_id == course_id)
        .where(CourseDocument.status == "ready")
        .order_by(CourseDocument.created_at.desc(), DocumentChunk.document_id, DocumentChunk.chunk_index)
        .limit(max_chunks)
    )
    rows = db.execute(stmt).all()
    parts: list[str] = []
    for content, title in rows:
        header = (title or "document").strip()
        parts.append(f"=== SOURCE: {header} ===\n{content}\n")
    return "\n".join(parts), len(rows)


def _dedupe_nodes(nodes: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for node in nodes:
        slug = str(node.get("slug", "")).strip()
        if not slug:
            continue
        if slug in seen:
            continue
        seen.add(slug)
        out.append(node)
    return out


def _normalize_nodes(raw_nodes: list[object]) -> list[dict]:
    nodes: list[dict] = []
    for item in raw_nodes:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        slug = str(item.get("slug", "")).strip() or slugify(name)
        slug = slugify(slug)
        desc = item.get("description")
        description = str(desc).strip() if desc is not None else None
        difficulty = item.get("difficulty")
        diff_int: int | None
        if difficulty is None:
            diff_int = None
        else:
            try:
                diff_int = int(difficulty)
            except (TypeError, ValueError):
                diff_int = None
            if diff_int is not None:
                diff_int = max(1, min(5, diff_int))
        nodes.append({"slug": slug, "name": name[:255], "description": description, "difficulty": diff_int})
    return _dedupe_nodes(nodes)


def _normalize_edges(raw_edges: list[object], *, allowed_slugs: set[str]) -> list[dict]:
    edges: list[dict] = []
    for item in raw_edges:
        if not isinstance(item, dict):
            continue
        a = slugify(str(item.get("from_slug", "")).strip())
        b = slugify(str(item.get("to_slug", "")).strip())
        if not a or not b or a == b:
            continue
        if a not in allowed_slugs or b not in allowed_slugs:
            continue
        et = str(item.get("edge_type", "related")).strip().lower()
        if et not in {"prerequisite", "related"}:
            et = "related"
        edges.append({"from_slug": a, "to_slug": b, "edge_type": et})
    dedup: set[tuple[str, str, str]] = set()
    out: list[dict] = []
    for e in edges:
        key = (e["from_slug"], e["to_slug"], e["edge_type"])
        if key in dedup:
            continue
        dedup.add(key)
        out.append(e)
    return out


def _heuristic_graph(corpus: str) -> tuple[list[dict], list[dict]]:
    nodes: list[dict] = []
    seen_slugs: set[str] = set()

    for raw in corpus.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            name = re.sub(r"^#+\s*", "", line).strip()
        elif len(line) <= 120 and not line.endswith(".") and len(line) >= 3:
            name = line
        else:
            continue

        slug = slugify(name)
        base = slug
        i = 2
        while slug in seen_slugs:
            slug = f"{base}-{i}"
            i += 1
        seen_slugs.add(slug)
        nodes.append({"slug": slug, "name": name[:255], "description": None, "difficulty": None})
        if len(nodes) >= 18:
            break

    if len(nodes) < 2:
        blob = re.sub(r"\s+", " ", corpus).strip()
        snippet = blob[:900]
        parts = [p.strip() for p in re.split(r"[.;\n]+", snippet) if 10 <= len(p.strip()) <= 120]
        for p in parts[:10]:
            slug = slugify(p)
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            nodes.append({"slug": slug, "name": p[:255], "description": None, "difficulty": None})
            if len(nodes) >= 8:
                break

    if len(nodes) < 2:
        return [], []

    edges: list[dict] = []
    for i in range(len(nodes) - 1):
        edges.append(
            {"from_slug": nodes[i]["slug"], "to_slug": nodes[i + 1]["slug"], "edge_type": "related"}
        )
    return nodes, edges


def _extract_llm(*, course_title: str, corpus: str) -> tuple[list[dict], list[dict]]:
    from openai import OpenAI

    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured")

    client = OpenAI(api_key=api_key)
    system = (
        "You extract a compact concept graph for a single university course. "
        "Return STRICT JSON with keys: nodes, edges. "
        "nodes is an array of objects {slug, name, description, difficulty?}. "
        "edges is an array of objects {from_slug, to_slug, edge_type}. "
        "edge_type must be prerequisite or related. "
        "Use 8-24 nodes. Slugs must be lowercase ascii words separated by hyphens. "
        "Only connect nodes that you defined. Avoid self loops."
    )
    user = f"COURSE_TITLE:\n{course_title}\n\nSOURCE_TEXT:\n{corpus[:120000]}\n"

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

    nodes = _normalize_nodes(list(data.get("nodes") or []))
    allowed = {n["slug"] for n in nodes}
    edges = _normalize_edges(list(data.get("edges") or []), allowed_slugs=allowed)
    return nodes, edges


def replace_course_graph(db: Session, *, course_id: uuid.UUID, nodes: list[dict], edges: list[dict]) -> None:
    db.execute(delete(ConceptEdge).where(ConceptEdge.course_id == course_id))
    db.execute(delete(ConceptNode).where(ConceptNode.course_id == course_id))
    db.flush()

    slug_to_id: dict[str, uuid.UUID] = {}
    for node in nodes:
        nid = uuid.uuid4()
        slug_to_id[node["slug"]] = nid
        db.add(
            ConceptNode(
                id=nid,
                course_id=course_id,
                slug=node["slug"],
                name=node["name"],
                description=node.get("description"),
                difficulty=node.get("difficulty"),
            )
        )
    db.flush()

    seen_edges: set[tuple[uuid.UUID, uuid.UUID, str]] = set()
    for edge in edges:
        from_id = slug_to_id.get(edge["from_slug"])
        to_id = slug_to_id.get(edge["to_slug"])
        if from_id is None or to_id is None:
            continue
        if from_id == to_id:
            continue
        et = edge["edge_type"]
        key = (from_id, to_id, et)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        db.add(
            ConceptEdge(
                id=uuid.uuid4(),
                course_id=course_id,
                from_node_id=from_id,
                to_node_id=to_id,
                edge_type=et,
            )
        )
    db.commit()


@dataclass(frozen=True)
class GraphExtractResult:
    mode: Literal["llm", "heuristic"]
    node_count: int
    edge_count: int
    chunks_sampled: int


def extract_course_graph(db: Session, *, course_id: uuid.UUID, max_chunks: int | None) -> GraphExtractResult:
    course = db.get(Course, course_id)
    if course is None:
        raise ValueError("Course not found")

    limit = max_chunks if max_chunks is not None else int(settings.graph_max_chunks)
    limit = max(1, min(200, limit))

    corpus, sampled = sample_course_corpus(db, course_id=course_id, max_chunks=limit)
    if sampled == 0:
        raise ValueError("No ready document chunks found for this course. Upload and process documents first.")

    if _openai_key_present():
        nodes, edges = _extract_llm(course_title=course.title, corpus=corpus)
        mode = "llm"
    else:
        nodes, edges = _heuristic_graph(corpus)
        mode = "heuristic"

    if len(nodes) < 2:
        raise ValueError("Graph extraction produced too few nodes for this corpus.")

    replace_course_graph(db, course_id=course_id, nodes=nodes, edges=edges)
    return GraphExtractResult(mode=mode, node_count=len(nodes), edge_count=len(edges), chunks_sampled=sampled)
