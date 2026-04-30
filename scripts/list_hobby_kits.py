"""Print available hobby kit JSON files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"


def main() -> int:
    if not KIT_DIR.exists():
        print("No kits directory found.")
        return 0
    files = sorted(p for p in KIT_DIR.glob("*.json") if p.is_file())
    if not files:
        print("No hobby kits found.")
        return 0
    print("Available hobby kits:")
    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            level = str(data.get("level", "unknown"))
            topic = str(data.get("topic", ""))
        except json.JSONDecodeError:
            level = "invalid-json"
            topic = ""
        suffix = f" [{level}]"
        if topic:
            suffix += f" - {topic}"
        print(f"- {p.name}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
