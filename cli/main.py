import json
import sys
from pathlib import Path
from typing import Optional

import click

from tools.validator import validate_tool, validate_tool_smart
from tools.mcp_converter import convert_mcp_file
from tools.converter import convert_to_enhanced, load_tool, save_tool


@click.group()
def cli():
    """ATDF command-line toolkit."""
    pass


@cli.command()
@click.argument('tool_path', type=click.Path(exists=True))
@click.option('--smart', '-s', is_flag=True, help='Auto-detect schema version.')
@click.option('--schema', '-m', type=click.Path(exists=True), help='Explicit schema path.')
@click.option('--ignore-additional', '-i', is_flag=True, help='Ignore additional properties for basic schema.')
def validate(tool_path: str, smart: bool, schema: Optional[str], ignore_additional: bool):
    """Validate an ATDF descriptor."""
    if smart:
        ok = validate_tool_smart(tool_path)
    else:
        ok = validate_tool(tool_path, schema_file=schema, ignore_additional_properties=ignore_additional)

    if ok:
        click.echo('✅ ATDF descriptor is valid.')
        sys.exit(0)
    click.echo('❌ ATDF descriptor failed validation.', err=True)
    sys.exit(1)


@cli.command()
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--enhanced', is_flag=True, help='Convert MCP input to enhanced ATDF.')
@click.option('--author', default='ATDF CLI', help='Author metadata for enhanced conversion.')
def convert(input: str, output: str, enhanced: bool, author: str):
    """Convert MCP catalog or ATDF file."""
    input_path = Path(input)
    output_path = Path(output)

    if input_path.suffix.lower() == '.json' and 'mcp' in input_path.stem:
        result = convert_mcp_file(input_path, output_path, enhanced=enhanced)
        if result is None:
            click.echo('❌ MCP conversion failed.', err=True)
            sys.exit(1)
        click.echo(f'✅ MCP converted to {output_path}')
        sys.exit(0)

    tool = load_tool(input_path)
    if enhanced:
        enriched = convert_to_enhanced(tool, author=author, extract_language=True)
        save_tool(enriched, output_path)
        click.echo(f'✅ Converted to enhanced ATDF at {output_path}')
    else:
        save_tool(tool, output_path)
        click.echo(f'✅ Copied ATDF to {output_path}')


@cli.command()
@click.argument('tool_path', type=click.Path(exists=True))
@click.option('--author', default='ATDF CLI', help='Author metadata for enhanced conversion.')
def enrich(tool_path: str, author: str):
    """Enrich a basic ATDF descriptor with metadata/localization heuristics."""
    path = Path(tool_path)
    tool = load_tool(path)
    enhanced = convert_to_enhanced(tool, author=author, extract_language=True)
    save_tool(enhanced, path)
    click.echo(f'✅ Enriched {tool_path} in place.')


if __name__ == '__main__':
    cli()
