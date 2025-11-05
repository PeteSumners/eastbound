# Quick Reference Guide

## Creating and Publishing Content (No Local Computer Needed!)

### 1. Create a New Draft

**Via GitHub Actions:**
1. Go to **Actions** tab
2. Click **"Create New Draft"**
3. Click **"Run workflow"**
4. Fill in:
   - Type: `weekly-analysis` or `translation`
   - Title: Your post title
   - Original URL (for translations only)
   - Schedule days (optional)
5. Click **"Run workflow"**

**Via GitHub Web:**
1. Go to `templates/` folder
2. Copy the template file content
3. Create new file in `content/drafts/` with name: `YYYY-MM-DD-your-title.md`
4. Paste template and edit

### 2. Edit Your Draft

1. Navigate to `content/drafts/[your-file].md`
2. Click the **pencil icon** (Edit)
3. Fill in all content sections
4. Preview with the **Preview** tab
5. **Commit changes** at the bottom

### 3. Schedule for Publishing

**Update these fields in frontmatter:**

```yaml
date: "2024-11-05"        # Publish date
publish_time: "14:00"     # Time in UTC (24-hour)
status: scheduled         # Change from 'draft' to 'scheduled'
```

**Move file:**
1. Copy file content
2. Delete file from `content/drafts/`
3. Create new file in `content/scheduled/` with same name
4. Paste content

**OR use GitHub's move:**
1. Edit the file
2. Change the path in the filename box from `content/drafts/` to `content/scheduled/`
3. Commit

### 4. Publish Immediately

**Via Manual Workflow:**
1. Go to **Actions** → **Manual Publish Post**
2. Click **Run workflow**
3. Enter filename (e.g., `2024-11-05-my-post.md`)
4. Click **Run workflow**

**Via Changing Schedule:**
1. Edit the file in `content/scheduled/`
2. Change `publish_time` to current time (in UTC)
3. Commit
4. Wait for hourly check (runs at :00 of each hour)

## Time Zone Conversion

The system uses **UTC time**. Convert your local time:

**EST/EDT → UTC:**
- EST (winter): Add 5 hours
- EDT (summer): Add 4 hours
- Example: 9:00 AM EST = 14:00 UTC

**Common publish times:**
- 9:00 AM EST = `publish_time: "14:00"`
- 12:00 PM EST = `publish_time: "17:00"`
- 5:00 PM EST = `publish_time: "22:00"`

Use: https://www.timeanddate.com/worldclock/converter.html

## Frontmatter Quick Reference

```yaml
---
title: "Your Compelling Title"
subtitle: "Optional explanatory subtitle"
date: "2024-11-05"                    # YYYY-MM-DD
publish_time: "14:00"                 # HH:MM in 24-hour UTC
status: draft                         # draft | scheduled | published
type: weekly-analysis                 # weekly-analysis | translation
tags:
  - analysis
  - tag2
original_url: "https://..."           # For translations only
original_author: "Author Name"        # For translations only
original_source: "Publication"        # For translations only
original_date: "2024-11-05"          # For translations only
author: "Eastbound Reports"
twitter_thread: true                  # Auto-generate thread
---
```

## Content Structure

### Weekly Analysis Post

1. **Hook** - What happened and why it matters (2-3 sentences)
2. **Russian Perspective** - Multiple sources, key quotes (300-400 words)
3. **Context** - Background Western audiences miss (300-400 words)
4. **Comparison** - How Western media differs (200-300 words)
5. **Implications** - Policy, business, culture impacts
6. **Bottom Line** - Key takeaway (2-3 sentences)
7. **Sources** - Full citations with links

### Translation Post

1. **Introduction** - Who, when, why it matters (2-3 paragraphs)
2. **Translation** - Full accurate translation
3. **Translator's Notes** - Idioms, cultural references
4. **Context and Analysis** - Background, what it reveals
5. **Sources** - Links to original and related sources

## File Status Workflow

```
draft → scheduled → published
  ↓         ↓           ↓
  📝       📅          ✅
```

**draft**: Work in progress in `content/drafts/`
**scheduled**: Ready to publish in `content/scheduled/` (auto-publishes at date/time)
**published**: Published in `content/published/` (archived)

## Automation Schedule

- **Hourly check** (at :00): Looks for scheduled posts ready to publish
- **Auto-publish**: Sends to Substack via email
- **Wait 3 minutes**: Allows Substack to process
- **Auto-tweet**: Posts thread to Twitter/X
- **Archive**: Moves to `content/published/`

## Twitter Thread Auto-Generation

The system automatically creates threads:

**Weekly Analysis:**
- Tweet 1: Title + hook + link
- Tweet 2: Policy implications
- Tweet 3: Bottom line
- Tweet 4: "Read more" + tags

**Translation:**
- Tweet 1: Title + intro + link
- Tweets 2-3: Key quotes from translation
- Tweet 4: What it reveals
- Tweet 5: "Read more" + tags

**Disable threads:** Set `twitter_thread: false` in frontmatter

## Common Tasks via GitHub Web

### View Scheduled Posts
Navigate to: `content/scheduled/`

### View Published Archive
Navigate to: `content/published/`

### Edit a Scheduled Post
1. Go to `content/scheduled/[file].md`
2. Click pencil icon
3. Make changes
4. Commit

### Cancel a Scheduled Post
1. Edit file in `content/scheduled/`
2. Change `status: scheduled` to `status: draft`
3. Move back to `content/drafts/`

### Reschedule a Post
1. Edit file in `content/scheduled/`
2. Update `date` and `publish_time`
3. Commit

## Checking Automation Status

**View workflow runs:**
1. Go to **Actions** tab
2. Click on **Publish Scheduled Posts**
3. Click latest run to see logs

**Verify a post published:**
1. Check `content/published/` for the file
2. Check Substack at https://eastboundreports.substack.com
3. Check Twitter at https://twitter.com/[your_handle]

## Emergency: Stop a Publishing Workflow

If a workflow is running and you need to stop it:

1. Go to **Actions** tab
2. Click the running workflow (yellow dot)
3. Click **"Cancel workflow"**

## Troubleshooting Quick Checks

**Post didn't publish:**
- [ ] File is in `content/scheduled/`?
- [ ] Status is `scheduled`?
- [ ] Time has passed (check UTC)?
- [ ] GitHub Actions enabled?

**Email to Substack failed:**
- [ ] Check Actions logs for error
- [ ] Verify SMTP credentials in Settings → Secrets

**Twitter thread didn't post:**
- [ ] Check Actions logs for error
- [ ] Verify Twitter API credentials
- [ ] Check API rate limits

## Pro Tips

✅ **Use meaningful filenames:** `2024-11-05-putin-speech-analysis.md`

✅ **Schedule in advance:** Use `--schedule-days 3` to plan ahead

✅ **Review before publish:** Posts to Substack go to drafts first

✅ **Test with dry-run:** Add `--dry-run` flag to preview

✅ **Archive sources:** Link all Russian sources in post

✅ **Tweet timing:** Schedule for peak audience times (9 AM - 5 PM EST)

✅ **Consistent schedule:** Pick a day/time and stick to it (e.g., every Monday 9 AM)

## Workflow Commands (via Actions Tab)

| Workflow | Use When | Inputs |
|----------|----------|--------|
| **Create New Draft** | Starting new post | Type, title, URL |
| **Manual Publish** | Publish immediately | Filename |
| **Publish Scheduled** | Runs automatically | None (automatic) |

## URL Structure

Your posts will be at:
```
https://eastboundreports.substack.com/p/[post-slug]
```

Post slug = filename without date prefix
- File: `2024-11-05-putin-speech-analysis.md`
- URL: `https://eastboundreports.substack.com/p/putin-speech-analysis`

## Getting Help

1. **Check logs:** Actions tab → Click workflow → View logs
2. **Read docs:** See `AUTOMATION_SETUP.md` for detailed setup
3. **Test locally:** Clone repo and run scripts with `--dry-run`
4. **Check APIs:**
   - Substack: https://substack.com/settings
   - Twitter: https://developer.twitter.com/en/portal/dashboard

---

**Remember:** Everything runs in the cloud. You never need a local computer! ☁️✨
