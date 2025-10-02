# AEP-003: ATDF CLI Toolkit

## Status
Planned

## Owner
Tooling working group

## Problem Statement
Los usuarios deben copiar scripts para validar/convertir herramientas. Falta un CLI oficial que encapsule operaciones básicas.

## Proposal
- Crear paquete tdf-cli con comandos alidate, convert, enrich, search (mínimo 3).
- Soporte para lectura de stdin/archivos y salida en JSON/YAML.
- Publicar en PyPI/NPM según corresponda (fase 2) y documentar en README.

## Acceptance Criteria
- CLI funcional empaquetada (pip install -e .).
- Documentación de uso con ejemplos y flags.
- Pipeline CI ejecuta smoke tests del CLI.

## Dependencies
ATDF-EPIC-003.

## Milestones
- MVP comandos validate/convert (Week 2)
- Enrich/search y packaging (Week 4)
- Public release (Week 6)
