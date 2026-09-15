#!/usr/bin/env python3
"""Generate or verify the evidence-backed OpenAPI document."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clue_api.contracts import build_openapi

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "openapi.json"


def rendered_contract() -> str:
    return json.dumps(build_openapi(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = rendered_contract()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            print("docs/openapi.json is stale; run: uv run python scripts/generate_openapi.py")
            return 1
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
