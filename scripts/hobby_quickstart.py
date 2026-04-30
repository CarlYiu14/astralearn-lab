"""Pick a hobby kit quickly and generate a local material file."""

from __future__ import annotations

import argparse
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT_DIR = ROOT / "packages" / "hobby-kits"


def _list_kits() -> list[str]:
    return sorted(p.name for p in KIT_DIR.glob("*.json") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", default="", help="Kit filename under packages/hobby-kits/")
    parser.add_argument("--random", action="store_true", help="Choose one random kit")
    args = parser.parse_args()

    kits = _list_kits()
    if not kits:
        raise SystemExit("No hobby kits found.")

    selected = args.kit.strip()
    if args.random:
        selected = random.choice(kits)
    if not selected:
        selected = kits[0]
    if selected not in kits:
        raise SystemExit(f"Unknown kit: {selected}")

    cmd = ["python", str(ROOT / "scripts" / "material_from_kit.py"), "--kit", selected]
    subprocess.run(cmd, cwd=ROOT, check=True)
    print(f"Quickstart kit: {selected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
