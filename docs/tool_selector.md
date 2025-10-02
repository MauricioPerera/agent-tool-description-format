# ATDF Tool Selector (Work in Progress)

This document tracks the implementation of the ATDF-aware tool selector,
note-worthy for providing catalog aggregation, persistence, and ranking of tool
descriptors exposed in ATDF/MCP environments.

## Overview

The selector centralises discovery, persistence, and ranking of ATDF tool
descriptors. It can load descriptors from local JSON/YAML files or from an MCP
bridge, stores metadata in SQLite (with optional vector backends later), and
exposes a FastAPI service for downstream agents or orchestration platforms such
as n8n.

## Current Components

| Module | Description |
|--------|-------------|
| `selector.catalog` | Catalogs ATDF descriptors, validates them against v1/v2 schemas, normalises metadata (languages, tags, usage hints), and syncs with storage. |
| `selector.storage` | SQLite persistence for MCP servers and tools (`servers`, `tools` tables) tracking cache timestamps and active tool versions. |
| `selector.ranker`  | Heuristic ranker that scores tools using query tokens, descriptions, tags, and language preference (filters by server/tool allow-lists). |
| `selector.cli`     | Command-line utility to load descriptors and inspect the catalog (`python -m selector.cli --storage selector.db --dir schema/examples`). |
| `selector.api`     | FastAPI application exposing `/recommend`, `/catalog`, `/servers`, `/catalog/reload`, and `/health` endpoints. |

## Quick Start

- **n8n Integration**: Usa el nodo *ATDF Tool Selector* para obtener recomendaciones del selector y pasar la lista filtrada al nodo MCP Client o al nodo ATDF MCP Client.

```bash
# Build the catalog and persist it in SQLite
env PYTHONPATH=. python -m selector.cli \
  --storage data/selector.db \
  --dir schema/examples \
  --mcp http://localhost:8001/tools

# Start the selector API (uses ATDF_SELECTOR_DB if provided)
env PYTHONPATH=. ATDF_SELECTOR_DB=data/selector.db \
  uvicorn selector.api:app --reload --port 8050

# Request recommendations filtered by server URL
curl -X POST http://127.0.0.1:8050/recommend \
  -H "Content-Type: application/json" \
  -d '{
        "query": "Necesito reservar un hotel en Madrid",
        "language": "es",
        "servers": ["http://localhost:8001/tools"],
        "allowed_tools": ["hotel_reservation", "flight_booking"]
      }'
```

Environment variables:

- `ATDF_CATALOG_DIR`: path(s) to directories with descriptors (use `os.pathsep`
  to separate multiple entries).
- `ATDF_MCP_TOOLS_URL`: optional MCP `/tools` endpoint ingested at startup.
- `ATDF_SELECTOR_DB`: SQLite database path used by the API (enables persistence
  and multi-process sharing).

## Persistence Model

- **servers**: stores MCP endpoints or local sources (`url`, `name`,
  `cache_timestamp`, `last_sync`).
- **tools**: stores descriptors per server (`tool_id`, `version_hash`,
  serialized descriptor, languages, tags, `active` flag).
- Synchronisation marks missing tools as inactive, allowing safe rollbacks and
  change detection when a tool is removed upstream.

## Feedback API

Use POST /feedback para registrar el resultado de una ejecución y ajustar el ranking:

``ash
curl -X POST http://127.0.0.1:8050/feedback \
  -H "Content-Type: application/json" \
  -d '{\n    "tool_id": "hotel_reservation",\n    "server": "http://localhost:8001/tools",\n    "outcome": "success"\n  }'
```

El selector acumula éxitos y errores por herramienta/origen y aplica un ajuste
(+0.5 por éxito, -0.75 por error, hasta tres eventos) al calcular nuevas recomendaciones.



## Known Gaps / Next Steps

1. **Semantic ranking** – plug sentence embeddings (e.g. `sentence-transformers`)
   and LanceDB/pgvector for similarity search beyond keyword heuristics.
2. **Observability** – expose Prometheus metrics (queries served, latency,
   precision) and integrate with the existing monitoring stack.
3. **Integration tests** – add end-to-end tests that hit /recommend while the
   MCP bridge serves live data and validate n8n node integration.
4. **Admin tooling** – add CLI/API commands to remove servers, inspect inactive
   tools, and trigger selective re-syncs.
4. **Admin tooling** – add CLI/API commands to remove servers, inspect inactive
   tools, and trigger selective re-syncs.

---
_Last updated: 2025-10-01_
