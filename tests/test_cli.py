import json
import sys
from pathlib import Path
from click.testing import CliRunner

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from cli.main import cli


def make_basic_tool(tool_id="sample", description="Sample tool", when="Use for tests"):
    return {
        "tool_id": tool_id,
        "description": description,
        "when_to_use": when,
        "how_to_use": {
            "inputs": [{"name": "text", "type": "string", "description": "Text"}],
            "outputs": {
                "success": "ok",
                "failure": [{"code": "error", "description": "Error"}],
            },
        },
    }


def test_cli_validate_success(tmp_path):
    path = tmp_path / "tool.json"
    path.write_text(json.dumps(make_basic_tool()))

    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(path)])

    assert result.exit_code == 0
    assert "ATDF descriptor is valid" in result.output


def test_cli_validate_failure(tmp_path):
    tool = make_basic_tool()
    tool.pop("when_to_use")
    path = tmp_path / "tool_invalid.json"
    path.write_text(json.dumps(tool))

    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(path)])

    assert result.exit_code == 1
    assert "ATDF descriptor failed validation" in result.output


def test_cli_enrich(tmp_path):
    path = tmp_path / "basic.json"
    path.write_text(json.dumps(make_basic_tool()))

    runner = CliRunner()
    result = runner.invoke(cli, ["enrich", str(path)])

    assert result.exit_code == 0
    enhanced = json.loads(path.read_text())
    assert enhanced.get("schema_version") == "2.0.0"


def test_cli_convert_enhanced(tmp_path):
    source = tmp_path / "basic.json"
    source.write_text(json.dumps(make_basic_tool()))
    target = tmp_path / "enhanced.json"

    runner = CliRunner()
    result = runner.invoke(
        cli, ["convert", str(source), str(target), "--enhanced", "--author", "QA"]
    )

    assert result.exit_code == 0
    enhanced = json.loads(target.read_text())
    assert enhanced.get("schema_version") == "2.0.0"
    assert enhanced.get("metadata", {}).get("author") == "QA"


def test_cli_search(tmp_path):
    # create matching tool
    sample = make_basic_tool(
        tool_id="translator_enhanced",
        description="Text translator",
        when="Use this tool to translate text",
    )
    (tmp_path / "sample.json").write_text(json.dumps(sample))
    other = make_basic_tool(
        tool_id="other", description="Otra herramienta", when="Para tareas distintas"
    )
    (tmp_path / "other.json").write_text(json.dumps(other))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["search", str(tmp_path), "translate some text to french"]
    )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data.get("tool_id") == "translator_enhanced"
