# Local Automation Setup

Eastbound runs entirely on your laptop using Windows Task Scheduler (cron equivalent). No GitHub Actions needed!

## System Overview

**Automated Daily Pipeline:**
1. Monitor Russian + East Asian media sources
2. Generate data visualizations
3. Generate article content with Claude Code (FREE)
4. Generate hero image with SDXL + Intelligent LoRA Selection (FREE)
5. Auto-publish to Jekyll
6. Commit and push to GitHub
7. Post to social media (optional)

**All processing happens locally on your laptop - completely free!**

## Requirements

```bash
# Python dependencies
pip install feedparser beautifulsoup4 requests python-dotenv
pip install diffusers transformers accelerate pillow torch peft
pip install matplotlib seaborn pandas

# Claude Code CLI (for content generation)
# Already installed and configured
```

## Running Manually

```bash
# Full automation (everything)
python scripts/run_daily_automation.py

# Draft only (no publish, no social)
python scripts/run_daily_automation.py --draft-only --skip-social

# Skip image generation (if already done)
python scripts/run_daily_automation.py --skip-image

# Include East Asian sources
python scripts/run_daily_automation.py --include-asia

# Verbose output (real-time progress)
python scripts/run_daily_automation.py --verbose
```

## Windows Task Scheduler Setup

### Create Scheduled Task

1. Open **Task Scheduler** (search in Start menu)
2. Click **"Create Task"** (not "Create Basic Task")
3. **General tab:**
   - Name: `Eastbound Daily Automation`
   - Description: `Run Eastbound media analysis and content generation`
   - Check: "Run whether user is logged on or not"
   - Check: "Run with highest privileges"

4. **Triggers tab:**
   - Click **"New..."**
   - Begin the task: **"On a schedule"**
   - Settings: **"Daily"**
   - Start: **6:00 AM** (or your preferred time)
   - Recur every: **1 days**
   - Check: "Enabled"
   - Click **"OK"**

5. **Actions tab:**
   - Click **"New..."**
   - Action: **"Start a program"**
   - Program/script: `C:\Python311\python.exe` (adjust to your Python path)
   - Add arguments: `scripts\run_daily_automation.py --include-asia`
   - Start in: `C:\Users\PeteS\Desktop\Eastbound` (your repo path)
   - Click **"OK"**

6. **Conditions tab:**
   - Uncheck: "Start the task only if the computer is on AC power"
   - Check: "Wake the computer to run this task" (optional)

7. **Settings tab:**
   - Check: "Allow task to be run on demand"
   - Check: "Run task as soon as possible after a scheduled start is missed"
   - If the task is already running: **"Do not start a new instance"**
   - Check: "Stop the task if it runs longer than: **6 hours**"

8. Click **"OK"** to save

### Find Python Path

```bash
where python
# Example output: C:\Python311\python.exe
```

### Test the Task

Right-click the task and select **"Run"** to test it immediately.

## Performance

**Typical Run Time:** ~60-90 minutes total
- Media monitoring: 10-15 minutes (Russian + East Asian sources)
- Visualizations: 2-3 minutes
- Content generation: 3-5 minutes
- **Image generation: 25-30 minutes** (full SDXL + LoRAs at 50 steps on CPU)
- Publishing & social: 1-2 minutes

## Intelligent LoRA Selection

The system automatically selects the optimal LoRA combination based on article content:

**8 Specialized Strategies:**
1. **photojournalism_standard** (default) - McCurry + Realism
2. **soviet_nostalgia** - Film Photography + McCurry (vintage aesthetic)
3. **kremlin_architecture** - McCurry + Realism (golden domes, red brick)
4. **diplomatic_summit** - McCurry + Realism (formal events)
5. **human_interest_portrait** - XPortrait + Realism (people-focused)
6. **military_operations** - McCurry + Realism (tactical photography)
7. **energy_infrastructure** - McCurry + Realism (industrial)
8. **east_asian_context** - McCurry + Realism (Asia-Pacific themes)

**Selection Process:**
- Analyzes article title + trending keywords
- Semantic matching against strategy keywords
- Generates optimized prompts with trigger words
- Applies correct LoRA strengths (0.4-0.7)

## LoRA Files

**Location:** `models/loras/`
- `steve_mccurry_v08.safetensors` (163 MB) - Photojournalism style
- `touch_of_realism_v2.safetensors` (436 MB) - Lens effects, depth of field
- `film_photography_v1.safetensors` (871 MB) - Vintage, analog aesthetic

All LoRAs downloaded and ready to use!

## Monitoring

**Check logs:**
- Task Scheduler → Task History tab
- Check generated files in `images/`, `_posts/`, `research/`

**Check output:**
- Images: `images/YYYY-MM-DD-generated.png`
- Articles: `_posts/YYYY-MM-DD-analysis.md`
- Briefings: `research/YYYY-MM-DD-briefing.json`

## Troubleshooting

**Task didn't run?**
- Check Task Scheduler → Last Run Result (should be 0x0 for success)
- Check "Start in" directory is set correctly
- Verify Python path is correct
- Check user permissions

**Image generation too slow?**
- 25-30 minutes is normal on CPU for full SDXL at 50 steps
- Quality is worth it (way better than Turbo)
- If needed, reduce steps to 35-40 in `run_daily_automation.py` line 367

**LoRA not loading?**
- Verify files exist in `models/loras/`
- Check PEFT installed: `pip install peft`
- Check file sizes (should be 100+ MB each)

## GitHub Actions (REMOVED)

All GitHub Actions workflows have been removed. The system now runs entirely locally using Windows Task Scheduler. This gives you:

- ✅ Full control over timing
- ✅ No GitHub Actions limits
- ✅ Faster iteration (no CI/CD wait times)
- ✅ Free SDXL generation on your hardware
- ✅ Real-time monitoring and debugging

## Cost Analysis

**Monthly Cost: $0**

| Component | Cost |
|-----------|------|
| Media monitoring | FREE (RSS feeds) |
| Visualizations | FREE (matplotlib) |
| Content generation | FREE (Claude Code on your account) |
| Image generation | FREE (local SDXL) |
| GitHub hosting | FREE (Pages) |
| Total | **$0/month** |

Only cost is optional social media API usage and your time.

## Next Steps

1. ✅ Set up Windows Task Scheduler (instructions above)
2. ✅ Test run manually first: `python scripts/run_daily_automation.py --draft-only`
3. ✅ Verify LoRA files in `models/loras/`
4. ✅ Configure social media API keys in `.env` (optional)
5. ✅ Let it run automatically every day!
