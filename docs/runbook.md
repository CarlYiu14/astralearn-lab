# Operations runbook

## Local stack

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

- API: `http://localhost:8000`
- Web: `http://localhost:3000`
- Postgres: `localhost:5432` (see compose for credentials)

## Migrations

```bash
cd apps/api
alembic upgrade head
```

## Smoke checks

| Check | Command / URL |
|-------|----------------|
| Liveness | `GET http://localhost:8000/internal/health` |
| Readiness | `GET http://localhost:8000/internal/ready` |
| Auth | Open `http://localhost:3000/courses/demo/auth` |

## Logs

- API emits **one JSON line per HTTP request** on logger `astralearn.http` (includes `request_id`, `status_code`, `duration_ms`).
- Correlate with browser or client via **`X-Request-ID`** response header.

## OpenAPI

- Live: `GET http://localhost:8000/openapi.json` (and `/docs` for Swagger UI).
- Regenerate to disk: `python scripts/export_openapi.py` → `packages/openapi/astralearn.openapi.json` (gitignored; see `packages/openapi/README.md`).
- Text route list: `python scripts/list_routes.py`.
- Hobby loop helper: `python scripts/hobby_session.py`.

## Evaluation

- Golden questions: `docs/eval/golden-qa.jsonl`
- Runner: `python scripts/run_golden_qa.py` (see `docs/eval/README.md`)
- Outputs: `eval-output/golden-qa-last.ndjson` (ignored by git except `.gitkeep`)

## Failure triage (short)

1. **503 on `/internal/ready`** — Postgres down, wrong `DATABASE_URL`, or migrations not applied.
2. **401 on course routes** — Missing or expired JWT; refresh or re-login.
3. **403 on course** — User is not in `course_members` for that course.
