# Agent Tool Description Format (ATDF)

## Overview
Agent Tool Description Format (ATDF) is an open protocol that standardizes how AI agents discover, describe, and operate external tools. It focuses on declarative interoperability: agents rely on rich tool metadata rather than hard-coded integrations to determine usage context, required inputs, and expected outcomes. ATDF also defines a complementary error-response envelope so agents can reason about failures and suggest corrective actions.

## Core Capabilities
- Tool discovery via JSON descriptors that define identity, usage context, and IO contracts.
- Enhanced descriptors with localization, metadata, prerequisites, and worked examples.
- Standardized error payloads carrying machine-actionable hints (`type`, `detail`, `suggested_value`, contextual objects).

## Schemas
- `schema/atdf_schema.json`: canonical schema (1.x, legacy v0.1) with `tool_id`/`id`, `description`, `when_to_use`, `how_to_use.inputs/outputs`.
- `schema/enhanced_atdf_schema.json`: extended schema (2.x, legacy v0.2) with metadata, localization, prerequisites, examples, feedback.
- `schema/enriched_response_schema.json`: shared structure for tool error responses and remediation suggestions.

## Tool Structure
Example descriptor:
```
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
```
Enhanced documents add optional fields such as `metadata.version`, `metadata.tags`, `localization["es"].description`, `prerequisites.tools`, `examples[]`, and `feedback`.

## Validation & Tooling
- `python tools/validator.py <file> --schema schema/atdf_schema.json`
- `python tools/validate_enhanced.py <file>` auto-selects the enhanced schema.
- Conversion utilities in `tools/` cover MCP ↔ ATDF translation and enriched payload handling.
- Python SDK (`sdk/`) and JS SDK (`js/`) expose `ATDFTool`, toolbox helpers, and optional vector search.
- `examples/mcp_atdf_bridge.py` provides a FastAPI→MCP bridge (CORS-enabled) for external clients.

## Integrations
- **n8n + MCP**: Multilingual guides under `docs/en|es|pt/n8n_mcp_*` explain architecture, native MCP nodes, and custom ATDF nodes (`n8n-nodes-atdf-mcp/`).
- **BMAD-METHOD**: See `docs/BMAD_INTEGRATION.md` and `bmad/` for agents, workflows, and orchestration.
- **Monitoring & Telemetry**: `docs/monitoring.md` covers metrics pipelines; sample dashboards live in `monitoring/`.

## Usage Patterns
1. Draft tool metadata (JSON/YAML) describing capabilities for agent consumption.
2. Validate against the appropriate schema.
3. Distribute the descriptor alongside the implementation endpoint or MCP bridge.
4. Emit enriched error responses conforming to `enriched_response_schema.json`.
5. Integrate via SDKs, the FastAPI bridge, or n8n nodes.

## Testing & Quality
- `python tests/run_all_tests.py` runs SDK, schema, multilingual, and enhanced-feature suites.
- `npm test` inside `js/` covers the JavaScript SDK.
- Sample workflows and bridges live under `examples/`; use them to validate MCP/n8n integrations before deployment.
- CLI smoke tests for MCP↔n8n: with FastAPI and the bridge running, execute `n8n execute --id codex-hotel-cli-test` and `n8n execute --id codex-flight-cli-test` to confirm hotel/flight flows remain healthy.

## Governance
- Use Conventional Commits.
- Keep `docs/en`, `docs/es`, and `docs/pt` in sync.
- Follow the PR checklist in `docs/en/contributing.md` (schema version, validation, tests, translations, BMAD workflows if applicable).
