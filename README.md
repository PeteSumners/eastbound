# Eastbound Reports

Daily financial analysis from Eastern international media sources.

## What It Does

**Fetches from 12 international sources:**
- **Russian media:** TASS, RT, Sputnik, RIAN
- **Chinese media:** Xinhua, People's Daily, CGTN
- **Japanese media:** NHK, Japan Times
- **Korean media:** Yonhap
- **North Korean analysis:** 38 North, Daily NK

Then:
- Uses Claude Code to generate a finance-focused 1-2 sentence summary
- Posts to Twitter/X and LinkedIn
- Commits and pushes to GitHub
- Saves all data locally

**Focus:** Economic policy, trade, energy markets, commodities, currencies, corporate developments, and infrastructure projects

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your API credentials (optional - only needed for social posting):
```
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_USER_URN=your_urn
```

3. Make sure Claude Code CLI is installed:
```bash
claude --version
```

## Usage

### Scheduled Automation

**The system runs automatically every day at 10:00 AM (local time)** via Windows Task Scheduler.

- See `SCHEDULE.md` for details on viewing, modifying, or disabling the schedule
- Logs saved to `LAST_RUN.log` and `logs/automation.log`

### Manual Run

```bash
python src/automate.py
```

Or double-click `run_daily.bat`

This will:
1. Fetch articles from all media sources
2. Generate finance-focused summary with Claude Code
3. Save data to `data/` and posts to `posts/`
4. Post to Twitter and LinkedIn (if credentials provided)
5. Commit and push to GitHub

## Files

- `src/daily_summary.py` - Core functions for fetching articles and creating prompts
- `src/automate.py` - Full automation with Claude Code, social posting, and git
- `run_daily.bat` - Windows entry point for scheduled task
- `setup_schedule.ps1` - PowerShell script to configure Task Scheduler
- `SCHEDULE.md` - Documentation on the automation schedule
- `requirements.txt` - Python dependencies
- `.gitignore` - Excludes data/ and .env from git

## Output

- `data/YYYY-MM-DD-HHMMSS-articles.json` - Raw article data + summary (timestamped)
- `posts/YYYY-MM-DD-HHMMSS-summary.md` - Formatted financial analysis post with sources
- `LAST_RUN.log` - Most recent automation run log
- `logs/automation.log` - Complete history of all runs

## Social Media

Twitter and LinkedIn credentials are stored in GitHub Secrets and loaded via .env locally.

To skip social posting, script will continue without errors if credentials aren't found.
