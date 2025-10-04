"""ARDF validation snippet using jsonschema (draft 2020-12)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).parents[2] / "schema" / "ardf.schema.json"
DEFAULT_SAMPLE = Path(__file__).with_name("tool_appointment_create.json")


def validate(sample_path: Path) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = json.loads(sample_path.read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))

    if errors:
        print("? Validation errors:")
        for error in errors:
            location = ".".join(str(p) for p in error.path)
            print(f"- {location or '<root>'}: {error.message}")
    else:
        print(f"? {sample_path} is a valid ARDF descriptor")


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SAMPLE
    validate(target)
