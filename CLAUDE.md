# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL: AUTOMATION-ONLY DEVELOPMENT ⚠️

**ZERO MANUAL INTERVENTION POLICY:**

You are ONLY allowed to modify:
1. `run_automation_with_claude.ps1` (main automation script executed by Task Scheduler)
2. Any Python scripts called by the automation pipeline (e.g., `scripts/monitor_russian_media.py`, `scripts/generate_images_local.py`)
3. Task Scheduler configuration (via `setup_daily_task.ps1`)

**ABSOLUTELY FORBIDDEN:**
- ❌ Manual fixes to posts, images, or content
- ❌ Manual deletion or moving of files
- ❌ Running one-off commands outside the pipeline
- ❌ Individual article fixes or patches
- ❌ Manual git operations for content (only for code changes)

**CORE PHILOSOPHY:**
If the automation produces bad output, you MUST:
1. Fix the automation script
2. Delete the bad output (via automation if needed)
3. Re-run the FULL pipeline from start to finish
4. Verify the output is correct

The system must be 100% reproducible and fully automated.

**TESTING AUTOMATION CHANGES:**
To test changes, you MUST use Task Scheduler (never run scripts directly):

1. Make changes to automation scripts
2. Commit changes to git
3. Run `test_run_soon.ps1` to reschedule task to run in 2 minutes
4. Wait for Task Scheduler to execute the automation
5. Review logs and output
6. If successful, run `setup_daily_task.ps1` to restore 9:50 AM schedule
7. If failed, fix scripts and repeat

**Never run automation scripts directly** - always go through Task Scheduler to ensure the system works end-to-end as it will in production.

## Project Overview

Eastbound is a Russian media analysis and translation service providing English-speaking audiences with accurate translations, context, and analysis of Russian media sources. This is a business/media project, NOT an intelligence operation.

## Core Principles (CRITICAL)

**Safety & Independence:**
- Everything published is public and transparent
- Completely independent from all governments
- Only analyze publicly available, open-source information
- Frame as journalism/research, NOT intelligence analysis
- Analyze perspectives from both Russian and American viewpoints

**Content Guidelines:**
- Translate accurately and provide cultural/political context
- Report objectively without taking partisan positions
- Acknowledge biases in sources
- Maintain professional, academic tone
- Never work with intelligence agencies or handle classified information

## Project Phases

**Phase 1 (MVP - Current):**
- GitHub Pages website (Jekyll)
- Twitter/X and LinkedIn for audience building
- Goal: 1,000+ website visitors per month

**Phase 2 (Growth - Future):**
- Enhanced website features (Next.js or similar)
- Stripe payment processing
- Premium tier: $20-50/month
- Corporate subscriptions: $500-2000/month

**Phase 3 (Scale - Years 1-3):**
- Team collaboration tools
- Custom CMS
- Analytics infrastructure

## Content Types

### Weekly Analysis Posts (1000-1500 words)
1. Hook: What happened and why it matters
2. Russian perspective from multiple sources
3. Context that Western audiences miss
4. Comparison with Western coverage
5. Implications for policy/business/culture
6. Source citations

### Translation Posts (500-1000 words + translation)
1. Introduction: Who, when, why it matters
2. Full accurate translation preserving tone
3. Context notes (cultural/political)
4. Analysis of what it reveals
5. Link to Russian original

## Russian Media Sources

**Major News:** TASS, RIA Novosti, Interfax, RT
**Business:** Kommersant, Vedomosti, RBC
**Analysis:** Carnegie Moscow, Telegram channels
**Government:** Kremlin.ru, MID Russia, Duma statements

## Development Notes

This repository contains a fully automated publishing system built on:

- Jekyll static site generator hosted on GitHub Pages
- Automated content generation using Claude AI (with anti-hallucination system)
- RSS feed monitoring of Russian media sources
- GitHub Actions for automated publishing workflows
- Twitter and LinkedIn API integration for social media posting
- Translation management tools
- Content scheduling/publishing workflow
- Analytics for tracking audience growth and engagement

When implementing features, prioritize:
1. Content creation and publishing workflow
2. Translation accuracy verification
3. Source citation management
4. AI safety and anti-hallucination measures
5. Analytics and metrics tracking

## CRITICAL: Automation Setup (REQUIRES ADMIN ACCESS)

**Problem Identified (Nov 14, 2025):**
The automation script `scripts/run_daily_automation.py` tries to invoke `claude` CLI command for content generation, but this PARTIALLY WORKS when run from Task Scheduler:
1. Claude Code CLI CAN be called from external automation (Task Scheduler works!)
2. BUT: When called non-interactively via stdin redirect, Claude Code executes but files aren't created in the expected location
3. Claude Code returns success (exit code 0) and logs show it "created" files, but they don't persist
4. Root cause: Non-interactive Claude Code runs in a sandboxed/temporary context

**Solution Implemented (Nov 15, 2025 - 8:23 PM):**

The automation now uses **external PowerShell script that calls Claude Code CLI**:

1. **Windows Task Scheduler** is configured and running
   - Task name: "Eastbound Daily Automation"
   - Schedule: Daily at 8:00 AM
   - Runs: `PowerShell.exe -ExecutionPolicy Bypass -File run_automation_with_claude.ps1`

2. **External Automation** (`run_automation_with_claude.ps1`):
   - Runs OUTSIDE of Claude Code (no recursion issues!)
   - Monitors Russian media: `scripts/monitor_russian_media.py`
   - Generates visualizations: `scripts/generate_visuals.py`
   - **Calls Claude Code CLI** with prompt to generate article
   - Passes control to Python automation for remaining steps

3. **Python Automation** (`scripts/run_daily_automation.py`):
   - Verifies draft exists (created by external script)
   - Generates SDXL images: `scripts/generate_images_local.py` with intelligent LoRA selection
   - Auto-publishes: Moves draft to `_posts/`
   - Extracts knowledge: `scripts/extract_knowledge_from_posts.py`
   - Commits to git and pushes
   - Posts to social media: Twitter and LinkedIn

4. **Setup Requirements:**
   - Ensure .env has Twitter and LinkedIn API keys (for social media posting)
   - Windows Task Scheduler setup: Run `setup_daily_task.ps1` as Administrator
   - Claude Code CLI must be available in PATH

5. **Manual Testing:**
   - Run once: `powershell -ExecutionPolicy Bypass -File run_automation_with_claude.ps1`
   - Or: `python scripts/run_daily_automation.py --skip-visuals` (assumes draft exists)
   - Skip images: Add `--skip-image` flag (saves ~30 minutes)

**Status:** ✅ AUTOMATION FULLY FUNCTIONAL - Runs daily at 8 AM without any API keys needed!
