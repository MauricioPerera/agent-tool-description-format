# ARDF Manager

ARDF Manager es un panel de control y plataforma de orquestaci�n para el ecosistema Agent Resource Description Format (ARDF) y Model Context Protocol (MCP). Permite a equipos de operaciones y desarrolladores descubrir, curar, puntuar, distribuir y monitorizar recursos (herramientas, prompts, workflows, pol�ticas, modelos) para agentes inteligentes.

## Componentes principales

- **API Service** (pps/api): expone endpoints REST/GraphQL para CRUD de recursos, sincronizaci�n MCP, ranking h�brido y anal�tica.
- **Web Console** (pps/web): interfaz React/Next.js para cat�logos, editor de workflows, dashboards y gesti�n de clientes.
- **Core Package** (packages/core): modelos compartidos, validadores ARDF/ATDF y utilidades de versionado.
- **MCP Client Package** (packages/mcp): envolturas alrededor de @modelcontextprotocol/sdk para sincronizaci�n, generaci�n de manifests y gesti�n multi-servidor.
- **Search Package** (packages/search): conectores de embeddings y motor de ranking h�brido (BM25 + vectores) compatible con OpenAI API u Ollama.

## Roadmap inicial

1. Scaffold de servicios con NestJS/Express y Next.js.
2. Ingesta ARDF v�a MCP SDK + validaci�n JSON Schema.
3. Indexaci�n vectorial con PGVector/Elastic y b�squeda h�brida.
4. Telemetr�a de ejecuci�n y paneles de m�tricas.
5. Generador de manifest/SDK por cliente con personalizaci�n de ranking.

Consulta README.dev.md para pautas de desarrollo y extensiones.
