"""Validate example JSON instances against packages/schemas (CI + local)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "packages" / "schemas" / "json"
EXAMPLE_DIR = ROOT / "packages" / "schemas" / "examples"

PAIRS: list[tuple[str, str]] = [
    ("course-qa-response.schema.json", "course-qa-response.valid.json"),
    ("document-process-response.schema.json", "document-process-response.valid.json"),
    ("hobby-kit.schema.json", "hobby-kit.valid.json"),
    ("internal-health.schema.json", "internal-health.valid.json"),
    ("internal-ready.schema.json", "internal-ready.valid.json"),
    ("lesson-compile-response.schema.json", "lesson-compile-response.valid.json"),
    ("lesson-compile-response.schema.json", "lesson-compile-response.async.valid.json"),
    ("lesson-summary.schema.json", "lesson-summary.valid.json"),
]


def main() -> int:
    errors = 0
    for schema_name, example_name in PAIRS:
        schema_path = SCHEMA_DIR / schema_name
        example_path = EXAMPLE_DIR / example_name
        if not schema_path.is_file():
            print(f"MISSING schema: {schema_path}", file=sys.stderr)
            errors += 1
            continue
        if not example_path.is_file():
            print(f"MISSING example: {example_path}", file=sys.stderr)
            errors += 1
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        instance = json.loads(example_path.read_text(encoding="utf-8"))
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        validator_cls(schema).validate(instance)
        print(f"OK  {schema_name}  <==  {example_name}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
