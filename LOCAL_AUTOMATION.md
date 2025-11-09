# Local Automation Setup

Run the entire Eastbound content pipeline **locally on your machine** for FREE!

## Why Local?

- 💰 **$0 Cost**: No GitHub Actions compute time, no Anthropic API costs
- ⚡ **Faster**: No waiting for Actions runners
- 🎮 **More Control**: Debug and iterate easily
- 🖼️ **SDXL Locally**: Generate images on your machine (16-20 min per image)
- 🤖 **Claude Code**: Use your subscription instead of API calls

## What Runs Locally

✅ Russian media monitoring (free public RSS feeds)
✅ SDXL image generation (local CPU, ~16-20 minutes)
✅ Data visualizations (matplotlib/pandas)
✅ **Content generation using Claude Code** (included in your subscription!)
✅ Git operations (commit & push)
✅ Social media posting (requires API keys below)

## Setup

### 1. Install Dependencies

Already done! Your environment has:
- Python 3.11+
- All required packages from `requirements.txt` and `requirements-images.txt`
- Claude Code CLI

### 2. Set API Keys (Social Media Only)

Edit `run_daily_automation.bat` and add your API keys:

```batch
set TWITTER_API_KEY=your_key_here
set TWITTER_API_SECRET=your_secret_here
set TWITTER_ACCESS_TOKEN=your_token_here
set TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
set TWITTER_BEARER_TOKEN=your_bearer_token_here
set LINKEDIN_ACCESS_TOKEN=your_linkedin_token_here
set LINKEDIN_USER_URN=your_linkedin_urn_here
```

**Note**: Social media posting is optional. Skip with `--skip-social` flag.

### 3. Set Up Daily Scheduling

**Option A: Automated Setup (Recommended)**

Run as Administrator:
```powershell
powershell -ExecutionPolicy Bypass -File setup_daily_task.ps1
```

This creates a Windows Task Scheduler task that runs daily at 8 AM.

**Option B: Manual Setup**

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Name: "Eastbound Daily Automation"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
   - Program: `C:\Users\PeteS\Desktop\Eastbound\run_daily_automation.bat`
   - Start in: `C:\Users\PeteS\Desktop\Eastbound`

## Usage

### Run Manually

```bash
# Full automation (everything)
python scripts/run_daily_automation.py

# Skip image generation (if already done)
python scripts/run_daily_automation.py --skip-image

# Create draft only (don't publish)
python scripts/run_daily_automation.py --draft-only

# Skip social media posting
python scripts/run_daily_automation.py --skip-social

# Skip visualizations
python scripts/run_daily_automation.py --skip-visuals
```

### Test the Scheduled Task

```powershell
# Run now
Start-ScheduledTask -TaskName "Eastbound Daily Automation"

# Check status
Get-ScheduledTask -TaskName "Eastbound Daily Automation"

# View history
Get-ScheduledTaskInfo -TaskName "Eastbound Daily Automation"

# Disable temporarily
Disable-ScheduledTask -TaskName "Eastbound Daily Automation"

# Re-enable
Enable-ScheduledTask -TaskName "Eastbound Daily Automation"
```

## How It Works

The automation runs these steps in order:

1. **Monitor Russian Media** (5-10 minutes)
   - Scrapes RSS feeds from TASS, RIA Novosti, Kommersant, etc.
   - Analyzes trending topics
   - Creates briefing JSON

2. **Generate SDXL Image** (16-20 minutes)
   - Runs Stable Diffusion XL locally
   - 50 inference steps for high quality
   - Completely free, no API calls

3. **Generate Visualizations** (1-2 minutes)
   - Creates charts and graphs from briefing data
   - Uses matplotlib/pandas

4. **Generate Content with Claude Code** (2-5 minutes)
   - Uses `claude --print` for non-interactive generation
   - Reads briefing and creates analysis article
   - Follows CLAUDE.md guidelines
   - **Included in your Claude Code subscription!**

5. **Auto-Publish** (instant)
   - Moves draft to `_posts/`
   - Updates frontmatter

6. **Commit & Push** (30 seconds)
   - Commits all changes to git
   - Pushes to GitHub
   - Triggers GitHub Pages rebuild

7. **Post to Social Media** (30 seconds)
   - Posts to Twitter/X
   - Posts to LinkedIn
   - Requires API keys

## Timeline

Total runtime: **25-35 minutes**

- Media monitoring: 5-10 min
- Image generation: 16-20 min
- Visualizations: 1-2 min
- Content generation: 2-5 min
- Publishing & social: 1 min

## Cost Comparison

### GitHub Actions (Old Way)
- GitHub Actions compute: ~$0.008/minute × 30 min = **$0.24/day**
- Anthropic API (content): ~$0.50/day
- **Total: ~$0.74/day = $22/month**

### Local Automation (New Way)
- Electricity (CPU for 30 min): ~$0.01
- Claude Code: **$0** (included in subscription)
- Social media APIs: Minimal (free tier available)
- **Total: ~$0.01/day = $0.30/month**

**Savings: ~$21.70/month!**

## Logs

Check `automation.log` for execution history:
```bash
type automation.log
```

## Troubleshooting

### Task doesn't run
- Check Task Scheduler event log
- Ensure computer is on and not in sleep mode
- Run manually first to test

### Image generation fails
- Check disk space (needs ~8GB for model)
- Ensure Python dependencies installed: `pip install -r requirements-images.txt`
- First run downloads model (~6.9GB)

### Claude Code fails
- Verify Claude Code is installed: `claude --version`
- Check authentication: `claude setup-token`
- Test manually: `claude --print "test prompt"`

### Social media posting fails
- Verify API keys are set correctly
- Check API rate limits
- Use `--skip-social` to bypass if not needed

## Disable GitHub Actions

Since you're running locally now, you can disable the GitHub Actions workflow:

```bash
# Rename to disable
git mv .github/workflows/daily-content.yml .github/workflows/daily-content.yml.disabled

# Or delete entirely
git rm .github/workflows/daily-content.yml

git commit -m "Disable GitHub Actions (running locally now)"
git push
```

## Re-enable GitHub Actions

If you want to switch back:

```bash
git mv .github/workflows/daily-content.yml.disabled .github/workflows/daily-content.yml
git commit -m "Re-enable GitHub Actions"
git push
```
