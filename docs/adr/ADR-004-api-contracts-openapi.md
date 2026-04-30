# ADR-004: API contracts (Pydantic, JSON Schema, OpenAPI)

## Status

Accepted

## Context

The API is implemented in **FastAPI** with **Pydantic** models. External systems (workers, CLIs, future TypeScript clients, LLM structured outputs) need stable contracts that can be reviewed and validated **without importing Python**.

## Decision

1. **Runtime validation** stays in **Pydantic** inside `apps/api`.
2. **Language-neutral contracts** for selected response shapes live in **`packages/schemas`** as JSON Schema + positive examples, enforced by `scripts/validate_schemas.py` and **`apps/api/tests/unit/test_contracts.py`**.
3. The **full HTTP surface** is described by **OpenAPI** emitted from FastAPI (`scripts/export_openapi.py`, live `/openapi.json`).
4. **CI** runs a **no-database** `contracts` job (schemas + unit contracts + OpenAPI export + route list) in parallel with integration tests so contract drift is caught early.

## Consequences

- Any change to a mirrored Pydantic model must update **JSON Schema + example** in the same pull request.
- OpenAPI is regenerated in CI and attached as an **artifact**; developers can regenerate locally for SDK generation or partner handoff.
- Internal probes (`/internal/health`, `/internal/ready`) have lightweight JSON Schemas so ops-facing payloads stay documented alongside product APIs.
