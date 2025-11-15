@echo off
cd /d C:\Users\PeteS\Desktop\Eastbound
echo [BATCH] Starting automation at %date% %time% > automation_run.log
echo [BATCH] Current directory: %cd% >> automation_run.log
python scripts\run_daily_automation.py --verbose >> automation_run.log 2>&1
echo [BATCH] Finished at %date% %time% >> automation_run.log
echo [BATCH] Exit code: %errorlevel% >> automation_run.log
pause
