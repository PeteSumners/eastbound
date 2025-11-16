# Eastbound Reports

Simple daily Russian media summary generator.

## What It Does

- Fetches recent articles from Russian media sources (TASS, RT, Sputnik, Interfax, RIAN)
- Uses Claude Code to generate a 1-2 sentence summary
- Posts to Twitter/X and LinkedIn
- Saves all data locally

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your API credentials (optional - only needed for social posting):
```
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token

LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_USER_URN=your_urn
```

3. Make sure Claude Code CLI is installed:
```bash
claude --version
```

## Usage

### Run Full Automation

```bash
python automate.py
```

This will:
1. Fetch articles from Russian media
2. Generate summary with Claude Code
3. Save data to `data/` and posts to `posts/`
4. Post to Twitter and LinkedIn (if credentials provided)

### Manual Mode

```bash
python daily_summary.py
```

This creates a prompt file, then you manually run:
```bash
claude code --print "$(cat data/prompt.txt)"
```

## Files

- `daily_summary.py` - Fetches articles and creates prompt
- `automate.py` - Full automation with social posting
- `requirements.txt` - Python dependencies
- `.gitignore` - Excludes data/ and .env from git

## Output

- `data/YYYY-MM-DD-articles.json` - Raw article data + summary
- `posts/YYYY-MM-DD-summary.md` - Formatted post with sources

## Social Media

Twitter and LinkedIn credentials are stored in GitHub Secrets and loaded via .env locally.

To skip social posting, script will continue without errors if credentials aren't found.
