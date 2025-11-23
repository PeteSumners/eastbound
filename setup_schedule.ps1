# Eastbound Daily Analysis - Task Scheduler Setup
# Schedules the automation to run at 10:00 AM every day (local time)

$TaskName = "EastboundDailyAnalysis"
$ScriptPath = Join-Path $PSScriptRoot "run_daily.bat"
$WorkingDir = $PSScriptRoot

Write-Host "Setting up daily schedule for Eastbound Financial Analysis..."
Write-Host "Task Name: $TaskName"
Write-Host "Script: $ScriptPath"
Write-Host "Schedule: Daily at 10:00 AM (local time)"
Write-Host ""

# Delete existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDir

# Create the trigger (daily at 10:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At "10:00AM"

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Eastbound Financial Analysis - Daily automated run at 10:00 AM" `
    -User $env:USERNAME

Write-Host ""
Write-Host "Task scheduled successfully!"
Write-Host ""
Write-Host "Task Details:"
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, Triggers

Write-Host ""
Write-Host "To view or modify the task:"
Write-Host "  1. Open Task Scheduler (taskschd.msc)"
Write-Host "  2. Look for the task in the list"
Write-Host ""
Write-Host "To run manually: schtasks /run /tn $TaskName"
Write-Host ""
