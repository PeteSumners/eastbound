# Full Automation System Test

## What This Does

Runs the complete Eastbound automation pipeline:
1. ✅ Monitor Russian media (318+ articles from 8 sources)
2. 🖼️ Generate SDXL image (8-10 min, downloads ~6.9GB first time)
3. 📊 Generate data visualizations (4 charts)
4. ✍️ Generate AI content with Claude Code (1500+ words)
5. 💾 Commit and push to GitHub
6. 🐦 Post to Twitter (optional, requires API keys)
7. 💼 Post to LinkedIn (optional, requires API keys)

## Prerequisites

✅ Already installed:
- Python 3.14
- All dependencies (diffusers, torch, transformers)
- SDXL Turbo model cached (~6.5GB)

⚠️ HuggingFace cache cleared - will re-download models

## Commands

### Option 1: Full Pipeline (with SDXL image generation)
```bash
# With verbose logging (recommended for first run)
python scripts/run_daily_automation.py --verbose --draft-only

# Without verbose (cleaner output)
python scripts/run_daily_automation.py --draft-only
```

**Expected time:** 15-20 minutes first run (includes SDXL download)
**Subsequent runs:** 10-15 minutes (model cached)

---

### Option 2: Skip Image Generation (faster testing)
```bash
python scripts/run_daily_automation.py --skip-image --draft-only --verbose
```

**Expected time:** 30-60 seconds

---

### Option 3: Full Pipeline + Auto-Publish + Social Media
```bash
# Removes --draft-only flag, publishes to _posts/ and social media
python scripts/run_daily_automation.py --verbose
```

**Prerequisites:**
- Twitter API keys in `.env`
- LinkedIn API keys in `.env`

---

## What to Watch For

### Step 1: Monitor Russian Media (10-15 seconds)
- Fetches 13 RSS feeds in parallel
- Some feeds may fail (TASS category feeds have XML issues)
- Should get 300-400 articles total
- Deduplicates and extracts top 10 trending topics

**Expected output:**
```
[OK] RIA Novosti: 50 articles
[OK] Interfax: 25 articles
[ERROR] TASS Economy: Feed parsing error
[STATS] Total articles fetched: 359
[OK] 318 unique articles remaining
```

---

### Step 2: Generate SDXL Image (8-10 min first run, 3-5 min cached)

**First run (cache cleared):**
- Downloads ~6.9GB model files
- Takes 8-10 minutes to download on typical connection
- Generation: 8-10 minutes on CPU (50 steps)

**Cached runs:**
- No download
- Generation: 8-10 minutes on CPU

**Expected output:**
```
[LOCAL-GEN] Using full SDXL: stabilityai/stable-diffusion-xl-base-1.0
[LOCAL-GEN] Loading model... (first run downloads ~6.9GB)
Fetching 18 files: 100%|██████████| 18/18 [08:17<00:00]
[LOCAL-GEN] This will take 8-10 minutes on CPU...
  0%|          | 0/50 [00:00<?, ?it/s]
 50%|█████     | 25/50 [04:23<04:23, 10.55s/it]
100%|██████████| 50/50 [08:46<00:00, 10.53s/it]
[OK] Generated: 2025-11-11-generated.png
```

---

### Step 3: Generate Visualizations (5-10 seconds)
- Creates 4 PNG charts:
  - Keywords trend chart
  - Source distribution chart
  - Social media card
  - Stats summary card

**Expected output:**
```
[OK] Keyword chart: 2025-11-11-keywords.png
[OK] Source chart: 2025-11-11-sources.png
[OK] Social card: 2025-11-11-featured.png
[OK] Stats card: 2025-11-11-stats.png
```

---

### Step 4: Generate AI Content (30-60 seconds)
- Calls Claude Code CLI
- Reads briefing JSON
- Generates 1500+ word analysis
- Saves to `content/drafts/2025-11-11-analysis.md`

**Expected output:**
```
Using Claude Code CLI for FREE content generation...
[OK] Content generation completed successfully
```

---

### Step 5: Commit & Push (5-10 seconds)
- Adds all new files
- Commits with automated message
- Pushes to GitHub

**Expected output:**
```
[main abc1234] AI content: 2025-11-11 [automated - local]
 7 files changed, 5194 insertions(+)
```

---

### Step 6-7: Social Media (5-10 seconds each)
Only runs if:
- `--draft-only` flag NOT used
- API keys present in `.env`

**Expected output:**
```
[TWITTER] Posting thread with 3 tweets...
   [OK] Tweet 1/3 posted (ID: 123456789)
[SUCCESS] Thread posted successfully!
```

---

## Troubleshooting

### Issue: RSS feeds failing
**Symptom:** `[ERROR] TASS Economy: Feed parsing error`
**Impact:** Low - you'll still get 300+ articles from working feeds
**Fix:** Already documented in CONTINUOUS_IMPROVEMENT_LOG.md

### Issue: SDXL timeout
**Symptom:** Process hangs during image generation
**Fix:** Use `--skip-image` flag, or increase timeout in script

### Issue: Claude Code not found
**Symptom:** `[ERROR] Claude Code execution failed`
**Fix:** Ensure `claude` command is in PATH

### Issue: Twitter Unicode error
**Symptom:** `UnicodeEncodeError` when posting to Twitter
**Status:** ✅ FIXED in latest commit (UTF-8 encoding wrapper)

---

## Files Created

After successful run, you'll find:

```
research/2025-11-11-briefing.json          # 318 articles, trending topics
images/2025-11-11-generated.png            # SDXL image (1024x1024)
images/2025-11-11-keywords.png             # Keyword trend chart
images/2025-11-11-sources.png              # Source distribution
images/2025-11-11-featured.png             # Social card
images/2025-11-11-stats.png                # Stats summary
content/drafts/2025-11-11-analysis.md      # Full analysis article (1500+ words)
```

If `--draft-only` NOT used:
```
_posts/2025-11-11-analysis.md              # Published article
```

---

## Performance Benchmarks

### Without Image Generation (--skip-image)
- Monitor Russian media: 10-15s
- Generate visualizations: 5-10s
- Generate AI content: 30-60s
- Commit & push: 5-10s
- **Total: 50-95 seconds**

### With Image Generation (full run)
- Monitor Russian media: 10-15s
- **Generate SDXL image: 8-10 minutes** ⏰
- Generate visualizations: 5-10s
- Generate AI content: 30-60s
- Commit & push: 5-10s
- **Total: 10-15 minutes**

### With SDXL Turbo (--fast flag on image script)
- Monitor Russian media: 10-15s
- **Generate SDXL Turbo: 1-2 minutes** ⚡
- Generate visualizations: 5-10s
- Generate AI content: 30-60s
- Commit & push: 5-10s
- **Total: 2-4 minutes**

---

## Cost Breakdown

- RSS monitoring: **FREE**
- SDXL image generation: **FREE** (local CPU)
- Data visualizations: **FREE** (matplotlib)
- AI content (Claude Code): **FREE** (local CLI)
- GitHub hosting: **FREE** (Pages)
- Git operations: **FREE**
- Twitter posting: **FREE** (uses your API keys)
- LinkedIn posting: **FREE** (uses your API keys)

**Total cost per post: $0** 🎉

---

## Next Steps After Successful Run

1. **Review the draft:**
   ```bash
   cat content/drafts/2025-11-11-analysis.md
   ```

2. **Check the generated image:**
   ```bash
   open images/2025-11-11-generated.png  # macOS
   start images/2025-11-11-generated.png # Windows
   ```

3. **Publish manually (if used --draft-only):**
   ```bash
   mv content/drafts/2025-11-11-analysis.md _posts/
   git add _posts/ && git commit -m "Publish analysis" && git push
   ```

4. **Set up Windows Task Scheduler:**
   - Run as Administrator: `setup_schedule.bat`
   - Creates daily 6:00 AM automated run

---

## Monitoring Long-Running Processes

The automation script supports `--verbose` flag for real-time output:

```bash
python scripts/run_daily_automation.py --verbose --draft-only
```

This shows:
- Command being executed
- Process PID
- Real-time streaming output (no buffering)
- Execution time
- Return codes
- Full traceback on errors

Perfect for debugging SDXL generation or other long steps!

---

**Last updated:** November 11, 2025
**System:** SDXL 1.0 Base, Python 3.14, Windows 11
