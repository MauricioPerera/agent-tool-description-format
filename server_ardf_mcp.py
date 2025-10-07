"""Minimal MCP-compatible server that exposes ARDF resources via HTTP endpoints."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jsonschema import validators

APP_ROOT = Path(__file__).parent
SAMPLES_DIR = APP_ROOT / "examples" / "ardf_samples"
UTF8_BOM_TOLERANT = "utf-8-sig"
MANIFEST_PATH = APP_ROOT / "mcp_manifest.json"
SCHEMA_PATH = APP_ROOT / "schema" / "ardf.schema.json"

app = FastAPI(title="ARDF MCP Server", version="1.0.0")

# CORS para facilitar integraciones de cliente durante desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"]
)


# Manejadores de errores para estandarizar el formato de respuesta
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else json.dumps(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": detail}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    # Evitar exponer detalles internos, retornar un error genérico
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Internal server error"}},
    )


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
            with path.open("r", encoding=UTF8_BOM_TOLERANT) as handle:
                resources.append(json.load(handle))
        return resources

    def all(self) -> List[Dict[str, object]]:
        return list(self._load_all())

    def by_type(self, resource_type: str) -> List[Dict[str, object]]:
        return [item for item in self._load_all() if item.get("resource_type") == resource_type]

    def validate_all(self) -> List[Dict[str, object]]:
        """Validate all sample files against the ARDF schema and return a list of errors."""
        errors: List[Dict[str, object]] = []
        validator = get_validator()
        for path in sorted(self.directory.glob("*.json")):
            try:
                with path.open("r", encoding=UTF8_BOM_TOLERANT) as handle:
                    data = json.load(handle)
            except Exception as e:
                errors.append({
                    "file": path.name,
                    "message": "Invalid JSON",
                    "details": str(e),
                })
                continue

            for err in validator.iter_errors(data):
                errors.append({
                    "file": path.name,
                    "message": err.message,
                    "path": list(err.path),
                })
        return errors


@lru_cache(maxsize=1)
def get_schema() -> Dict[str, object]:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"ARDF schema file not found: {SCHEMA_PATH}")
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def get_validator():
    schema = get_schema()
    ValidatorCls = validators.validator_for(schema)
    ValidatorCls.check_schema(schema)
    return ValidatorCls(schema)


@lru_cache(maxsize=1)
def get_index() -> ResourceIndex:
    return ResourceIndex(SAMPLES_DIR)


def build_response(items: List[Dict[str, object]]) -> Dict[str, object]:
    return {"count": len(items), "resources": items}


# Helper para obtener items con manejo de errores consistente
def safe_get_items(resource_type: Optional[str] = None) -> List[Dict[str, object]]:
    try:
        index = get_index()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"ARDF sample directory not found: {SAMPLES_DIR}")
    if resource_type is None:
        return index.all()
    return index.by_type(resource_type)


@app.get("/manifest")
def manifest() -> Dict[str, object]:
    if not MANIFEST_PATH.exists():
        raise HTTPException(status_code=500, detail="Manifest file not found")
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@app.get("/resources")
def list_all_resources() -> Dict[str, object]:
    items = safe_get_items()
    return build_response(items)


@app.get("/tools")
def list_tools() -> Dict[str, object]:
    return build_response(safe_get_items("tool"))


@app.get("/prompts")
def list_prompts() -> Dict[str, object]:
    return build_response(safe_get_items("prompt"))


@app.get("/documents")
def list_documents() -> Dict[str, object]:
    return build_response(safe_get_items("document"))


@app.get("/workflows")
def list_workflows() -> Dict[str, object]:
    return build_response(safe_get_items("workflow"))


@app.get("/policies")
def list_policies() -> Dict[str, object]:
    return build_response(safe_get_items("policy"))


@app.get("/models")
def list_models() -> Dict[str, object]:
    return build_response(safe_get_items("model"))


@app.get("/datasets")
def list_datasets() -> Dict[str, object]:
    return build_response(safe_get_items("dataset"))


@app.get("/connectors")
def list_connectors() -> Dict[str, object]:
    return build_response(safe_get_items("connector"))


@app.get("/resources/{resource_type}")
def list_by_type(resource_type: str) -> Dict[str, object]:
    items = safe_get_items(resource_type)
    if not items:
        raise HTTPException(status_code=404, detail=f"No resources found for type '{resource_type}'")
    return build_response(items)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> Dict[str, str]:
    try:
        if not SAMPLES_DIR.exists():
            raise FileNotFoundError(f"ARDF sample directory not found: {SAMPLES_DIR}")
        if not MANIFEST_PATH.exists():
            raise FileNotFoundError("Manifest file not found")
        _ = get_schema()
        _ = get_index()
        _ = get_index().all()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "ready"}


@app.get("/validate")
def validate_samples() -> Dict[str, object]:
    try:
        index = get_index()
        errors = index.validate_all()
        return {"count": len(errors), "errors": errors}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"ARDF sample directory not found: {SAMPLES_DIR}")


if __name__ == "__main__":
    import uvicorn
    import platform

    reload_enabled = platform.system() != "Windows"
    uvicorn.run("server_ardf_mcp:app", host="0.0.0.0", port=8000, reload=reload_enabled)
