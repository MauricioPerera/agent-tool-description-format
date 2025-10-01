# Guia MCP para n8n (Português)

Este guia centraliza como conectar o n8n ao ATDF MCP Bridge e como importar workflows (Code v3) com autenticação via API REST do n8n.

## Visão geral
- Conectar o n8n a um servidor MCP (ATDF-MCP Bridge).
- Listar e executar ferramentas ATDF via nós MCP ou nós dedicados `n8n-nodes-atdf-mcp`.
- Importar workflows pelo REST do n8n com autenticação adequada.

## Início rápido
```bash
# Iniciar o Bridge MCP com ATDF local
python examples/fastapi_mcp_integration.py
python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000

# Endpoints típicos (SSE)
# http://localhost:8001/sse
```

No n8n:
- Configure nós MCP apontando para `http://localhost:8001/sse`.
- Alternativamente, instale e use `n8n-nodes-atdf-mcp` para metadados completos do ATDF.

## API REST do n8n e autenticação
- Veja `../../n8n_setup_complete.md` para detalhes de tokens, headers e endpoints.
- Suporte a importação/exportação de workflows, execução de nós e gerenciamento de credenciais.

Exemplo de importação de workflow por REST:
```bash
curl -X POST \
  -H "Authorization: Bearer <SEU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d @n8n-workflows/exported/complete_travel_booking.json \
  http://localhost:5678/rest/workflows
```

## Workflows Code v3 (n8n)
- Consulte `../../n8n-workflows/README.md` para um exemplo completo (reserva de viagem) usando MCP Bridge.
- Ajuste credenciais e endpoints antes de importar.

## Verificação
- Liste ferramentas via nó MCP: operação `listTools` com `serverUrl` = `http://localhost:8001/sse`.
- Execute uma ferramenta ATDF com `callTool` informando `toolName` e `arguments` conforme o descritor.
- Verifique logs do bridge e do n8n para respostas enriquecidas do ATDF.

## Conteúdos relacionados
- Índice central n8n + MCP + ATDF: `../n8n_mcp_atdf_index.md`
- API REST e Autenticação do n8n: `../../n8n_setup_complete.md`
- Workflow Code v3 (n8n): `../../n8n-workflows/README.md`
- Fluxo ATDF + MCP + n8n (PT): `n8n_mcp_fluxo_integracao.md`
- Guia rápido (ES): `../../GUIA_INTEGRACION_N8N.md`
- Guia MCP (EN): `../en/n8n_mcp_server_guide.md`
