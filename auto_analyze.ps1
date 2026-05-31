# Stock Analysis Auto Script
# Runs daily at 17:00, analyzes stocks and deploys to GitHub Pages

param(
    [switch]$Setup,
    [switch]$RunNow,
    [switch]$Remove,
    [switch]$Help
)

# Configuration
$ScriptPath = $PSScriptRoot
$PythonScript = Join-Path $ScriptPath "daily_analyze_stock.py"
$LogDir = Join-Path $ScriptPath "logs"
$LogFile = Join-Path $LogDir "$(Get-Date -Format 'yyyyMMdd')_ps.log"

# Create log directory if not exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Log function
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
}

# Run stock analysis
function Invoke-StockAnalysis {
    Write-Log "Starting stock analysis..."
    try {
        Set-Location $ScriptPath
        python $PythonScript --today
        Write-Log "Stock analysis completed"
        return $true
    }
    catch {
        Write-Log "Stock analysis failed: $($_.Exception.Message)"
        return $false
    }
}

# Deploy to GitHub Pages
function Deploy-ToGitHubPages {
    Write-Log "Deploying to GitHub Pages..."
    try {
        Set-Location $ScriptPath
        mkdocs gh-deploy --force
        Write-Log "Deployment completed"
        return $true
    }
    catch {
        Write-Log "Deployment failed: $($_.Exception.Message)"
        return $false
    }
}

# Main task
function Invoke-MainTask {
    Write-Log "========================================"
    Write-Log "Auto task started"
    
    try {
        $AnalysisSuccess = Invoke-StockAnalysis
        
        if ($AnalysisSuccess) {
            Deploy-ToGitHubPages
        }
    }
    catch {
        Write-Log "Error: $($_.Exception.Message)"
    }
    
    Write-Log "Auto task finished"
    Write-Log "========================================"
    Write-Log ""
}

# Setup scheduled task
function Set-ScheduledTask {
    param([string]$TaskName = "StockAutoAnalysis")
    
    $TaskExists = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if ($TaskExists) {
        Write-Log "Task '$TaskName' exists, removing old task..."
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -RunNow"
    $Trigger = New-ScheduledTaskTrigger -Daily -At 5:00PM
    $Settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest -Force | Out-Null
    
    Write-Log "Scheduled task '$TaskName' created, runs daily at 17:00"
    Write-Log "Note: Task configured to wake computer to run"
}

# Show help
function Show-Help {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Stock Analysis Auto Script" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\auto_analyze.ps1 -Setup     # Create scheduled task (Run as Admin)"
    Write-Host "  .\auto_analyze.ps1 -RunNow    # Run immediately"
    Write-Host "  .\auto_analyze.ps1 -Remove    # Delete scheduled task (Run as Admin)"
    Write-Host "  .\auto_analyze.ps1 -Help      # Show help"
    Write-Host ""
    Write-Host "Features:" -ForegroundColor Yellow
    Write-Host "  - Auto runs daily at 17:00"
    Write-Host "  - Auto deploy to GitHub Pages"
    Write-Host "  - Support wake to run"
    Write-Host ""
    Write-Host "Log directory: $LogDir" -ForegroundColor Gray
    Write-Host ""
}

# Remove scheduled task
function Remove-ScheduledTaskWrapper {
    param([string]$TaskName = "StockAutoAnalysis")
    
    $TaskExists = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if ($TaskExists) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Log "Scheduled task '$TaskName' removed"
    }
    else {
        Write-Log "Task '$TaskName' does not exist"
    }
}

# ========================================
# Main entry point
# ========================================

if ($Help) {
    Show-Help
    exit
}

if ($Setup) {
    Set-ScheduledTask
    exit
}

if ($Remove) {
    Remove-ScheduledTaskWrapper
    exit
}

if ($RunNow) {
    Invoke-MainTask
    exit
}

Show-Help
