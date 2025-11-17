param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = (Resolve-Path (Join-Path $scriptRoot '..')).Path

$pidMap = [ordered]@{
    'ATDF server'   = '.atdf_server.pid'
    'MCP bridge'    = '.mcp_bridge.pid'
    'ATDF selector' = '.selector.pid'
}

function Remove-PidFile {
    param([string]$File)
    if (Test-Path $File) { Remove-Item $File -ErrorAction SilentlyContinue }
}

function Stop-ServiceWithPid {
    param([string]$Name, [string]$PidFile)

    $path = Join-Path $root $PidFile
    if (-not (Test-Path $path)) {
        Write-Host "No PID file for $Name" -ForegroundColor Yellow
        return $false
    }

    $servicePid = (Get-Content $path | Select-Object -First 1)
    if (-not $servicePid) {
        Write-Host "PID file for $Name is empty" -ForegroundColor Yellow
        Remove-PidFile $path
        return $false
    }

    $process = Get-Process -Id $servicePid -ErrorAction SilentlyContinue
    if (-not $process) {
        Write-Host "$Name (PID $servicePid) not running" -ForegroundColor Yellow
        Remove-PidFile $path
        return $false
    }

    Write-Host "Stopping $Name (PID $servicePid)" -ForegroundColor Cyan
    try {
        Stop-Process -Id $servicePid -Force:$Force.IsPresent -ErrorAction Stop
        Write-Host "$Name stopped" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to stop $Name (PID $servicePid). $_" -ForegroundColor Red
        return $false
    }

    Remove-PidFile $path
    return $true
}

function Stop-ServiceByPort {
    param([string]$Name, [int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        Write-Host "$Name not listening on port $Port" -ForegroundColor Yellow
        return
    }

    $owningPids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($owningPid in $owningPids) {
        if ($owningPid -eq $PID) { continue }
        Write-Host "Stopping $Name process on port $Port (PID $owningPid)" -ForegroundColor Cyan
        try {
            Stop-Process -Id $owningPid -Force:$Force.IsPresent -ErrorAction Stop
            Write-Host "$Name (PID $owningPid) stopped" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to stop $Name (PID $owningPid). $_" -ForegroundColor Red
        }
    }
}

Write-Host "Stopping ATDF + MCP + n8n services" -ForegroundColor Cyan
Write-Host "================================="

$anyStopped = $false
foreach ($entry in $pidMap.GetEnumerator()) {
    if (Stop-ServiceWithPid -Name $entry.Key -PidFile $entry.Value) {
        $anyStopped = $true
    }
}

if (-not $anyStopped) {
    Write-Host "Attempting port-based shutdown" -ForegroundColor Cyan
    Stop-ServiceByPort -Name 'ATDF server' -Port 8000
    Stop-ServiceByPort -Name 'MCP bridge' -Port 8001
    Stop-ServiceByPort -Name 'ATDF selector' -Port 8050
}
else {
    # Remove lingering PID files in case services spawned new pids we killed by port later
    foreach ($entry in $pidMap.GetEnumerator()) {
        Remove-PidFile (Join-Path $root $entry.Value)
    }
}

Write-Host "Cleanup complete." -ForegroundColor Cyan