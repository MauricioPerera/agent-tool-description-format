from pathlib import Path
import json
from typing import Optional

import click


def _load_tool(path: Path):
    from tools.converter import load_tool

    return load_tool(path)


@click.group()
def cli():
    """ATDF command-line toolkit."""
    pass


@cli.command()
@click.argument("tool_path", type=click.Path(exists=True))
@click.option("--smart", "-s", is_flag=True, help="Auto-detect schema version.")
@click.option(
    "--schema", "-m", type=click.Path(exists=True), help="Explicit schema path."
)
@click.option(
    "--ignore-additional",
    "-i",
    is_flag=True,
    help="Ignore additional properties for basic schema.",
)
def validate(
    tool_path: str, smart: bool, schema: Optional[str], ignore_additional: bool
):
    """Validate an ATDF descriptor."""
    from tools.validator import validate_tool, validate_tool_smart

    source = tool_path
    if smart:
        ok = validate_tool_smart(source)
    else:
        ok = validate_tool(
            source, schema_file=schema, ignore_additional_properties=ignore_additional
        )

    if ok:
        click.echo("✅ ATDF descriptor is valid.")
        raise SystemExit(0)
    click.echo("❌ ATDF descriptor failed validation.", err=True)
    raise SystemExit(1)


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--enhanced", is_flag=True, help="Convert MCP input to enhanced ATDF.")
@click.option(
    "--author", default="ATDF CLI", help="Author metadata for enhanced conversion."
)
def convert(input: str, output: str, enhanced: bool, author: str):
    """Convert MCP catalog or ATDF file."""
    from tools.mcp_converter import convert_mcp_file
    from tools.converter import convert_to_enhanced, save_tool

    input_path = Path(input)
    output_path = Path(output)

    if input_path.suffix.lower() == ".json" and "mcp" in input_path.stem:
        result = convert_mcp_file(input_path, output_path, enhanced=enhanced)
        if result is None:
            click.echo("❌ MCP conversion failed.", err=True)
            raise SystemExit(1)
        click.echo(f"✅ MCP converted to {output_path}")
        raise SystemExit(0)

    tool = _load_tool(input_path)
    if enhanced:
        enriched = convert_to_enhanced(tool, author=author, extract_language=True)
        save_tool(enriched, output_path)
        click.echo(f"✅ Converted to enhanced ATDF at {output_path}")
    else:
        save_tool(tool, output_path)
        click.echo(f"✅ Copied ATDF to {output_path}")


@cli.command()
@click.argument("tool_path", type=click.Path(exists=True))
@click.option(
    "--author", default="ATDF CLI", help="Author metadata for enhanced conversion."
)
def enrich(tool_path: str, author: str):
    """Enrich a basic ATDF descriptor with metadata/localization heuristics."""
    from tools.converter import convert_to_enhanced, save_tool

    path = Path(tool_path)
    tool = _load_tool(path)
    enhanced = convert_to_enhanced(tool, author=author, extract_language=True)
    save_tool(enhanced, path)
    click.echo(f"✅ Enriched {tool_path} in place.")


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.argument("goal", type=str)
@click.option(
    "--language", "-l", help="Language code to bias selection (e.g., en, es)."
)
def search(directory: str, goal: str, language: Optional[str]):
    """Search for a tool matching GOAL within DIRECTORY."""
    from improved_loader import load_tools_from_directory, select_tool_by_goal

    dir_path = Path(directory)
    tools = load_tools_from_directory(dir_path)
    if not tools:
        click.echo("❌ No ATDF tools found in directory.", err=True)
        raise SystemExit(1)

    tool = select_tool_by_goal(tools, goal, language=language)
    if not tool:
        click.echo("❌ No matching tool found.", err=True)
        raise SystemExit(1)

    click.echo(json.dumps(tool, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    cli()
