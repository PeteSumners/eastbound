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
python scripts/monitor_global_sources.py --regions all --categories news,research --workers 10 --output knowledge_base
python scripts/generate_visuals.py --briefing $BriefingPath --output images/

# NO CACHING - Always regenerate draft
Write-Host "[INFO] Generating content using Claude Code..." -ForegroundColor Cyan

# Delete existing draft if present (no caching)
if (Test-Path $DraftPath) {
    Write-Host "[INFO] Removing cached draft: $DraftPath" -ForegroundColor Yellow
    Remove-Item $DraftPath -Force
}

# Create prompt file for Claude Code
$PromptFile = "temp_claude_prompt_$Date.txt"

$Prompt = @"
You are a content writer for Eastbound, a Russian media analysis service.

Read the briefing file at: $BriefingPath

Generate a high-quality analysis article following the format in CLAUDE.md.

CRITICAL REQUIREMENTS:
1. Include 'layout: post' in the frontmatter (REQUIRED for Jekyll)
2. Include proper frontmatter with: title, date, author, categories, tags, excerpt, image
3. Categories must be from [Analysis, News, Translation] and ONE region [Russia, Ukraine, EasternEurope, CentralAsia, Caucasus]
4. Image path: /images/$Date-generated.png
5. NO H1 heading after frontmatter (Jekyll handles this)
6. Include AI-generated image transparency caption
7. Include Data Visualizations section
8. Include Stakeholder Perspectives section (use scripts/generate_stakeholder_personas.py)
9. Include Key Articles Referenced section
10. Save to: $DraftPath

Use the Write tool to create the file.
"@

$Prompt | Out-File -FilePath $PromptFile -Encoding UTF8

Write-Host "[DEBUG] Prompt file created: $PromptFile" -ForegroundColor Gray
Write-Host "[DEBUG] Invoking Claude Code CLI..." -ForegroundColor Gray

# Run Claude Code with the prompt
# NOTE: This works because we're calling from OUTSIDE Claude Code
try {
    $Output = Get-Content $PromptFile | claude --print --output-format text --tools Read,Write,Glob 2>&1

    Write-Host "`n[CLAUDE OUTPUT]" -ForegroundColor Cyan
    Write-Host $Output

    # Clean up prompt file
    Remove-Item $PromptFile -ErrorAction SilentlyContinue

    # Verify draft was created
    if (Test-Path $DraftPath) {
        Write-Host "`n[OK] Draft created successfully: $DraftPath" -ForegroundColor Green
    } else {
        Write-Host "`n[ERROR] Draft not found after Claude Code execution" -ForegroundColor Red
        Write-Host "[INFO] Attempting to find any new drafts..." -ForegroundColor Yellow

        $RecentDrafts = Get-ChildItem "content/drafts/*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($RecentDrafts) {
            Write-Host "[FOUND] Most recent draft: $($RecentDrafts.Name)" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] No drafts found. Manual intervention required." -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "[ERROR] Claude Code execution failed: $_" -ForegroundColor Red
    Remove-Item $PromptFile -ErrorAction SilentlyContinue
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
