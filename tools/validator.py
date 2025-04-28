import json
import jsonschema
import sys
import os

def load_json(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{file_path}': {e}")
        sys.exit(1)

def validate_tool(tool_file, schema_file):
    """Validate a tool description against the ATDF schema."""
    # Load schema and tool description
    schema = load_json(schema_file)
    tool = load_json(tool_file)

    # Validate
    try:
        jsonschema.validate(instance=tool, schema=schema)
        print(f"✅ '{tool_file}' is valid according to the ATDF schema.")
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ Validation error in '{tool_file}':")
        print(f"  - {e.message}")
        print(f"  - Path: {e.json_path}")
        sys.exit(1)

if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python validator.py <path_to_tool_json>")
        print("Example: python validator.py ../schema/examples/hole_maker.json")
        sys.exit(1)

    # Paths
    tool_file = sys.argv[1]
    schema_file = os.path.join(os.path.dirname(__file__), "../schema/atdf_schema.json")

    # Validate
    validate_tool(tool_file, schema_file)
