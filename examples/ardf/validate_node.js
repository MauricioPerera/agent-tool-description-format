#!/usr/bin/env node
// Quick ARDF validation sample using Ajv (JSON Schema draft 2020-12 support required).

const fs = require("fs");
const path = require("path");
const Ajv = require("ajv/dist/2020");

const schema = {
  $schema: "https://json-schema.org/draft/2020-12/schema",
  $id: "https://example.org/ardf.schema.json",
  title: "ARDF Resource",
  type: "object",
  required: ["schema_version", "resource_id", "resource_type", "description"],
  properties: {
    schema_version: { type: "string" },
    resource_id: { type: "string" },
    resource_type: { type: "string" },
    description: { type: "string" },
    content: { type: "object" }
  }
};

function main() {
  const file = process.argv[2];
  if (!file) {
    console.error("Usage: node validate_node.js <path-to-ardf.json>");
    process.exit(1);
  }

  const payload = JSON.parse(fs.readFileSync(path.resolve(file), "utf8"));
  const ajv = new Ajv();
  const validate = ajv.compile(schema);

  if (!validate(payload)) {
    console.error("Validation errors:", validate.errors);
    process.exit(1);
  }

  console.log(`? ${file} is structurally valid (basic ARDF checks).`);
}

main();
