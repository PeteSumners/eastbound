# Setup Instructions

## Windows Task Scheduler Setup

To run the automation daily at 6:00 AM:

1. Open Task Scheduler (search "Task Scheduler" in Start menu)

2. Click "Create Basic Task..."

3. Name: `Eastbound Daily Automation`

4. Trigger: Daily at 6:00 AM

5. Action: Start a program
   - Program/script: `C:\Users\PeteS\Desktop\Eastbound\run_daily.bat`
   - Start in: `C:\Users\PeteS\Desktop\Eastbound`

6. Check "Open Properties dialog when I click Finish"

7. In Properties:
   - Under "General" tab: Check "Run whether user is logged on or not"
   - Under "Conditions" tab: Uncheck "Start the task only if the computer is on AC power"

8. Click OK

## Manual Testing

To test the automation manually:

```bash
cd C:\Users\PeteS\Desktop\Eastbound
python automate.py
```

## Viewing Logs

Logs are saved to `logs\automation.log`

```bash
type logs\automation.log
```

## GitHub Pages Setup

1. Go to https://github.com/petesumners/eastbound/settings/pages

2. Under "Source", select:
   - Branch: `main`
   - Folder: `/` (root)

3. Click "Save"

4. Your site will be live at: https://petesumners.github.io/eastbound/

## Adding API Credentials

Create a `.env` file in the project root:

```
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_USER_URN=your_urn
```

**IMPORTANT**: The `.env` file is gitignored and will never be committed.
