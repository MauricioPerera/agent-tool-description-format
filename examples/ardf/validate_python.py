"""Quick ARDF validation sample using jsonschema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ARDF_SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ardf.schema.json",
    "title": "ARDF Resource",
    "type": "object",
    "required": ["schema_version", "resource_id", "resource_type", "description"],
    "properties": {
        "schema_version": {"type": "string"},
        "resource_id": {"type": "string"},
        "resource_type": {"type": "string"},
        "description": {"type": "string"},
        "content": {"type": "object"},
    },
}


def validate(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=payload, schema=ARDF_SCHEMA)
    print(f"? {path} is structurally valid (basic ARDF checks).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_python.py <path-to-ardf.json>", file=sys.stderr)
        raise SystemExit(1)
    validate(Path(sys.argv[1]))
