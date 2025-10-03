from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.mcp_converter import mcp_to_atdf
from tools.validator import validate_tool_smart
from tools.converter import convert_to_enhanced, save_tool


def _load_mcp_catalog(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "tools" in data and isinstance(data["tools"], list):
        return data["tools"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported MCP catalog structure in {path}")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run_migration(
    mcp_file: Path,
    basic_dir: Path,
    enhanced_dir: Optional[Path],
    author: str,
    validate: bool,
) -> None:
    tools = _load_mcp_catalog(mcp_file)
    _ensure_dir(basic_dir)
    if enhanced_dir:
        _ensure_dir(enhanced_dir)

    total = len(tools)
    enhanced_count = 0

    for tool in tools:
        atdf_basic = mcp_to_atdf(tool, enhanced=False, author=author)
        tool_id = atdf_basic.get("tool_id") or atdf_basic.get("id")
        if not tool_id:
            raise ValueError("Converted tool is missing tool_id/id")

        basic_path = basic_dir / f"{tool_id}.json"
        save_tool(atdf_basic, basic_path, format="json")

        if validate and not validate_tool_smart(basic_path):
            raise ValueError(f"Validation failed for {basic_path}")

        if enhanced_dir:
            atdf_enh = convert_to_enhanced(
                atdf_basic, author=author, extract_language=True
            )
            if validate and not validate_tool_smart(atdf_enh):
                raise ValueError(f"Validation failed for enhanced tool {tool_id}")
            save_tool(atdf_enh, enhanced_dir / f"{tool_id}.json", format="json")
            enhanced_count += 1

    print(f"Converted {total} MCP tools into ATDF basic format at {basic_dir}")
    if enhanced_dir:
        print(f"Enhanced tools stored at {enhanced_dir} (count={enhanced_count})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MCP → ATDF migration pipeline")
    parser.add_argument("mcp_file", type=Path, help="Path to MCP catalog JSON")
    parser.add_argument(
        "--basic-dir",
        type=Path,
        default=Path("atdf"),
        help="Directory to store basic ATDF files",
    )
    parser.add_argument(
        "--enhanced-dir", type=Path, help="Directory to store enhanced ATDF files"
    )
    parser.add_argument(
        "--author",
        default="ATDF Migration",
        help="Author metadata for enhanced conversion",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation after conversion",
    )

    args = parser.parse_args()

    run_migration(
        mcp_file=args.mcp_file,
        basic_dir=args.basic_dir,
        enhanced_dir=args.enhanced_dir,
        author=args.author,
        validate=not args.skip_validation,
    )


if __name__ == "__main__":
    main()
