@echo off
cd /d %~dp0
cd examples
uvicorn fastapi_mcp_integration:app --port 8000 --no-reload 