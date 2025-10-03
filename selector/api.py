"""FastAPI application exposing ATDF tool recommendations."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .catalog import ToolCatalog
from .ranker import ToolRanker
from .storage import CatalogStorage

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "schema" / "examples"
DB_PATH = os.environ.get("ATDF_SELECTOR_DB")

_storage = CatalogStorage(Path(DB_PATH)) if DB_PATH else None
_catalog = ToolCatalog(storage=_storage)
_ranker = ToolRanker(_catalog)

app = FastAPI(title="ATDF Tool Selector", version="0.2.0")


class RecommendRequest(BaseModel):
    query: str = Field(
        ..., min_length=1, description="User request or task description"
    )
    top_n: int = Field(5, ge=1, le=50)
    language: Optional[str] = Field(
        None, description="Preferred language code (e.g. 'en', 'es')"
    )
    include_raw: bool = Field(
        False, description="Return full ATDF descriptor in the results"
    )
    servers: Optional[List[str]] = Field(
        None, description="Filter by server URLs registered in the catalog"
    )
    allowed_tools: Optional[List[str]] = Field(
        None, description="Restrict ranking to specific tool identifiers"
    )


class FeedbackRequest(BaseModel):
    tool_id: str = Field(..., description="ATDF tool identifier")
    server: str = Field(..., description="Server URL or source identifier")
    outcome: Literal["success", "error"] = Field(
        ..., description="Result of the execution"
    )
    detail: Optional[str] = Field(None, description="Optional context or error message")


class RecommendResponse(BaseModel):
    count: int
    results: List[dict]


class ReloadRequest(BaseModel):
    directory: Optional[str] = None
    mcp_endpoint: Optional[str] = None
    server_label: Optional[str] = None


@app.on_event("startup")
async def load_initial_catalog() -> None:
    if _storage and _storage.bootstrap_records():
        _catalog.list_tools()
        return

    sources = os.environ.get("ATDF_CATALOG_DIR")
    if sources:
        for value in sources.split(os.pathsep):
            path = Path(value)
            if path.exists():
                _catalog.load_directory(path)
    elif DEFAULT_DATA_DIR.exists():
        _catalog.load_directory(DEFAULT_DATA_DIR)

    mcp_endpoint = os.environ.get("ATDF_MCP_TOOLS_URL")
    if mcp_endpoint:
        _catalog.load_from_mcp(mcp_endpoint)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if _storage:
        _storage.close()


@app.get("/health", tags=["meta"])
def healthcheck() -> dict:
    return {"status": "ok", "tool_count": len(_catalog.list_tools())}


@app.get("/catalog", tags=["catalog"])
def list_catalog(limit: int = 0, server: Optional[str] = None) -> dict:
    sources = [server] if server else None
    records = _catalog.list_tools(sources=sources)
    if limit > 0:
        records = records[:limit]
    return {
        "count": len(records),
        "tools": [record.to_dict() for record in records],
    }


@app.get("/servers", tags=["catalog"])
def list_servers() -> dict:
    if not _storage:
        return {"servers": []}
    return {"servers": _storage.list_servers()}


@app.post("/recommend", response_model=RecommendResponse, tags=["ranking"])
def recommend_tools(payload: RecommendRequest) -> RecommendResponse:
    try:
        ranked = _ranker.rank(
            query=payload.query,
            top_n=payload.top_n,
            preferred_language=payload.language,
            sources=payload.servers,
            tool_ids=payload.allowed_tools,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = [item.to_dict(include_descriptor=payload.include_raw) for item in ranked]
    return RecommendResponse(count=len(results), results=results)


@app.post("/catalog/reload", tags=["catalog"])
def reload_catalog(request: ReloadRequest) -> dict:
    _catalog.tools.clear()
    _catalog.errors.clear()

    loaded = 0
    if request.directory:
        loaded += _catalog.load_directory(
            Path(request.directory),
            server_label=request.server_label,
        )
    if request.mcp_endpoint:
        loaded += _catalog.load_from_mcp(request.mcp_endpoint)
    if not request.directory and not request.mcp_endpoint and DEFAULT_DATA_DIR.exists():
        loaded += _catalog.load_directory(DEFAULT_DATA_DIR)

    return {
        "tool_count": len(_catalog.list_tools()),
        "loaded": loaded,
        "errors": list(_catalog.errors),
    }


@app.post("/feedback", tags=["ranking"])
def submit_feedback(payload: FeedbackRequest) -> dict:
    if not _catalog.storage:
        raise HTTPException(
            status_code=400, detail="Feedback requires persistent storage"
        )
    _catalog.storage.record_feedback(
        server_url=payload.server,
        tool_id=payload.tool_id,
        outcome=payload.outcome,
        detail=payload.detail,
    )
    summary = _catalog.storage.feedback_summary() if _catalog.storage else {}
    key = f"{payload.server}::{payload.tool_id}"
    return {"status": "recorded", "stats": summary.get(key, {"success": 0, "error": 0})}
