# Hobby Lab Guide

This project is intentionally a serious **hobby** build: technically strong, but fun and sustainable for one maintainer.

## Principles

- Build in small slices you can finish in one evening.
- Keep contracts and tests sharp; keep process lightweight.
- Prefer visible demos over hidden architecture complexity.

## Suggested local loop

```bash
python scripts/hobby_session.py
python scripts/make_hobby_material.py
python scripts/list_hobby_kits.py
python scripts/new_hobby_kit.py --title "My Kit" --topic "My Topic" --level easy
python scripts/hobby_quickstart.py --random
python scripts/material_from_kit.py --kit quickstart-ai-study.json
python scripts/kit_drill.py --kit quickstart-ai-study.json --count 3
python scripts/kit_to_golden_qa.py --kit quickstart-ai-study.json --limit 6
python scripts/kit_pack_golden.py --level medium --per-kit-limit 3
```

Then pick one focused improvement and run only relevant checks:

- `npm run validate:schemas`
- `npm run test:api:unit`
- `npm run sdk:ts:check` (only if API contract/client changed)
- `npm run hobby:kits:validate` (when you add or edit kit JSON files)

Use the generated `tmp/hobby-course-notes.txt` for the document upload demo to avoid repeatedly preparing manual test files.
You can also generate kit-based materials from `packages/hobby-kits/` for more varied local experiments.
In `/lab`, you can filter kits by difficulty (`easy`/`medium`/`hard`) before generating material commands.

## Good "small but valuable" tasks

- Improve one demo page's copy/UX clarity.
- Add one contract test for an edge case response.
- Strengthen one prompt template with explicit output constraints.
- Simplify one service function with better naming.
