"""Build one combined golden-QA JSONL from multiple hobby kits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"
OUT_DIR = ROOT / "docs" / "eval"
LEVELS = {"easy", "medium", "hard"}


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")


def _collect_kits(level: str, explicit: list[str]) -> list[Path]:
    all_kits = sorted(p for p in KIT_DIR.glob("*.json") if p.is_file())
    if explicit:
        wanted = {x.strip() for x in explicit if x.strip()}
        return [p for p in all_kits if p.name in wanted]
    if level == "all":
        return all_kits
    filtered: list[Path] = []
    for p in all_kits:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if str(data.get("level")) == level:
            filtered.append(p)
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", default="all", help="all/easy/medium/hard (default all)")
    parser.add_argument("--kits", default="", help="Comma-separated kit file names (overrides --level)")
    parser.add_argument("--per-kit-limit", type=int, default=3, help="Max prompts per kit (default 3)")
    args = parser.parse_args()

    level = args.level.strip().lower()
    if level != "all" and level not in LEVELS:
        raise SystemExit(f"Invalid level: {level}")
    explicit = [x for x in args.kits.split(",") if x.strip()]
    per_kit = max(1, args.per_kit_limit)

    kits = _collect_kits(level=level, explicit=explicit)
    if not kits:
        raise SystemExit("No kits selected.")

    rows: list[dict[str, str]] = []
    for p in kits:
        data = json.loads(p.read_text(encoding="utf-8"))
        title = str(data.get("title", "Untitled Kit"))
        kit_level = str(data.get("level", "unknown"))
        prompts = [str(x).strip() for x in (data.get("practice_prompts") or []) if str(x).strip()]
        for q in prompts[:per_kit]:
            rows.append(
                {
                    "question": q,
                    "source": "hobby-kit-pack",
                    "kit": p.name,
                    "title": title,
                    "level": kit_level,
                }
            )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tag = _slug(level if not explicit else "custom")
    out_path = OUT_DIR / f"hobby-pack-{tag}.jsonl"
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path} ({len(rows)} questions from {len(kits)} kits)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
