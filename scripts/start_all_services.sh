#!/bin/bash

set -u

echo "Starting ATDF + MCP + n8n integration services"
echo "==============================================="

if [ ! -f "examples/fastapi_mcp_integration.py" ]; then
    echo "Error: please run this script from the project root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "Starting services in sequence..."

echo

check_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :"${port}" >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ln | grep ":${port} " >/dev/null 2>&1
    else
        timeout 1 bash -c "echo >/dev/tcp/localhost/${port}" >/dev/null 2>&1
    fi
}

ROOT_DIR="$(pwd)"
SELECTOR_DB="${ROOT_DIR}/selector_workflow.db"
MCP_TOOLS_URL="http://localhost:8001/tools"

# ATDF server
echo "Starting ATDF server on port 8000..."
if check_port 8000; then
    echo "Port 8000 already in use â€“ skipping"
else
    python -m examples.fastapi_mcp_integration &
    ATDF_PID=$!
    echo "ATDF server PID: ${ATDF_PID}"
    sleep 5
fi

# MCP bridge
echo "Starting MCP bridge on port 8001..."
if check_port 8001; then
    echo "Port 8001 already in use â€“ skipping"
else
    python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000 &
    MCP_PID=$!
    echo "MCP bridge PID: ${MCP_PID}"
    sleep 3
fi

# Selector API
echo "Starting ATDF selector on port 8050..."
if check_port 8050; then
    echo "Port 8050 already in use â€“ skipping"
else
    PYTHONPATH="${ROOT_DIR}" \
    ATDF_MCP_TOOLS_URL="${MCP_TOOLS_URL}" \
    ATDF_SELECTOR_DB="${SELECTOR_DB}" \
        python -m uvicorn selector.api:app --host 127.0.0.1 --port 8050 --log-level info &
    SELECTOR_PID=$!
    echo "Selector PID: ${SELECTOR_PID}"
    sleep 3
fi

# n8n status
echo "Checking n8n on port 5678..."
if check_port 5678; then
    echo "n8n already running"
else
    echo "n8n not detected â€“ start manually with 'npx n8n'"
fi

echo

echo "Waiting for services to initialise..."
sleep 10

check_service() {
    local name=$1
    local url=$2
    echo "Checking ${name}..."
    if curl -s "${url}" >/dev/null 2>&1; then
        echo "${name} responding at ${url}"
    else
        echo "${name} not responding"
    fi
}

check_service "ATDF server" "http://localhost:8000/tools"
check_service "MCP bridge" "http://localhost:8001/tools"
check_service "ATDF selector" "http://localhost:8050/health"
check_service "n8n" "http://localhost:5678"

echo

echo "Available services:"
echo "  - ATDF server:   http://localhost:8000"
echo "  - MCP bridge:    http://localhost:8001"
echo "  - ATDF selector: http://localhost:8050"
echo "  - n8n:           http://localhost:5678"

echo

echo "Useful workflows:"
echo "  - n8n-workflows/hotel-reservation-test.json"
echo "  - n8n-workflows/flight-booking-test.json"
echo "  - n8n-workflows/complete-travel-booking.json"
echo "  - workflow_selector_builtin.json"

echo

echo "Documentation:"
echo "  - n8n-workflows/README.md"
echo "  - estado_final_integracion.md"

echo

echo "To stop services run: scripts/stop_all_services.sh"

if [ -n "${ATDF_PID:-}" ]; then
    echo "${ATDF_PID}" > .atdf_server.pid
fi
if [ -n "${MCP_PID:-}" ]; then
    echo "${MCP_PID}" > .mcp_bridge.pid
fi
if [ -n "${SELECTOR_PID:-}" ]; then
    echo "${SELECTOR_PID}" > .selector.pid
fi

echo "Press Ctrl+C to exit"
wait