# PowerShell script to set up Windows Task Scheduler for daily automation
# Run this as Administrator

$TaskName = "Eastbound Daily Automation"
$TaskDescription = "Runs daily content generation for Eastbound using local SDXL and Claude Code (external runner)"
$ScriptPath = Join-Path $PSScriptRoot "run_automation_with_claude.ps1"
$WorkingDirectory = $PSScriptRoot

# Set the time to run (8 AM daily)
$TriggerTime = "08:00"

Write-Host "Setting up Windows Task Scheduler..." -ForegroundColor Green
Write-Host "Task Name: $TaskName"
Write-Host "Script: $ScriptPath"
Write-Host "Time: $TriggerTime daily"
Write-Host ""

# Create the scheduled task action (PowerShell script runner)
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`"" -WorkingDirectory $WorkingDirectory

# Create the trigger (daily at 8 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime

# Create the principal (run whether user is logged on or not)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# Register the task
try {
    # Remove existing task if it exists
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

    # Register new task
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $TaskDescription `
        -Action $Action `
        -Trigger $Trigger `
        -Principal $Principal `
        -Settings $Settings

    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The automation will run daily at $TriggerTime" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To modify the schedule:" -ForegroundColor Yellow
    Write-Host "1. Open Task Scheduler (taskschd.msc)"
    Write-Host "2. Find '$TaskName' in the task list"
    Write-Host "3. Right-click > Properties to modify"
    Write-Host ""
    Write-Host "To test now:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "To disable:" -ForegroundColor Yellow
    Write-Host "  Disable-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""

} catch {
    Write-Host "Error creating task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you run this script as Administrator!" -ForegroundColor Yellow
}
