# AEP-002: ATDF Error Schema Standardization

## Status
Completed

## Owner
Documentation & API consortium

## Problem Statement
Los errores ATDF están ejemplificados en el servidor FastAPI, pero no existe un schema oficial reutilizable. Esto limita interoperabilidad y tooling.

## Proposal
- Publicar schema/error_atdf.json con campos normativos (	ype, 	itle, detail, instance, 	ool_name, parameter_name, context, suggested_value).
- Actualizar ejemplos y guías (docs/ErrorHandling.md o equivalente) con payloads válidos.
- Ajustar server demo y SDKs para usar el schema.

## Acceptance Criteria
- Schema público versionado (1.0.0) con validación por jsonschema.
- Ejemplo FastAPI responde usando el schema.
- Documentación detalla mapeo de errores comunes.

## Dependencies
Alineación con EPIC ATDF-EPIC-002.

## Milestones
- Schema draft (Week 1)
- Server + docs update (Week 2)
- SDK alignment (Week 3)
