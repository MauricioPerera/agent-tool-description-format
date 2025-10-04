# ARDF Manager

ARDF Manager es un panel de control y plataforma de orquestación para el ecosistema Agent Resource Description Format (ARDF) y Model Context Protocol (MCP). Permite a equipos de operaciones y desarrolladores descubrir, curar, puntuar, distribuir y monitorizar recursos (herramientas, prompts, workflows, políticas, modelos) para agentes inteligentes.

## Componentes principales

- **API Service** (pps/api): expone endpoints REST/GraphQL para CRUD de recursos, sincronización MCP, ranking híbrido y analítica.
- **Web Console** (pps/web): interfaz React/Next.js para catálogos, editor de workflows, dashboards y gestión de clientes.
- **Core Package** (packages/core): modelos compartidos, validadores ARDF/ATDF y utilidades de versionado.
- **MCP Client Package** (packages/mcp): envolturas alrededor de @modelcontextprotocol/sdk para sincronización, generación de manifests y gestión multi-servidor.
- **Search Package** (packages/search): conectores de embeddings y motor de ranking híbrido (BM25 + vectores) compatible con OpenAI API u Ollama.

## Roadmap inicial

1. Scaffold de servicios con NestJS/Express y Next.js.
2. Ingesta ARDF vía MCP SDK + validación JSON Schema.
3. Indexación vectorial con PGVector/Elastic y búsqueda híbrida.
4. Telemetría de ejecución y paneles de métricas.
5. Generador de manifest/SDK por cliente con personalización de ranking.

Consulta README.dev.md para pautas de desarrollo y extensiones.
