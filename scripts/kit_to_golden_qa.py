"""Generate a JSONL golden-QA question set from a hobby kit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"
OUT_DIR = ROOT / "docs" / "eval"


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", default="quickstart-ai-study.json", help="Kit filename under packages/hobby-kits/")
    parser.add_argument("--limit", type=int, default=6, help="Maximum questions to emit (default 6)")
    args = parser.parse_args()

    kit_path = KIT_DIR / args.kit
    if not kit_path.exists():
        raise SystemExit(f"Kit not found: {kit_path}")

    data = json.loads(kit_path.read_text(encoding="utf-8"))
    title = str(data.get("title", "Untitled Kit"))
    prompts = [str(p).strip() for p in (data.get("practice_prompts") or []) if str(p).strip()]
    if not prompts:
        raise SystemExit("Kit has no practice_prompts.")

    limit = max(1, args.limit)
    selected = prompts[:limit]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"hobby-kit-{_slug(kit_path.stem)}.jsonl"
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for q in selected:
            row = {"question": q, "source": "hobby-kit", "kit": kit_path.name, "title": title}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
