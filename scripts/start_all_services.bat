@echo off
echo 🚀 Starting ATDF + MCP + n8n Integration Services
echo ================================================

REM Check if we're in the correct directory
if not exist "examples\fastapi_mcp_integration.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo 📃 Starting services in sequence...
echo.

REM Start ATDF Server
echo 🔧 Starting ATDF Server on port 8000...
start "ATDF Server" cmd /k "python -m examples.fastapi_mcp_integration"
timeout /t 5 /nobreak >nul

REM Start MCP Bridge
echo 🌐 Starting MCP Bridge on port 8001...
start "MCP Bridge" cmd /k "python examples/mcp_atdf_bridge.py --port 8001 --atdf-server http://localhost:8000"
timeout /t 3 /nobreak >nul

REM Start ATDF Selector
echo 🔎 Starting ATDF Selector on port 8050...
start "ATDF Selector" cmd /k "set PYTHONPATH=%CD% && set ATDF_MCP_TOOLS_URL=http://localhost:8001/tools && set ATDF_SELECTOR_DB=%CD%\selector_workflow.db && python -m uvicorn selector.api:app --host 127.0.0.1 --port 8050 --log-level info"
timeout /t 3 /nobreak >nul

REM Check if n8n is already running
echo 🔍 Checking if n8n is already running...
curl -s http://localhost:5678 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ n8n is already running on port 5678
) else (
    echo 📊 n8n not detected. Please start n8n manually:
    echo    npx n8n
    echo    or visit: http://localhost:5678
)

echo.
echo 🎯 Service Status Check
echo =====================

REM Wait a moment for services to start
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check ATDF Server
echo 🔧 Checking ATDF Server...
curl -s http://localhost:8000/tools >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ ATDF Server is running on http://localhost:8000
) else (
    echo ❌ ATDF Server is not responding
)

REM Check MCP Bridge
echo 🌐 Checking MCP Bridge...
curl -s http://localhost:8001/tools >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MCP Bridge is running on http://localhost:8001
) else (
    echo ❌ MCP Bridge is not responding
)

REM Check ATDF Selector
echo 🔎 Checking ATDF Selector...
curl -s http://localhost:8050/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ ATDF Selector is running on http://localhost:8050
) else (
    echo ❌ ATDF Selector is not responding
)

REM Check n8n
echo 📊 Checking n8n...
curl -s http://localhost:5678 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ n8n is running on http://localhost:5678
) else (
    echo ❌ n8n is not responding
)

echo.
echo 🎉 Integration Setup Complete!
echo ==============================
echo.
echo 📃 Available Services:
echo   • ATDF Server:   http://localhost:8000
echo   • MCP Bridge:    http://localhost:8001
echo   • ATDF Selector: http://localhost:8050
echo   • n8n:           http://localhost:5678
echo.
echo 📁 Available Workflows:
echo   • n8n-workflows/hotel-reservation-test.json
echo   • n8n-workflows/flight-booking-test.json
echo   • n8n-workflows/complete-travel-booking.json
echo   • workflow_selector_builtin.json (CLI selector demo)
echo.
echo 📚 Documentation:
echo   • n8n-workflows/README.md
echo   • estado_final_integracion.md
echo.
echo Press any key to exit...
pause >nul