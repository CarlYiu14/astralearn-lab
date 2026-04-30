# Hobby Kits (`packages/hobby-kits`)

Reusable mini learning kits for local demos and weekend experiments.

Each kit is a small JSON file that describes:

- title
- level (`easy` / `medium` / `hard`)
- topic
- key points
- practice prompts

These kits are intentionally simple and local-first. They are not telemetry-backed and do not create usage logs.

## Build a text material from a kit

From repo root:

```bash
python scripts/list_hobby_kits.py
python scripts/new_hobby_kit.py --title "My Kit" --topic "My Topic" --level easy
python scripts/validate_hobby_kits.py
python scripts/hobby_quickstart.py --random
python scripts/material_from_kit.py --kit quickstart-ai-study.json
python scripts/kit_drill.py --kit quickstart-ai-study.json --count 3
python scripts/kit_to_golden_qa.py --kit quickstart-ai-study.json --limit 6
python scripts/kit_pack_golden.py --level all --per-kit-limit 3
```

Output:

- `tmp/kit-quickstart-ai-study.txt`

Use that file directly in the document upload demo.
For eval experimentation, use `scripts/kit_to_golden_qa.py` to create a kit-based JSONL under `docs/eval/`.
Use `scripts/kit_pack_golden.py` to combine multiple kits into one JSONL for broader local eval.
