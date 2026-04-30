"""Generate a plain-text learning material from a hobby kit JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"
OUT_DIR = ROOT / "tmp"


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", default="quickstart-ai-study.json", help="Kit file name under packages/hobby-kits/")
    args = parser.parse_args()

    kit_path = KIT_DIR / args.kit
    if not kit_path.exists():
        raise SystemExit(f"Kit not found: {kit_path}")

    data = json.loads(kit_path.read_text(encoding="utf-8"))
    title = data.get("title", "Untitled Kit")
    level = data.get("level", "unknown")
    topic = data.get("topic", "")
    points = data.get("key_points", [])
    prompts = data.get("practice_prompts", [])

    lines: list[str] = [title, "=" * len(title), ""]
    lines += [f"Level: {level}", ""]
    if topic:
        lines += [f"Topic: {topic}", ""]

    lines += ["Key Points"]
    for i, p in enumerate(points, 1):
        lines.append(f"{i}. {p}")
    lines.append("")

    lines += ["Practice Prompts"]
    for i, p in enumerate(prompts, 1):
        lines.append(f"{i}) {p}")
    lines.append("")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"kit-{_slug(kit_path.stem)}.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
