"""Print a lightweight local-first coding session checklist for hobby development."""

from __future__ import annotations

import random

PROMPTS = [
    "Try one tiny UX improvement in /dashboard or /lab.",
    "Add one small contract test that catches a real edge case.",
    "Improve one prompt template with safer output constraints.",
    "Refactor one service function for clearer names and comments.",
]


def main() -> int:
    print("AstraLearn hobby session")
    print("=======================")
    print("1) npm run validate:schemas")
    print("2) npm run test:api:unit")
    print("3) Pick one focus:")
    print(f"   - {random.choice(PROMPTS)}")
    print("4) End session by running only the checks affected by your change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
