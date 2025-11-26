# Eastbound Automation Schedule

## Current Schedule
**Runs weekly on Mondays at 10:00 AM local time** (displays UTC timestamps in output)

## Task Details
- **Task Name:** EastboundWeeklyAnalysis
- **Script:** run_weekly.bat
- **Scheduler:** Windows Task Scheduler
- **Settings:**
  - Runs even on battery power
  - Starts if missed (e.g., computer was off)
  - Requires network connection

## Viewing the Schedule

Open Task Scheduler:
```
taskschd.msc
```

Look for **EastboundWeeklyAnalysis** in the task list.

## Running Manually

To trigger an immediate run:
```
schtasks /run /tn EastboundWeeklyAnalysis
```

Or simply double-click `run_weekly.bat`

## Logs

All output is saved to:
- **Latest run:** `LAST_RUN.log` (overwritten each run)
- **Full history:** `logs/automation.log` (appended continuously)

## Changing the Schedule

1. **Quick change:** Re-run `setup_schedule.ps1` after editing the time on line 25:
   ```powershell
   powershell -ExecutionPolicy Bypass -File setup_schedule.ps1
   ```

2. **Manual change:** Open Task Scheduler (taskschd.msc) and modify the trigger

## Disabling the Schedule

To stop automatic runs:
```
schtasks /change /tn EastboundWeeklyAnalysis /disable
```

To delete the task entirely:
```
schtasks /delete /tn EastboundWeeklyAnalysis /f
```
