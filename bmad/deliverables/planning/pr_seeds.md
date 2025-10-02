# PR Seeds for ATDF Roadmap

| PR Seed ID | Epic | Description | Components |
|------------|------|-------------|-------------|
| PR-SEED-001 | ATDF-EPIC-001 | Implement alidate_tool_dict, actualizar alidate_tool_smart y refactor tests. | tools/validator.py, tools/mcp_converter.py, tests/ |
| PR-SEED-002 | ATDF-EPIC-002 | Añadir schema/error_atdf.json, ejemplos y doc de errores. | schema/, docs/ErrorHandling.md, examples/ |
| PR-SEED-003 | ATDF-EPIC-003 | Crear CLI tdf (validate/convert/enrich) y documentación inicial. | cli/, pyproject.toml, docs/cli.md |
| PR-SEED-004 | ATDF-EPIC-004 | Publicar ATDF Server Profile v1 y actualizar FastAPI. | docs/server_profile.md, examples/fastapi_mcp_integration.py |

Notas:
- Cada seed incluye pruebas unitarias y actualización de docs.
- Las ramas sugeridas siguen convención eature/<seed-id-lower>.
