@echo off
setlocal EnableDelayedExpansion

echo Starting ATDF + MCP + n8n integration services
echo ===============================================

echo after header

if not exist "examples\fastapi_mcp_integration.py" (
    echo Error: please run this script from the project root directory
    echo Current directory: !CD!
    pause
    exit /b 1
)

echo passed directory check

echo Starting services in sequence...

echo.

set "ROOT_DIR=%CD%"
set "SELECTOR_DB=%ROOT_DIR%\selector_workflow.db"

echo root dir is !ROOT_DIR!

echo Starting ATDF server on port 8000...
start "ATDF Server" cmd /k "python -m examples.fastapi_mcp_integration"