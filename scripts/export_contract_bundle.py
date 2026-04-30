"""Build a contract bundle artifact for partners, SDK generation, and release QA.

Bundle contents (under output dir):
- schemas/json/*.schema.json
- schemas/examples/*.valid.json
- routes/routes.txt (from scripts/list_routes.py output)
- openapi/astralearn.openapi.json (from scripts/export_openapi.py output)
- manifest.json (counts + generated timestamp)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_JSON_DIR = ROOT / "packages" / "schemas" / "json"
SCHEMA_EXAMPLE_DIR = ROOT / "packages" / "schemas" / "examples"
DEFAULT_OUT = ROOT / "artifacts" / "contracts" / "latest"


def _copy_tree(src: Path, dst: Path, pattern: str) -> int:
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in sorted(src.glob(pattern)):
        if item.is_file():
            shutil.copy2(item, dst / item.name)
            count += 1
    return count


def _run_script_capture_stdout(script_name: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["python", str(ROOT / "scripts" / script_name)]
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        subprocess.run(cmd, cwd=ROOT, check=True, stdout=f, stderr=subprocess.STDOUT)


def _run_export_openapi(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["python", str(ROOT / "scripts" / "export_openapi.py"), "-o", str(output_path)]
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Bundle output directory (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args()

    out = args.output_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    schema_count = _copy_tree(SCHEMA_JSON_DIR, out / "schemas" / "json", "*.schema.json")
    example_count = _copy_tree(SCHEMA_EXAMPLE_DIR, out / "schemas" / "examples", "*.json")

    _run_script_capture_stdout("list_routes.py", out / "routes" / "routes.txt")
    _run_export_openapi(out / "openapi" / "astralearn.openapi.json")

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "schema_count": schema_count,
        "example_count": example_count,
        "paths": {
            "schemas_json": "schemas/json",
            "schemas_examples": "schemas/examples",
            "routes": "routes/routes.txt",
            "openapi": "openapi/astralearn.openapi.json",
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Contract bundle written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
