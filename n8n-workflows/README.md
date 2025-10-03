# 📚 N8N Workflows Documentation - ATDF + MCP Integration

## 🎯 Overview

This directory contains n8n workflows that demonstrate the integration between ATDF (Agent Tool Description Format), MCP (Model Context Protocol), the ATDF Tool Selector, and the n8n automation platform.

## 🧭 Table of Contents
- Overview and Architecture
- Available Workflows
- Complete Travel Booking via ATDF-MCP (Code v3)
- Configuration Requirements
- MCP Bridge & Selector Endpoints
- Quick Start: Import and Execute

## 🔗 Quick References
- n8n REST API & Auth: `../n8n_setup_complete.md`
- Spanish quick-start guide: `../GUIA_INTEGRACION_N8N.md`

## 🏗️ Architecture

```
ATDF Server (Port 8000) → MCP Bridge (Port 8001) → ATDF Tool Selector (Port 8050) → n8n (Port 5678)
```

- **ATDF Server**: Provides tool definitions and execution capabilities.
- **MCP Bridge**: Translates between ATDF and MCP protocols.
- **ATDF Tool Selector**: Ranks tools based on natural-language queries (FastAPI service backed by SQLite catalog).
- **n8n**: Workflow automation platform that consumes MCP tools (via HTTP or native nodes).

## 📁 Available Workflows

### 1. Hotel Reservation Test (`hotel-reservation-test.json`)

**Purpose**: Test the hotel reservation tool through the ATDF-MCP integration.

**Key Features**:
- Validates MCP bridge connectivity
- Checks tool availability
- Executes hotel reservation with sample data
- Handles success/error scenarios
- Sends Slack notifications

### 2. Flight Booking Test (`flight-booking-test.json`)

**Purpose**: Test the flight booking tool through the ATDF-MCP integration.

**Key Features**:
- Validates MCP bridge connectivity
- Checks flight booking tool availability
- Executes flight booking with sample data
- Handles booking confirmation
- Sends notifications via Slack and email

### 3. Complete Travel Booking (`complete-travel-booking.json`)

**Purpose**: Demonstrate end-to-end travel booking combining both hotel and flight reservations.

**Key Features**:
- Sequential booking workflow
- Data sharing between hotel and flight bookings
- Comprehensive error handling
- Final confirmation email
- Complete travel itinerary generation

### 4. Complete Travel Booking via ATDF-MCP (Code v3) (`complete-travel-workflow-code-v3.json`)

**Purpose**: End-to-end travel booking using Code nodes that call the MCP Bridge directly.

**Key Features**:
- Uses naïve date strings to avoid timezone offset issues
- Reads input from `$json` in Code nodes
- Calls MCP Bridge via `this.helpers.httpRequest` (`POST http://localhost:8001/mcp`)
- Sequential execution: hotel then flight

**Workflow Steps**:
1. `Set Travel Data`: provides parameters such as `traveler_name`, `email`, `departure_city`, `arrival_city`, `travel_date`, `check_in`, `check_out`, `room_type`, `guests`.
2. `Book Hotel` (Code): calls `hotel_reservation` tool via MCP Bridge.
3. `Book Flight` (Code): calls `flight_booking` tool via MCP Bridge.

### 5. Hotel Booking via Selector (HTTP) (`workflow_selector_builtin.json` → workflow ID `PNvGdiK9rbvmEnKl`)

**Purpose**: Demonstrate how to consume the selector service and MCP bridge using only core n8n nodes (no custom packages).

**Key Features**:
- `HTTP Request` node posts to `http://127.0.0.1:8050/recommend`.
- Second `HTTP Request` node posts to `http://127.0.0.1:8001/mcp` using the selector response.
- `Code` node parses JSON-RPC responses into structured data.
- CLI-friendly: `n8n execute --id PNvGdiK9rbvmEnKl` (requires selector + bridge running).

## ⚙️ Configuration Requirements

- Python 3.10+ with `uvicorn`, `fastapi`, and project dependencies installed.
- Node.js 18+ with `n8n` (CLI or desktop) available.
- Services running:
  - ATDF Server on port 8000
  - MCP Bridge on port 8001
  - ATDF Selector on port 8050
  - n8n on port 5678

Scripts `../scripts/start_all_services.sh` and `../scripts/start_all_services.bat` boot the three Python services automatically and verify health endpoints.

## 🌐 MCP Bridge & Selector Endpoints

- MCP Bridge health/tool list: `http://localhost:8001/health`, `http://localhost:8001/tools`
- ATDF Selector health/recommend: `http://localhost:8050/health`, `http://localhost:8050/recommend`
- MCP RPC gateway: `http://localhost:8001/mcp`

## 🚀 Quick Start: Import and Execute

```bash
# Import workflows (example):
n8n import:workflow --input n8n-workflows/hotel-reservation-test.json

# Execute selector-driven workflow (after importing workflow_selector_builtin.json)
n8n execute --id PNvGdiK9rbvmEnKl
```

For automated startup use the scripts in `../scripts/`. For manual commands, see `../estado_final_integracion.md`.

Happy automating! 🚀

## Selector Client Quick Reference

- Scripts para servicios: `scripts/start_all_services.ps1 -StartupDelay 15` (Windows) / `./scripts/start_all_services.sh` (Linux/macOS) y sus pares `stop_all_services.*`.
- Uso sin n8n: realizar POST a `http://127.0.0.1:8050/recommend` (ver ejemplo en `docs/tool_selector.md`).
- Uso con n8n: `n8n execute --id PNvGdiK9rbvmEnKl` tras importar `workflow_selector_builtin.json`.



