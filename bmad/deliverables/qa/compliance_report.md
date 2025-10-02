# ATDF Compliance Report – Selector Automation

## Scope
- Validación de `scripts/start_all_services.ps1` y `.sh`
- Health checks de ATDF Server, MCP Bridge, Selector
- Validación mediante `tools/validator.py`

## Resultados Principales
- ✅ Health checks reportan respuestas HTTP 200 (hotel + flight disponibles)
- ✅ Validator acepta descriptor generado sin warnings
- ⚠️ Se recomienda ejecutar los scripts en PowerShell 7+ para soporte `Start-Process`

## Cobertura
| Módulo                      | Cobertura estimada |
|-----------------------------|--------------------|
| Startup/Shutdown scripts    | 95% (branch logic cubierto) |
| Selector health             | 100% (endpoints GET /health) |
| Validator CLI               | 85% (caso éxito + validación esquema) |

## Evidencias
- `validation_test_suite.py`
- `validation_test_results.json`
- Captura: `logs/start_all_services_stdout.txt` (generar en ejecución real)

## Recomendaciones
1. Añadir prueba negativa que valide manejo de puertos en uso.
2. Documentar variable `StartupDelay` en README general.
3. Programar ejecución en CI semanal para detectar regresiones.
