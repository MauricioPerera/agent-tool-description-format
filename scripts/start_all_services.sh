#!/bin/bash

echo "🚀 Starting ATDF + MCP + n8n Integration Services"
echo "================================================"

# Check if we're in the correct directory
if [ ! -f "examples/fastapi_mcp_integration.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "📃 Starting services in sequence..."
echo

# Function to check if a port is in use
check_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :$port >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ln | grep ":$port " >/dev/null 2>&1
    else
        # Fallback: try to connect
        timeout 1 bash -c "echo >/dev/tcp/localhost/$port" >/dev/null 2>&1
    fi
}

ROOT_DIR="$(pwd)"
SELECTOR_DB="$ROOT_DIR/selector_workflow.db"
MCP_TOOLS_URL="http://localhost:8001/tools"

# Start ATDF Server
echo "🔧 Starting ATDF Server on port 8000..."
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Skipping ATDF Server startup."
else
    python -m examples.fastapi_mcp_integration &
    ATDF_PID=$!
    echo "   Started with PID: $ATDF_PID"
    sleep 5
fi

# Start MCP Bridge
echo "🌐 Starting MCP Bridge on port 8001..."
if check_port 8001; then
    echo "⚠️  Port 8001 is already in use. Skipping MCP Bridge startup."
else
    python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000 &
    MCP_PID=$!
    echo "   Started with PID: $MCP_PID"
    sleep 3
fi

# Start Selector API
echo "🔎 Starting ATDF Selector on port 8050..."
if check_port 8050; then
    echo "⚠️  Port 8050 is already in use. Skipping Selector startup."
else
    PYTHONPATH="$ROOT_DIR" ATDF_MCP_TOOLS_URL="$MCP_TOOLS_URL" ATDF_SELECTOR_DB="$SELECTOR_DB" \
        python -m uvicorn selector.api:app --host 127.0.0.1 --port 8050 --log-level info &
    SELECTOR_PID=$!
    echo "   Started with PID: $SELECTOR_PID"
    sleep 3
fi

# Check if n8n is already running
echo "🔍 Checking if n8n is already running..."
if check_port 5678; then
    echo "✅ n8n is already running on port 5678"
else
    echo "📊 n8n not detected. Please start n8n manually:"
    echo "   npx n8n"
    echo "   or visit: http://localhost:5678"
fi

echo
echo "🎯 Service Status Check"
echo "====================="

# Wait a moment for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 10

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    echo "🔍 Checking $name..."
    if curl -s "$url" >/dev/null 2>&1; then
        echo "✅ $name is running on $url"
        return 0
    else
        echo "❌ $name is not responding"
        return 1
    fi
}

# Check all services
check_service "ATDF Server" "http://localhost:8000/tools"
check_service "MCP Bridge" "http://localhost:8001/tools"
check_service "ATDF Selector" "http://localhost:8050/health"
check_service "n8n" "http://localhost:5678"

echo
echo "🎉 Integration Setup Complete!"
echo "=============================="
echo
echo "📃 Available Services:"
echo "  • ATDF Server:   http://localhost:8000"
echo "  • MCP Bridge:    http://localhost:8001"
echo "  • ATDF Selector: http://localhost:8050"
echo "  • n8n:           http://localhost:5678"
echo
echo "📁 Available Workflows:"
echo "  • n8n-workflows/hotel-reservation-test.json"
echo "  • n8n-workflows/flight-booking-test.json"
echo "  • n8n-workflows/complete-travel-booking.json"
echo "  • workflow_selector_builtin.json (CLI selector demo)"
echo
echo "📚 Documentation:"
echo "  • n8n-workflows/README.md"
echo "  • estado_final_integracion.md"
echo
echo "🛑 To stop all services, run: scripts/stop_all_services.sh"
echo

# Save PIDs for later cleanup
if [ ! -z "$ATDF_PID" ]; then
    echo $ATDF_PID > .atdf_server.pid
fi
if [ ! -z "$MCP_PID" ]; then
    echo $MCP_PID > .mcp_bridge.pid
fi
if [ ! -z "$SELECTOR_PID" ]; then
    echo $SELECTOR_PID > .selector.pid
fi

echo "Press Ctrl+C to exit..."
wait