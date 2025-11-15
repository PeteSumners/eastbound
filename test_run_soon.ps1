# Reschedule automation to run in 2 minutes for testing
# This is the ONLY way to manually trigger runs - always use Task Scheduler

$MinutesFromNow = 2
$RunTime = (Get-Date).AddMinutes($MinutesFromNow)
$TimeString = $RunTime.ToString("HH:mm")

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  RESCHEDULING AUTOMATION FOR IMMEDIATE TEST" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "[INFO] Current time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow
Write-Host "[INFO] Scheduled run: $TimeString ($MinutesFromNow minutes from now)" -ForegroundColor Yellow
Write-Host ""

# Get the existing task
$Task = Get-ScheduledTask -TaskName "Eastbound Daily Automation"

# Create new trigger
$Trigger = New-ScheduledTaskTrigger -Once -At $RunTime

# Update the task with new trigger
Set-ScheduledTask -TaskName "Eastbound Daily Automation" -Trigger $Trigger

Write-Host "[OK] Task rescheduled successfully!" -ForegroundColor Green
Write-Host "[INFO] The automation will run at $TimeString" -ForegroundColor Cyan
Write-Host "[INFO] After testing, run setup_daily_task.ps1 to restore 9:50 AM schedule" -ForegroundColor Yellow
Write-Host ""

# Show task info
$TaskInfo = Get-ScheduledTaskInfo -TaskName "Eastbound Daily Automation"
Write-Host "Next run time: $($TaskInfo.NextRunTime)" -ForegroundColor Green
Write-Host ""
