#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Starting ATDF + MCP + n8n integration services"
echo "==============================================="

if [[ ! -f examples/fastapi_mcp_integration.py ]]; then
  echo "Error: please run this script from the project root directory" >&2
  echo "Current directory: $(pwd)" >&2
  exit 1
fi

declare -A PID_FILES=(
  ["ATDF server"]=".atdf_server.pid"
  ["MCP bridge"]=".mcp_bridge.pid"
  ["ATDF selector"]=".selector.pid"
)

check_port() {
  local port=$1
  if command -v lsof >/dev/null 2>&1; then
    lsof -i:"${port}" >/dev/null 2>&1
  elif command -v ss >/dev/null 2>&1; then
    ss -ltnp "sport = :${port}" >/dev/null 2>&1
  elif command -v netstat >/dev/null 2>&1; then
    netstat -ln | grep -q ":${port} "
  else
    timeout 1 bash -c "</dev/tcp/127.0.0.1/${port}" >/dev/null 2>&1 || return 1
    return 0
  fi
}

save_pid() {
  local name=$1 pid=$2
  local file="${PID_FILES[$name]}"
  printf '%s\n' "$pid" >"$file"
}

start_service() {
  local name=$1 delay=$2
  shift 2

  if [[ -f ${PID_FILES[$name]} ]] && kill -0 "$(cat "${PID_FILES[$name]}")" 2>/dev/null; then
    echo "$name already running (PID $(cat "${PID_FILES[$name]}"))."
    return
  fi

  echo "Starting $name..."
  "$@" &
  local pid=$!
  save_pid "$name" "$pid"
  echo "$name PID: $pid"
  sleep "$delay"
}

ROOT_ENV=(
  "PYTHONPATH=$ROOT_DIR"
  "ATDF_MCP_TOOLS_URL=http://localhost:8001/tools"
  "ATDF_SELECTOR_DB=$ROOT_DIR/selector_workflow.db"
)

start_service "ATDF server" 5 env "${ROOT_ENV[@]}" python -m examples.fastapi_mcp_integration
start_service "MCP bridge" 3 env "${ROOT_ENV[@]}" python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000
start_service "ATDF selector" 3 env "${ROOT_ENV[@]}" python -m uvicorn selector.api:app --host 127.0.0.1 --port 8050 --log-level info

echo "Checking n8n on port 5678..."
if check_port 5678; then
  echo "n8n already running"
else
  echo "n8n not detected - start manually with 'npx n8n'"
fi

echo

echo "Waiting for services to initialise..."
sleep 10

check_service() {
  local name=$1 url=$2
  if curl -fsS "$url" >/dev/null 2>&1; then
    echo "$name responding ($url)"
  else
    echo "$name not responding ($url)"
  fi
}

check_service "ATDF server" "http://localhost:8000/tools"
check_service "MCP bridge" "http://localhost:8001/tools"
check_service "ATDF selector" "http://localhost:8050/health"
check_service "n8n" "http://localhost:5678"

echo

echo "Services available:"
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

echo "To stop services use: scripts/stop_all_services.sh"

echo "Services are running in the background. Use scripts/stop_all_services.sh when finished."
