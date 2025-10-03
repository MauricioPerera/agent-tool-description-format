# Checklist de Migración MCP → ATDF

## 1. Inventario
- [ ] Exportar catálogo MCP (`/tools`) a JSON.
- [ ] Identificar herramientas críticas por frecuencia/impacto.
- [ ] Confirmar esquemas (`inputSchema`) y anotaciones (`annotations.context`).

## 2. Conversión inicial
- [ ] Ejecutar `tools/mcp_converter.py` en modo básico para lote completo.
- [ ] Validar en bloque con `python tools/validator.py --smart --ignore-additional`.
- [ ] Revisar manualmente `description`/`when_to_use` en herramientas críticas.

## 3. Enriquecimiento
- [ ] Reconvertir a versión enhanced (`enhanced=True` o `tools/converter.py`).
- [ ] Completar `metadata.version`, `metadata.tags` y `prerequisites`.
- [ ] Añadir `examples` realistas y `feedback` (códigos de éxito/error).

## 4. Calidad y pruebas
- [ ] Validación estricta (`python tools/validator.py --smart` sin `--ignore-additional`).
- [ ] `tests/run_all_tests.py` (Python) y `npm test` si se usa SDK JS.
- [ ] Ejecutar las suites internas necesarias (`validation_test_suite.py`, `integration_test_suite.py`, `performance_test_suite.py`).

## 5. Publicación y servidor
- [ ] Deploy del catálogo en servidor FastAPI (`examples/fastapi_mcp_integration.py`).
- [ ] Exponer métricas `/metrics` a Prometheus.
- [ ] Documentar endpoints y errores ATDF para consumidores.

## 6. Descubrimiento y selección
- [ ] Configurar `improved_loader.py` o capa vectorial (LanceDB/SQLite-VSS).
- [ ] Sembrar índices con idiomas relevantes (`localization`).
- [ ] Definir monitoreo de consultas/respuestas para ajuste continuo.

## 7. Integraciones aguas abajo
- [ ] Actualizar workflows n8n (`workflow_selector_builtin.json`) y pipelines internos.
- [ ] Ajustar scripts de arranque (`scripts/start_all_services.*`).
- [ ] Propagar documentación multilingüe (docs/en|es|pt).

## 8. Post-migración
- [ ] Plan de rollout (beta → GA) con puntos de reversa.
- [ ] Capturar métricas de adopción (ver `adoption_metrics.csv`).
- [ ] Programar retroalimentación con equipos de herramientas/agents.


## Automatización de referencia
- Ejecuta `scripts/run_atdf_migration.py` para orquestar conversión y validación (usa `tests/fixtures/mcp_tools_sample.json` como plantilla).
- Workflow CI: `.github/workflows/atdf-migration.yml` valida conversiones en cada PR relacionado.

## Observabilidad sugerida
- Dashboard Grafana: `monitoring/grafana/dashboards/atdf-migration-overview.json` con métricas de conversión, fallos y accuracy de selección.
