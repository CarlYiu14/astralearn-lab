#!/usr/bin/env python3
"""Run golden QA questions against a live API (no extra deps beyond stdlib).

Environment:
  API_BASE_URL          default http://127.0.0.1:8000
  GOLDEN_EMAIL          instructor / member account email
  GOLDEN_PASSWORD       password
  GOLDEN_COURSE_ID      course UUID with indexed chunks for meaningful QA

Input:  docs/eval/golden-qa.jsonl (override with --input)
Output: eval-output/golden-qa-last.ndjson (override with --output)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "docs" / "eval" / "golden-qa.jsonl"
DEFAULT_OUT_DIR = ROOT / "eval-output"


def _post_json(url: str, payload: dict, headers: dict | None = None) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"content-type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        return exc.code, err


def main() -> int:
    parser = argparse.ArgumentParser(description="Golden QA runner (stdlib HTTP).")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    base = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    email = os.environ.get("GOLDEN_EMAIL")
    password = os.environ.get("GOLDEN_PASSWORD")
    course_id = os.environ.get("GOLDEN_COURSE_ID")
    if not email or not password or not course_id:
        print(
            "Set GOLDEN_EMAIL, GOLDEN_PASSWORD, GOLDEN_COURSE_ID (and optionally API_BASE_URL).",
            file=sys.stderr,
        )
        return 2

    if not args.input.is_file():
        print(f"Missing input file: {args.input}", file=sys.stderr)
        return 2

    code, body = _post_json(f"{base}/auth/login", {"email": email, "password": password})
    if code != 200:
        print(f"Login failed {code}: {body}", file=sys.stderr)
        return 1
    token = json.loads(body)["access_token"]
    auth_headers = {"authorization": f"Bearer {token}"}

    DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = args.output or (DEFAULT_OUT_DIR / "golden-qa-last.ndjson")

    failures = 0
    with args.input.open(encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for line_no, line in enumerate(fin, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            row = json.loads(line)
            question = row["question"]
            top_k = int(row.get("top_k", 8))
            t0 = time.perf_counter()
            qc, qb = _post_json(
                f"{base}/courses/{course_id}/qa",
                {"question": question, "top_k": top_k},
                headers=auth_headers,
            )
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            record = {
                "line": line_no,
                "question": question,
                "status_code": qc,
                "elapsed_ms": elapsed_ms,
                "citation_count": None,
                "mode": None,
            }
            if qc == 200:
                try:
                    obj = json.loads(qb)
                    record["citation_count"] = len(obj.get("citations") or [])
                    record["mode"] = obj.get("mode")
                except json.JSONDecodeError:
                    record["parse_error"] = True
            else:
                failures += 1
                record["error_body"] = qb[:2000]
            fout.write(json.dumps(record, default=str) + "\n")

    print(f"Wrote {out_path} (failures={failures})")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
