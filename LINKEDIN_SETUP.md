# LinkedIn API Setup Guide

Follow these steps to enable automated posting to LinkedIn.

## Prerequisites

- LinkedIn account
- LinkedIn Company Page (required for app creation)

## Step 1: Create LinkedIn App

1. Go to: https://www.linkedin.com/developers/apps/new
2. Fill in app details:
   - **App name:** Eastbound Reports
   - **LinkedIn Page:** Select your company page
   - **Privacy policy URL:** https://petesumners.github.io/eastbound/about
   - **App logo:** (optional, upload if you have one)
3. Click **Create app**

## Step 2: Verify and Enable Products

1. In your app settings, go to **Settings** tab
2. Verify your app (follow LinkedIn's verification steps)
3. Go to **Products** tab
4. Request access to:
   - ✅ **Share on LinkedIn**
   - ✅ **Sign In with LinkedIn using OpenID Connect**
5. Wait for approval (usually instant for personal apps)

## Step 3: Generate Access Token

1. Go to: https://www.linkedin.com/developers/tools/oauth/token-generator
2. Select your app: **Eastbound Reports**
3. Check all available scopes:
   - `openid`
   - `profile`
   - `w_member_social`
   - `email`
4. Click **Request access token**
5. Copy the access token (starts with `AQV...`)
   - **Note:** Token is valid for 60 days, you'll need to regenerate periodically

## Step 4: Get Your User URN

Run this command with your access token:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "https://api.linkedin.com/v2/userinfo"
```

You'll get a response like:

```json
{
  "sub": "abc123xyz",
  "name": "Your Name",
  "email": "your@email.com"
}
```

The `sub` value is your **User URN** - save this!

## Step 5: Add Secrets to GitHub

Run these commands:

```bash
cd C:\Users\PeteS\Desktop\Eastbound

# Add LinkedIn access token
echo "YOUR_ACCESS_TOKEN_HERE" | gh secret set LINKEDIN_ACCESS_TOKEN

# Add LinkedIn user URN
echo "YOUR_USER_URN_HERE" | gh secret set LINKEDIN_USER_URN
```

## Done!

Your automation will now post to LinkedIn automatically when publishing content.

---

## Token Expiration

LinkedIn access tokens expire after **60 days**. When your automation stops posting to LinkedIn:

1. Go back to: https://www.linkedin.com/developers/tools/oauth/token-generator
2. Generate a new token
3. Update the secret: `echo "NEW_TOKEN" | gh secret set LINKEDIN_ACCESS_TOKEN`

---

## Testing

To test LinkedIn posting manually, see `scripts/test_linkedin_api.py`
