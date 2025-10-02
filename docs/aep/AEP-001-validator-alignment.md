# AEP-001: Validator & MCP Pipeline Alignment

## Status
In Progress

## Owner
Core validation team (QA + Developer)

## Problem Statement
El conversor MCP?ATDF y pipelines de validaci�n requieren soporte para validar estructuras en memoria. Actualmente alidate_tool_smart solo acepta rutas, lo que obliga a escribir archivos temporales o falla.

## Proposal
- Incorporar soporte nativo para dicts (alidate_tool_dict) reutilizando la l�gica existente.
- Ajustar alidate_tool_smart para delegar en la nueva funci�n cuando reciba un dict.
- Actualizar suite de tests y documentaci�n con contratos claros (modo estricto vs laxo).

## Acceptance Criteria
- Conversi�n en lote MCP?ATDF funciona sin archivos temporales.
- Nuevas pruebas cubren validaci�n en memoria y por archivo.
- Documentaci�n describe el contrato del validador.

## Dependencies
Ninguna externa; se coordina con EPIC ATDF-EPIC-001.

## Milestones
- Draft implementation (Week 1)
- Test alignment (Week 2)
- Release in minor version (Week 3)
