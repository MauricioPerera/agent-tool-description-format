# Newcomer Overview

## Quick summary
Agent Tool Description Format (ATDF) is an implementation-agnostic specification that standardizes how AI agents discover and operate external tools. It defines JSON schemas for tool catalogs and enriched error payloads so agents can reason about when and how to call available capabilities.

## Current status
⚠️ This onboarding track is still pending implementation. Treat the outline below as a draft checklist until the program is staffed and the supporting materials are built.

## Repository structure at a glance
- **Schemas (`schema/`)** – Authoritative JSON Schema documents for the classic (1.x) and enhanced (2.x) ATDF descriptors as well as the enriched error envelope.
- **Python tooling (`tools/`, `sdk/`)** – Command line validators, conversion helpers, and a Python SDK (`ATDFTool`, toolbox loaders, multilingual search, auto-selection) that parse descriptors and execute catalog queries programmatically.
- **JavaScript SDK (`js/`)** – Node.js/browser utilities mirroring the Python SDK features, including optional vector search, localization helpers, and MCP→ATDF conversion helpers.
- **Examples (`examples/`)** – FastAPI reference application, scenario demos, and integration tests that demonstrate end-to-end ATDF error handling, booking flows, and Model Context Protocol (MCP) wiring.
- **Documentation (`docs/`)** – Specification, implementation guides, integration walkthroughs (FastAPI, n8n, monitoring), and multilingual content kept in sync across English/Spanish/Portuguese.
- **Automation & workflows (`n8n-*`, `monitoring/`, `scripts/`)** – Ready-to-import n8n workflows, monitoring dashboards, and helper scripts for spinning up demo environments.

## Concepts to learn first
1. **Tool descriptors** – Understand required vs. optional fields in classic vs. enhanced ATDF schemas, including localization metadata, prerequisites, and worked examples.
2. **Enriched error responses** – Study the shared error envelope (`schema/enriched_response_schema.json`) so your services surface actionable remediation hints for agents.
3. **SDK usage patterns** – Review how the Python/JS SDKs load catalogs, perform text/vector search, and auto-select tools so you avoid re-implementing parsing logic.
4. **FastAPI MCP bridge** – Treat the sample app in `examples/` as both a reference implementation and an integration testbed when wiring ATDF into new runtimes.

## Working effectively in the repo
- Validate descriptors early with `tools/validator.py` or `tools/validate_enhanced.py` before distributing them.
- Run both Python and JavaScript test suites (`python tests/run_all_tests.py`, `npm test` inside `js/`) to catch regressions across SDKs.
- Use the FastAPI + n8n workflows as system tests when adjusting server logic or MCP integrations.
- Keep documentation localized: whenever you change guides in `docs/en`, mirror the updates in `docs/es` and `docs/pt`.

## Next steps for onboarding
1. Read the **Implementation Guide** (`docs/IMPLEMENTATION_GUIDE.md`) for architectural patterns, validation strategy, and deployment considerations.
2. Explore the **SDK examples** under `sdk/` and `js/` to see catalog loading, multilingual metadata handling, and schema extraction in practice.
3. Follow the **n8n + MCP walkthroughs** (`docs/*n8n*`) to understand end-to-end orchestration and error handling in automation workflows.
4. Review the **monitoring playbooks** (`monitoring/`) to learn how production deployments track ATDF error metrics and operational health.
