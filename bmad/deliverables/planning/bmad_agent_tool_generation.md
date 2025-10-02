# BMAD Agent Workflow – Generating ATDF Tools

## Objetivo
Demostrar que los agentes BMAD pueden producir descriptores ATDF listos para consumo.

## Pasos
1. Ejecutar `python tools/bmad_atdf_integration.py --plan` para listar tareas de generación.
2. Invocar el orquestador BMAD cargando `bmad/agents/bmad-orchestrator.md` y usar el comando `*start atdf-enhancement`.
3. Asignar al agente `developer` la tarea `generate_tool_descriptor` que produce JSON compatible con `schema/atdf_schema.json`.
4. Validar el descriptor con `python tools/validator.py <archivo> --schema schema/atdf_schema.json` y `python tools/validate_enhanced.py` si aplica.
5. Registrar el artefacto generado en `bmad/tools/` y actualizar `bmad/deliverables/qa/validation_test_results.json` con la evidencia.

## Evidencia
- Herramientas de referencia: `bmad/tools/atdf_all_tools.json`.
- Validación documentada en `bmad/deliverables/qa/validation_test_suite.py` (test `test_validation_cli`).
- Flujo de QA interno confirma cobertura >=0.90 con nuevas entradas.
