#!/bin/bash

set -u

echo "Stopping ATDF + MCP + n8n integration services"
echo "=============================================="

stop_service_by_pid() {
    local name=$1
    local pid_file=$2

    if [ -f "${pid_file}" ]; then
        local pid
        pid=$(cat "${pid_file}")
        echo "Stopping ${name} (PID ${pid})"
        if kill -0 "${pid}" >/dev/null 2>&1; then
            kill "${pid}" >/dev/null 2>&1
            sleep 2
            if kill -0 "${pid}" >/dev/null 2>&1; then
                echo "Force killing ${name}"
                kill -9 "${pid}" >/dev/null 2>&1
            fi
            echo "${name} stopped"
        else
            echo "${name} was not running"
        fi
        rm -f "${pid_file}"
    else
        echo "No PID file for ${name}"
    fi
}

stop_service_by_port() {
    local name=$1
    local port=$2

    echo "Checking ${name} on port ${port}"
    if command -v lsof >/dev/null 2>&1; then
        local pid
        pid=$(lsof -ti :"${port}")
        if [ -n "${pid}" ]; then
            echo "Stopping ${name} (PID ${pid})"
            kill "${pid}" >/dev/null 2>&1
            sleep 2
            if kill -0 "${pid}" >/dev/null 2>&1; then
                echo "Force killing ${name}"
                kill -9 "${pid}" >/dev/null 2>&1
            fi
            echo "${name} stopped"
        else
            echo "${name} not running on port ${port}"
        fi
    else
        echo "lsof not available – cannot stop ${name} by port"
    fi
}

stop_service_by_pid "ATDF server" ".atdf_server.pid"
stop_service_by_pid "MCP bridge" ".mcp_bridge.pid"
stop_service_by_pid "ATDF selector" ".selector.pid"

echo

echo "Checking for remaining services by port"
stop_service_by_port "ATDF server" "8000"
stop_service_by_port "MCP bridge" "8001"
stop_service_by_port "ATDF selector" "8050"

echo

echo "If n8n was started manually (port 5678) stop it from its terminal or service manager"

echo

echo "Service cleanup completed"