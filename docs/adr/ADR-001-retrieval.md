# ADR-001: Retrieval Baseline

## Status
Accepted (Day 1 baseline)

## Decision
Use PostgreSQL + pgvector as the initial retrieval backend before introducing a dedicated vector database.

## Rationale
Reduces operational complexity while supporting hybrid relational and embedding workloads.
