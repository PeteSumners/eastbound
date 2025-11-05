# Setup Checklist - Eastbound Automation

Follow these steps in order to get your automation running. Check off each item as you complete it.

---

## Part 1: GitHub Setup (5 minutes)

### Step 1: Create Private GitHub Repository

1. Go to https://github.com/new
2. **Repository name:** `eastbound` (or whatever you prefer)
3. **Visibility:** ⚠️ **PRIVATE** (very important!)
4. **Do NOT initialize** with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

✅ Repository created

### Step 2: Push Your Code

Open terminal/command prompt in `C:\Users\PeteS\Desktop\Eastbound` and run:

```bash
git init
git add .
git commit -m "Initial commit: Eastbound automation system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/eastbound.git
git push -u origin main
```

**Replace `YOUR_USERNAME` with your GitHub username!**

If prompted for credentials:
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your password)
  - Get token at: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Select scopes: `repo` (all repo permissions)
  - Copy the token and use it as password

✅ Code pushed to GitHub

---

## Part 2: Substack Email Publishing (10 minutes)

Substack accepts posts via email sent to: `your-subdomain@substack.com`

We'll use **Gmail** to send these emails automatically.

### Step 3: Set Up Gmail App Password

1. **Go to:** https://myaccount.google.com/security
2. **Enable 2-Step Verification** (if not already enabled):
   - Click "2-Step Verification"
   - Follow the setup process
   - ⚠️ This is required for app passwords
3. **Create App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other" → Type: "Eastbound Automation"
   - Click "Generate"
   - **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)
   - ⚠️ Save this somewhere - you can't view it again!

**Note:** If you don't have a Gmail account or prefer another email provider, that's fine too. Just use your provider's SMTP settings instead.

### Alternative Email Providers

**If using a different email:**

| Provider | SMTP Server | Port |
|----------|-------------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook/Hotmail | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| iCloud | smtp.mail.me.com | 587 |

✅ Gmail app password created: `________________` (write it here temporarily)

### Step 4: Verify Your Substack Email Address

Your Substack publication accepts emails at:
```
eastboundreports@substack.com
```

**Test it:**
1. Send a test email from your Gmail to `eastboundreports@substack.com`
2. Subject: "Test Post"
3. Body: "This is a test"
4. Check your Substack drafts at: https://eastboundreports.substack.com/publish/posts
5. You should see "Test Post" in drafts

✅ Substack email verified (test post received)

---

## Part 3: Twitter API Setup (15-20 minutes)

### Step 5: Apply for Twitter Developer Account

1. **Go to:** https://developer.twitter.com/en/portal/petition/essential/basic-info
2. **Sign in** with your Twitter account (the one for @eastboundreports or your personal account)
3. **Application questions:**
   - **What's your use case?** Select: "Making a bot"
   - **Will you make Twitter content available?** Yes
   - **Describe your use case:**
     ```
     I run a newsletter called Eastbound Reports that translates and analyzes
     Russian media for English-speaking audiences. I want to automatically post
     thread summaries of my articles when they're published to my Substack
     newsletter. This will help readers discover my content and provide value
     through curated insights from Russian media sources.
     ```
   - **Are you affiliated with government?** No

4. **Click "Next"** and complete the application
5. **Wait for approval** (usually instant to 24 hours)

✅ Twitter Developer account approved

### Step 6: Create Twitter App

Once approved:

1. **Go to:** https://developer.twitter.com/en/portal/dashboard
2. Click **"+ Create Project"**
   - **Project name:** "Eastbound Automation"
   - **Use case:** "Making a bot"
   - **Project description:** "Automated posting for Eastbound Reports newsletter"
3. **Create App:**
   - **App name:** "eastbound-publisher" (must be unique)
   - **Environment:** Production
4. **Click "Complete"**

✅ Twitter app created

### Step 7: Generate API Keys and Tokens

Still in the Twitter Developer Portal:

1. **Go to your app** → "Keys and tokens" tab
2. **API Key and Secret:**
   - Should be visible (if not, click "Regenerate")
   - Copy both:
     - `API_KEY`: `_________________________`
     - `API_SECRET`: `_________________________`

3. **Bearer Token:**
   - Click "Regenerate" if not visible
   - Copy:
     - `BEARER_TOKEN`: `_________________________`

4. **Access Token and Secret:**
   - Click "Generate" under "Access Token and Secret"
   - ⚠️ **IMPORTANT:** Set access permissions to **"Read and Write"** (not "Read Only"!)
   - Copy both:
     - `ACCESS_TOKEN`: `_________________________`
     - `ACCESS_TOKEN_SECRET`: `_________________________`

⚠️ **Save all 5 credentials somewhere safe - you'll need them in the next step!**

✅ All 5 Twitter credentials saved:
- [ ] API_KEY
- [ ] API_SECRET
- [ ] BEARER_TOKEN
- [ ] ACCESS_TOKEN
- [ ] ACCESS_TOKEN_SECRET

---

## Part 4: Configure GitHub Secrets (5 minutes)

Now we'll add all your credentials to GitHub so the automation can use them.

### Step 8: Add Secrets to GitHub

1. **Go to your GitHub repository:** `https://github.com/YOUR_USERNAME/eastbound`
2. Click **"Settings"** (top menu)
3. Click **"Secrets and variables"** → **"Actions"** (left sidebar)
4. Click **"New repository secret"** (green button)

**Add these secrets ONE BY ONE:**

#### Substack/Email Secrets

**Secret 1:**
- Name: `SUBSTACK_EMAIL`
- Value: `eastboundreports@substack.com`
- Click "Add secret"

**Secret 2:**
- Name: `SMTP_SERVER`
- Value: `smtp.gmail.com` (or your email provider's SMTP server)
- Click "Add secret"

**Secret 3:**
- Name: `SMTP_PORT`
- Value: `587`
- Click "Add secret"

**Secret 4:**
- Name: `SMTP_USERNAME`
- Value: Your full Gmail address (e.g., `yourname@gmail.com`)
- Click "Add secret"

**Secret 5:**
- Name: `SMTP_PASSWORD`
- Value: The 16-character app password from Step 3
- Click "Add secret"

#### Twitter API Secrets

**Secret 6:**
- Name: `TWITTER_API_KEY`
- Value: (paste your API Key)
- Click "Add secret"

**Secret 7:**
- Name: `TWITTER_API_SECRET`
- Value: (paste your API Secret)
- Click "Add secret"

**Secret 8:**
- Name: `TWITTER_BEARER_TOKEN`
- Value: (paste your Bearer Token)
- Click "Add secret"

**Secret 9:**
- Name: `TWITTER_ACCESS_TOKEN`
- Value: (paste your Access Token)
- Click "Add secret"

**Secret 10:**
- Name: `TWITTER_ACCESS_TOKEN_SECRET`
- Value: (paste your Access Token Secret)
- Click "Add secret"

✅ All 10 secrets added to GitHub

**Verify:** You should see 10 secrets listed in Settings → Secrets → Actions

---

## Part 5: Enable GitHub Actions (2 minutes)

### Step 9: Enable Workflows

1. **Go to your repository:** `https://github.com/YOUR_USERNAME/eastbound`
2. Click the **"Actions"** tab
3. If you see "Workflows aren't being run on this repository":
   - Click **"I understand my workflows, go ahead and enable them"**
4. You should now see 3 workflows:
   - ✅ Create New Draft
   - ✅ Manual Publish Post
   - ✅ Publish Scheduled Posts

✅ GitHub Actions enabled

---

## Part 6: Test Everything (10 minutes)

### Step 10: Create a Test Draft

Let's test the automation with a real post!

1. **Go to:** Actions tab → "Create New Draft" → "Run workflow"
2. **Fill in:**
   - Type: `weekly-analysis`
   - Title: `TEST - Automation Test Post`
   - Schedule days: `0` (leave empty for today)
3. Click **"Run workflow"**
4. Wait ~30 seconds, then refresh
5. Click the workflow run to see logs
6. Should complete successfully ✅

✅ Test draft created

### Step 11: Edit the Test Draft

1. **Go to:** Code tab → `content/drafts/`
2. Find your test post (should be `YYYY-MM-DD-test-automation-test-post.md`)
3. Click the file → Click pencil icon (Edit)
4. **Fill in at least:**
   - The hook section (2-3 sentences)
   - One source
   - A bottom line
5. **Change in frontmatter:**
   - `date: "2024-11-05"` → today's date
   - `publish_time: "14:00"` → current time + 5 minutes (in UTC!)
     - **Convert your time to UTC:** https://www.timeanddate.com/worldclock/converter.html
     - Example: 3:00 PM EST = 20:00 UTC
   - `status: draft` → `status: scheduled`
6. **Change the file path** at the top from:
   - `content/drafts/...` → `content/scheduled/...`
7. Click **"Commit changes"**

✅ Test post edited and scheduled

### Step 12: Test Manual Publish (Optional but Recommended)

Instead of waiting for the hourly check, let's publish immediately:

1. **Go to:** Actions → "Manual Publish Post" → "Run workflow"
2. **Fill in:**
   - Filename: (your test post filename from step 11)
   - Skip Substack: `false` (unchecked)
   - Skip Twitter: `true` (checked) ← Skip Twitter for first test
3. Click **"Run workflow"**
4. Wait ~2 minutes for it to complete
5. Click the workflow run to see logs

**Check results:**
1. **Substack:** Go to https://eastboundreports.substack.com/publish/posts
   - You should see your test post in DRAFTS
   - ⚠️ Review it and click "Publish" manually (email posts go to drafts first)
2. **GitHub:** Check `content/published/` - your file should be there

✅ Manual publish successful

### Step 13: Test Automatic Publishing (Optional)

If you want to test the hourly automation:

1. Create another test draft (Actions → Create New Draft)
2. Edit it and schedule for current time + 10 minutes
3. Move to `content/scheduled/`
4. Wait for the next hour mark (automation runs at :00 of each hour)
5. Check workflow logs in Actions → "Publish Scheduled Posts"

✅ Automatic publishing tested

---

## Part 7: Clean Up and Go Live! (5 minutes)

### Step 14: Delete Test Posts

1. **Delete from Substack:**
   - Go to your Substack drafts
   - Delete any test posts

2. **Delete from GitHub:**
   - Go to `content/published/`
   - Delete test post files
   - Or just commit: "Cleaned up test posts"

✅ Test posts cleaned up

### Step 15: Delete Example File

1. Go to `content/drafts/EXAMPLE-weekly-analysis.md`
2. Delete this file (or keep it as reference)

✅ Example file handled

---

## 🎉 You're Live!

Your automation is now fully configured and tested. Here's what happens now:

### Creating Real Posts

**Method 1: GitHub Web Interface (No computer needed)**
1. Actions → Create New Draft → Run workflow
2. Edit the file in `content/drafts/`
3. When ready: change status to `scheduled`, set date/time
4. Move to `content/scheduled/`
5. Automation publishes at scheduled time

**Method 2: Local Development**
```bash
git pull  # Get latest changes
python scripts/create_draft.py --type weekly-analysis --title "Your Title"
# Edit the file
git add content/
git commit -m "New post: Your Title"
git push
```

### Publishing Schedule

The automation checks every hour at :00 for scheduled posts:
- 12:00 PM UTC
- 1:00 PM UTC
- 2:00 PM UTC
- etc.

If a post's scheduled time has passed, it publishes immediately.

---

## 📋 Quick Reference

### Your Credentials (Store Securely!)

**Substack:**
- Email: `eastboundreports@substack.com`
- Your Gmail app password: `________________`

**Twitter:**
- Developer portal: https://developer.twitter.com/en/portal/dashboard
- All 5 API credentials stored in GitHub Secrets

**GitHub:**
- Repository: `https://github.com/YOUR_USERNAME/eastbound` (PRIVATE)
- All secrets stored in Settings → Secrets → Actions

### Important URLs

- **Substack posts:** https://eastboundreports.substack.com/publish/posts
- **Twitter developer:** https://developer.twitter.com/en/portal/dashboard
- **GitHub repo:** https://github.com/YOUR_USERNAME/eastbound
- **GitHub Actions:** https://github.com/YOUR_USERNAME/eastbound/actions

### Support

- **Workflow logs:** Actions tab → Click any workflow run
- **Test setup:** Run `python scripts/test_setup.py` locally
- **Documentation:** See AUTOMATION_SETUP.md and QUICK_REFERENCE.md

---

## Troubleshooting

### Posts not publishing?
- ✅ Check Actions tab for errors
- ✅ Verify all 10 secrets are set correctly
- ✅ Verify file is in `content/scheduled/` with `status: scheduled`
- ✅ Verify time has passed (use UTC time!)

### Substack email not working?
- ✅ Test by sending manual email to eastboundreports@substack.com
- ✅ Verify Gmail app password is correct
- ✅ Check SMTP_USERNAME is your full email address

### Twitter not posting?
- ✅ Verify all 5 Twitter credentials are correct
- ✅ Verify app has "Read and Write" permissions
- ✅ Check rate limits (1,500 tweets/month on free tier)

---

## 🚀 Next Steps

1. ✅ Complete all steps in this checklist
2. 📝 Create your first real post
3. 📅 Schedule it for a good time (weekday morning, 9-11 AM EST)
4. 📊 Monitor the results
5. 🔁 Establish a regular publishing cadence (e.g., every Monday & Thursday)

**You're all set! Happy publishing! 🎉**

---

*Last updated: November 5, 2024*
