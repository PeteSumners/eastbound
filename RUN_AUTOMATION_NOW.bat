@echo off
REM ============================================================
REM   EASTBOUND AUTOMATION - MANUAL RUN WITH PROGRESS
REM ============================================================
REM
REM Double-click this file to run automation with live progress.
REM Console window stays open so you can see real-time updates.
REM
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo   EASTBOUND DAILY AUTOMATION - MANUAL RUN
echo ============================================================
echo.
echo This will run the complete automation pipeline:
echo   1. Monitor Russian media (15-30s)
echo   2. Generate SDXL image (8-10 minutes with progress bar)
echo   3. Generate visualizations (10s)
echo   4. Generate AI content (30-60s)
echo   5. Commit and push to GitHub (10s)
echo.
echo Mode: DRAFT-ONLY (review before publishing)
echo.
echo Press Ctrl+C to cancel or
pause

echo.
echo ============================================================
echo Starting automation...
echo Start time: %date% %time%
echo ============================================================
echo.

REM Run with verbose output for real-time progress
python scripts\run_daily_automation.py --draft-only --verbose

echo.
echo ============================================================
echo Automation completed!
echo End time: %date% %time%
echo ============================================================
echo.
echo Check content/drafts/ for the generated article.
echo.

pause
