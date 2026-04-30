"""Create a new hobby kit JSON template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"
LEVELS = {"easy", "medium", "hard"}


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Kit title")
    parser.add_argument("--topic", required=True, help="Kit topic")
    parser.add_argument("--level", default="easy", help="easy/medium/hard")
    args = parser.parse_args()

    level = args.level.strip().lower()
    if level not in LEVELS:
        raise SystemExit(f"Invalid level: {level}")

    filename = f"{_slug(args.title)}.json"
    path = KIT_DIR / filename
    if path.exists():
        raise SystemExit(f"Kit already exists: {path}")

    data = {
        "title": args.title.strip(),
        "level": level,
        "topic": args.topic.strip(),
        "key_points": [
            "Add 3-5 short bullet points here.",
            "Keep each point concrete and learner-friendly.",
        ],
        "practice_prompts": [
            "Add 3-6 practice prompts here.",
            "Make prompts short, clear, and answerable.",
        ],
    }
    KIT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    print("Next: run `python scripts/validate_hobby_kits.py`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
