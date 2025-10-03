import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Tuple, Union

import jsonschema

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("atdf_validator")

ToolSource = Union[str, os.PathLike, dict]


def load_json(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error: Invalid JSON in '{file_path}': {e}")
        return None


def _resolve_tool_source(tool: ToolSource) -> Tuple[Any, str]:
    """Return the tool payload and a label describing its origin."""
    if isinstance(tool, dict):
        return tool, "<in-memory>"
    if isinstance(tool, (str, os.PathLike, Path)):
        path = Path(tool)
        data = load_json(path)
        return data, str(path)
    raise TypeError(f"Unsupported tool type: {type(tool)!r}")


def _load_schema(schema_path: str) -> Any:
    schema = load_json(schema_path)
    if not schema:
        logger.error(f"Could not load schema from '{schema_path}'.")
        return None
    return schema


def _validate_tool_data(
    tool_data: Any, schema: Any, ignore_additional_properties: bool, label: str
) -> bool:
    if tool_data is None:
        logger.error(f"Could not load tool from '{label}'.")
        return False

    try:
        if ignore_additional_properties:
            validator_class = jsonschema.validators.extend(
                jsonschema.validators.validator_for(schema),
                {"additionalProperties": lambda validator, aP, instance, schema: None},
            )
            validator = validator_class(schema)
            error = next(validator.iter_errors(tool_data), None)
            if error:
                logger.error(f"✘ Validation error in '{label}':")
                logger.error(f"  - {error.message}")
                logger.error(f"  - Path: {error.json_path}")
                return False
        else:
            jsonschema.validate(instance=tool_data, schema=schema)

        logger.info(f"✅ '{label}' is valid according to the ATDF schema.")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"✘ Validation error in '{label}':")
        logger.error(f"  - {e.message}")
        logger.error(f"  - Path: {e.json_path}")
        return False


def validate_tool(
    tool: ToolSource,
    schema_file: str = None,
    ignore_additional_properties: bool = False,
) -> bool:
    """Validate a tool description against the ATDF schema."""
    if schema_file is None:
        schema_file = os.path.join(
            os.path.dirname(__file__), "../schema/atdf_schema.json"
        )

    schema = _load_schema(schema_file)
    if not schema:
        return False

    tool_data, label = _resolve_tool_source(tool)
    return _validate_tool_data(tool_data, schema, ignore_additional_properties, label)


def validate_tool_smart(
    tool: ToolSource, schema_basic: str = None, schema_enhanced: str = None
) -> bool:
    """Validate a tool description automatically selecting the appropriate schema."""
    if schema_basic is None:
        schema_basic = os.path.join(
            os.path.dirname(__file__), "../schema/atdf_schema.json"
        )

    if schema_enhanced is None:
        schema_enhanced = os.path.join(
            os.path.dirname(__file__), "../schema/enhanced_atdf_schema.json"
        )

    tool_data, label = _resolve_tool_source(tool)
    if tool_data is None:
        logger.error(f"Could not load tool from '{label}'.")
        return False

    schema_version = tool_data.get("schema_version", "1.0.0")
    if schema_version == "1.0.0" and "schema_version" not in tool_data:
        is_enhanced = any(
            key in tool_data
            for key in [
                "metadata",
                "examples",
                "localization",
                "prerequisites",
                "feedback",
            ]
        )
        if is_enhanced:
            schema_version = "2.0.0"

    if schema_version.startswith("2."):
        logger.info(
            f"Detected enhanced schema version {schema_version}, using enhanced validation"
        )
        schema = _load_schema(schema_enhanced)
        return (
            _validate_tool_data(
                tool_data, schema, ignore_additional_properties=False, label=label
            )
            if schema
            else False
        )

    logger.info(
        f"Detected basic schema version {schema_version}, using basic validation"
    )
    schema = _load_schema(schema_basic)
    return (
        _validate_tool_data(
            tool_data, schema, ignore_additional_properties=True, label=label
        )
        if schema
        else False
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate ATDF tool descriptions against a schema."
    )
    parser.add_argument(
        "tool_file", help="Path to the ATDF tool description JSON file to validate"
    )
    parser.add_argument(
        "--schema",
        "-s",
        help="Path to the schema file to validate against (default: auto-detect)",
    )
    parser.add_argument(
        "--smart",
        "-m",
        action="store_true",
        help="Use smart validation to auto-detect schema version",
    )
    parser.add_argument(
        "--ignore-additional",
        "-i",
        action="store_true",
        help="Ignore additional properties",
    )

    args = parser.parse_args()

    target: ToolSource = args.tool_file
    if args.smart:
        success = validate_tool_smart(target)
    else:
        success = validate_tool(target, args.schema, args.ignore_additional)

    sys.exit(0 if success else 1)
