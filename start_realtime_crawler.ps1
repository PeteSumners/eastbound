# Start Real-Time Global Knowledge Crawler
# Runs continuously in the background, checking sources every 5 minutes

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  REAL-TIME GLOBAL KNOWLEDGE CRAWLER" -ForegroundColor Cyan
Write-Host "  Monitoring news and research sources continuously" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Configuration
$CheckInterval = 5  # minutes
$Regions = "all"    # all, or comma-separated: russian,europe,americas,asia
$Categories = "news,research"  # news, research, data

Write-Host "[CONFIG] Check interval: $CheckInterval minutes" -ForegroundColor Yellow
Write-Host "[CONFIG] Regions: $Regions" -ForegroundColor Yellow
Write-Host "[CONFIG] Categories: $Categories" -ForegroundColor Yellow
Write-Host ""

# Start crawler
Write-Host "[START] Launching real-time crawler..." -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python scripts/monitor_global_sources.py `
    --mode realtime `
    --interval $CheckInterval `
    --regions $Regions `
    --categories $Categories `
    --workers 10
