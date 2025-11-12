# Windows Task Scheduler - Verification & Setup

## ✅ CONFIRMED: What Will Run at 6:00 AM Daily

### Scheduled Task Configuration:

**Task Name:** `Eastbound Daily Automation`
**Schedule:** Every day at 6:00 AM
**Script Called:** `C:\Users\PeteS\Desktop\Eastbound\run_daily_automation.bat`

### What the Script Runs:

**File:** `run_daily_automation.bat`
```batch
cd /d "%~dp0"
python scripts\run_daily_automation.py --draft-only
echo Automation completed at %date% %time% >> automation.log
```

### Full Automation Pipeline (Draft-Only Mode):

1. **Monitor Russian Media** (~15-30s)
   - Fetches 13 RSS feeds in parallel
   - Deduplicates articles
   - Extracts trending topics
   - Saves to `research/YYYY-MM-DD-briefing.json`

2. **Generate SDXL Image** (~8-10 minutes)
   - Uses SDXL Base 1.0 (stable-diffusion-xl-base-1.0)
   - 50 inference steps
   - 512x512 resolution
   - **NOW WITH LIVE PROGRESS:** Shows Step X/Y updates
   - Saves to `images/YYYY-MM-DD-generated.png`

3. **Generate Data Visualizations** (~10 seconds)
   - Keyword trends chart
   - Source distribution chart
   - Social media card
   - Statistics summary
   - Saves 4 PNG files to `images/`

4. **Generate AI Content** (~30-60 seconds)
   - Claude Code reads briefing
   - Creates 1500+ word analysis
   - Follows CLAUDE.md guidelines
   - Saves to `content/drafts/YYYY-MM-DD-analysis.md`

5. **Commit and Push to GitHub** (~5-10 seconds)
   - Adds all new files (briefing, images, draft)
   - Commits with automated message
   - Pushes to GitHub repository

**Total Time:** 10-15 minutes per run

---

## ⚠️ Current Status: Task NOT YET Created

The scheduled task **does not exist yet**. You must create it manually.

### To Create the Scheduled Task:

#### Option 1: Automated Setup (Easiest)

1. **Right-click** `setup_schedule.bat`
2. Select **"Run as administrator"**
3. Click **"Yes"** on UAC prompt
4. Wait for success message
5. Press any key to close

#### Option 2: Manual Command

Open **PowerShell or Command Prompt as Administrator**:

```powershell
cd C:\Users\PeteS\Desktop\Eastbound
setup_schedule.bat
```

#### Option 3: Direct schtasks Command

```cmd
schtasks /create ^
  /tn "Eastbound Daily Automation" ^
  /tr "C:\Users\PeteS\Desktop\Eastbound\run_daily_automation.bat" ^
  /sc daily ^
  /st 06:00 ^
  /rl highest ^
  /f
```

---

## ✅ Verify Task Creation:

After running setup, verify the task was created:

```cmd
schtasks /query /tn "Eastbound Daily Automation" /fo LIST
```

**Expected Output:**
```
TaskName:        Eastbound Daily Automation
Status:          Ready
Next Run Time:   [Tomorrow at 6:00 AM]
Last Run Time:   N/A
Schedule:        Scheduling data is not available in this format.
```

Or in detailed format:
```cmd
schtasks /query /tn "Eastbound Daily Automation" /v /fo LIST
```

---

## 🧪 Test the Task Manually:

Before waiting for 6:00 AM, test it now:

```cmd
schtasks /run /tn "Eastbound Daily Automation"
```

This will:
- Run the automation immediately
- Show results in Task Scheduler console
- Generate today's content
- Save to `content/drafts/`

---

## 📋 What Gets Created Daily:

### Generated Files:
```
research/YYYY-MM-DD-briefing.json          # 300+ articles, trending topics
images/YYYY-MM-DD-generated.png            # SDXL image (512x512)
images/YYYY-MM-DD-keywords.png             # Keyword trends
images/YYYY-MM-DD-sources.png              # Source distribution
images/YYYY-MM-DD-featured.png             # Social card
images/YYYY-MM-DD-stats.png                # Statistics
content/drafts/YYYY-MM-DD-analysis.md      # 1500+ word article
```

### Log File:
```
automation.log                              # Completion timestamps
```

**NOT Created (Draft-Only Mode):**
- ❌ `_posts/` (not auto-published)
- ❌ Twitter posts (not auto-posted)
- ❌ LinkedIn posts (not auto-posted)

**You review and publish manually when ready!**

---

## 🔄 To Change Behavior:

### Enable Auto-Publishing + Social Media:

Edit `run_daily_automation.bat` line 9:
```batch
REM Change from:
python scripts\run_daily_automation.py --draft-only

REM To:
python scripts\run_daily_automation.py
```

**Warning:** This will:
- ✅ Automatically publish to `_posts/`
- ✅ Automatically post to Twitter (if keys set)
- ✅ Automatically post to LinkedIn (if keys set)

**Only do this when you're confident in the system!**

---

### Skip Image Generation (Faster):

Edit `run_daily_automation.bat` line 9:
```batch
python scripts\run_daily_automation.py --skip-image --draft-only
```

**Result:** 50-60 second runs (no 10-minute SDXL wait)

---

## 📊 Monitoring the Scheduled Task:

### View Task History:

1. Open **Task Scheduler** (search in Start menu)
2. Navigate to **Task Scheduler Library**
3. Find **"Eastbound Daily Automation"**
4. Click **History** tab (if disabled, click Actions → Enable All Tasks History)

### Check Logs:

```cmd
type automation.log
```

Shows completion timestamps like:
```
Automation completed at 11/12/2025 06:15:23.45
Automation completed at 11/13/2025 06:14:58.12
```

---

## ⚙️ Task Scheduler Settings (What's Configured):

| Setting | Value |
|---------|-------|
| Task Name | Eastbound Daily Automation |
| Trigger | Daily at 6:00 AM |
| Action | Run batch file |
| Script | `run_daily_automation.bat` |
| Privilege Level | Highest (Administrator) |
| Run whether user logged on or not | No (default) |
| Wake computer to run | No (default) |
| Start only if on AC power | No (default) |

---

## 🛠️ Troubleshooting:

### Task doesn't run at 6:00 AM:

1. **Check if task exists:**
   ```cmd
   schtasks /query /tn "Eastbound Daily Automation"
   ```

2. **Check computer is on at 6:00 AM**
   - Task won't run if computer is off/sleeping
   - Enable "Wake computer to run this task" if needed

3. **Check Task Scheduler History:**
   - Open Task Scheduler GUI
   - Find task → History tab
   - Look for errors

### Task runs but fails:

1. **Check automation.log:**
   ```cmd
   type automation.log
   ```

2. **Test manually:**
   ```cmd
   schtasks /run /tn "Eastbound Daily Automation"
   ```

3. **Run batch file directly:**
   ```cmd
   cd C:\Users\PeteS\Desktop\Eastbound
   run_daily_automation.bat
   ```

4. **Check Python is in PATH:**
   ```cmd
   python --version
   ```

---

## ✅ Summary Checklist:

- [ ] Task created (run `setup_schedule.bat` as Admin)
- [ ] Task verified (run `schtasks /query`)
- [ ] Manual test successful (run `schtasks /run`)
- [ ] Understand what runs (draft-only mode)
- [ ] Know where files are saved (`content/drafts/`)
- [ ] Can check logs (`automation.log`)

---

**Once the task is created, your system will run fully automated daily at 6:00 AM!** 🎉

**Last Updated:** November 12, 2025
**Script Version:** Draft-only mode with SDXL progress tracking
**Repo:** Cleaned of superfluous files
