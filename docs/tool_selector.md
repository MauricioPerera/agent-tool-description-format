# ATDF Tool Selector

This document tracks the implementation of the ATDF-aware tool selector, note-worthy for providing catalog aggregation, persistence, and ranking of tool descriptors exposed in ATDF/MCP environments.

## Overview

The selector centralises discovery, persistence, and ranking of ATDF tool descriptors. It can load descriptors from local JSON/YAML files or from an MCP bridge, stores metadata in SQLite (with optional vector backends later), and exposes a FastAPI service for downstream agents or orchestration platforms such as n8n.

## Current Components

| Module | Description |
|--------|-------------|
| `selector.catalog` | Catalogs ATDF descriptors, validates them against v1/v2 schemas, normalises metadata (languages, tags, usage hints), and syncs with storage. Recent updates parse MCP descriptions (`When to use`), hydrate `how_to_use.inputs`, and apply default success messages. |
| `selector.storage` | SQLite persistence for MCP servers and tools (`servers`, `tools` tables) tracking cache timestamps and active tool versions. |
| `selector.ranker`  | Heuristic ranker that scores tools using query tokens, descriptions, tags, language preference, and (optionally) feedback adjustments. |
| `selector.cli`     | Command-line utility to load descriptors and inspect the catalog (`python -m selector.cli --storage selector.db --dir schema/examples`). |
| `selector.api`     | FastAPI application exposing `/recommend`, `/catalog`, `/servers`, `/catalog/reload`, `/feedback`, and `/health` endpoints. |

## Quick Start

### Boot via project scripts

The helper scripts start all three Python services (ATDF server, MCP bridge, selector) with the appropriate environment variables:

```bash
# Linux / macOS
./scripts/start_all_services.sh

# Windows
scripts\start_all_services.bat
```

Each script exports `PYTHONPATH`, `ATDF_MCP_TOOLS_URL=http://localhost:8001/tools` and `ATDF_SELECTOR_DB=selector_workflow.db` before launching `uvicorn selector.api:app` on port 8050.

### Manual setup

```bash
# Build the catalog and persist it in SQLite
env PYTHONPATH=. python -m selector.cli \
  --storage data/selector.db \
  --dir schema/examples \
  --mcp http://localhost:8001/tools

# Start the selector API (uses ATDF_SELECTOR_DB if provided)
env PYTHONPATH=. ATDF_SELECTOR_DB=data/selector.db \
  python -m uvicorn selector.api:app --host 127.0.0.1 --port 8050 --log-level info

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

- `ATDF_CATALOG_DIR`: path(s) to directories with descriptors (use `os.pathsep` to separate multiple entries).
- `ATDF_MCP_TOOLS_URL`: optional MCP `/tools` endpoint ingested at startup.
- `ATDF_SELECTOR_DB`: SQLite database path used by the API (enables persistence and multi-process sharing).

## Persistence Model

- **servers**: stores MCP endpoints or local sources (`url`, `name`, `cache_timestamp`, `last_sync`).
- **tools**: stores descriptors per server (`tool_id`, `version_hash`, serialized descriptor, languages, tags, `active` flag`). The latest build normalises `description`, `when_to_use`, `how_to_use.inputs`, and default success/failure semantics.
- Synchronisation marks missing tools as inactive, allowing safe rollbacks and change detection when a tool is removed upstream.

## Feedback API

Use POST `/feedback` to registrar el resultado de una ejecución y ajustar el ranking:

```bash
curl -X POST http://127.0.0.1:8050/feedback \
  -H "Content-Type: application/json" \
  -d '{
        "tool_id": "hotel_reservation",
        "server": "http://localhost:8001/tools",
        "outcome": "success"
      }'
```

The selector accumulates successes and failures per tool/server pair and applies a heuristic adjustment (+0.5 per success, -0.75 per failure, capped at three events) when ranking.

## Integration Notes

- The n8n workflow `workflow_selector_builtin.json` demonstrates how to consume the selector using standard `HTTP Request` nodes and fall back to `hotel_reservation` if no recommendation is returned.
- `selector_workflow.db` ships pre-populated after `scripts/start_all_services.sh` runs once (loads `schema/examples` plus MCP `/tools`).
- When developing locally, stop the selector with `scripts/stop_all_services.sh` (kills port 8050 and removes `.selector.pid`).

## Known Gaps / Next Steps

1. **Semantic ranking** – plug sentence embeddings (e.g. `sentence-transformers`) and LanceDB/pgvector for similarity search beyond keyword heuristics.
2. **Observability** – expose Prometheus metrics (queries served, latency, precision) and integrate with the existing monitoring stack.
3. **Integration tests** – add end-to-end tests that hit `/recommend` while the MCP bridge serves live data and validate n8n HTTP-node integration.
4. **Admin tooling** – add CLI/API commands to remove servers, inspect inactive tools, and trigger selective re-syncs.

---
_Last updated: 2025-10-02_