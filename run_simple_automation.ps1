# SIMPLE AUTOMATION - Russian News Analysis Only
# Uses Claude Code CLI (free!) - no API keys needed

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  EASTBOUND SIMPLE AUTOMATION" -ForegroundColor Cyan
Write-Host "  Russian News → Claude Code → Publish" -ForegroundColor Cyan
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

# Step 2: Generate analysis using Claude Code CLI
Write-Host "`n[2/3] Generating analysis with Claude Code..." -ForegroundColor Yellow

# Create prompt for Claude Code
$Prompt = @"
You are a professional journalist analyzing Russian media coverage.

Read the briefing file at: $BriefingPath

Generate a concise, unbiased analysis article following this EXACT format:

---
layout: post
title: "[Create compelling title based on main story]"
date: $Date
author: Eastbound Analysis
categories: [Analysis, Russia]
tags: [key, topics, from, briefing]
excerpt: "One-sentence summary of main story"
---

## Overview

[2-3 paragraphs: What are Russian media sources reporting today? What's the main narrative?]

## Key Stories

### [Story 1 Title]
[What Russian sources are saying, with specific quotes and links]

### [Story 2 Title]
[What Russian sources are saying, with specific quotes and links]

### [Story 3 Title - if relevant]
[What Russian sources are saying, with specific quotes and links]

## Context

[What might Western audiences not understand about this coverage?]

## Analysis

[What does this tell us about Russian priorities, concerns, or narratives right now?]

---

CRITICAL REQUIREMENTS:
1. Be factual and unbiased - report what Russian media is saying
2. Use direct quotes from the briefing articles
3. Include actual links to source articles
4. Keep it under 1000 words total
5. Professional, journalistic tone
6. NO H1 headers (Jekyll handles title)
7. Save the article to: $DraftPath

Use the Write tool to create the file at $DraftPath
"@

# Save prompt to temp file
$PromptFile = "temp_prompt_$Date.txt"
$Prompt | Out-File -FilePath $PromptFile -Encoding UTF8

# Run Claude Code
echo $Prompt | claude --dangerously-skip-system-prompt

# Clean up
Remove-Item $PromptFile -ErrorAction SilentlyContinue

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
