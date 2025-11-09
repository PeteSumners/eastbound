@echo off
REM Daily Automation Runner for Windows Task Scheduler
REM This batch file runs the daily automation script
REM API keys are loaded from .env file (not committed to git)

cd /d "%~dp0"

REM Run the automation script
python scripts\run_daily_automation.py

REM Log completion
echo Automation completed at %date% %time% >> automation.log

pause
