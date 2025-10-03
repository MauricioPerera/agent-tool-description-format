> **Selector Client enlaces rápidos:** [Guía de uso](../tool_selector.md#client-usage) | [README de workflows](../n8n-workflows/README.md#selector-client-quick-reference)

Esta guía reúne lo esencial para conectar n8n con el Bridge MCP de ATDF e importar workflows verificados (Code v3).

## Inicio rápido
- Inicia el Bridge MCP local:
  ```bash
  python examples/fastapi_mcp_integration.py
  python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
  ```

## API REST y Autenticación
- Sigue `../../n8n_setup_complete.md` para:
  - Generar API key y autenticar peticiones.
  - Importar workflows por REST (incluido Code v3).
  - Comandos de verificación y solución de problemas.

## Workflow Code v3
- Consulta `../../n8n-workflows/README.md` para:
  - Propósito y funciones clave de “Complete Travel Booking via ATDF-MCP (Code v3)”.
  - Estructura de nodos, endpoints del MCP Bridge y notas de payload.
  - Cómo importar/ejecutar el flujo desde la UI y por API.

## Verificación
- Listar workflows (ejemplo):
  ```bash
  # Sustituye por tu base URL y API key
  curl -H "Authorization: Bearer <N8N_API_KEY>" \
       -H "Content-Type: application/json" \
       <N8N_BASE_URL>/rest/workflows
  ```

## Relacionados
- API y autenticación de n8n: `../../n8n_setup_complete.md`
- Workflow Code v3 (n8n): `../../n8n-workflows/README.md`
- Guía rápida (ES): `../../GUIA_INTEGRACION_N8N.md`
- Guía MCP (PT): `../pt/n8n_mcp_server_guide.md`
 - Índice central n8n + MCP + ATDF: `../n8n_mcp_atdf_index.md`

