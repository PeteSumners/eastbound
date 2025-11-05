# Eastbound Automation Setup

This document explains how to set up the fully automated, cloud-based publishing system for Eastbound Reports using GitHub Actions.

## Overview

The automation system allows you to:
- ✍️ Create new drafts from templates via GitHub UI
- 📅 Schedule posts for automatic publishing
- 📧 Auto-publish to Substack
- 🐦 Auto-post threads to Twitter/X
- ☁️ Run everything in the cloud (no local computer needed)

## Architecture

```
GitHub Repository (Cloud Storage)
    ↓
GitHub Actions (Cloud Automation)
    ↓
    ├─→ Substack (via Email API)
    └─→ Twitter/X (via API)
```

## Quick Start

### 1. Push to GitHub

First, push this repository to GitHub:

```bash
git init
git add .
git commit -m "Initial commit: Eastbound automation setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/eastbound.git
git push -u origin main
```

### 2. Set Up API Credentials

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

#### Substack Publishing (via Email)

Substack accepts posts sent via email to: `your-subdomain@substack.com`

**Required secrets:**
- `SUBSTACK_EMAIL` = `eastboundreports@substack.com`
- `SMTP_SERVER` = Your email provider's SMTP server (e.g., `smtp.gmail.com`)
- `SMTP_PORT` = `587` (for TLS)
- `SMTP_USERNAME` = Your email address
- `SMTP_PASSWORD` = Your email password or app-specific password

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an app-specific password at https://myaccount.google.com/apppasswords
3. Use that password as `SMTP_PASSWORD`

#### Twitter/X API

Get API credentials from https://developer.twitter.com/en/portal/dashboard

**Required secrets:**
- `TWITTER_API_KEY` = Your API Key
- `TWITTER_API_SECRET` = Your API Secret
- `TWITTER_ACCESS_TOKEN` = Your Access Token
- `TWITTER_ACCESS_TOKEN_SECRET` = Your Access Token Secret
- `TWITTER_BEARER_TOKEN` = Your Bearer Token

**To get Twitter API access:**
1. Apply for a Twitter Developer account
2. Create a new project and app
3. Generate access tokens with "Read and Write" permissions
4. Copy all credentials to GitHub Secrets

### 3. Enable GitHub Actions

Go to your repository → **Actions** tab

If prompted, click **"I understand my workflows, go ahead and enable them"**

## Workflows

### Create New Draft

**Location:** Actions → Create New Draft → Run workflow

**Inputs:**
- `type`: weekly-analysis or translation
- `title`: Your post title
- `original_url`: (For translations) URL to Russian original
- `schedule_days`: (Optional) Schedule N days from now

**What it does:**
1. Creates a new draft from template in `content/drafts/`
2. Commits and pushes to GitHub
3. You can then pull changes, edit the draft, and push back

### Publish Scheduled Posts (Automated)

**Location:** Runs automatically every hour

**What it does:**
1. Checks `content/scheduled/` for posts with `status: scheduled`
2. If the scheduled date/time has passed:
   - Publishes to Substack via email
   - Waits 3 minutes for Substack to process
   - Posts Twitter thread
   - Moves file to `content/published/`
   - Commits changes

### Manual Publish

**Location:** Actions → Manual Publish Post → Run workflow

**Inputs:**
- `filename`: Name of the file to publish (e.g., `2024-11-05-my-post.md`)
- `skip_substack`: Skip Substack publishing
- `skip_twitter`: Skip Twitter posting

**What it does:**
- Immediately publishes the specified post
- Useful for urgent posts or testing

## Content Workflow

### Option A: Use GitHub Web Interface (No Local Computer)

1. **Create Draft:**
   - Go to Actions → Create New Draft → Run workflow
   - Fill in title and type
   - Wait for workflow to complete

2. **Edit Draft:**
   - Go to `content/drafts/` → your file
   - Click the pencil icon to edit
   - Fill in all sections (see templates for structure)
   - Commit changes directly on GitHub

3. **Schedule Publishing:**
   - Set `status: scheduled`
   - Set `date: "YYYY-MM-DD"`
   - Set `publish_time: "HH:MM"` (24-hour format, UTC)
   - Move file to `content/scheduled/` folder
   - Commit changes

4. **Automatic Publishing:**
   - GitHub Actions checks hourly
   - When time arrives, auto-publishes to Substack and Twitter
   - File moves to `content/published/`

### Option B: Use GitHub Codespaces (Cloud Development)

1. Click the green **Code** button → **Codespaces** tab → **Create codespace**
2. This gives you a full VS Code environment in your browser
3. Create and edit drafts locally, then commit and push

### Option C: Local Development (Optional)

If you want to work locally:

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/eastbound.git
cd eastbound

# Install dependencies
pip install -r requirements.txt

# Create a new draft
python scripts/create_draft.py --type weekly-analysis --title "Your Title"

# Edit the draft in content/drafts/

# When ready, move to scheduled and set status
mv content/drafts/YYYY-MM-DD-your-title.md content/scheduled/
# Edit file: change status to "scheduled"

# Push to GitHub
git add content/
git commit -m "Scheduled new post"
git push

# The automated workflow will publish at the scheduled time
```

## File Organization

```
eastbound/
├── content/
│   ├── drafts/          # Work in progress
│   ├── scheduled/       # Ready to publish (with date/time)
│   └── published/       # Already published (archive)
├── templates/
│   ├── weekly-analysis.md
│   └── translation.md
├── scripts/
│   ├── create_draft.py
│   ├── publish_to_substack.py
│   └── post_to_twitter.py
└── .github/
    └── workflows/       # GitHub Actions automation
```

## Post Frontmatter

Every post has YAML frontmatter at the top:

```yaml
---
title: "Your Post Title"
subtitle: "Optional subtitle"
date: "2024-11-05"
publish_time: "09:00"  # 24-hour format, UTC
status: draft  # draft, scheduled, or published
type: weekly-analysis  # or translation
tags:
  - analysis
  - russia
author: "Eastbound Reports"
twitter_thread: true  # Auto-generate Twitter thread
---
```

**Status values:**
- `draft`: Work in progress, won't be published
- `scheduled`: Ready to publish at specified date/time
- `published`: Already published (set automatically)

## Testing

### Test Without Publishing

```bash
# Test Substack publishing (dry run)
python scripts/publish_to_substack.py --file content/drafts/your-file.md --dry-run

# Test Twitter thread generation (dry run)
python scripts/post_to_twitter.py --file content/drafts/your-file.md --dry-run
```

### Test Manual Publish Workflow

1. Create a test draft
2. Go to Actions → Manual Publish Post
3. Use `skip_substack: true` and `skip_twitter: true` to test without publishing
4. Check the workflow logs to verify everything runs correctly

## Troubleshooting

### Posts Not Publishing Automatically

**Check:**
1. File is in `content/scheduled/` directory
2. Status is set to `status: scheduled`
3. Date/time has passed (use UTC time)
4. GitHub Actions is enabled
5. API credentials are set correctly in GitHub Secrets

**View logs:**
- Go to Actions → Publish Scheduled Posts → Click latest run

### Substack Email Not Sending

**Check:**
1. `SUBSTACK_EMAIL` is correct (`eastboundreports@substack.com`)
2. SMTP credentials are correct
3. For Gmail: using app-specific password, not regular password
4. SMTP port is 587 for TLS

**Note:** Posts sent via email appear as drafts in Substack. You may need to review and click "Publish" in the Substack web interface.

### Twitter Thread Not Posting

**Check:**
1. All 5 Twitter API credentials are set
2. App has "Read and Write" permissions
3. Tweet character limits (280 chars)
4. API rate limits not exceeded

## Cost Estimate

**GitHub Actions:**
- 2,000 free minutes/month for public repos
- Unlimited for private repos with GitHub Pro
- This automation uses ~5 minutes per post
- **Cost: FREE** (for typical usage)

**Substack:**
- **Cost: FREE** (Substack handles hosting)

**Twitter API:**
- Free tier: 1,500 tweets/month
- **Cost: FREE** (for typical usage)

**Total: $0/month** ✨

## Advanced: AI-Assisted Writing

To integrate Claude API for AI-assisted draft writing:

1. Add `ANTHROPIC_API_KEY` to GitHub Secrets
2. Create a new workflow that calls Claude API to help generate drafts
3. Use prompts like:
   - "Translate this Russian article: [URL]"
   - "Analyze Russian media coverage of [topic]"
   - "Compare Russian and Western framing of [event]"

(Contact me if you want help setting this up)

## Security Notes

- Never commit API keys or passwords to the repository
- Always use GitHub Secrets for credentials
- Regularly rotate API keys and passwords
- Use app-specific passwords for email (not main password)
- Review GitHub Actions logs for any exposed credentials (GitHub auto-masks secrets)

## Support

If you encounter issues:

1. Check workflow logs in the Actions tab
2. Verify all GitHub Secrets are set correctly
3. Test scripts locally with dry-run mode
4. Check Substack and Twitter API documentation

## Next Steps

1. ✅ Push repository to GitHub
2. ✅ Add all API credentials to GitHub Secrets
3. ✅ Test creating a draft via GitHub Actions
4. ✅ Test manual publishing with skip flags
5. ✅ Schedule your first real post!

Happy automating! 🚀
