"""Command-line interface for managing the ATDF tool catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import shorten
from typing import Iterable, List, Optional

from .catalog import ATDFToolRecord, ToolCatalog


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect ATDF tool descriptors and build a normalized catalog.",
    )
    parser.add_argument(
        "--dir",
        type=str,
        help="Directory containing ATDF descriptor files (JSON/YAML).",
    )
    parser.add_argument(
        "--mcp",
        type=str,
        help="MCP bridge endpoint returning a /tools payload.",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not traverse subdirectories when loading descriptors from --dir.",
    )
    parser.add_argument(
        "--format",
        choices={"table", "json"},
        default="table",
        help="Output format for catalog summary (default: table).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of tools displayed in the summary (0 = no limit).",
    )
    return parser


def _render_table(records: Iterable[ATDFToolRecord], limit: int) -> None:
    header = f"{'tool_id':<30} {'version':<8} {'languages':<12} description"
    print(header)
    print("-" * len(header))
    count = 0
    for record in records:
        if limit and count >= limit:
            break
        languages = ",".join(record.languages)
        description = shorten(record.description or record.when_to_use or "", width=60, placeholder="…")
        print(f"{record.tool_id:<30} {record.schema_version:<8} {languages:<12} {description}")
        count += 1


def _render_json(records: Iterable[ATDFToolRecord], limit: int) -> None:
    output: List[dict] = []
    count = 0
    for record in records:
        if limit and count >= limit:
            break
        payload = record.to_dict()
        payload["source"] = record.source
        output.append(payload)
        count += 1
    print(json.dumps(output, indent=2, ensure_ascii=False))


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.dir and not args.mcp:
        parser.error("Provide at least one source via --dir or --mcp")

    catalog = ToolCatalog()
    loaded = 0

    if args.dir:
        loaded += catalog.load_directory(Path(args.dir), recursive=not args.no_recursive)
    if args.mcp:
        loaded += catalog.load_from_mcp(args.mcp)

    records = catalog.list_tools()
    if args.format == "json":
        _render_json(records, args.limit)
    else:
        _render_table(records, args.limit)

    if catalog.errors:
        print("\nWarnings:")
        for message in catalog.errors:
            print(f" - {message}")

    return 0 if loaded else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
