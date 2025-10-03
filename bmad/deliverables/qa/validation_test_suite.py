"""Validation test suite for ATDF selector automation.

Generated for BMAD workflow task T1 (Schema Validation Testing).
The suite documents how to execute critical validation checks using pytest.
"""

from pathlib import Path
import shutil
import subprocess
import json


def _powershell_exe() -> list[str]:
    if shutil.which("pwsh"):
        return ["pwsh", "-NoLogo", "-NoProfile"]
    return ["powershell", "-NoLogo", "-NoProfile"]


def test_start_script_runs_healthcheck(tmp_path):
    """`scripts/start_all_services.ps1` should exit with 0 and emit health status."""
    script = Path("scripts/start_all_services.ps1").resolve()
    cmd = _powershell_exe() + ["-File", str(script), "-StartupDelay", "5"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "Service status" in result.stdout


def test_selector_health_endpoint():
    """Selector `/health` endpoint must respond with tool_count >= 2 (hotel + flight)."""
    import requests

    response = requests.get("http://127.0.0.1:8050/health", timeout=5)
    payload = response.json()
    assert response.status_code == 200
    assert payload.get("tool_count", 0) >= 2


def test_validation_cli(tmp_path):
    """Document validator usage for ATDF descriptors."""
    descriptor = tmp_path / "tool.json"
    descriptor.write_text(
        '{"tool_id":"test","description":"demo","when_to_use":"Usar para QA","how_to_use":{"inputs":[],"outputs":{"success":"Reserva confirmada","failure":[]}}}',
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "python",
            "tools/validator.py",
            str(descriptor),
            "--schema",
            "schema/atdf_schema.json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
