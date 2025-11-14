# Fix Git Push from Task Scheduler

## Problem

The automation script successfully creates content but **fails to push to GitHub** when run from Task Scheduler because it can't access your saved credentials.

## Solution: Configure Git with Personal Access Token

### Step 1: Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name it: `Eastbound Automation`
4. Set expiration: **No expiration** (or 1 year)
5. Select scopes:
   - ✅ `repo` (Full control of private repositories)
6. Click **"Generate token"**
7. **COPY THE TOKEN** (you won't see it again!)

### Step 2: Configure Git Remote with Token

```cmd
cd C:\Users\PeteS\Desktop\Eastbound

REM Update remote URL with token
git remote set-url origin https://YOUR_TOKEN@github.com/PeteSumners/eastbound.git

REM Verify it's set
git remote -v
```

Replace `YOUR_TOKEN` with the token you copied.

### Step 3: Test Push

```cmd
git push origin main
```

Should push without asking for credentials!

### Step 4: Re-run Automation

```cmd
schtasks /run /tn "Eastbound Daily Automation"
```

Now the automation will push successfully!

---

## Alternative Solution: Git Credential Manager

If you don't want the token in the remote URL:

```cmd
git config --global credential.helper manager
git config --global credential.https://github.com.username PeteSumners
```

Then manually run `git push` once to save credentials, then the automation should work.

---

## Security Note

- Never commit the token to the repository
- The token gives full access to your GitHub repos
- You can revoke it anytime at https://github.com/settings/tokens

---

**Once configured, your automation will push automatically at 6:15 AM every day!**
