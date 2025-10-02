# ATDF + MCP Selector Automation – Requirements

## Context
- **Project**: Agent Tool Description Format (ATDF) Enhancement via BMAD-METHOD
- **Sprint Focus**: Operational automation for selector-enabled workflows
- **Stakeholders**: Platform engineering, workflow automation (n8n), QA

## Business Goals
1. Reducir la intervención manual para iniciar/detener la pila ATDF + MCP + Selector.
2. Proveer evidencias de QA alineadas con los flujos `atdf-enhancement` y `tool-integration`.
3. Mantener la documentación sincronizada para equipos BMAD (agentes Analyst, PM, QA).

## Functional Requirements
- **R1**: Scripts multiplataforma deben iniciar los servicios ATDF Server, MCP Bridge y Selector con health checks.
- **R2**: Scripts de parada deben cerrar servicios de forma segura usando PIDs o puertos.
- **R3**: Documentación principal (estado_final_integracion.md, README y docs/tool_selector.md) debe reflejar los nuevos entry points.
- **R4**: Entregables de requisitos, historias de usuario y criterios de aceptación deben existir en el repo para desbloquear la fase Planning del workflow BMAD `atdf-enhancement`.
- **R5**: Entregables de QA (suites, reportes y resultados) deben documentar la cobertura mínima (90%) y pruebas clave sobre el selector HTTP.

## Non-Functional Requirements
- **NFR1**: Solución sin prompts interactivos; ejecución headless desde CI.
- **NFR2**: Scripts deben funcionar en Windows PowerShell/BAT y Linux/macOS Bash.
- **NFR3**: Documentos deben residir bajo `bmad/deliverables` para trazabilidad.
- **NFR4**: Notación en español para cumplir con la guía operativa del repositorio.

## Assumptions
- n8n ya está instalado o corriendo de forma independiente.
- Servicios ATDF/MCP/Selector se ejecutan en localhost (puertos 8000, 8001, 8050, 5678).
- Usuarios tienen Python 3.10+ y PowerShell 7+ (para scripts `.ps1`).

## Constraints
- Mantener compatibilidad con scripts existentes (`integration:full`, `bridge:start`).
- No se modifican workflows n8n fuera de la importación proporcionada.
- Repositorio opera sin entorno virtual forzado (scripts no activan `.venv`).

## Deliverables (Planning)
- `requirements_document.md`
- `user_stories.yml`
- `acceptance_criteria.json`

## Deliverables (QA)
- Suites y reportes descritos en la fase Testing del workflow BMAD.

## Approval
- **PM/Analyst**: Responsable de validar requisitos y user stories.
- **QA**: Confirma que la documentación cubre métricas y escenarios críticos.
- **ATDF Specialist**: Verifica alineación con el roadmap ATDF 2.x.
