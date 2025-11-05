# 🚀 START HERE - Quick Setup Guide

**Time needed:** ~45 minutes | **Cost:** $0/month

Follow these steps in order. Check ✅ each box as you complete it.

---

## Step 1: Push Code to GitHub (5 min)

Open terminal in this folder and run:

```bash
git init
git add .
git commit -m "Initial commit: Eastbound automation"
git branch -M main
```

**Create private repo:** Go to https://github.com/new
- Name: `eastbound`
- Visibility: **PRIVATE** ⚠️
- Don't initialize with anything
- Click "Create repository"

**Push code:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/eastbound.git
git push -u origin main
```

*Replace YOUR_USERNAME with your GitHub username*

**If asked for password:** Use a Personal Access Token from https://github.com/settings/tokens
- Generate new token → Select `repo` permissions → Copy and use as password

✅ **Step 1 Complete** - Code is on GitHub

---

## Step 2: Get Gmail App Password (5 min)

**Go to:** https://myaccount.google.com/apppasswords

**Prerequisites:**
- Must have 2-Step Verification enabled
- Enable at: https://myaccount.google.com/security

**Generate password:**
1. Select app: "Mail"
2. Select device: "Other" → Type "Eastbound"
3. Click "Generate"
4. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

**Write it here temporarily:**
```
Gmail address: ________________________@gmail.com
App password: ____ ____ ____ ____
```

**Test it:**
Send email from your Gmail to `eastboundreports@substack.com`
Check https://eastboundreports.substack.com/publish/posts - should appear in drafts

✅ **Step 2 Complete** - Gmail app password works

---

## Step 3: Get Twitter API Credentials (15-20 min)

### 3A: Apply for Developer Account

**Go to:** https://developer.twitter.com/en/portal/petition/essential/basic-info

**Application:**
- Use case: "Making a bot"
- Description:
  ```
  Automated posting for my newsletter "Eastbound Reports"
  which translates and analyzes Russian media. I want to
  post thread summaries when articles are published.
  ```

**Wait for approval** (usually instant to 24 hours)

### 3B: Create App

**Go to:** https://developer.twitter.com/en/portal/dashboard

**Create:**
1. Click "+ Create Project"
   - Name: "Eastbound Automation"
   - Use case: "Making a bot"
2. Create app: "eastbound-publisher" (must be unique)

### 3C: Get 5 Credentials

**Go to:** Your app → "Keys and tokens" tab

**Copy these 5 values:**

```
1. API Key: ________________________________________

2. API Secret: _____________________________________

3. Bearer Token: ___________________________________

4. Access Token: ___________________________________

5. Access Token Secret: ____________________________
```

⚠️ **IMPORTANT:** When generating Access Token, set permissions to **"Read and Write"** (not "Read Only")!

✅ **Step 3 Complete** - All 5 Twitter credentials saved

---

## Step 4: Add Secrets to GitHub (5 min)

**Go to:** `https://github.com/YOUR_USERNAME/eastbound/settings/secrets/actions`

Click **"New repository secret"** for each:

### Email Secrets (5 secrets)

1. Name: `SUBSTACK_EMAIL` → Value: `eastboundreports@substack.com`
2. Name: `SMTP_SERVER` → Value: `smtp.gmail.com`
3. Name: `SMTP_PORT` → Value: `587`
4. Name: `SMTP_USERNAME` → Value: *your-gmail@gmail.com*
5. Name: `SMTP_PASSWORD` → Value: *your 16-char app password*

### Twitter Secrets (5 secrets)

6. Name: `TWITTER_API_KEY` → Value: *from Step 3*
7. Name: `TWITTER_API_SECRET` → Value: *from Step 3*
8. Name: `TWITTER_BEARER_TOKEN` → Value: *from Step 3*
9. Name: `TWITTER_ACCESS_TOKEN` → Value: *from Step 3*
10. Name: `TWITTER_ACCESS_TOKEN_SECRET` → Value: *from Step 3*

**Verify:** You should see 10 secrets listed

✅ **Step 4 Complete** - All 10 secrets added

---

## Step 5: Enable & Test (10 min)

### 5A: Enable GitHub Actions

**Go to:** `https://github.com/YOUR_USERNAME/eastbound/actions`

Click **"I understand my workflows, go ahead and enable them"**

You should see 3 workflows available

### 5B: Create Test Post

1. Go to **Actions** tab
2. Click **"Create New Draft"**
3. Click **"Run workflow"**
4. Fill in:
   - Type: `weekly-analysis`
   - Title: `TEST - My First Post`
5. Click **"Run workflow"**
6. Wait 30 seconds, refresh, click the workflow run
7. Should show ✅ success

### 5C: Edit & Publish Test

1. Go to **Code** tab → `content/drafts/`
2. Click your test post → Click pencil icon (Edit)
3. Add some text to the Hook section
4. **In the frontmatter at top:**
   - Change `status: draft` to `status: scheduled`
   - Change `publish_time: "09:00"` to **current time + 5 minutes in UTC**
     - Convert at: https://www.timeanddate.com/worldclock/converter.html
5. **Change the file path at top** from `drafts/` to `scheduled/`
6. Click **"Commit changes"**

### 5D: Manual Publish (Skip the Wait)

1. Go to **Actions** → **"Manual Publish Post"**
2. Click **"Run workflow"**
3. Enter your filename (from step 5C)
4. Check "Skip Twitter" (test Substack only first)
5. Click **"Run workflow"**
6. Wait 2 minutes
7. Check https://eastboundreports.substack.com/publish/posts
8. Your test post should be there! 🎉

✅ **Step 5 Complete** - Test post published!

---

## 🎉 You're Live!

### Clean up test posts:
- Delete test posts from Substack drafts
- Delete from GitHub `content/published/`
- Delete `content/drafts/EXAMPLE-weekly-analysis.md`

### Create your first real post:
1. **Actions → Create New Draft**
2. Edit in browser or pull locally
3. Schedule for a good time (weekday morning)
4. Let automation handle the rest!

---

## 📚 Full Documentation

- **Complete setup guide:** [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
- **Where to get keys:** [API_KEYS_LOCATIONS.md](API_KEYS_LOCATIONS.md)
- **Daily usage:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Technical details:** [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md)

---

## 🆘 Troubleshooting

**Workflow failed?**
- Click the failed workflow → View logs → See what went wrong
- Common issues: Wrong secret name, expired tokens, typos

**Email not sending?**
- Test manually: send email to eastboundreports@substack.com
- Verify Gmail app password is correct (not your regular password)

**Twitter not posting?**
- Verify app has "Read and Write" permissions
- Regenerate Access Token with correct permissions if needed

**Need help?**
- Check [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) for detailed troubleshooting
- View workflow logs for specific error messages

---

## ⚡ Quick Commands

**Local development:**
```bash
# Pull latest changes
git pull

# Create a draft
python scripts/create_draft.py --type weekly-analysis --title "Your Title"

# Test publishing (dry run)
python scripts/publish_to_substack.py --file content/drafts/file.md --dry-run

# Interactive menu
bash scripts/local_dev.sh
```

---

**Time to celebrate! Your automation is ready! 🚀**

Next: Create your first real post and watch the magic happen ✨
