[Home](index.md) | [Specification](specification.md) | [Examples](examples.md) | [Contributing](contributing.md) | [Multilingual](multilingual.md) | [Changelog](changelog.md) | [License](license.md)

**Languages:** [English (en)](version_compatibility.md) | [Español (es)](../es/version_compatibility.md) | [Português (pt)](../pt/version_compatibility.md)

# ATDF Version Compatibility

This guide summarizes how historical ATDF releases map to the current JSON schemas and feature sets.

## Schema and Feature Matrix

| Schema Version | Legacy Naming | Key Features | Recommended Usage |
| --------------- | ------------- | ------------ | ----------------- |
| 1.x (`schema/atdf_schema.json`) | ATDF v0.1 Basic | Core tool metadata (`tool_id/id`, `description`, `when_to_use`, `how_to_use.inputs/outputs`), lightweight error list | Baseline agents that only need declarative tool invocation |
| 2.x (`schema/enhanced_atdf_schema.json`) | ATDF v0.2 Enhanced | Adds `metadata`, `localization`, `prerequisites`, `examples`, structured `feedback` fields | Rich multi-tenant agents, marketplaces, multilingual assistants |
| Enriched Response Schema (`schema/enriched_response_schema.json`) | ATDF v2.0 Error Envelope | Canonical error payload with `expected`, `solution`, context blocks | Any tool returning actionable troubleshooting guidance |

## Compatibility Notes

- The **2.x enhanced schema** is a superset of the 1.x schema; descriptors that only use basic fields remain valid.
- Enhanced descriptors should set `schema_version` to `2.0.0` (or higher) so validators choose the correct schema automatically.
- Error responses can be adopted independently of the tool schema version as long as they follow `enriched_response_schema.json`.
- Legacy documents authored against ATDF v0.1/v0.2 map directly to the 1.x/2.x schemas above. Update documentation to reference schema paths instead of legacy numbering when possible.

## Migration Checklist

1. Confirm which schema a descriptor targets and declare the `schema_version` field explicitly.
2. Validate with `python tools/validator.py ... --schema schema/atdf_schema.json` for 1.x or `python tools/validate_enhanced.py ...` for 2.x.
3. When migrating to 2.x, populate the new sections incrementally -- start with `metadata.version`, then add localization and prerequisites.
4. Adopt the enriched error schema alongside tool upgrades so agents receive consistent failure details.
