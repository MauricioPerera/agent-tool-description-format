# Compatibility Report – Selector Workflow

## Platforms Evaluated
| Platform | Status | Notes |
|----------|--------|-------|
| Windows 11 (PowerShell 7.4) | ✅ | `scripts/start_all_services.ps1` funcional, wrappers BAT verificados |
| Windows 11 (PowerShell 5.1) | ⚠️ | Requiere `pwsh` (instalar PowerShell 7) |
| Ubuntu 22.04 (Bash)         | ✅ | `./scripts/start_all_services.sh` ejecuta health checks |
| macOS Ventura (zsh/bash)    | ✅ | Se requiere `lsof` (incluido por defecto) |

## Integration Highlights
- Selector responde en `http://127.0.0.1:8050/health` con `tool_count=6` tras StartupDelay 15 s.
- MCP Bridge (`http://127.0.0.1:8001/mcp`) mantiene compatibilidad JSON-RPC 2.0.
- n8n CLI (`n8n execute --id EJNFSpfWrmNxWKEo`) consume selector + bridge sin nodos personalizados.

## Known Issues
1. PowerShell 5.1 no soporta `pwsh` -> Documentado como prerequisito.
2. Scripts Bash requieren `timeout` utilitario (GNU coreutils). Añadir nota para macOS en README.

## Recommendations
- Añadir test automatizado GitHub Actions (Windows/Linux) para n8n CLI.
- Publicar snippet `curl` en README principal para verificación rápida.
- Monitorizar latencia del selector (>150 ms dispara alerta).
