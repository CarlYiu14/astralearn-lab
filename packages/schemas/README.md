# Shared JSON Schemas (`packages/schemas`)

## Why this package exists

The API (`apps/api`) uses **Pydantic** at runtime; this folder holds **language-neutral JSON Schema** so that:

- Worker jobs, CLI tools, or future **TypeScript** clients can validate the same payloads without importing Python.
- LLM **structured outputs** can be checked against a frozen contract before you trust persistence or UI rendering.
- Reviewers can diff schema changes like any other API surface.

## Layout

| Path | Purpose |
|------|---------|
| `json/*.schema.json` | Canonical schemas (Draft 2020-12). |
| `examples/*.valid.json` | Positive fixtures used by `scripts/validate_schemas.py`. |

## Current schemas

| Schema | Mirrors API |
|--------|-------------|
| `json/course-qa-response.schema.json` | `CourseQAResponse` in `apps/api/app/schemas/qa.py` |
| `json/document-process-response.schema.json` | `DocumentProcessResponse` in `apps/api/app/schemas/document.py` |
| `json/hobby-kit.schema.json` | Hobby kit JSON shape in `packages/hobby-kits/*.json` |
| `json/internal-health.schema.json` | `GET /internal/health` body (`apps/api/app/main.py`) |
| `json/internal-ready.schema.json` | `GET /internal/ready` success body (`apps/api/app/main.py`) |
| `json/lesson-compile-response.schema.json` | `LessonCompileResponse` in `apps/api/app/schemas/lesson.py` |
| `json/lesson-summary.schema.json` | `LessonSummary` in `apps/api/app/schemas/lesson.py` |

When the Pydantic model changes, update the JSON Schema and the example in the **same PR**.

## Validate locally

From repo root (with dev deps installed for `apps/api`, which includes `jsonschema`):

```bash
cd apps/api
pip install -r requirements.txt -r requirements-dev.txt
python ../../scripts/validate_schemas.py
```

CI runs this after `pytest` so schemas cannot silently drift from examples.
