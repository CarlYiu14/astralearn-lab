"""Generate a small plain-text study material for quick local demos."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "tmp"
OUT_FILE = OUT_DIR / "hobby-course-notes.txt"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    text = """AstraLearn Hobby Material
========================

Module 1: Retrieval QA
- Good answers must cite chunk ids.
- High confidence requires direct evidence in top chunks.

Module 2: Lesson Design
- Keep lesson objectives explicit.
- Use short sections and one quiz question per concept.

Module 3: Assessment Loop
- Adapt difficulty from recent correctness.
- Track why a learner missed a concept, not just score.

Mini Exercises
1) Explain why citations prevent hallucination in study assistants.
2) Draft a 5-minute micro-lesson from one paragraph.
3) Propose one low-friction way to improve question quality.
"""
    OUT_FILE.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
