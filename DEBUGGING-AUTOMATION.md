# Automation Debugging Guide

This guide helps diagnose and fix automation issues quickly.

## Quick Diagnostics

### 1. Check Logs

All automation runs create logs in `logs/` directory:

```bash
# View latest automation log
ls -lt logs/ | head -5

# Tail live automation log
tail -f logs/automation_YYYYMMDD_HHMMSS.log

# Search for errors in all logs
grep -i error logs/*.log
```

### 2. Test Individual Components

#### Test Media Monitoring
```bash
python scripts/monitor_russian_media.py --output research/test-briefing.json --parallel
```

**Expected output:**
- Should fetch 300+ articles
- Should create `research/test-briefing.json`

**Common issues:**
- Network timeouts → Check internet connection
- Feed parsing errors → Some TASS feeds are intermittently broken (OK to continue)
- 0 articles → Check if feed URLs are still valid

#### Test Visualizations
```bash
python scripts/generate_visuals.py --briefing research/YYYY-MM-DD-briefing.json --output images/
```

**Expected output:**
- Should create 4 PNG files: keywords, sources, featured, stats

**Common issues:**
- `ModuleNotFoundError` → Run `pip install -r requirements.txt`
- Permission errors → Check `images/` directory exists and is writable

#### Test AI Content Generation
```bash
python scripts/generate_ai_draft.py --briefing research/YYYY-MM-DD-briefing.json --output content/drafts/
```

**Expected output:**
- Should create `content/drafts/YYYY-MM-DD-analysis.md`

**Common issues:**
- `ANTHROPIC_API_KEY environment variable not set` → Add to `.env` file (see below)
- API rate limit errors → Wait a few minutes and retry
- Halluc human: Let's skip the debugging doc for now. Please just check on and finish the automation test