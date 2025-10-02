import unittest
import json
import os
from tools.validator import validate_tool_smart

class TestExamples(unittest.TestCase):
    def setUp(self):
        self.examples_dir = os.path.join(os.path.dirname(__file__), "../schema/examples")

    def test_all_examples_valid(self):
        if not os.path.exists(self.examples_dir):
            self.fail(f"Examples directory '{self.examples_dir}' does not exist.")

        found_files = False
        for filename in os.listdir(self.examples_dir):
            if filename.endswith(".json"):
                found_files = True
                filepath = os.path.join(self.examples_dir, filename)
                with self.subTest(filename=filename):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        json.load(f)
                    self.assertTrue(
                        validate_tool_smart(filepath),
                        msg=f"Validation failed for '{filename}'"
                    )

        if not found_files:
            self.fail("No JSON files found in the examples directory.")

if __name__ == "__main__":
    unittest.main()
