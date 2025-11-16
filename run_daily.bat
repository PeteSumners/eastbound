@echo off
REM Daily automation script for Windows Task Scheduler
REM Run this at 6:00 AM daily

cd /d "%~dp0"
python automate.py >> logs\automation.log 2>&1
