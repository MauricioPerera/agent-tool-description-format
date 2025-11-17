@echo off
REM BMAD-METHOD Installation Script for Windows
REM ATDF Project Integration Setup
REM Version: 1.0.0

echo.
echo ========================================
echo  BMAD-METHOD Installation for ATDF
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Running without administrator privileges
    echo Some operations may require elevated permissions
    echo.
)

REM Set color for better visibility
color 0A

echo [INFO] Starting BMAD-METHOD installation...
echo.

REM Check Node.js installation
echo [STEP 1/7] Checking Node.js installation...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    echo Minimum required version: 20.0.0
    pause
    exit /b 1
) else (
    echo [OK] Node.js is installed
    node --version
)
echo.

REM Check Python installation
echo [STEP 2/7] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    echo Minimum required version: 3.8.0
    pause
    exit /b 1
) else (
    echo [OK] Python is installed
    python --version
)
echo.

REM Check if package.json exists
echo [STEP 3/7] Checking project configuration...
if not exist "package.json" (
    echo [ERROR] package.json not found in current directory
    echo Please run this script from the ATDF project root directory
    pause
    exit /b 1
) else (
    echo [OK] package.json found
)

if not exist "bmad.config.yml" (
    echo [ERROR] bmad.config.yml not found
    echo Please ensure BMAD configuration is present
    pause
    exit /b 1
) else (
    echo [OK] bmad.config.yml found
)
echo.

REM Install Node.js dependencies
echo [STEP 4/7] Installing Node.js dependencies...
echo [INFO] Running npm install...
call npm install
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
) else (
    echo [OK] Node.js dependencies installed successfully
)
echo.

REM Install Python dependencies
echo [STEP 5/7] Installing Python dependencies...
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing Python requirements...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to install Python dependencies
        pause
        exit /b 1
    ) else (
        echo [OK] Python dependencies installed successfully
    )
) else (
    echo [WARNING] requirements.txt not found, skipping Python dependencies
)
echo.

REM Install BMAD-METHOD
echo [STEP 6/7] Installing BMAD-METHOD...
echo [INFO] Installing BMAD-METHOD via npm...
call npm install -g bmad-method
if %errorLevel% neq 0 (
    echo [WARNING] Global installation failed, trying local installation...
    call npm install bmad-method
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to install BMAD-METHOD
        echo Please check your npm configuration and try again
        pause
        exit /b 1
    ) else (
        echo [OK] BMAD-METHOD installed locally
    )
) else (
    echo [OK] BMAD-METHOD installed globally
)
echo.

REM Setup BMAD-ATDF Integration
echo [STEP 7/7] Setting up BMAD-ATDF Integration...
echo [INFO] Running BMAD-ATDF integration setup...

if exist "tools\bmad_atdf_integration.py" (
    python tools\bmad_atdf_integration.py
    if %errorLevel% neq 0 (
        echo [WARNING] BMAD-ATDF integration setup encountered issues
        echo Please check the logs and run manually if needed
    ) else (
        echo [OK] BMAD-ATDF integration setup completed
    )
) else (
    echo [WARNING] BMAD-ATDF integration script not found
    echo Please ensure tools\bmad_atdf_integration.py exists
)
echo.

REM Create BMAD directories if they don't exist
echo [INFO] Ensuring BMAD directory structure...
if not exist "bmad" mkdir bmad
if not exist "bmad\tools" mkdir bmad\tools
if not exist "bmad\agents" mkdir bmad\agents
if not exist "bmad\workflows" mkdir bmad\workflows
echo [OK] BMAD directory structure verified

echo.
echo ========================================
echo  BMAD-METHOD Installation Complete!
echo ========================================
echo.
echo [SUCCESS] BMAD-METHOD has been successfully installed and configured for ATDF
echo.
echo Next Steps:
echo 1. Visit https://gemini.google.com or https://chat.openai.com
echo 2. Upload the bmad-orchestrator.md file from bmad\agents\
echo 3. Start with: *help or *status
echo.
echo Available Commands:
echo   npm run bmad:update    - Update BMAD-METHOD
echo   npm run bmad:status    - Check BMAD status
echo   npm run bmad:tools     - List available tools
echo   npm run bmad:agents    - List configured agents
echo.
echo Documentation:
echo   - BMAD Configuration: bmad.config.yml
echo   - Agent Definitions: bmad\agents\
echo   - Workflow Definitions: bmad\workflows\
echo   - Tool Definitions: bmad\tools\
echo   - Project Brief: bmad\project_brief.md
echo.
echo For support and documentation:
echo   - ATDF Docs: docs\ATDF_SPECIFICATION.md
echo   - BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD
echo   - Issues: https://github.com/your-repo/agent-tool-description-format/issues
echo.

REM Check if installation was successful
if exist "bmad\bmad_status.json" (
    echo [VERIFICATION] BMAD integration status file found
    echo [INFO] Installation verification successful
) else (
    echo [WARNING] BMAD status file not found
    echo Installation may be incomplete
)

echo.
echo Press any key to exit...
pause >nul

REM Reset color
color

exit /b 0