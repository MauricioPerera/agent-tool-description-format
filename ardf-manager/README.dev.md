# ARDF Manager � Developer Notes

Esta gu�a resume decisiones arquitect�nicas, dependencias clave y pr�ximas tareas para el ARDF Manager.

## Paquetes

- pps/api: Servicio Node/NestJS (Express en MVP) con endpoints REST + WebSockets.
- pps/web: Consola Next.js (App Router) con UI para cat�logo y anal�tica.
- packages/core: Tipos TypeScript compartidos, validadores JSON Schema, l�gica de versionado y normalizaci�n.
- packages/mcp: Adaptadores sobre @modelcontextprotocol/sdk (descubrimiento, sync, generaci�n de manifests, clientes preconfigurados).
- packages/search: Motor h�brido (BM25 + vectores) con conectores a OpenAI API u Ollama.

## Dependencias sugeridas

| Dominio | Librer�as | Notas |
| ------ | --------- | ----- |
| API | NestJS / Express, Zod o AJV, Prisma/TypeORM | Validaci�n fuerte y DX productiva |
| Web | Next.js, TanStack Query, Chakra/Tailwind, Recharts | Data fetching y dashboards |
| Vector | pgvector, langchain, @pinecone-database/pinecone (opcional) | Encapsular en packages/search |
| Anal�tica | ClickHouse/TimescaleDB, Apache Superset (opcional) | M�tricas y visualizaci�n |
| Streaming | Kafka/NATS, BullMQ | Ingesta de eventos y jobs |

## Pr�ximos pasos (MVP)

1. **Bootstrap API**: Express + TypeScript, endpoints /api/catalog, /api/mcp/sync, /api/search (stub).
2. **Integrar MCP SDK**: establecer servicio en packages/mcp con m�todos listResources, syncEndpoint, uildManifest.
3. **Dise�ar modelos**: esquema Postgres inicial (esources, endpoints, executions, clients, manifests).
4. **Vector search stub**: wrapper en packages/search con interfaz EmbeddingProvider y HybridRanker (mock en memoria inicialmente).
5. **Web skeleton**: layout Next.js, p�ginas /resources, /workflows, /analytics, /clients con datos mock.
6. **Configurar lint/test**: ESLint, Prettier, Vitest/Jest en monorepo.

## Buenas pr�cticas

- Mantener Schemas ARDF (1.x/2.x) en packages/core/schema con validaci�n mediante AJV/Zod.
- Versionar recursos mediante semantic_version y guardar historiales esource_revisions.
- Guardar embeddings con metadatos (model, dimensions, created_at) para reindexaci�n.
- Implementar capa de autorizaci�n (RBAC) desde el inicio (por ejemplo, Keycloak/Auth0).

## Ideas futuras

- **Policy Guard Rails**: inspeccionar policy/rules y asegurar cumplimiento antes de ejecutar herramientas.
- **Feedback Learning**: actualizar puntuaciones seg�n outcomes (bandit/reciprocal rank fusion).
- **A/B Ranking Experiments**: comparar estrategias de ranking y capturar m�tricas autom�ticas.
- **MCP Federation**: cach� multi-tenant + scheduler de sincronizaci�n con diff y alertas.

Documentar cualquier decisi�n adicional en esta gu�a para mantener alineado al equipo.
