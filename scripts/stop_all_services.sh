#!/bin/bash

echo "🛑 Stopping ATDF + MCP + n8n Integration Services"
echo "================================================"

# Function to stop a service by PID file
stop_service_by_pid() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "🔍 Stopping $service_name (PID: $pid)..."
        
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force killing $service_name..."
                kill -9 "$pid"
            fi
            
            echo "✅ $service_name stopped"
        else
            echo "⚠️  $service_name was not running"
        fi
        
        rm -f "$pid_file"
    else
        echo "⚠️  No PID file found for $service_name"
    fi
}

# Function to stop services by port
stop_service_by_port() {
    local service_name=$1
    local port=$2
    
    echo "🔍 Looking for $service_name on port $port..."
    
    if command -v lsof >/dev/null 2>&1; then
        local pid=$(lsof -ti :$port)
        if [ ! -z "$pid" ]; then
            echo "🛑 Stopping $service_name (PID: $pid)..."
            kill "$pid" 2>/dev/null
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Force killing $service_name..."
                kill -9 "$pid" 2>/dev/null
            fi
            echo "✅ $service_name stopped"
        else
            echo "⚠️  $service_name not found on port $port"
        fi
    else
        echo "⚠️  lsof not available, cannot stop by port"
    fi
}

# Stop services by PID files first
stop_service_by_pid "ATDF Server" ".atdf_server.pid"
stop_service_by_pid "MCP Bridge" ".mcp_bridge.pid"

# Fallback: stop by port
echo
echo "🔍 Checking for remaining services by port..."
stop_service_by_port "ATDF Server" "8000"
stop_service_by_port "MCP Bridge" "8001"

# Note about n8n
echo
echo "📊 Note: n8n (port 5678) should be stopped manually if needed:"
echo "   • If started with npx: Press Ctrl+C in the terminal"
echo "   • If running as service: Use appropriate service management commands"

echo
echo "✅ Service cleanup complete!"
echo "=========================="