# Agent Resource Description Format (ARDF) & ATDF

## ATDF Overview
Agent Tool Description Format (ATDF) is an open protocol that standardizes how AI agents discover, describe, and operate external tools. It focuses on declarative interoperability: agents rely on rich metadata rather than hard-coded integrations to determine usage context, required inputs, and expected outcomes. ATDF also defines a complementary error-response envelope so agents can reason about failures and suggest corrective actions.

### Core Capabilities
- Tool discovery through JSON descriptors that cover identity, usage context, and IO contracts.
- Enhanced descriptors with localization, metadata, prerequisites, and worked examples.
- Standardized error payloads carrying machine-actionable hints (`type`, `detail`, `suggested_value`, contextual objects).

### Schemas
- `schema/atdf_schema.json`: canonical schema (1.x, legacy v0.1) with `tool_id`/`id`, `description`, `when_to_use`, `how_to_use.inputs/outputs`.
- `schema/enhanced_atdf_schema.json`: extended schema (2.x, legacy v0.2) with metadata, localization, prerequisites, examples, feedback.
- `schema/enriched_response_schema.json`: shared structure for tool error responses and remediation suggestions.

### Tool Structure Example
```json
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
  },
  "metadata": {
    "version": "1.0.0",
    "tags": ["category"]
  },
  "examples": [
    {"name": "basic call", "input": {"foo": "bar"}, "output": {"result": true}}
  ]
}
```

### Validation & Tooling
- `python tools/validator.py <file> --schema schema/atdf_schema.json`
- `python tools/validate_enhanced.py <file>` auto-selects the enhanced schema.
- Conversion utilities in `tools/` cover MCP <-> ATDF translation and enriched payload handling.
- Python SDK (`sdk/`) and JS SDK (`js/`) expose `ATDFTool`, toolbox helpers, and optional vector search.
- `examples/mcp_atdf_bridge.py` provides a FastAPI-MCP bridge (CORS-enabled) for external clients.

### Integrations
- **n8n + MCP**: Multilingual guides under `docs/en|es|pt/n8n_mcp_*` explain architecture, native MCP nodes, and custom ATDF nodes (`n8n-nodes-atdf-mcp/`).
- **Internal automation tooling**: Follow the internal coordination notes for agent workflows and orchestration.
- **Monitoring & telemetry**: `docs/monitoring.md` covers metrics pipelines; sample dashboards live in `monitoring/`.

### Usage Patterns
1. Draft tool metadata (JSON or YAML) describing capabilities for agent consumption.
2. Validate against the appropriate schema.
3. Distribute the descriptor alongside the implementation endpoint or MCP bridge.
4. Emit enriched error responses conforming to `schema/enriched_response_schema.json`.
5. Integrate via SDKs, the FastAPI bridge, or n8n nodes.

## From ATDF to ARDF
ATDF solved the problem of expressing callable tools. Modern agent ecosystems also need to describe prompts, workflows, documents, datasets, models, and policies. The Agent Resource Description Format (ARDF) generalizes ATDF into a resource-centric grammar so any capability can be published, discovered, and orchestrated inside Model Context Protocol (MCP) environments.

### Why ARDF
- **Broader coverage**: Agents frequently consume knowledge bases, guardrails, prompts, and ML models in addition to tools.
- **Unified discovery**: MCP servers expose multiple resource collections (`/tools`, `/prompts`, `/documents`, `/policies`, etc.). ARDF provides one descriptor dialect for all of them.
- **Composability**: Workflows can reference other resources (tools, prompts, policies) declaratively, enabling orchestration without bespoke code.
- **Governance**: Shared metadata, localization, prerequisites, feedback, and maturity signals apply across resource types.

### ARDF Resource Types
| Resource type | Purpose | Typical `how_to_use` block |
| ------------- | ------- | -------------------------- |
| `tool` | Executable function, API, or agent skill | `invocation` (inputs, outputs, endpoint, method) |
| `prompt` | Strategy or instruction set for orchestration | `content` or `composition` describing guidance |
| `document` | Knowledge base, SOP, or reference material | `access` (mode, format, endpoint) |
| `workflow` | Sequenced or conditional orchestration | `composition` (steps, control flow, prerequisites) |
| `policy` | Guardrails, compliance rules, constraints | `guardrails` (rules, enforcement, applies_to) |
| `model` | ML or cognitive capability | `invocation` with model-specific metadata |
| `dataset` | Structured data resource | `access` with selectors or schemas |
| `connector` | Bridge to external systems | `invocation` or `access` depending on semantics |
| `custom` | Extension point for domain-specific resource types | Any combination of the above |

### ARDF Descriptor Outline
```json
{
  "schema_version": "1.0.0",
  "resource_id": "appointment_coordinator",
  "resource_type": "prompt",
  "description": "Guide the agent through medical appointment coordination.",
  "when_to_use": "Whenever a user asks to book, reschedule, or cancel an appointment.",
  "how_to_use": {
    "composition": {
      "control_flow": "conditional",
      "steps": [
        {"order": 1, "resource_ref": "patient_privacy_policy"},
        {"order": 2, "resource_ref": "patient_lookup", "notes": "Ensure consent."},
        {"order": 3, "resource_ref": "appointment_create"}
      ]
    }
  },
  "metadata": {
    "version": "1.0.0",
    "author": "HealthAI Team",
    "tags": ["coordination", "healthcare"],
    "maturity": "beta"
  },
  "examples": [
    {
      "name": "Book visit",
      "input": "Book a medical appointment for next Monday",
      "output": "Appointment confirmed"
    }
  ],
  "prerequisites": {
    "policies": ["patient_privacy_policy"],
    "resources": ["appointment_create", "patient_lookup"]
  }
}
```

### ARDF Schema Highlights (draft v1.0.0)
- Extends ATDF by replacing `tool_id` with `resource_id` and introducing `resource_type`.
- `how_to_use` becomes a container for contextual blocks: `invocation`, `access`, `composition`, `guardrails`.
- Keeps cross-cutting structures (`metadata`, `localization`, `examples`, `prerequisites`, `feedback`).
- Enforces resource-specific requirements (for example, `tool` must supply `how_to_use.invocation`, `document` must provide `how_to_use.access`).
- Supports MCP discovery across `/tools`, `/prompts`, `/docs`, `/workflows`, `/policies`, `/models`, and future endpoints.

### Example Resource Catalog (ARDF)
| ID | Type | Summary |
| -- | ---- | ------- |
| `flight_booking` | tool | Reserve flights with fare validation. |
| `medical_guidelines` | document | Official clinical protocols (read-only). |
| `appointment_coordinator` | prompt | Guides tool usage for scheduling. |
| `patient_privacy_policy` | policy | Hard guardrails for PHI handling. |
| `symptom_classifier` | model | ML endpoint returning triage categories. |
| `emergency_intake` | workflow | Conditional sequence for emergency admissions. |

### MCP Integration Pattern
- MCP manifest can advertise multiple resource collections:
  ```json
  {
    "resources": [
      {"type": "tool", "path": "/tools"},
      {"type": "prompt", "path": "/prompts"},
      {"type": "document", "path": "/documents"},
      {"type": "policy", "path": "/policies"},
      {"type": "workflow", "path": "/workflows"}
    ]
  }
  ```
- Agents query the catalog, filter by `resource_type`, inspect ARDF descriptors, and decide how to execute, consult, or enforce each resource.
- Feedback loops (`feedback.success_rate`, `feedback.notes`) help selectors and rankers adapt recommendations.

### Migration Considerations (ATDF -> ARDF)
- Rename `tool_id` to `resource_id` and set `resource_type` to `tool` for existing descriptors.
- Preserve `how_to_use` payloads; the ARDF schema still accepts `inputs`, `outputs`, and endpoints under `how_to_use.invocation`.
- Promote enhanced descriptors (metadata, localization, examples, feedback) without modification.
- Update validators (`tools/validator.py`) and CLI commands (`atdf validate`) to detect ATDF vs ARDF automatically.
- Expand selectors (`selector/`) to rank by `resource_type`, supporting workflows, documents, and policies alongside tools.

## Testing & Quality
- `python tests/run_all_tests.py` runs SDK, schema, multilingual, and enhanced-feature suites.
- `npm test` inside `js/` covers the JavaScript SDK.
- Sample workflows and bridges live under `examples/`; use them to validate MCP and n8n integrations before deployment.
- CLI smoke tests for MCP and n8n: with FastAPI and the bridge running, execute `n8n execute --id codex-hotel-cli-test` and `n8n execute --id codex-flight-cli-test` to confirm hotel and flight flows remain healthy.

## Governance
- Use Conventional Commits.
- Keep `docs/en`, `docs/es`, and `docs/pt` in sync.
- Follow the PR checklist in `docs/en/contributing.md` (schema version, validation, tests, translations, internal workflows when applicable).

## Next Steps Toward ARDF Adoption
1. Publish `schema/ardf_resource_schema.json` alongside the existing ATDF schemas.
2. Extend validators, converters, and CLI ergonomics to support dual ATDF/ARDF descriptors.
3. Update documentation (`docs/ATDF_SPECIFICATION.md`, `docs/examples.md`, multilingual copies) with ARDF guidance and samples.
4. Enhance selectors and SDKs so ranking, search, and vector enrichment operate across mixed resource catalogs.
5. Pilot ARDF descriptors in MCP and n8n workflows to validate interoperability across tools, prompts, documents, and policies.
