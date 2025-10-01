# ATDF Tool Selector (Work in Progress)

This document tracks the initial implementation of the ATDF-aware tool selector.

## Overview

The selector centralises discovery and ranking of ATDF tool descriptors. It can
load descriptors from local JSON/YAML files or from an MCP bridge and exposes a
simple FastAPI service for downstream agents.

## Current Components

| Module | Description |
|--------|-------------|
| `selector.catalog` | Catalogs ATDF descriptors, validates them against v1/v2 schemas, normalises metadata (languages, tags, usage hints). |
| `selector.ranker`  | Provides a heuristic ranker that scores tools using query tokens, descriptions, tags, and language preference. |
| `selector.cli`     | Command-line utility to load descriptors and inspect the catalog (`python -m selector.cli --dir schema/examples`). |
| `selector.api`     | FastAPI application exposing `/recommend`, `/catalog`, and `/health` endpoints. |

## Quick Start

```bash
# Inspect descriptors shipped with the repository
env PYTHONPATH=. python -m selector.cli --dir schema/examples --limit 5

# Start the API with uvicorn
uvicorn selector.api:app --reload --port 8050

# Request recommendations
curl -X POST http://127.0.0.1:8050/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Necesito reservar un hotel en Madrid", "language": "es"}'
```

Environment variables:

- `ATDF_CATALOG_DIR`: path(s) to directories with descriptors (use `os.pathsep` to
  separate multiple entries).
- `ATDF_MCP_TOOLS_URL`: optional MCP `/tools` endpoint that will be ingested at
  startup.

## Known Gaps / Next Steps

1. **Semantic ranking** – plug sentence embeddings (e.g. `sentence-transformers`) and
   LanceDB/FAISS for similarity search.
2. **Feedback loop** – ingest ATDF error payloads to boost/penalise tools based on
   success rate.
3. **Persistence** – persist the catalog index in SQLite/PostgreSQL for team usage.
4. **Observability** – expose Prometheus metrics (queries served, latency, hit rate).
5. **Integration tests** – add end-to-end tests that hit `/recommend` while the MCP
   bridge serves live data.

---
_Last updated: 2025-10-01_
