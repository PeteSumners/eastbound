# SIMPLE AUTOMATION - Russian News Analysis Only
# No SDXL, no database, no research crawling - just news and analysis

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  EASTBOUND SIMPLE AUTOMATION" -ForegroundColor Cyan
Write-Host "  Russian News → Analysis → Publish" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$Date = Get-Date -Format "yyyy-MM-dd"
$BriefingPath = "research/$Date-briefing.json"
$DraftPath = "_posts/$Date-analysis.md"

# Step 1: Monitor Russian media
Write-Host "[1/3] Monitoring Russian media sources..." -ForegroundColor Yellow
python scripts/monitor_russian_media.py --output $BriefingPath --parallel

if (-not (Test-Path $BriefingPath)) {
    Write-Host "[ERROR] Briefing generation failed" -ForegroundColor Red
    exit 1
}

# Step 2: Generate analysis using Anthropic API
Write-Host "`n[2/3] Generating analysis with AI..." -ForegroundColor Yellow
python scripts/generate_simple_analysis.py --briefing $BriefingPath --output $DraftPath

if (-not (Test-Path $DraftPath)) {
    Write-Host "[ERROR] Analysis generation failed" -ForegroundColor Red
    exit 1
}

# Step 3: Commit and push
Write-Host "`n[3/3] Publishing to GitHub..." -ForegroundColor Yellow
git add research/ _posts/
git commit -m "Daily analysis: $Date [automated]

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  AUTOMATION COMPLETE!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green
Write-Host "Published: $DraftPath" -ForegroundColor Green
Write-Host "View at: https://petesumners.github.io/eastbound/" -ForegroundColor Cyan
