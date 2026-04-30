# Evaluation Plan

This document turns “we have RAG and lessons” into **measurable** quality. Use it to regress changes to retrieval, prompts, and compilers without guessing.

## 1. Retrieval & QA

| Metric | Definition | Target (initial) |
|--------|--------------|------------------|
| **Citation hit rate** | Share of answers where every `citations[].chunk_id` ∈ `retrieved_chunk_ids` | ≥ 0.98 |
| **Quote integrity** | Share where `citations[].quote` is a **substring** of the cited chunk text | ≥ 0.95 |
| **Groundedness (human)** | Blind score 1–5: answer only uses retrieved material | Mean ≥ 4.0 on a fixed rubric |
| **Empty retrieval rate** | `len(retrieved_chunk_ids)==0` for non-trivial questions | Trend ↓ week over week |
| **Latency p95** | Server time for `POST /qa` | Track; alert on 2× baseline |

**Harness (recommended)**

1. Freeze a **golden question set** (20–50 items) per demo course: `docs/eval/golden-qa.jsonl` (add when you lock content).
2. Script calls API with auth, stores `answer`, `citations`, `retrieved_chunk_ids`, timings.
3. Automated checks run citation/quote rules; human spot-checks a rotating 10% sample.

## 2. Lesson compiler

| Metric | Definition |
|--------|------------|
| **Schema validity** | Compiled JSON / DB rows validate against lesson DTOs |
| **Section coverage** | ≥ N sections and ≥ 1 quiz when source length > threshold |
| **Hallucination flags** | Claims with no chunk id in `extra` / provenance fields (when you add them) |

Start with **manual rubric** on 10 documents; automate once the shape stabilizes.

## 3. Adaptive assessment

| Metric | Definition |
|--------|------------|
| **Session completion** | % sessions reaching K attempts without errors |
| **θ stability** | Variance of `ability_theta` across repeated simulations with fixed item bank |
| **Item exposure** | Min / max times each `question_bank` row is drawn in simulation |

Monte-Carlo item banks in staging before changing the online update rule.

## 4. Ops & regressions

- **CI**: `pytest` + JSON schema validation (already wired).
- **Nightly** (optional): run golden QA + export CSV to `artifacts/` for trend charts.

## 5. What to build next (concrete artifacts)

1. `docs/eval/golden-qa.jsonl` — one JSON per line: `{ "course_id", "question", "min_citation_count" }`.
2. `scripts/run_golden_qa.py` — reads golden file, hits API, writes `eval-results.ndjson`.
3. Wire **OpenTelemetry** or **Prometheus** when you deploy beyond a laptop.
