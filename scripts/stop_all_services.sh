#!/bin/bash

echo "ðŸ›‘ Stopping ATDF + MCP + n8n Integration Services"
echo "================================================"

# Function to stop a service by PID file
stop_service_by_pid() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "ðŸ” Stopping $service_name (PID: $pid)..."
        
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "âš ï¸  Force killing $service_name..."
                kill -9 "$pid"
            fi
            
            echo "âœ… $service_name stopped"
        else
            echo "âš ï¸  $service_name was not running"
        fi
        
        rm -f "$pid_file"
    else
        echo "âš ï¸  No PID file found for $service_name"
    fi
}

# Function to stop services by port
stop_service_by_port() {
    local service_name=$1
    local port=$2
    
    echo "ðŸ” Looking for $service_name on port $port..."
    
    if command -v lsof >/dev/null 2>&1; then
        local pid=$(lsof -ti :$port)
        if [ ! -z "$pid" ]; then
            echo "ðŸ›‘ Stopping $service_name (PID: $pid)..."
            kill "$pid" 2>/dev/null
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "âš ï¸  Force killing $service_name..."
                kill -9 "$pid" 2>/dev/null
            fi
            echo "âœ… $service_name stopped"
        else
            echo "âš ï¸  $service_name not found on port $port"
        fi
    else
        echo "âš ï¸  lsof not available, cannot stop by port"
    fi
}

# Stop services by PID files first
stop_service_by_pid "ATDF Server" ".atdf_server.pid"
stop_service_by_pid "MCP Bridge" ".mcp_bridge.pid"
stop_service_by_pid "ATDF Selector" ".selector.pid"

# Fallback: stop by port
echo
echo "ðŸ” Checking for remaining services by port..."
stop_service_by_port "ATDF Server" "8000"
stop_service_by_port "MCP Bridge" "8001"
stop_service_by_port "ATDF Selector" "8050"

# Note about n8n
echo
echo "ðŸ“Š Note: n8n (port 5678) should be stopped manually if needed:"
echo "   â€¢ If started with npx: Press Ctrl+C in the terminal"
echo "   â€¢ If running as service: Use appropriate service management commands"

echo
echo "âœ… Service cleanup complete!"
echo "=========================="