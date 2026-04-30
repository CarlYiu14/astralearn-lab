"""Print HTTP method + path for every mounted route (useful for audits and changelog baselines)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"


def main() -> int:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+psycopg://astralearn:astralearn@127.0.0.1:5432/astralearn",
    )
    os.environ.setdefault("JWT_SECRET", "local-dev-jwt-secret-at-least-32-chars!!")

    sys.path.insert(0, str(API_ROOT))
    from app.main import app  # noqa: PLC0415

    rows: list[tuple[str, str]] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        if not path or not isinstance(path, str):
            continue
        methods = getattr(route, "methods", None) or set()
        for m in sorted(methods):
            if m == "HEAD":
                continue
            rows.append((m, path))
    rows.sort(key=lambda x: (x[1], x[0]))
    for method, path in rows:
        print(f"{method:7} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
