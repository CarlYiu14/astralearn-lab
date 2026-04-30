# TypeScript SDK (`packages/sdk-ts`)

Typed SDK for AstraLearn API using OpenAPI-derived TypeScript types.

## Workflow

1. Export latest OpenAPI:

```bash
python scripts/export_openapi.py
```

2. Generate types + compile SDK:

```bash
cd packages/sdk-ts
npm install
npm run check
```

`npm run check` executes:

- `generate:types` (writes `src/generated/openapi.ts`)
- `build` (TypeScript compile to `dist/`)

## Current surface

- `auth.register(payload)`
- `auth.login(payload)` (also stores access token in client)
- `auth.me()`
- `courses.list()`
- `courses.qa(courseId, payload)`
- `courses.listDocuments(courseId)`
