# Prompting Strategy

## Where templates live

- **Authoritative copies**: `packages/prompts/v*/` (Markdown, versioned folders).
- **Runtime**: FastAPI services may still inline prompts while iterating; when a prompt stabilizes, **move** the text here and load by path so diffs stay reviewable.

## Validation pipeline

1. **LLM output** → parse JSON.
2. Validate against **Pydantic** in `apps/api` for request/response cycles.
3. For cross-language checks, validate the same payload against **`packages/schemas/json/*.schema.json`** (see `scripts/validate_schemas.py`).

## Change discipline

- Bump **`vN`** only for breaking instruction or schema changes.
- Record `prompt_id` + file hash in audit metadata when you start logging prompt lineage in production jobs.

