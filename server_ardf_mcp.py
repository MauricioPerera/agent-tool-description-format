"""Minimal MCP-compatible server that exposes ARDF resources via HTTP endpoints."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException

APP_ROOT = Path(__file__).parent
SAMPLES_DIR = APP_ROOT / "examples" / "ardf_samples"
MANIFEST_PATH = APP_ROOT / "mcp_manifest.json"

app = FastAPI(title="ARDF MCP Server", version="1.0.0")


class ResourceIndex:
    """Accessor for ARDF sample descriptors grouped by resource type."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        if not self.directory.exists():
            raise FileNotFoundError(f"ARDF sample directory not found: {directory}")

    @lru_cache(maxsize=1)
    def _load_all(self) -> List[Dict[str, object]]:
        resources: List[Dict[str, object]] = []
        for path in sorted(self.directory.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                resources.append(json.load(handle))
        return resources

    def all(self) -> List[Dict[str, object]]:
        return list(self._load_all())

    def by_type(self, resource_type: str) -> List[Dict[str, object]]:
        return [item for item in self._load_all() if item.get("resource_type") == resource_type]


@lru_cache(maxsize=1)
def get_index() -> ResourceIndex:
    return ResourceIndex(SAMPLES_DIR)


def build_response(items: List[Dict[str, object]]) -> Dict[str, object]:
    return {"count": len(items), "resources": items}


@app.get("/manifest")
def manifest() -> Dict[str, object]:
    if not MANIFEST_PATH.exists():
        raise HTTPException(status_code=500, detail="Manifest file not found")
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@app.get("/resources")
def list_all_resources() -> Dict[str, object]:
    items = get_index().all()
    return {"total": len(items), "resources": items}


@app.get("/tools")
def list_tools() -> Dict[str, object]:
    return build_response(get_index().by_type("tool"))


@app.get("/prompts")
def list_prompts() -> Dict[str, object]:
    return build_response(get_index().by_type("prompt"))


@app.get("/documents")
def list_documents() -> Dict[str, object]:
    return build_response(get_index().by_type("document"))


@app.get("/workflows")
def list_workflows() -> Dict[str, object]:
    return build_response(get_index().by_type("workflow"))


@app.get("/policies")
def list_policies() -> Dict[str, object]:
    return build_response(get_index().by_type("policy"))


@app.get("/models")
def list_models() -> Dict[str, object]:
    return build_response(get_index().by_type("model"))


@app.get("/datasets")
def list_datasets() -> Dict[str, object]:
    return build_response(get_index().by_type("dataset"))


@app.get("/connectors")
def list_connectors() -> Dict[str, object]:
    return build_response(get_index().by_type("connector"))


@app.get("/resources/{resource_type}")
def list_by_type(resource_type: str) -> Dict[str, object]:
    items = get_index().by_type(resource_type)
    if not items:
        raise HTTPException(status_code=404, detail=f"No resources found for type '{resource_type}'")
    return build_response(items)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server_ardf_mcp:app", host="0.0.0.0", port=8000, reload=True)
