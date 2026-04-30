# Contributing to AstraLearn OS

## Prerequisites

- Python **3.12+**
- Node **20+**
- Docker (recommended) for PostgreSQL + pgvector locally

## Clone and install

```bash
git clone <repo-url>
cd "LLM-powered feature"
```

**API**

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt -r requirements-dev.txt
```

**Web**

```bash
cd apps/web
npm install
```

## Common commands (repo root)

Uses root `package.json` scripts:

| Command | Purpose |
|---------|---------|
| `npm run test:api` | Full pytest (Postgres required; see CI). |
| `npm run test:api:unit` | Unit tests only (JSON schema ↔ Pydantic; no DB). |
| `npm run validate:schemas` | Validate `packages/schemas` examples. |
| `npm run openapi:export` | Write `packages/openapi/astralearn.openapi.json` (ignored by git; see `packages/openapi/README.md`). |
| `npm run routes:list` | Print `METHOD path` for every mounted API route. |
| `npm run contracts:bundle` | Build `artifacts/contracts/latest` (schema/examples + routes + OpenAPI + manifest). |
| `npm run sdk:ts:check` | Generate SDK OpenAPI types + compile `packages/sdk-ts`. |
| `npm run eval:golden` | Golden QA runner (needs live API + `GOLDEN_*` env vars). |
| `python scripts/hobby_session.py` | Print a small, local-first session checklist for hobby development. |
| `npm run hobby:material` | Generate `tmp/hobby-course-notes.txt` for quick document demo runs. |
| `npm run hobby:kits` | List available kit JSON files under `packages/hobby-kits/`. |
| `npm run hobby:kits:validate` | Validate hobby kit JSON shape for local quality checks. |
| `npm run hobby:kit:new -- --title "My Kit" --topic "Topic" --level easy` | Create a new hobby kit JSON template. |
| `npm run hobby:kit` | Generate `tmp/kit-*.txt` from `packages/hobby-kits/*.json`. |
| `npm run hobby:quickstart` | Pick a random kit and generate material in one command. |
| `npm run hobby:drill -- --kit <name>.json --count 3` | Print a short random practice drill from a kit. |
| `npm run hobby:golden -- --kit <name>.json --limit 6` | Build a kit-based JSONL question set in `docs/eval/`. |
| `npm run hobby:golden:pack -- --level all --per-kit-limit 3` | Build one combined kit-pack JSONL for eval runs. |

## Database

```bash
cd apps/api
alembic upgrade head
```

Seed a dev user + course:

```bash
python ../../scripts/seed_dev_course.py
```

## Style

- Match existing formatting and typing in touched files.
- Update **JSON Schema examples** in the same PR when Pydantic contracts change.
- Prefer small, reviewable PRs over large mixed refactors.

## Security

- Never commit `.env` or real JWT secrets.
- Do not put `INTERNAL_API_KEY` or production refresh tokens in browser demos.
