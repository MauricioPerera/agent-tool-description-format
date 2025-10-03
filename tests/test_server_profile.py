"""Tests targeting the ATDF Server Profile reference implementation."""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json

import httpx
import jsonschema

from httpx import ASGITransport

from examples.fastapi_mcp_integration import app, TOOL_CATALOG

PROJECT_ROOT = Path(__file__).parent.parent
ERROR_SCHEMA_PATH = PROJECT_ROOT / "schema" / "error_atdf.json"
with ERROR_SCHEMA_PATH.open(encoding="utf-8") as handle:
    ERROR_SCHEMA = json.load(handle)

TRANSPORT = ASGITransport(app=app)


async def _request(method: str, url: str, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient(transport=TRANSPORT, base_url="http://testserver") as client:
        return await client.request(method, url, **kwargs)


def request(method: str, url: str, **kwargs) -> httpx.Response:
    return asyncio.run(_request(method, url, **kwargs))


def validate_error_payload(payload):
    """Validate that a payload matches the ATDF error schema."""
    jsonschema.validate(instance=payload, schema=ERROR_SCHEMA)


def test_health_endpoint_reports_status():
    response = request("GET", "/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0
    assert "version" in data
    assert "metrics" in data and "total_hotel_reservations" in data["metrics"]


def test_metrics_endpoint_is_prometheus_text():
    response = request("GET", "/metrics")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("text/plain")
    assert "atdf_requests_total" in response.text


def test_tools_catalog_contains_expected_fields():
    response = request("GET", "/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data and data["tools"], "Tools array should not be empty"
    tool = data["tools"][0]
    assert {"tool_id", "description", "when_to_use", "how_to_use"}.issubset(tool.keys())
    assert "inputs" in tool["how_to_use"]


def test_tool_lookup_not_found_returns_atdf_error():
    response = request("GET", "/tools/nonexistent")
    assert response.status_code == 404
    payload = response.json()
    validate_error_payload(payload)
    assert payload["errors"][0]["code"] == "tool_not_found"


def test_tools_validate_accepts_valid_descriptor():
    descriptor = list(TOOL_CATALOG.values())[0]
    response = request("POST", "/tools/validate", json=descriptor)
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["results"], "Validation response should contain descriptor metadata"


def test_tools_validate_rejects_invalid_descriptor():
    response = request("POST", "/tools/validate", json={"tool_id": "broken"})
    assert response.status_code == 400
    payload = response.json()
    validate_error_payload(payload)
    assert payload["errors"][0]["tool_name"] == "broken"


def test_convert_mcp_returns_atdf_payload():
    mcp_payload = {
        "name": "demo_tool",
        "description": "Simple MCP tool",
        "inputSchema": {
            "type": "object",
            "properties": {"foo": {"type": "string", "description": "Foo value"}},
            "required": ["foo"],
        },
    }
    response = request("POST", "/convert/mcp", json={"mcp": mcp_payload, "enhanced": False})
    assert response.status_code == 200
    body = response.json()
    assert body["tools"] and body["tools"][0]["tool_id"] == "demo_tool"


def test_search_returns_ranked_results():
    response = request("POST", "/search", json={"query": "Need a hotel booking", "limit": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["results"], "Search must return at least one result"
    for result in body["results"]:
        assert "tool_id" in result
        assert "score" in result
        assert isinstance(result["score"], float)


def test_hotel_reservation_rejects_past_check_in():
    payload = {
        "guest_name": "Test Guest",
        "email": "guest@example.com",
        "check_in": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
        "check_out": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "room_type": "double",
        "guests": 2,
    }
    response = request("POST", "/api/hotel/reserve", json=payload)
    assert response.status_code == 400
    payload = response.json()
    validate_error_payload(payload)
    assert payload["errors"][0]["code"] == "invalid_dates"
