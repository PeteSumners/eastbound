# Schedule test run in 2 minutes

$TaskName = 'Eastbound Simple Automation'
$RunTime = (Get-Date).AddMinutes(2)
$TimeString = $RunTime.ToString('HH:mm')

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  SCHEDULING TEST RUN" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$Trigger = New-ScheduledTaskTrigger -Once -At $RunTime
Set-ScheduledTask -TaskName $TaskName -Trigger $Trigger

Write-Host "[OK] Task scheduled for $TimeString" -ForegroundColor Green
Write-Host "[INFO] Current time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow

$TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
Write-Host "[INFO] Next run: $($TaskInfo.NextRunTime)" -ForegroundColor Cyan
Write-Host ""
