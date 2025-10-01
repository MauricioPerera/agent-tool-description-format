# n8n + MCP + ATDF Integration Guide

This guide centralizes the essentials to connect n8n with the ATDF MCP Bridge and import tested workflows (Code v3).

## Quick Start
- Launch the MCP Bridge locally:
  ```bash
  python examples/fastapi_mcp_integration.py
  python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
  ```

## REST API & Authentication
- Follow `../../n8n_setup_complete.md` for:
  - Generating an API key and authenticating requests.
  - Importing workflows via REST (including Code v3).
  - Verification commands and troubleshooting.

## Code v3 Workflow
- See `../../n8n-workflows/README.md` for:
  - Purpose and key features of “Complete Travel Booking via ATDF-MCP (Code v3)”.
  - Node structure, MCP Bridge endpoints, and payload schema notes.
  - How to import/execute the workflow via UI and API.

## Verification
- List workflows (example):
  ```bash
  # Replace with your base URL and API key
  curl -H "Authorization: Bearer <N8N_API_KEY>" \
       -H "Content-Type: application/json" \
       <N8N_BASE_URL>/rest/workflows
  ```

## Related
- n8n REST API & Auth: `../../n8n_setup_complete.md`
- Code v3 Workflow (n8n): `../../n8n-workflows/README.md`
- Spanish quick-start: `../../GUIA_INTEGRACION_N8N.md`
- Portuguese MCP guide: `../pt/n8n_mcp_server_guide.md`
 - Central index n8n + MCP + ATDF: `../n8n_mcp_atdf_index.md`
