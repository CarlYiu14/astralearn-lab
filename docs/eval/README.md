# Golden evaluation data

## `golden-qa.jsonl`

One JSON object per line (JSONL). Each record:

| Field | Required | Description |
|-------|----------|-------------|
| `question` | yes | Sent to `POST /courses/{id}/qa`. |
| `top_k` | no | Default `8`. |

Lines starting with `#` are treated as comments by `scripts/run_golden_qa.py` only when the **entire** line begins with `#`.  
**Do not** put `#` comments on the same line as JSON — that line would be invalid JSON.

## Run locally

1. Seed or pick a course with **ready** chunks (`scripts/seed_dev_course.py` + documents demo upload/process).
2. Export credentials (example uses the seed dev user):

```bash
export API_BASE_URL=http://127.0.0.1:8000
export GOLDEN_EMAIL=dev@local.test
export GOLDEN_PASSWORD=devpassword123
export GOLDEN_COURSE_ID=<uuid from seed output>
python scripts/run_golden_qa.py
```

Results append to `eval-output/golden-qa-last.ndjson` (gitignored content; directory tracked via `.gitkeep`).

## CI

Golden runs are **optional** (live API + secrets). Wire them into a scheduled workflow when you have a stable staging URL and bot account.
