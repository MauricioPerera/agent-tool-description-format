# AEP-001: Validator & MCP Pipeline Alignment

## Status
Planned

## Owner
Core validation team (QA + Developer)

## Problem Statement
El conversor MCP→ATDF y pipelines de validación requieren soporte para validar estructuras en memoria. Actualmente alidate_tool_smart solo acepta rutas, lo que obliga a escribir archivos temporales o falla.

## Proposal
- Incorporar soporte nativo para dicts (alidate_tool_dict) reutilizando la lógica existente.
- Ajustar alidate_tool_smart para delegar en la nueva función cuando reciba un dict.
- Actualizar suite de tests y documentación con contratos claros (modo estricto vs laxo).

## Acceptance Criteria
- Conversión en lote MCP→ATDF funciona sin archivos temporales.
- Nuevas pruebas cubren validación en memoria y por archivo.
- Documentación describe el contrato del validador.

## Dependencies
Ninguna externa; se coordina con EPIC ATDF-EPIC-001.

## Milestones
- Draft implementation (Week 1)
- Test alignment (Week 2)
- Release in minor version (Week 3)
