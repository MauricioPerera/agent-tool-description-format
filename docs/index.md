# Agent Tool Description Format (ATDF)

<div align="center">
  <h2>Describe once, reuse everywhere</h2>
  <p>ATDF is the open protocol that lets agents, APIs, and workflows discover tools through a single, declarative contract.</p>
  <p>
    <a href="en/index.md">English</a> ·
    <a href="es/index.md">Español</a> ·
    <a href="pt/index.md">Português</a>
  </p>
</div>

---

## 🚀 Quick launch
1. **Pick your schema**
   - Basic 1.x → [`schema/atdf_schema.json`](../schema/atdf_schema.json)
   - Enhanced 2.x → [`schema/enhanced_atdf_schema.json`](../schema/enhanced_atdf_schema.json)
2. **Draft a descriptor**
```json
{
  "schema_version": "2.0.0",
  "tool_id": "date_validator",
  "description": "Validates date ranges with enriched error responses",
  "when_to_use": "Use when you need a full explanation of invalid date ranges",
  "how_to_use": {
    "inputs": [
      {"name": "start_date", "type": "string", "description": "Start date in ISO 8601 format", "required": true},
      {"name": "end_date", "type": "string", "description": "End date in ISO 8601 format", "required": true}
    ],
    "outputs": {
      "success": "Date range is valid",
      "failure": [
        {"code": "INVALID_DATE_RANGE", "description": "Start date must be before end date"}
      ]
    }
  }
}
```
3. **Validate and iterate**
```bash
python tools/validator.py examples/date_validator.json --schema schema/atdf_schema.json
python tools/validate_enhanced.py examples/date_validator.json
```
4. **Wire it up** – plug the descriptor into the [FastAPI ↔ MCP bridge](../examples/mcp_atdf_bridge.py) or the [n8n integration](en/n8n_mcp_integration_flow.md).

---

## 📚 Essential guides
| Topic | Description |
| --- | --- |
| [ATDF Specification](ATDF_SPECIFICATION.md) | Canonical reference for both basic and enhanced schemas. |
| [Implementation Guide](IMPLEMENTATION_GUIDE.md) | Step-by-step instructions to publish descriptors and enrich error payloads. |
| [Best Practices](BEST_PRACTICES.md) | Patterns for security, validation, localization, and feedback loops. |
| [Examples Library](examples.md) | Real descriptors, bridges, and SDK snippets ready to run. |
| [Version Compatibility](en/version_compatibility.md) | How legacy v0.1/v0.2 map to the current 1.x/2.x schemas. |
| [ATDF + MCP + n8n Flow](atdf_mcp_n8n_integration_flow.md) | Architecture and language-specific guides for workflow automation. |

---

## 🔌 Featured integrations
<div class="cards">
  <div class="card">
    <h3>n8n + MCP + ATDF</h3>
    <p>Run ATDF tools from native MCP nodes or custom ATDF nodes inside n8n workflows.</p>
    <p><a href="en/n8n_mcp_integration_flow.md">English guide →</a></p>
  </div>
  <div class="card">
    <h3>BMAD-METHOD</h3>
    <p>Automate multi-agent development with BMAD orchestrators, ATDF specialists, and QA agents.</p>
    <p><a href="BMAD_INTEGRATION.md">Integration playbook →</a></p>
  </div>
  <div class="card">
    <h3>Monitoring & Telemetry</h3>
    <p>Capture metrics, alerts, and dashboards for ATDF-powered services.</p>
    <p><a href="monitoring.md">Monitoring guide →</a></p>
  </div>
</div>

> 💡 Need localized quick-starts? Visit the language hubs above to get the same playbook in Spanish and Portuguese.

---

## 🧭 More to explore
- [Multilingual strategy](multilingual.md)
- [Workflow automation ideas](workflow.md)
- [Enhancement proposals](enhancement_proposal.md)
- [Mermaid diagrams](MERMAID_DIAGRAMS.md)
- [Changelog](changelog.md)

### Contribute
Pull requests are welcome! Review the [contributing checklist](en/contributing.md) and validate descriptors + tests before opening a PR.

<div align="center">
  <a href="../README.md">Back to repository README</a>
</div>
