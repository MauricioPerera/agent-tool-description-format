#!/bin/bash
cd "$(dirname "$0")/examples"
uvicorn fastapi_mcp_integration:app --port 8000 --no-reload 