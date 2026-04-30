import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class GraphExtractRequest(BaseModel):
    max_chunks: int | None = Field(
        default=None,
        description="If omitted, server default GRAPH_MAX_CHUNKS is used (clamped to 1..200).",
    )

    @field_validator("max_chunks")
    @classmethod
    def _clamp_max_chunks(cls, value: int | None) -> int | None:
        if value is None:
            return None
        return max(1, min(200, int(value)))


class GraphExtractResponse(BaseModel):
    mode: Literal["llm", "heuristic"]
    node_count: int
    edge_count: int
    chunks_sampled: int


class GraphNodeOut(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    description: str | None
    difficulty: int | None

    model_config = {"from_attributes": True}


class GraphEdgeOut(BaseModel):
    id: uuid.UUID
    from_node_id: uuid.UUID
    to_node_id: uuid.UUID
    edge_type: str
    weight: float

    model_config = {"from_attributes": True}


class GraphSnapshot(BaseModel):
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]
