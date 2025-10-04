#!/usr/bin/env node
// ARDF validation snippet using Ajv (JSON Schema draft 2020-12).

const fs = require("fs");
const path = require("path");
const Ajv2020 = require("ajv/dist/2020");
const addFormats = require("ajv-formats");

const schemaPath = path.resolve(__dirname, "..", "..", "schema", "ardf.schema.json");
const samplePath = process.argv[2] || path.resolve(__dirname, "tool_appointment_create.json");

const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
const data = JSON.parse(fs.readFileSync(samplePath, "utf8"));

const ajv = new Ajv2020({ allErrors: true });
addFormats(ajv);

const validate = ajv.compile(schema);
const valid = validate(data);

if (valid) {
  console.log(`? ${samplePath} is a valid ARDF descriptor.`);
} else {
  console.error("? Validation errors:");
  console.error(validate.errors);
  process.exitCode = 1;
}
