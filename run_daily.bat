@echo off
REM ========================================================================
REM EASTBOUND DAILY AUTOMATION - Windows Task Scheduler Entry Point
REM ========================================================================
REM This script is triggered by Windows Task Scheduler
REM It runs the Python automation with extensive debugging
REM All output goes to LAST_RUN.log in the project root for easy debugging
REM ========================================================================

REM Change to script directory
cd /d "%~dp0"

REM Log start
echo ======================================================================== > LAST_RUN.log
echo EASTBOUND AUTOMATION RUN >> LAST_RUN.log
echo ======================================================================== >> LAST_RUN.log
echo Start Time: %DATE% %TIME% >> LAST_RUN.log
echo Working Directory: %CD% >> LAST_RUN.log
echo User: %USERNAME% >> LAST_RUN.log
echo ======================================================================== >> LAST_RUN.log
echo. >> LAST_RUN.log

REM Run Python automation from src/ directory
echo Running automation script... >> LAST_RUN.log
python src\automate.py >> LAST_RUN.log 2>&1

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

REM Log completion
echo. >> LAST_RUN.log
echo ======================================================================== >> LAST_RUN.log
echo End Time: %DATE% %TIME% >> LAST_RUN.log
echo Exit Code: %EXIT_CODE% >> LAST_RUN.log
echo ======================================================================== >> LAST_RUN.log

REM Also append to logs\automation.log for history
type LAST_RUN.log >> logs\automation.log

REM Exit with the Python script's exit code
exit /b %EXIT_CODE%
