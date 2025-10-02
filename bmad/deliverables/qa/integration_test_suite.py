"""Integration test suite covering selector + MCP bridge interoperability.
Generated for BMAD workflow task T2 (Integration Testing).
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

N8N_WORKFLOW_ID = "EJNFSpfWrmNxWKEo"  # Hotel Booking via Selector (HTTP)


def run_n8n_workflow():
    """Helper to execute the workflow and return parsed JSON text."""
    if not shutil.which("n8n"):
        pytest.skip("n8n CLI not available on PATH")
    result = subprocess.run(
        ["n8n", "execute", "--id", N8N_WORKFLOW_ID],
        capture_output=True,
        text=True,
        check=False,
    )
    return result


def test_n8n_selector_workflow_executes():
    """Workflow should complete successfully and emit reservation data."""
    result = run_n8n_workflow()
    assert result.returncode == 0, result.stderr
    assert 'reservation_id' in result.stdout


def test_selector_recommendation_payload(tmp_path):
    """Call selector via curl and capture JSON payload for traceability."""
    capture = tmp_path / "recommend.json"
    proc = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://127.0.0.1:8050/recommend",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(
                {
                    "query": "Necesito reservar un hotel en Madrid",
                    "language": "es",
                    "top_n": 1,
                    "servers": ["http://127.0.0.1:8001/tools"],
                    "allowed_tools": ["hotel_reservation"]
                }
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    capture.write_text(proc.stdout, encoding='utf-8')
    payload = json.loads(proc.stdout)
    assert payload["count"] >= 1
    assert payload["results"][0]["tool_id"] == "hotel_reservation"


def test_mcp_bridge_response(tmp_path):
    """Invoke MCP bridge and ensure JSON-RPC structure is valid."""
    proc = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "POST",
            "http://127.0.0.1:8001/mcp",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(
                {
                    "method": "tools/call",
                    "params": {
                        "name": "hotel_reservation",
                        "arguments": {
                            "guest_name": "QA Bot",
                            "email": "qa@example.com",
                            "check_in": "2025-12-05T15:00:00",
                            "check_out": "2025-12-08T11:00:00",
                            "room_type": "deluxe",
                            "guests": 2
                        }
                    }
                }
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(proc.stdout)
    assert payload["jsonrpc"] == "2.0"
    assert "reservation_id" in payload["result"]["content"][0]["text"]
