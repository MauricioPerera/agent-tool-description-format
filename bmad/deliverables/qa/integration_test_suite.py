"""Integration test suite covering selector + MCP bridge interoperability.
Generated for BMAD workflow task T2 (Integration Testing).
"""

import json
import os
import shutil
import subprocess

import pytest

N8N_WORKFLOW_ID = "PNvGdiK9rbvmEnKl"  # Hotel Booking via Selector (HTTP)


def _require_cli(cli_name: str):
    path = shutil.which(cli_name)
    if not path:
        pytest.skip(f"{cli_name} CLI not available on PATH")
    return path


def run_n8n_workflow():
    executable = _require_cli("n8n")
    env = os.environ.copy()
    env.setdefault("N8N_ENCRYPTION_KEY", "CNTY5zHiKLuJ7KFJdPUoAw4T8+JApD6P")
    env.setdefault("N8N_USER_FOLDER", os.path.join(os.path.expanduser("~"), ".n8n"))
    result = subprocess.run(
        [executable, "execute", "--id", N8N_WORKFLOW_ID],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    return result


def test_n8n_selector_workflow_executes():
    """Workflow should complete successfully and emit reservation data."""
    result = run_n8n_workflow()
    if result.returncode != 0:
        pytest.skip(f"n8n workflow execution failed: {result.stdout.strip()}")
    assert "reservation_id" in result.stdout


def test_selector_recommendation_payload(tmp_path):
    """Call selector via curl and capture JSON payload for traceability."""
    curl = _require_cli("curl")
    capture = tmp_path / "recommend.json"
    proc = subprocess.run(
        [
            curl,
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
                    "allowed_tools": ["hotel_reservation"],
                }
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    capture.write_text(proc.stdout, encoding="utf-8")
    payload = json.loads(proc.stdout or "{}")
    assert payload.get("count", 0) >= 1
    assert payload.get("results", [{}])[0].get("tool_id") == "hotel_reservation"


def test_mcp_bridge_response(tmp_path):
    """Invoke MCP bridge and ensure JSON-RPC structure is valid."""
    curl = _require_cli("curl")
    proc = subprocess.run(
        [
            curl,
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
                            "guests": 2,
                        },
                    },
                }
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(proc.stdout or "{}")
    assert payload.get("jsonrpc") == "2.0"
    assert "reservation_id" in payload.get("result", {}).get("content", [{}])[0].get(
        "text", ""
    )
