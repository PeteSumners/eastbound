# Setup Simple Daily Automation Task
# Runs at 9:50 AM daily - just Russian news + analysis

$TaskName = "Eastbound Simple Automation"
$ScriptPath = Join-Path $PSScriptRoot "run_simple_automation.ps1"

# Remove old task if exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[INFO] Removed existing task" -ForegroundColor Yellow
}

# Create action
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`"" `
    -WorkingDirectory $PSScriptRoot

# Create trigger (9:50 AM daily)
$Trigger = New-ScheduledTaskTrigger -Daily -At "09:50"

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Register task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Simple Eastbound automation: Russian news → analysis → publish"

Write-Host "`n[OK] Task scheduled successfully!" -ForegroundColor Green
Write-Host "[INFO] Daily run at 9:50 AM" -ForegroundColor Cyan
Write-Host "[INFO] Script: $ScriptPath" -ForegroundColor Gray
