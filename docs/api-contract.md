# API Contract (Draft)

## Health / readiness (Day 10)

- `GET /internal/health` — process liveness (no DB).

- `GET /internal/ready` — readiness: runs `SELECT 1` against PostgreSQL; returns **503** when the database is unreachable.

- Successful HTTP responses include header **`X-Request-ID`** (also exposed to browsers via CORS `expose_headers`).

## Auth (Day 8–9)

All `/courses/**` routes require `Authorization: Bearer <access_token>` unless noted otherwise.

- `POST /auth/register`
  - request: `{ "email": "string", "password": "string (min 8)", "name": "optional string" }`
  - response: `{ "access_token", "refresh_token", "token_type": "bearer", "expires_in", "refresh_expires_in" }`
  - creates a global `users.role=student` account; course access still requires a `course_members` row (invite).

- `POST /auth/login`
  - request: `{ "email": "string", "password": "string" }`
  - response: same token envelope as register (includes **refresh_token**).

- `POST /auth/refresh`
  - request: `{ "refresh_token": "opaque string" }`
  - response: new access + new refresh (previous refresh row is revoked; **one-time rotation**).

- `POST /auth/logout` (204, empty body)
  - body `{ "refresh_token": "…" }` revokes that refresh session; optional `Authorization` improves audit actor linkage.
  - body `{ "revoke_all_sessions": true }` requires `Authorization: Bearer` and revokes **all** refresh tokens for that user.

- `GET /auth/me`
  - headers: `Authorization: Bearer …`
  - response: `{ id, email, name, role, created_at }`

- `GET /auth/audit/me?limit=50`
  - headers: `Authorization: Bearer …`
  - response: newest-first audit rows where `actor_user_id` is the current user (login, refresh, course actions, etc.).

Server settings: `JWT_SECRET` (min 32 chars), `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (default 30), `REFRESH_TOKEN_EXPIRE_DAYS` (default 14).

## Courses (Day 8)

- `GET /courses`
  - lists courses where the current user has a `course_members` row.

- `POST /courses`
  - request: `{ "title", "code?", "term?", "description?" }` (no `owner_id`; caller becomes owner).

- `GET /courses/{course_id}`
  - requires course membership.

- `GET /courses/{course_id}/members`
  - instructor or owner only; returns `{ user_id, email, name, role }[]`.

- `POST /courses/{course_id}/members`
  - instructor or owner; body `{ "email": "registered-user@...", "role": "student" | "instructor" }`
  - only owners may invite `instructor`; invitee must already exist (`POST /auth/register` first).

- `GET /courses/{course_id}/audit-log?limit=80`
  - instructor or owner; returns newest-first `audit_log_entries` scoped to `course_id`.

## Documents (Day 3, Day 8 auth)

- `POST /courses/{course_id}/documents/upload` (multipart) — **instructor or owner**
- `POST /courses/{course_id}/documents/{document_id}/process` — **instructor or owner**
- `GET /courses/{course_id}/documents` — any member

## QA (Day 4, Day 8 auth)

- `POST /courses/{course_id}/qa` — any member

## Graph (Day 5, Day 8 auth)

- `POST /courses/{course_id}/graph/extract` — **instructor or owner**
- `GET /courses/{course_id}/graph` — any member

## Lessons (Day 6, Day 8 auth + visibility)

- `POST /courses/{course_id}/lessons/compile` — **instructor or owner**
- `GET /courses/{course_id}/lessons` — any member; **students** only ever see `published` rows (query `status` is coerced).
- `GET /courses/{course_id}/lessons/{lesson_id}` — any member; **students** cannot fetch draft lessons.
- `POST .../publish` / `POST .../unpublish` — **instructor or owner**

## Lessons publishing (Day 7)

- `POST /courses/{course_id}/lessons/{lesson_id}/publish`
  - requires at least one lesson section
  - sets `status=published` and `published_at=now()`

- `POST /courses/{course_id}/lessons/{lesson_id}/unpublish`
  - sets `status=draft` and clears `published_at`

## Assessment (Day 6–8)

- `POST /courses/{course_id}/assessment/sessions`
  - body may be `{}`; session `user_id` is always the authenticated user.

- `POST /courses/{course_id}/assessment/sessions/{session_id}/next-question`
  - session must belong to the current user.

- `POST /courses/{course_id}/assessment/sessions/{session_id}/submit`
  - request: `{ "question_id": "uuid", "user_answer": "string" }`
  - response: `{ "is_correct": bool, "score": float, "q_type": string, "ability_theta": float }`

## Jobs (Day 6)

- `GET /internal/jobs/{job_id}`
  - response: async job record (`pending|running|succeeded|failed`)

## Internal auth (Day 7)

- When `INTERNAL_API_KEY` is set, internal endpoints require header `X-Internal-Key: <key>`.
- When unset, internal endpoints remain open for local development.

## Next

- Day 11+: OAuth2 providers, Redis-backed rate limits, Celery workers, item calibration datasets
