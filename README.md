# AstraLearn OS

Monorepo for course-oriented AI workflows: content ingest, grounded Q&A, concept graph extraction, lesson generation, and adaptive assessment.

## Architecture

- `apps/api`: FastAPI service, data model, migrations, auth/RBAC, feature endpoints
- `apps/web`: Next.js client and demo routes
- `apps/worker`: asynchronous job runner
- `packages/schemas`: JSON Schema contracts and examples
- `packages/openapi`: OpenAPI export documentation
- `packages/sdk-ts`: typed TypeScript SDK generated from OpenAPI
- `packages/hobby-kits`: reusable local experiment kits
- `packages/prompts`: prompt templates
- `infra/docker`: local runtime stack
- `scripts`: local automation (validation, kit tooling, contract helpers)

## Runtime Requirements

- Docker + Docker Compose
- Python 3.12+
- Node.js 20+

## Local Setup

All commands below are executed in a terminal.

### 1) Start infrastructure and services

Run from repository root:

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

Default endpoints:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- Postgres: `localhost:5432`

### 2) Apply migrations and seed sample data

Open a second terminal at repository root:

```bash
cd apps/api
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
cd ../..
python scripts/seed_dev_course.py
```

The seed command prints login credentials and a `COURSE_ID` for demo routes.

### 3) Exercise the application

- `http://localhost:3000/courses/demo/auth`
- `http://localhost:3000/dashboard`
- `http://localhost:3000/lab`

## Verification

From repository root:

```bash
npm run validate:schemas
npm run test:api:unit
```

Integration tests:

```bash
cd apps/api
pytest -q
```

Frontend lint:

```bash
cd apps/web
npm run lint
```

## Core Developer Commands

- `npm run openapi:export`
- `npm run routes:list`
- `npm run contracts:bundle`
- `npm run sdk:ts:check`
- `npm run eval:golden`

## Hobby Kit Commands

- `npm run hobby:kits`
- `npm run hobby:kits:validate`
- `npm run hobby:kit:new -- --title "My Kit" --topic "My Topic" --level easy`
- `npm run hobby:kit -- --kit quickstart-ai-study.json`
- `npm run hobby:quickstart`
- `npm run hobby:drill -- --kit quickstart-ai-study.json --count 3`
- `npm run hobby:golden -- --kit quickstart-ai-study.json --limit 6`
- `npm run hobby:golden:pack -- --level all --per-kit-limit 3`

## Additional Documentation

- `docs/README.md`
- `CONTRIBUTING.md`
- `docs/runbook.md`
