# ARDF Manager — Developer Notes

Esta guía resume decisiones arquitectónicas, dependencias clave y próximas tareas para el ARDF Manager.

## Paquetes

- pps/api: Servicio Node/NestJS (Express en MVP) con endpoints REST + WebSockets.
- pps/web: Consola Next.js (App Router) con UI para catálogo y analítica.
- packages/core: Tipos TypeScript compartidos, validadores JSON Schema, lógica de versionado y normalización.
- packages/mcp: Adaptadores sobre @modelcontextprotocol/sdk (descubrimiento, sync, generación de manifests, clientes preconfigurados).
- packages/search: Motor híbrido (BM25 + vectores) con conectores a OpenAI API u Ollama.

## Dependencias sugeridas

| Dominio | Librerías | Notas |
| ------ | --------- | ----- |
| API | NestJS / Express, Zod o AJV, Prisma/TypeORM | Validación fuerte y DX productiva |
| Web | Next.js, TanStack Query, Chakra/Tailwind, Recharts | Data fetching y dashboards |
| Vector | pgvector, langchain, @pinecone-database/pinecone (opcional) | Encapsular en packages/search |
| Analítica | ClickHouse/TimescaleDB, Apache Superset (opcional) | Métricas y visualización |
| Streaming | Kafka/NATS, BullMQ | Ingesta de eventos y jobs |

## Próximos pasos (MVP)

1. **Bootstrap API**: Express + TypeScript, endpoints /api/catalog, /api/mcp/sync, /api/search (stub).
2. **Integrar MCP SDK**: establecer servicio en packages/mcp con métodos listResources, syncEndpoint, uildManifest.
3. **Diseñar modelos**: esquema Postgres inicial (esources, endpoints, executions, clients, manifests).
4. **Vector search stub**: wrapper en packages/search con interfaz EmbeddingProvider y HybridRanker (mock en memoria inicialmente).
5. **Web skeleton**: layout Next.js, páginas /resources, /workflows, /analytics, /clients con datos mock.
6. **Configurar lint/test**: ESLint, Prettier, Vitest/Jest en monorepo.

## Buenas prácticas

- Mantener Schemas ARDF (1.x/2.x) en packages/core/schema con validación mediante AJV/Zod.
- Versionar recursos mediante semantic_version y guardar historiales esource_revisions.
- Guardar embeddings con metadatos (model, dimensions, created_at) para reindexación.
- Implementar capa de autorización (RBAC) desde el inicio (por ejemplo, Keycloak/Auth0).

## Ideas futuras

- **Policy Guard Rails**: inspeccionar policy/rules y asegurar cumplimiento antes de ejecutar herramientas.
- **Feedback Learning**: actualizar puntuaciones según outcomes (bandit/reciprocal rank fusion).
- **A/B Ranking Experiments**: comparar estrategias de ranking y capturar métricas automáticas.
- **MCP Federation**: caché multi-tenant + scheduler de sincronización con diff y alertas.

Documentar cualquier decisión adicional en esta guía para mantener alineado al equipo.
