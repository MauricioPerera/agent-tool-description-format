param(
    [int]$StartupDelay = 10
)

$ErrorActionPreference = 'Stop'

function Write-Section {
    param([string]$Text)
    Write-Host "`n$Text" -ForegroundColor Cyan
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = (Resolve-Path (Join-Path $scriptRoot '..')).Path
$pythonScript = Join-Path $root 'examples\fastapi_mcp_integration.py'
if (-not (Test-Path $pythonScript)) {
    Write-Host 'Error: please run this script from the project root directory' -ForegroundColor Red
    Write-Host "Current directory: $root" -ForegroundColor Yellow
    exit 1
}

$python = (Get-Command python.exe -ErrorAction Stop).Path

$env:PYTHONPATH = $root
$env:ATDF_MCP_TOOLS_URL = 'http://localhost:8001/tools'
$env:ATDF_SELECTOR_DB = Join-Path $root 'selector_workflow.db'

$pidMap = @{ 
    'ATDF server'   = '.atdf_server.pid'
    'MCP bridge'    = '.mcp_bridge.pid'
    'ATDF selector' = '.selector.pid'
}

function Save-Pid {
    param([string]$Name, [int]$ProcessId)
    $pidFile = Join-Path $root $pidMap[$Name]
    Set-Content -Path $pidFile -Value $ProcessId -Encoding ascii
}

function Is-Running {
    param([string]$Name)
    $pidFile = Join-Path $root $pidMap[$Name]
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile | Select-Object -First 1
        if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
            return $pid
        }
        Remove-Item $pidFile -ErrorAction SilentlyContinue
    }
    return $null
}

function Start-ServiceProcess {
    param(
        [string]$Name,
        [string[]]$ArgumentList,
        [int]$DelaySeconds
    )

    $existing = Is-Running $Name
    if ($existing) {
        Write-Host "$Name already running (PID $existing)" -ForegroundColor Green
        return
    }

    $process = Start-Process -FilePath $python -ArgumentList $ArgumentList -WorkingDirectory $root -PassThru
    Save-Pid -Name $Name -ProcessId $process.Id
    Write-Host "$Name started (PID $($process.Id))" -ForegroundColor Green
    if ($DelaySeconds -gt 0) {
        Start-Sleep -Seconds $DelaySeconds
    }
}

Write-Section 'Starting ATDF + MCP + n8n integration services'

Start-ServiceProcess -Name 'ATDF server' -ArgumentList @('-m','examples.fastapi_mcp_integration') -DelaySeconds 5
Start-ServiceProcess -Name 'MCP bridge' -ArgumentList @('examples\mcp_atdf_bridge.py','--port','8001','--atdf-server','http://localhost:8000') -DelaySeconds 3
Start-ServiceProcess -Name 'ATDF selector' -ArgumentList @('-m','uvicorn','selector.api:app','--host','127.0.0.1','--port','8050','--log-level','info') -DelaySeconds 3

Write-Host 'Checking n8n on port 5678...' -NoNewline
try {
    Invoke-WebRequest -Uri 'http://localhost:5678' -TimeoutSec 3 | Out-Null
    Write-Host ' already running' -ForegroundColor Green
}
catch {
    Write-Host " not detected - start manually with 'npx n8n'" -ForegroundColor Yellow
}

if ($StartupDelay -gt 0) {
    Write-Host "Waiting $StartupDelay seconds for services to initialise..."
    Start-Sleep -Seconds $StartupDelay
}

function Test-Service {
    param([string]$Name, [string]$Url)
    try {
        Invoke-WebRequest -Uri $Url -TimeoutSec 3 | Out-Null
        Write-Host "$Name responding ($Url)" -ForegroundColor Green
    }
    catch {
        Write-Host "$Name not responding ($Url)" -ForegroundColor Yellow
    }
}

Write-Section 'Service status'
Test-Service 'ATDF server' 'http://localhost:8000/tools'
Test-Service 'MCP bridge' 'http://localhost:8001/tools'
Test-Service 'ATDF selector' 'http://localhost:8050/health'
Test-Service 'n8n UI' 'http://localhost:5678'

Write-Section 'Useful workflows'
Write-Host '  - n8n-workflows/hotel-reservation-test.json'
Write-Host '  - n8n-workflows/flight-booking-test.json'
Write-Host '  - n8n-workflows/complete-travel-booking.json'
Write-Host '  - workflow_selector_builtin.json'

Write-Section 'Documentation'
Write-Host '  - n8n-workflows/README.md'
Write-Host '  - estado_final_integracion.md'

Write-Host 'Startup complete.' -ForegroundColor Cyan
