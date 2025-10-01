"""FastAPI application exposing ATDF tool recommendations."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .catalog import ToolCatalog
from .ranker import ToolRanker

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "schema" / "examples"

app = FastAPI(title="ATDF Tool Selector", version="0.1.0")
_catalog = ToolCatalog()
_ranker = ToolRanker(_catalog)


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User request or task description")
    top_n: int = Field(5, ge=1, le=50)
    language: Optional[str] = Field(None, description="Preferred language code (e.g. 'en', 'es')")
    include_raw: bool = Field(False, description="Return full ATDF descriptor in the results")


class RecommendResponse(BaseModel):
    count: int
    results: List[dict]


@app.on_event("startup")
async def load_initial_catalog() -> None:
    sources = os.environ.get("ATDF_CATALOG_DIR")
    mcp_endpoint = os.environ.get("ATDF_MCP_TOOLS_URL")

    if sources:
        for value in sources.split(os.pathsep):
            path = Path(value)
            if path.exists():
                _catalog.load_directory(path)
    elif DEFAULT_DATA_DIR.exists():
        _catalog.load_directory(DEFAULT_DATA_DIR)

    if mcp_endpoint:
        _catalog.load_from_mcp(mcp_endpoint)


@app.get("/health", tags=["meta"])
def healthcheck() -> dict:
    return {"status": "ok", "tool_count": len(_catalog.tools)}


@app.get("/catalog", tags=["catalog"])
def list_catalog(limit: int = 0) -> dict:
    records = _catalog.list_tools()
    if limit > 0:
        records = records[:limit]
    return {
        "count": len(records),
        "tools": [record.to_dict() for record in records],
    }


@app.post("/recommend", response_model=RecommendResponse, tags=["ranking"])
def recommend_tools(payload: RecommendRequest) -> RecommendResponse:
    try:
        ranked = _ranker.rank(
            query=payload.query,
            top_n=payload.top_n,
            preferred_language=payload.language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = [item.to_dict(include_descriptor=payload.include_raw) for item in ranked]
    return RecommendResponse(count=len(results), results=results)


@app.post("/catalog/reload", tags=["catalog"])
def reload_catalog(directory: Optional[str] = None, mcp_endpoint: Optional[str] = None) -> dict:
    _catalog.tools.clear()
    _catalog.errors.clear()

    if directory:
        _catalog.load_directory(Path(directory))
    if mcp_endpoint:
        _catalog.load_from_mcp(mcp_endpoint)
    if not directory and not mcp_endpoint:
        load_dir = DEFAULT_DATA_DIR if DEFAULT_DATA_DIR.exists() else None
        if load_dir:
            _catalog.load_directory(load_dir)

    return {"tool_count": len(_catalog.tools), "errors": list(_catalog.errors)}
