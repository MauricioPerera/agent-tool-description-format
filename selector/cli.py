"""Command-line interface for managing the ATDF tool catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import shorten
from typing import Iterable, List, Optional

from .catalog import ATDFToolRecord, ToolCatalog
from .storage import CatalogStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect ATDF tool descriptors and build a normalized catalog.",
    )
    parser.add_argument(
        "--storage",
        type=str,
        help="Path to the SQLite database used for persistent catalog storage.",
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
    parser.add_argument(
        "--servers",
        nargs="*",
        help="Filter catalog listing by server URL identifiers.",
    )
    parser.add_argument(
        "--tools",
        nargs="*",
        help="Filter catalog listing by specific tool identifiers.",
    )
    return parser


def _render_table(records: Iterable[ATDFToolRecord], limit: int) -> None:
    header = (
        f"{'source':<30} {'tool_id':<28} {'version':<8} {'languages':<12} description"
    )
    print(header)
    print("-" * len(header))
    count = 0
    for record in records:
        if limit and count >= limit:
            break
        languages = ",".join(record.languages)
        description = shorten(
            record.description or record.when_to_use or "", width=50, placeholder="…"
        )
        print(
            f"{record.source:<30} {record.tool_id:<28} {record.schema_version:<8} {languages:<12} {description}"
        )
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

    storage = CatalogStorage(Path(args.storage)) if args.storage else None
    catalog = ToolCatalog(storage=storage)

    loaded = 0
    if args.dir:
        loaded += catalog.load_directory(
            Path(args.dir),
            recursive=not args.no_recursive,
            server_label=f"file://{Path(args.dir).resolve()}",
        )
    if args.mcp:
        loaded += catalog.load_from_mcp(args.mcp)

    records = catalog.list_tools(sources=args.servers, tool_ids=args.tools)
    if args.format == "json":
        _render_json(records, args.limit)
    else:
        _render_table(records, args.limit)

    if catalog.errors:
        print("\nWarnings:")
        for message in catalog.errors:
            print(f" - {message}")

    if storage:
        storage.close()

    return 0 if (loaded or records) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
