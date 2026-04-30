from __future__ import annotations

import sys
import time
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1] / "api"
sys.path.insert(0, str(API_ROOT))

from app.db.database import SessionLocal
from app.services.async_jobs import process_next_async_job


def main() -> None:
    print("AstraLearn worker started", flush=True)
    while True:
        with SessionLocal() as db:
            try:
                processed = process_next_async_job(db)
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                print(f"worker tick failed: {exc}", flush=True)
                processed = False
        if not processed:
            time.sleep(2)


if __name__ == "__main__":
    main()
