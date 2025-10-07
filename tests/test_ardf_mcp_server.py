"""Integration tests for the ARDF MCP FastAPI server."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from httpx import ASGITransport, AsyncClient, Response

from server_ardf_mcp import app

TRANSPORT = ASGITransport(app=app)
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = PROJECT_ROOT / "schema" / "ardf.schema.json"


async def _get(path: str) -> Response:
    async with AsyncClient(transport=TRANSPORT, base_url="http://testserver") as client:
        return await client.request("GET", path)


def _request_json(path: str) -> Dict[str, Any]:
    response = asyncio.run(_get(path))
    assert response.status_code == 200, f"Unexpected {response.status_code} for {path}: {response.text}"
    return response.json()


def test_manifest_lists_dataset_and_connector_collections():
    manifest = _request_json("/manifest")
    assert manifest["schema"]["id"] == "https://ardf.io/schema/v1"
    assert manifest["schema"]["path"] == "/schema/ardf.schema.json"

    resource_types = {entry["type"] for entry in manifest["resources"]}
    assert {"dataset", "connector"}.issubset(resource_types)


def test_schema_static_route_serves_canonical_descriptor():
    served_schema = _request_json("/schema/ardf.schema.json")
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        local_schema = json.load(handle)
    assert served_schema == local_schema
