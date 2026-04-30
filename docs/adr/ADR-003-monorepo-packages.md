# ADR-003: Monorepo `packages/*` layout

## Status

Accepted (Day 10+)

## Context

The repository is a **modular monorepo**: runnable apps live under `apps/*`, while `packages/*` holds **shared, versioned artifacts** that should not be duplicated across API, worker, and web.

## Decision

- **`packages/schemas`**: JSON Schema (and examples) that mirror critical API / LLM contracts so non-Python consumers and CI can validate payloads.
- **`packages/prompts`**: Markdown prompt bundles versioned by directory (`v1`, `v2`, …).
- **`packages/ui`**: Reserved until a second frontend or a real design system needs extraction from `apps/web`.

## Consequences

- Until prompts are loaded from disk in production, **Pydantic remains authoritative** at runtime; schemas and Markdown must be updated in lockstep when contracts change.
- CI runs `scripts/validate_schemas.py` so schemas and examples cannot drift unnoticed.
