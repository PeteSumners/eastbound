# Where to Get Your API Keys

Quick reference for finding all the credentials you need.

---

## 🔑 Gmail (for Substack Email Publishing)

**What you need:** App-specific password

**Where to get it:**

1. **URL:** https://myaccount.google.com/apppasswords
2. **Prerequisites:** Must have 2-Step Verification enabled
   - Enable at: https://myaccount.google.com/security
3. **Steps:**
   - Select app: "Mail"
   - Select device: "Other" → Type "Eastbound Automation"
   - Click "Generate"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

**What to save:**
- ✅ `SMTP_USERNAME` = Your full Gmail address (e.g., yourname@gmail.com)
- ✅ `SMTP_PASSWORD` = The 16-character app password

**Test it:**
Send an email from your Gmail to `eastboundreports@substack.com` to verify it works.

---

## 🐦 Twitter API

**What you need:** 5 different credentials

**Where to get them:**

### Step 1: Developer Account
1. **URL:** https://developer.twitter.com/en/portal/petition/essential/basic-info
2. **Sign in** with your Twitter account
3. **Fill out application:**
   - Use case: "Making a bot"
   - Describe: "Automated posting for my newsletter about Russian media analysis"
4. **Wait for approval** (usually instant to 24 hours)

### Step 2: Create App
1. **URL:** https://developer.twitter.com/en/portal/dashboard
2. Click **"+ Create Project"**
   - Name: "Eastbound Automation"
   - Use case: "Making a bot"
3. **Create app** under the project
   - Name: "eastbound-publisher" (must be unique globally)

### Step 3: Get Credentials
1. **Go to:** Your app → "Keys and tokens" tab
2. **Get these 5 credentials:**

   **API Key & Secret:**
   - Should be visible (regenerate if needed)
   - ✅ `TWITTER_API_KEY` = (looks like: `abcd1234ABCD1234abcd1234`)
   - ✅ `TWITTER_API_SECRET` = (looks like: `xxxx...` ~50 chars)

   **Bearer Token:**
   - Click "Regenerate" if not visible
   - ✅ `TWITTER_BEARER_TOKEN` = (starts with: `AAAAAAA...` ~100+ chars)

   **Access Token & Secret:**
   - Click "Generate" under "Access Token and Secret"
   - ⚠️ **CRITICAL:** Set permissions to **"Read and Write"** (NOT "Read Only")
   - ✅ `TWITTER_ACCESS_TOKEN` = (looks like: `1234567890-xxxx...`)
   - ✅ `TWITTER_ACCESS_TOKEN_SECRET` = (looks like: `xxxx...` ~50 chars)

**Test it:**
- Use the "post_to_twitter.py" script with `--dry-run` to test

---

## 🗂️ GitHub Secrets

**Where to add them:**

1. **URL:** `https://github.com/YOUR_USERNAME/eastbound/settings/secrets/actions`
2. Click **"New repository secret"**
3. **Add each secret individually:**

### Substack/Email (5 secrets)

| Secret Name | Value | Example |
|------------|-------|---------|
| `SUBSTACK_EMAIL` | eastboundreports@substack.com | (literal value) |
| `SMTP_SERVER` | smtp.gmail.com | (or your email provider) |
| `SMTP_PORT` | 587 | (literal number) |
| `SMTP_USERNAME` | Your Gmail address | yourname@gmail.com |
| `SMTP_PASSWORD` | Gmail app password | abcd efgh ijkl mnop |

### Twitter (5 secrets)

| Secret Name | Value |
|------------|-------|
| `TWITTER_API_KEY` | From Twitter Developer Portal |
| `TWITTER_API_SECRET` | From Twitter Developer Portal |
| `TWITTER_BEARER_TOKEN` | From Twitter Developer Portal |
| `TWITTER_ACCESS_TOKEN` | From Twitter Developer Portal |
| `TWITTER_ACCESS_TOKEN_SECRET` | From Twitter Developer Portal |

**Total: 10 secrets**

---

## ✅ Verification Checklist

After adding all credentials:

### Substack/Email
- [ ] Sent test email to eastboundreports@substack.com
- [ ] Test email appeared in Substack drafts
- [ ] All 5 email secrets added to GitHub

### Twitter
- [ ] Developer account approved
- [ ] App created in developer portal
- [ ] App permissions set to "Read and Write"
- [ ] All 5 Twitter credentials copied
- [ ] All 5 Twitter secrets added to GitHub

### GitHub
- [ ] Repository is PRIVATE
- [ ] All 10 secrets visible in Settings → Secrets → Actions
- [ ] GitHub Actions enabled
- [ ] Test workflow run successful

---

## 🔒 Security Best Practices

**DO:**
- ✅ Use app-specific passwords (not your main email password)
- ✅ Keep the GitHub repo PRIVATE
- ✅ Store credentials in GitHub Secrets (they're encrypted)
- ✅ Rotate credentials periodically
- ✅ Review GitHub Actions logs for any exposed secrets (GitHub auto-masks them)

**DON'T:**
- ❌ Commit credentials to the repository
- ❌ Share credentials in screenshots or messages
- ❌ Use your main email password
- ❌ Make the repository public with secrets configured

---

## 📞 Support Links

- **Gmail Security:** https://myaccount.google.com/security
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Twitter Developer Portal:** https://developer.twitter.com/en/portal/dashboard
- **GitHub Personal Access Tokens:** https://github.com/settings/tokens
- **Time Zone Converter:** https://www.timeanddate.com/worldclock/converter.html

---

## ⏱️ Estimated Time

- **Gmail setup:** 5 minutes
- **Twitter setup:** 15-20 minutes (including approval wait)
- **GitHub secrets:** 5 minutes
- **Testing:** 10 minutes

**Total: ~35-45 minutes**

---

## 🆘 Troubleshooting

### Can't generate Gmail app password
- **Problem:** Option not available
- **Solution:** Enable 2-Step Verification first at https://myaccount.google.com/security

### Twitter Developer application rejected
- **Problem:** Application denied
- **Solution:** Provide more detail about your use case. Mention it's for a legitimate newsletter about media analysis.

### Twitter API credentials not working
- **Problem:** Authorization errors
- **Solution:**
  1. Verify app permissions are "Read and Write"
  2. Regenerate Access Token & Secret with correct permissions
  3. Update GitHub Secrets with new values

### GitHub Actions not running
- **Problem:** Workflows disabled
- **Solution:** Go to Actions tab → Enable workflows

### Secrets not working
- **Problem:** Authentication errors in workflow logs
- **Solution:**
  1. Double-check spelling of secret names (case-sensitive)
  2. Verify no extra spaces in secret values
  3. Regenerate credentials and re-add to GitHub

---

Need help? Check the workflow logs in the Actions tab for specific error messages!
