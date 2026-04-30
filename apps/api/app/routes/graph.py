import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps.auth import get_current_user
from app.deps.course_access import get_course_or_404, require_course_faculty, require_course_member
from app.models import ConceptEdge, ConceptNode, User
from app.schemas.graph import GraphExtractRequest, GraphExtractResponse, GraphEdgeOut, GraphNodeOut, GraphSnapshot
from app.services.graph_extract import extract_course_graph

router = APIRouter(tags=["graph"])


@router.post("/courses/{course_id}/graph/extract", response_model=GraphExtractResponse)
def extract_graph(
    course_id: uuid.UUID,
    payload: GraphExtractRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> GraphExtractResponse:
    require_course_faculty(db, course_id=course_id, user=current)
    try:
        result = extract_course_graph(db, course_id=course_id, max_chunks=payload.max_chunks)
    except ValueError as exc:
        msg = str(exc)
        if msg == "Course not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from exc

    return GraphExtractResponse(
        mode=result.mode,
        node_count=result.node_count,
        edge_count=result.edge_count,
        chunks_sampled=result.chunks_sampled,
    )


@router.get("/courses/{course_id}/graph", response_model=GraphSnapshot)
def get_graph(
    course_id: uuid.UUID, db: Session = Depends(get_db), current: User = Depends(get_current_user)
) -> GraphSnapshot:
    require_course_member(db, course_id=course_id, user=current)
    _ = get_course_or_404(db, course_id)

    nodes = (
        db.execute(select(ConceptNode).where(ConceptNode.course_id == course_id).order_by(ConceptNode.name))
        .scalars()
        .all()
    )
    edges = (
        db.execute(
            select(ConceptEdge)
            .where(ConceptEdge.course_id == course_id)
            .order_by(ConceptEdge.edge_type, ConceptEdge.from_node_id, ConceptEdge.to_node_id)
        )
        .scalars()
        .all()
    )

    return GraphSnapshot(
        nodes=[GraphNodeOut.model_validate(n) for n in nodes],
        edges=[GraphEdgeOut.model_validate(e) for e in edges],
    )
