import unittest
import json
import os
import tempfile
from jsonschema.exceptions import ValidationError
from tools.validator import load_json, validate_tool

class TestValidator(unittest.TestCase):
    def setUp(self):
        """Set up paths and sample data for testing."""
        self.schema_path = os.path.join(os.path.dirname(__file__), "../schema/atdf_schema.json")
        self.valid_tool = {
            "tool_id": "test_tool_v1",
            "description": "Test tool for validation",
            "when_to_use": "Use for testing purposes",
            "how_to_use": {
                "inputs": [
                    {"name": "test_input", "type": "string", "description": "Test input"}
                ],
                "outputs": {
                    "success": "Test completed successfully",
                    "failure": [
                        {"code": "test_error", "description": "Test error occurred"}
                    ]
                }
            }
        }
        self.invalid_tool = {
            "tool_id": "test_tool_v1",
            "description": "Test tool for validation",
            # Missing required field: when_to_use
            "how_to_use": {
                "inputs": [],
                "outputs": {
                    "success": "Test completed successfully",
                    "failure": []
                }
            }
        }

    def test_load_json_valid(self):
        """Test loading a valid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_tool, f)
            temp_path = f.name
        result = load_json(temp_path)
        self.assertEqual(result, self.valid_tool)
        os.unlink(temp_path)

    def test_load_json_file_not_found(self):
        """Test loading a non-existent file."""
        with self.assertRaises(SystemExit):
            load_json("non_existent.json")

    def test_load_json_invalid_json(self):
        """Test loading an invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name
        with self.assertRaises(SystemExit):
            load_json(temp_path)
        os.unlink(temp_path)

    def test_validate_tool_valid(self):
        """Test validating a valid tool description."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_tool, f)
            temp_tool_path = f.name
        # Should not raise an exception
        validate_tool(temp_tool_path, self.schema_path)
        os.unlink(temp_tool_path)

    def test_validate_tool_invalid(self):
        """Test validating an invalid tool description."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.invalid_tool, f)
            temp_tool_path = f.name
        with self.assertRaises(SystemExit):
            validate_tool(temp_tool_path, self.schema_path)
        os.unlink(temp_tool_path)

if __name__ == "__main__":
    unittest.main()
