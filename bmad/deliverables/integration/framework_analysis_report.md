# Framework Analysis – ATDF Selector Workflows

## FastAPI + MCP
- FastAPI server expone `/tools` y `/mcp` mediante examples/fastapi_mcp_integration.py y mcp_atdf_bridge.py.
- Selector HTTP consume MCP `/tools` (`http://localhost:8001/tools`).

## n8n
- Workflow `workflow_selector_builtin.json` encadena HTTP Request -> MCP -> Code node.
- README n8n destaca scripts start/stop y ejecución CLI (`n8n execute --id PNvGdiK9rbvmEnKl`).
