# Índice central: n8n + MCP + ATDF

Este índice agrupa toda la documentación relevante para integrar n8n, el Bridge MCP de ATDF y los workflows verificados (Code v3).

## Enlaces principales
- API REST y Autenticación de n8n: `../n8n_setup_complete.md`
- Workflow Code v3 (n8n): `../n8n-workflows/README.md`
- Guía rápida (ES): `../GUIA_INTEGRACION_N8N.md`
- Guía EN (n8n + MCP + ATDF): `./en/n8n_mcp_server_guide.md`
- Guía ES (n8n + MCP + ATDF): `./es/n8n_mcp_integracion_flujo.md`

## Checklist rápido
- n8n corriendo en `http://localhost:5678`.
- API habilitada y `X-N8N-API-KEY` configurada.
- Bridge MCP activo en `http://localhost:8001`.
- Workflow Code v3 importado y visible desde la UI.

## Verificación
```bash
# UI
curl -s http://localhost:5678 | head -c 200

# API (lista de workflows)
curl -s -H "X-N8N-API-KEY: <API_KEY>" \
  http://localhost:5678/api/v1/workflows | head -c 300

# Bridge MCP
curl -s http://localhost:8001/health
curl -s http://localhost:8001/tools | head -c 300
```

## Notas
- El payload de creación de workflow debe incluir solo: `name`, `nodes`, `connections`, `settings`.
- Evita campos de solo lectura como `active`, `staticData`, etc.
- Puedes importar un archivo específico con `WORKFLOW_FILE` al usar el script de importación.