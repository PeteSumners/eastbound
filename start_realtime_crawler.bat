@echo off
REM Start Real-Time Knowledge Crawler
REM Double-click to run, or execute from command line

cd /d "%~dp0"

echo ============================================================
echo   REAL-TIME GLOBAL KNOWLEDGE CRAWLER
echo   Monitoring worldwide sources continuously
echo ============================================================
echo.
echo This will run in the foreground. Press Ctrl+C to stop.
echo.
pause

REM Run in foreground so you can see output
python scripts\monitor_global_sources.py --mode realtime --interval 5 --regions all --categories news,research --workers 10

pause
