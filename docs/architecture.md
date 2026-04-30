# Architecture (Layered Evolution)

AstraLearn OS starts as a modular monorepo:

- `apps/web` serves the learner and instructor interface.
- `apps/api` serves HTTP APIs for content and learner workflows.
- `apps/worker` handles async ingestion and model jobs.
- `postgres + pgvector` stores relational data and vector search data.
- `redis` supports queueing and caching patterns.

Layer 2 introduces data models and migration workflows.

Layer 3 adds document ingestion: uploads are stored on disk, processed into `document_chunks`, and embedded using OpenAI when configured, otherwise a deterministic offline vector for local development.

Layer 4 adds retrieval QA: question embeddings, pgvector nearest-neighbor search scoped to a course, and optional OpenAI JSON answers with citation validation against retrieved chunk ids.

Layer 5 adds a course-scoped concept graph (`concept_nodes`, `concept_edges`) extracted from sampled chunks, persisted for reuse, and exposed via dedicated graph endpoints.

Layer 6 adds lesson compilation (`lesson_units` + sections + quizzes), a minimal adaptive assessment loop (`question_bank`, `assessment_sessions`, `attempts`), and a DB-backed `async_jobs` queue processed by a lightweight worker process.

Layer 7 adds lesson publishing metadata (`published_at`), an online 1PL-style ability estimate (`ability_theta`) updated after each graded attempt, optional `INTERNAL_API_KEY` protection for internal job reads, and safer job claiming using `SELECT ... FOR UPDATE SKIP LOCKED` with transactional lesson compilation inside the worker.

Layer 8 adds password-backed users (`users.password_hash` with bcrypt), JWT access tokens (`Authorization: Bearer`), course-scoped RBAC via `course_members` (student vs instructor vs owner), protected `/courses/**` routes, roster listing and invite-by-email for faculty, and assessment sessions that are always bound to the authenticated principal.

Layer 9 adds opaque refresh tokens persisted as SHA-256 hashes with rotation on `/auth/refresh`, optional session-wide revocation on logout, shorter-lived access JWTs by default, and append-only `audit_log_entries` (JSONB detail) for auth flows plus high-value course mutations (create course, invites, document upload, lesson compile/publish/unpublish). Faculty can read a course-scoped audit tail; users can read their own actor trail via `/auth/audit/me`.

Layer 10 adds **pytest** integration coverage (auth + refresh rotation + course RBAC + health/ready), CI running **PostgreSQL + pgvector** with `pytest` on every push, per-test **TRUNCATE** isolation for committed API work, **JSON request logs** with `X-Request-ID` correlation via middleware, and a **`GET /internal/ready`** probe suitable for Kubernetes readiness checks.

Layer 11 fills **`packages/schemas`** with a real **JSON Schema + example** for course QA (CI-validated), adds **`packages/prompts/v1`** Markdown skeletons, documents the monorepo packages in **ADR-003**, adds **`docs/README.md`** as a documentation index, and expands **`docs/eval-plan.md`** with measurable retrieval/lesson/assessment dimensions.

Layer 12 extends **`packages/schemas`** with **lesson compile** and **lesson summary** JSON Schemas (plus CI-validated examples), adds **`apps/api/tests/unit/test_contracts.py`** to assert **Pydantic ↔ JSON Schema** alignment, reorganizes pytest into **`tests/integration`** vs **`tests/unit`**, introduces a **golden QA** runner (`scripts/run_golden_qa.py` + `docs/eval/golden-qa.jsonl`), a root **`package.json`** convenience scripts layer, **`CONTRIBUTING.md`**, **`docs/runbook.md`**, and a **`/dashboard`** Next.js page that lists member courses behind JWT.

Layer 13 widens **`packages/schemas`** to cover **document processing** and **internal health/ready** payloads, adds **`scripts/export_openapi.py`** + **`scripts/list_routes.py`** with **`packages/openapi/README.md`**, a parallel **CI `contracts`** job (schemas + unit contracts + OpenAPI artifact + route inventory log), **ESLint** (`eslint.config.mjs` + `npm run lint`) in the web CI job, a new **`packages/prompts/v1/graph_concept_extract.md`** template, root **`SECURITY.md`**, and **ADR-004** documenting the contract strategy.

Layer 14 adds a **contract bundle** pipeline (`scripts/export_contract_bundle.py`) that packages schemas/examples, OpenAPI, and route inventory into a single artifact (`artifacts/contracts/latest`) and publishes it in CI (`astralearn-contract-bundle`) for release QA and external integration handoff.

Layer 15 introduces **`packages/sdk-ts`**, a typed TypeScript SDK that regenerates types from exported OpenAPI (`openapi-typescript`) and compiles in CI. This creates a direct API-consumer surface and makes contract drift visible to frontend/tooling consumers before merge.

Layer 16 adds a hobby-focused **Lab workflow** with a dedicated `/lab` page in the web app, plus `docs/hobby-lab.md` and `scripts/hobby_session.py` so solo development stays playful and sustainable without heavyweight release tracking.

For a quick map of every Markdown file under `docs/`, start at [`docs/README.md`](./README.md).
