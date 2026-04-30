# Contract Bundle (`packages/contracts`)

This package documents how to produce a **single contract artifact** for API consumers:

- JSON Schema contracts + examples (`packages/schemas`)
- OpenAPI document (`/openapi.json` exported to file)
- Route inventory (method/path table)

## Generate locally

From repo root:

```bash
python scripts/export_contract_bundle.py
```

Default output:

`artifacts/contracts/latest`

## Why this exists

- Gives QA / partner teams one stable payload instead of browsing the repo.
- Supports release checks (what contracts shipped in this cut).
- Makes API changes auditable over time via artifact diffs.
