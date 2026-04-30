"""Validate hobby kits against shared JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"
SCHEMA_PATH = ROOT / "packages" / "schemas" / "json" / "hobby-kit.schema.json"


def main() -> int:
    errors = 0
    if not SCHEMA_PATH.exists():
        print(f"Missing schema: {SCHEMA_PATH}", file=sys.stderr)
        return 1
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)

    files = sorted(p for p in KIT_DIR.glob("*.json") if p.is_file())
    if not files:
        print("No hobby kits found.", file=sys.stderr)
        return 1
    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"INVALID JSON  {p.name}: {exc}", file=sys.stderr)
            errors += 1
            continue
        try:
            validator.validate(data)
        except jsonschema.ValidationError as exc:
            loc = ".".join(str(i) for i in exc.path) or "<root>"
            print(f"INVALID SHAPE  {p.name} @ {loc}: {exc.message}", file=sys.stderr)
            errors += 1
            continue
        print(f"OK  {p.name}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
