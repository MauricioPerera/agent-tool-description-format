# AEP-004: ATDF Server Profile v1

## Status
Planned

## Owner
Architecture council

## Problem Statement
El servidor FastAPI de ejemplo demuestra buenas pr�cticas, pero no existe un perfil formal de endpoints/m�tricas obligatorio para implementaciones ATDF.

## Proposal
- Definir perfil de servidor ATDF Server Profile v1 con endpoints m�nimos (GET /tools, GET /tools/{id}, POST /tools/validate, POST /convert/mcp, POST /search, GET /metrics, GET /health).
- Actualizar ejemplo FastAPI para cumplir 100% con el perfil y documentar autenticaci�n opcional.
- Publicar contrato OpenAPI y gu�a de conformidad.

## Acceptance Criteria
- Documento de perfil publicado en docs/ con reglas claras.
- Servidor de referencia actualizado y probado.
- Checklist de conformidad incorporado al TCK.

## Dependencies
ATDF-EPIC-004.

## Milestones
- Specification draft (Week 2)
- Reference implementation (Week 4)
- TCK integration (Week 6)
