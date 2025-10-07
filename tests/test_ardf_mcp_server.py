"""Integration tests for the ARDF MCP FastAPI server."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from httpx import ASGITransport, AsyncClient, Response

from server_ardf_mcp import app, get_validator

TRANSPORT = ASGITransport(app=app)
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = PROJECT_ROOT / "schema" / "ardf.schema.json"
SAMPLES_DIR = PROJECT_ROOT / "examples" / "ardf_samples"


async def _get(path: str) -> Response:
    async with AsyncClient(transport=TRANSPORT, base_url="http://testserver") as client:
        return await client.request("GET", path)


def _request_json(path: str) -> Dict[str, Any]:
    response = asyncio.run(_get(path))
    assert response.status_code == 200, f"Unexpected {response.status_code} for {path}: {response.text}"
    return response.json()


async def _post(path: str, payload: Dict[str, Any]) -> Response:
    async with AsyncClient(transport=TRANSPORT, base_url="http://testserver") as client:
        return await client.request("POST", path, json=payload)


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


def test_validate_endpoint_accepts_valid_descriptors():
    dataset_sample_path = SAMPLES_DIR / "dataset_products.json"
    with dataset_sample_path.open("r", encoding="utf-8") as handle:
        dataset_descriptor = json.load(handle)

    response = asyncio.run(_post("/validate", dataset_descriptor))
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 0
    assert body["errors"] == []


def test_dataset_descriptor_rejects_incorrect_content_type():
    validator = get_validator()
    invalid_dataset = {
        "schema_version": "1.0.0",
        "resource_id": "invalid_dataset_fixture",
        "resource_type": "dataset",
        "description": "Dataset with the wrong content type",
        "content": {
            "type": "document/ref",
            "data": {
                "schema": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                    "required": ["id"],
                },
                "query": "SELECT id FROM products",
                "connector": "connector_crm_v1",
            },
        },
    }

    errors = list(validator.iter_errors(invalid_dataset))
    assert errors, "Expected validation errors for an invalid dataset descriptor"
    assert any("dataset/spec" in error.message for error in errors)


def test_connector_descriptor_requires_endpoints_payload():
    validator = get_validator()
    invalid_connector = {
        "schema_version": "1.0.0",
        "resource_id": "invalid_connector_fixture",
        "resource_type": "connector",
        "description": "Connector without endpoint definitions",
        "content": {
            "type": "connector/spec",
            "data": {
                "interface": "http",
                "base_url": "https://api.example.com",
            },
        },
    }

    errors = list(validator.iter_errors(invalid_connector))
    assert errors, "Expected validation errors for an invalid connector descriptor"
    assert any("endpoints" in error.message for error in errors)


def test_validate_endpoint_reports_schema_violations():
    invalid_dataset = {
        "schema_version": "1.0.0",
        "resource_id": "invalid_dataset_via_http",
        "resource_type": "dataset",
        "description": "Dataset routed through HTTP validation",
        "content": {"type": "document/ref", "data": {}},
    }

    response = asyncio.run(_post("/validate", invalid_dataset))
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert any("dataset/spec" in error["message"] for error in payload["errors"])
