# OpenAPI (`packages/openapi`)

The HTTP surface is defined by **FastAPI** in `apps/api`. This folder holds **machine-generated** artifacts for consumers who do not want to import Python.

## Generate

From the monorepo root (with `apps/api` dependencies installed):

```bash
pip install -r apps/api/requirements.txt -r apps/api/requirements-dev.txt
python scripts/export_openapi.py
```

Optional output path:

```bash
python scripts/export_openapi.py -o /tmp/astralearn.openapi.json
```

## Route inventory (text)

```bash
python scripts/list_routes.py
```

## Live server

When the API is running, the same document is available at **`/openapi.json`** (and interactive docs at `/docs`).
