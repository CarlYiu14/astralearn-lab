# Prompt templates (`packages/prompts`)

## Purpose

- **Single place** for instruction text that would otherwise rot inside Python strings.
- **Versioned folders** (`v1/`, `v2/`, …) so audits and experiments can say “we ran `course_qa_rag@v1`”.
- **Review-friendly**: copy editors and subject-matter experts can PR Markdown without touching FastAPI routes.

## How this ties to the API today

The FastAPI services currently embed prompts in Python for speed of iteration (`apps/api/app/services/*`). As prompts stabilize, **lift** the Markdown bodies from `packages/prompts/v*` into code loaders (or a tiny template renderer) and record `prompt_id` + `sha256` in `audit_log_entries.detail` for reproducibility.

## Layout

```
packages/prompts/
  README.md          ← you are here
  v1/
    README.md      ← versioning rules
    course_qa_rag.md
    lesson_compile_outline.md
```
