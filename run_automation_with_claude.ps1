# External Automation Script - Calls Claude Code from OUTSIDE Claude Code
# This runs as a scheduled task and can invoke the claude CLI successfully

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  EASTBOUND AUTOMATION - EXTERNAL RUNNER" -ForegroundColor Cyan
Write-Host "  Calling Claude Code from external PowerShell process" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$Date = Get-Date -Format "yyyy-MM-dd"
$BriefingPath = "research/$Date-briefing.json"
$DraftPath = "content/drafts/$Date-analysis.md"

# NO CACHING - Always run full pipeline
Write-Host "[INFO] Running media monitoring..." -ForegroundColor Yellow

# Run Steps 1-3: Media monitoring, global knowledge crawling, and visualizations
python scripts/monitor_russian_media.py --output $BriefingPath --parallel
python scripts/monitor_global_sources.py --regions all --categories news,research,theology --workers 10 --output knowledge_base
python scripts/generate_visuals.py --briefing $BriefingPath --output images/

# NO CACHING - Always regenerate draft
Write-Host "[INFO] Generating content using Anthropic API..." -ForegroundColor Cyan

# Delete existing draft if present (no caching)
if (Test-Path $DraftPath) {
    Write-Host "[INFO] Removing cached draft: $DraftPath" -ForegroundColor Yellow
    Remove-Item $DraftPath -Force
}

# Use Anthropic API to generate draft (non-interactive)
python scripts/generate_ai_draft.py --briefing $BriefingPath --output $DraftPath

# Verify draft was created
if (Test-Path $DraftPath) {
    Write-Host "`n[OK] Draft created successfully: $DraftPath" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] Draft generation failed" -ForegroundColor Red
    Write-Host "[INFO] Check that ANTHROPIC_API_KEY is set in .env file" -ForegroundColor Yellow
    exit 1
}

# Continue with rest of automation
Write-Host "`n[INFO] Continuing with automation pipeline..." -ForegroundColor Cyan

# Run Python automation (which will skip content generation since draft exists)
python scripts/run_daily_automation.py --skip-visuals

# Verify GitHub Pages deployment
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  VERIFYING GITHUB PAGES DEPLOYMENT" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

python scripts/verify_publish.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================================" -ForegroundColor Green
    Write-Host "  AUTOMATION COMPLETE - ARTICLE VERIFIED LIVE" -ForegroundColor Green
    Write-Host "============================================================`n" -ForegroundColor Green
} else {
    Write-Host "`n============================================================" -ForegroundColor Red
    Write-Host "  AUTOMATION COMPLETE - VERIFICATION FAILED" -ForegroundColor Red
    Write-Host "  Article may not be accessible on GitHub Pages" -ForegroundColor Red
    Write-Host "============================================================`n" -ForegroundColor Red
    exit 1
}
