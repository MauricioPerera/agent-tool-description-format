import unittest
import json
import os
import jsonschema

class TestExamples(unittest.TestCase):
    def setUp(self):
        """Set up paths and load schema for testing."""
        self.schema_path = os.path.join(os.path.dirname(__file__), "../schema/atdf_schema.json")
        self.examples_dir = os.path.join(os.path.dirname(__file__), "../schema/examples")
        
        # Load schema
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

    def test_all_examples_valid(self):
        """Test that all JSON files in the examples directory are valid according to the schema."""
        if not os.path.exists(self.examples_dir):
            self.fail(f"Examples directory '{self.examples_dir}' does not exist.")

        found_files = False
        for filename in os.listdir(self.examples_dir):
            if filename.endswith(".json"):
                found_files = True
                filepath = os.path.join(self.examples_dir, filename)
                with self.subTest(filename=filename):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tool = json.load(f)
                    try:
                        jsonschema.validate(instance=tool, schema=self.schema)
                    except jsonschema.exceptions.ValidationError as e:
                        self.fail(f"Validation failed for '{filename}': {e.message} at {e.json_path}")
                    except json.JSONDecodeError as e:
                        self.fail(f"Invalid JSON in '{filename}': {e}")

        if not found_files:
            self.fail("No JSON files found in the examples directory.")

if __name__ == "__main__":
    unittest.main()
