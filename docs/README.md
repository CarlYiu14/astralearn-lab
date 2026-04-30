# Documentation index (`docs/`)

Short guide to every Markdown file in this folder and how to use it.

| File | Role |
|------|------|
| [architecture.md](./architecture.md) | High-level system narrative by capability layer: what each layer adds and how services relate. |
| [api-contract.md](./api-contract.md) | Human-readable HTTP contract: routes, bodies, auth, and notable headers (`X-Request-ID`, internal keys). |
| [prompting.md](./prompting.md) | Where prompts live (`packages/prompts`) and how structured outputs should be validated before trust. |
| [eval-plan.md](./eval-plan.md) | How to score retrieval, lessons, and assessment quality over time (metrics + harness outline). |
| [eval/README.md](./eval/README.md) | Golden QA JSONL + `scripts/run_golden_qa.py` (staging-style regression checks). |
| [hobby-lab.md](./hobby-lab.md) | Lightweight guide for sustainable solo iteration loops. |
| [runbook.md](./runbook.md) | Short ops checklist: compose, migrations, smoke URLs, logs, eval outputs. |
| [adr/ADR-001-retrieval.md](./adr/ADR-001-retrieval.md) | Architecture Decision Record: retrieval / RAG approach. |
| [adr/ADR-002-assessment-strategy.md](./adr/ADR-002-assessment-strategy.md) | ADR: adaptive assessment MVP choices. |
| [adr/ADR-003-monorepo-packages.md](./adr/ADR-003-monorepo-packages.md) | ADR: why `packages/*` exists and when to grow it (`schemas` / `prompts` / `ui`). |
| [adr/ADR-004-api-contracts-openapi.md](./adr/ADR-004-api-contracts-openapi.md) | ADR: Pydantic + JSON Schema + OpenAPI alignment and CI contract gates. |
| [../packages/contracts/README.md](../packages/contracts/README.md) | How to produce a single contract bundle for external consumers. |
| [../packages/sdk-ts/README.md](../packages/sdk-ts/README.md) | TypeScript SDK generated from OpenAPI types. |
| [../packages/hobby-kits/README.md](../packages/hobby-kits/README.md) | Reusable local-first kit materials for hobby experiments. |

**ADRs** are short, durable decisions (“why we chose X”). When you change strategy, add a new ADR rather than silently rewriting history.

Security disclosures: see the repository root [`SECURITY.md`](../SECURITY.md).
