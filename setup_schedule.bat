@echo off
REM Setup Windows Task Scheduler for Eastbound Daily Automation
REM This creates a scheduled task that runs every day at 6:00 AM

echo ========================================
echo Setting up Eastbound Daily Automation
echo ========================================
echo.

REM Get the current directory
set "SCRIPT_DIR=%~dp0"

REM Create scheduled task
schtasks /create ^
    /tn "Eastbound Daily Automation" ^
    /tr "\"%SCRIPT_DIR%run_daily_automation.bat\"" ^
    /sc daily ^
    /st 08:00 ^
    /rl highest ^
    /f

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task created!
    echo.
    echo Task name: Eastbound Daily Automation
    echo Schedule: Every day at 8:00 AM
    echo Script: %SCRIPT_DIR%run_daily_automation.bat
    echo.
    echo To view the task:
    echo   schtasks /query /tn "Eastbound Daily Automation" /v /fo LIST
    echo.
    echo To run it manually now:
    echo   schtasks /run /tn "Eastbound Daily Automation"
    echo.
    echo To delete the task:
    echo   schtasks /delete /tn "Eastbound Daily Automation" /f
    echo.
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
    echo Make sure you run this as Administrator
    echo.
)

pause
