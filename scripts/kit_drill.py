"""Print a short random drill from a hobby kit (local-only, no persistence)."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", default="quickstart-ai-study.json", help="Kit filename in packages/hobby-kits/")
    parser.add_argument("--count", type=int, default=3, help="How many prompts to sample (default 3)")
    args = parser.parse_args()

    kit_path = KIT_DIR / args.kit
    if not kit_path.exists():
        raise SystemExit(f"Kit not found: {kit_path}")

    data = json.loads(kit_path.read_text(encoding="utf-8"))
    title = str(data.get("title", "Untitled Kit"))
    level = str(data.get("level", "unknown"))
    prompts = [str(p) for p in (data.get("practice_prompts") or []) if isinstance(p, str) and p.strip()]
    if not prompts:
        raise SystemExit("No practice prompts in kit.")

    count = max(1, min(args.count, len(prompts)))
    sampled = random.sample(prompts, k=count)

    print(f"{title} [{level}]")
    print("-" * (len(title) + len(level) + 3))
    for i, p in enumerate(sampled, 1):
        print(f"{i}. {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
