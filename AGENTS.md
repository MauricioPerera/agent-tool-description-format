# Agent Tool Description Format (ATDF)

## Overview
Agent Tool Description Format (ATDF) is an open protocol that standardizes how AI agents discover, describe, and operate external tools. It focuses on declarative interoperability: agents rely on rich tool metadata rather than hard-coded integrations to determine usage context, required inputs, and expected outcomes. ATDF also defines a complementary error-response envelope so agents can reason about failures and suggest corrective actions.

## Core Capabilities
- Tool discovery via JSON descriptors that define identity, usage context, and IO contracts.
- Enhanced descriptors with localization, metadata, prerequisites, and worked examples.
- Standardized error payloads carrying machine-actionable hints (type, detail, suggested_value, contextual objects).

## Schemas
- schema/atdf_schema.json: canonical schema (v1.x) requiring tool_id/id, description, when_to_use, and how_to_use.inputs/outputs.
- schema/enhanced_atdf_schema.json: extended schema (v2.x) with metadata, localization, prerequisites, examples, feedback.
- schema/enriched_response_schema.json: shared structure for tool error responses and remediation suggestions.

## Tool Structure
Example descriptor:
    {
      "tool_id": "string",
      "description": "clear, user-facing summary",
      "when_to_use": "when the agent should call the tool",
      "how_to_use": {
        "inputs": [{ "name": "...", "type": "...", "description": "..." }],
        "outputs": {
          "success": "success semantics",
          "failure": [{ "code": "...", "description": "..." }]
        }
      }
    }

Enhanced documents add optional fields such as metadata.version, metadata.tags, localization["es"].description, prerequisites.tools, examples[], and feedback.

## Validation & Tooling
- python tools/validator.py <file> --schema schema/atdf_schema.json
- python tools/validate_enhanced.py <file> auto-selects the enhanced schema.
- Converters and loaders in tools/ cover MCP to ATDF translation and enriched payload handling.
- Python SDK (sdk/) and JS SDK (js/) expose classes (ATDFTool, ATDFToolbox) plus vector-search helpers for semantic tool selection.

## Usage Patterns
1. Draft tool metadata (JSON or YAML) describing capabilities for agent consumption.
2. Validate against the appropriate schema.
3. Distribute the descriptor alongside the implementation endpoint.
4. Optionally emit enriched error responses conforming to enriched_response_schema.json.
5. Integrate via SDKs or load dynamically inside agent platforms.

## Testing & Quality
- Run python tests/run_all_tests.py for SDK, schema, multilingual, and enhanced-feature coverage.
- JavaScript SDK tests live under js/tests (npm test).
- Examples in examples/ demonstrate FastAPI hosting, MCP conversion, vector search, and real-world integrations.

## Governance
- Conventional Commits and Pull Request workflow.
- Multi-language docs under docs/ (EN, ES, PT) must stay in sync.
- Agents contributing should follow AGENTS.md guidelines for workflows, validation, and style.
