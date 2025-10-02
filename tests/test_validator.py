import unittest
import json
import os
import tempfile

from tools.validator import load_json, validate_tool, validate_tool_smart


class TestValidator(unittest.TestCase):
    def setUp(self):
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_tool, f)
            temp_path = f.name
        result = load_json(temp_path)
        self.assertEqual(result, self.valid_tool)
        os.unlink(temp_path)

    def test_load_json_file_not_found(self):
        self.assertIsNone(load_json("non_existent.json"))

    def test_load_json_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name
        self.assertIsNone(load_json(temp_path))
        os.unlink(temp_path)

    def test_validate_tool_valid_path(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_tool, f)
            temp_tool_path = f.name
        self.assertTrue(validate_tool(temp_tool_path, self.schema_path))
        os.unlink(temp_tool_path)

    def test_validate_tool_invalid_path(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.invalid_tool, f)
            temp_tool_path = f.name
        self.assertFalse(validate_tool(temp_tool_path, self.schema_path))
        os.unlink(temp_tool_path)

    def test_validate_tool_dict_success(self):
        self.assertTrue(validate_tool(self.valid_tool, self.schema_path))

    def test_validate_tool_dict_failure(self):
        self.assertFalse(validate_tool(self.invalid_tool, self.schema_path))

    def test_validate_tool_smart_enhanced_dict(self):
        enhanced_tool = {
            "tool_id": "enhanced",
            "schema_version": "2.0.0",
            "description": "Enhanced tool",
            "when_to_use": "Use when enhanced",
            "how_to_use": self.valid_tool["how_to_use"],
            "metadata": {"version": "1.0.0"}
        }
        self.assertTrue(validate_tool_smart(enhanced_tool))


if __name__ == "__main__":
    unittest.main()
