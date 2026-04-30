"""Emit FastAPI OpenAPI document for SDK generation, partner review, or contract diffing."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
DEFAULT_OUT = REPO_ROOT / "packages" / "openapi" / "astralearn.openapi.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output path (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args()

    # Import-time only: no DB round-trip until a request uses get_db.
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+psycopg://astralearn:astralearn@127.0.0.1:5432/astralearn",
    )
    os.environ.setdefault("JWT_SECRET", "local-dev-jwt-secret-at-least-32-chars!!")

    sys.path.insert(0, str(API_ROOT))
    from app.main import app  # noqa: PLC0415 — after sys.path

    spec = app.openapi()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    n_paths = len(spec.get("paths") or {})
    print(f"Wrote {args.output} ({n_paths} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
