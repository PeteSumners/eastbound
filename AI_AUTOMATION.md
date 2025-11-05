# AI-Powered Automated Content Generation

## Overview

Eastbound Reports now includes a **fully automated AI content generation system** that:
- Monitors Russian media sources daily
- Generates analysis posts using Claude AI
- Publishes automatically (with clear AI disclaimers)
- Runs entirely on GitHub Actions (free)

**Cost:** ~$0.10-0.30 per post (Claude API usage)

---

## How It Works

### Daily Workflow (Automated)

```
8:00 AM UTC - GitHub Actions triggers
    ↓
1. Monitor Russian Media
   - Fetches RSS feeds from TASS, RIA Novosti, Kommersant, RT, Interfax
   - Identifies trending stories (covered by multiple sources)
   - Creates research briefing with top stories
    ↓
2. Generate Analysis with Claude AI
   - Sends briefing to Claude 3.5 Sonnet
   - Uses impartial analysis prompt
   - Generates 1000-1500 word structured analysis
   - Follows Eastbound Reports template
    ↓
3. Create Draft Post
   - Saves as markdown in content/drafts/
   - Includes AI-generated disclaimer
   - Cites all Russian sources
    ↓
4. Auto-Publish (default) OR Review
   - Scheduled runs: Auto-publishes to website
   - Manual runs: Creates draft for review
    ↓
5. Website Updates
   - GitHub Pages rebuilds automatically
   - Post goes live at petesumners.github.io/eastbound
    ↓
6. Twitter Thread (optional)
   - Auto-generates thread from post
   - Posts to @eastboundreport
```

---

## AI Disclaimers

Every AI-generated post includes:

### Top of Post:
```
⚠️ AI-GENERATED CONTENT: This post was automatically generated using
Claude AI based on Russian media monitoring. While we strive for accuracy
and objectivity, this content should be reviewed critically. All source
citations link to original Russian media.
```

### Bottom of Post:
```
## Disclaimer

This analysis was generated automatically by AI (Claude 3.5 Sonnet) as
part of Eastbound Reports' experimental automated content system. The AI
was prompted to:

- Analyze Russian media coverage objectively
- Maintain strict impartiality
- Cite sources accurately
- Provide context for English-speaking audiences
- Avoid partisan positions

Human review and editing may improve accuracy and nuance. Treat
AI-generated analysis as a starting point for understanding Russian media
narratives, not definitive interpretation.
```

### Frontmatter:
```yaml
author: "Eastbound Reports (AI-Generated)"
ai_generated: true
tags:
  - ai-generated
```

---

## The Impartiality Prompt

The AI is given strict instructions to maintain objectivity:

```
CRITICAL PRINCIPLES:
- Maintain complete objectivity and impartiality
- Do NOT take sides in geopolitical conflicts
- Do NOT endorse or condemn any narrative
- EXPLAIN Russian perspectives without validating them
- Acknowledge biases in all sources (Russian and Western)
- Use neutral, analytical language
- Cite sources accurately
- Focus on WHAT Russian media is saying, not whether it's true
```

---

## Usage

### Automatic Daily Posts

By default, the system runs daily at 8:00 AM UTC and auto-publishes:

**No action required** - posts appear automatically on your website each morning.

### Manual Generation (with Review)

To generate a draft for review instead of auto-publishing:

1. **Go to:** https://github.com/PeteSumners/eastbound/actions/workflows/daily-ai-content.yml
2. Click **"Run workflow"**
3. Set `auto_publish` to `false`
4. Click **"Run workflow"**

This will:
- Monitor sources
- Generate draft
- Create GitHub Issue for review
- Wait for your approval before publishing

### Review and Edit Drafts

If you choose manual review:

1. **Check GitHub Issues** for "Review AI-generated draft" notifications
2. **Open the draft** file in `content/drafts/`
3. **Edit in GitHub web** (click pencil icon) or pull locally
4. **Approve:** Move to `content/scheduled/`, change status to `scheduled`
5. **Reject:** Delete the draft file

---

## Configuration

### Change Publishing Schedule

Edit `.github/workflows/daily-ai-content.yml`:

```yaml
on:
  schedule:
    # Currently: 8:00 AM UTC daily
    - cron: '0 8 * * *'

    # Examples:
    # Every 6 hours: '0 */6 * * *'
    # Twice daily: '0 8,20 * * *'
    # Weekdays only: '0 8 * * 1-5'
```

### Change AI Model

Edit `scripts/generate_ai_draft.py`:

```python
model="claude-3-5-sonnet-20241022"  # Current
# model="claude-3-opus-20240229"    # More expensive, higher quality
# model="claude-3-haiku-20240307"   # Cheaper, faster
```

### Modify Analysis Prompt

Edit the `ANALYSIS_PROMPT` in `scripts/generate_ai_draft.py` to:
- Adjust tone
- Change structure
- Add/remove requirements
- Emphasize different aspects

---

## Monitoring Sources

Current Russian media sources monitored:

| Source | Type | Language |
|--------|------|----------|
| TASS | State news | English/Russian |
| RIA Novosti | State news | Russian |
| Interfax | Independent | Russian |
| RT | State media | English |
| Kommersant | Business | Russian |

**To add more sources:**

Edit `RSS_SOURCES` in `scripts/monitor_russian_media.py`:

```python
RSS_SOURCES = {
    'Source Name': 'https://example.com/rss',
    # Add more here
}
```

---

## Quality Control

### What the AI Does Well:
✅ Identifies trending stories across sources
✅ Structures analysis consistently
✅ Cites sources accurately
✅ Maintains neutral tone
✅ Provides cultural context

### What to Watch For:
⚠️ **Factual errors** - AI may misinterpret or invent details
⚠️ **Nuance** - May miss subtle implications
⚠️ **Translation** - May not perfectly capture Russian idioms
⚠️ **Western comparison** - Has limited real-time Western news access
⚠️ **Recency** - Training data has cutoff (currently April 2024)

### Recommended Review Process:
1. **Verify sources** - Check links work and quotes are accurate
2. **Check tone** - Ensure it's objective, not partisan
3. **Fact-check** - Verify key claims
4. **Add context** - Supplement with recent developments AI missed
5. **Edit as needed** - Treat AI output as first draft

---

## Cost Estimate

**Claude API pricing (as of 2024):**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**Per post (~1500 words):**
- Input (briefing + prompt): ~2,000 tokens = $0.006
- Output (analysis): ~2,500 tokens = $0.0375
- **Total:** ~$0.04-0.10 per post

**Monthly (30 posts):**
- **~$1.20-3.00/month**

Much cheaper than hiring a human analyst! 💰

---

## Limitations & Ethics

### What This System Is:
✅ **A research tool** for monitoring Russian media at scale
✅ **A starting point** for understanding narratives
✅ **Transparent** - clearly labeled as AI-generated
✅ **Objective** - prompted to maintain strict impartiality

### What This System Is NOT:
❌ **Not a replacement for human analysis** - AI lacks nuance
❌ **Not propaganda** - doesn't endorse any narrative
❌ **Not intelligence work** - uses only public sources
❌ **Not perfect** - may make errors or miss context

### Ethical Considerations:
- **Transparency:** All AI content clearly labeled
- **Source citation:** Links to original Russian media
- **Impartiality:** Prompts emphasize objectivity
- **Human oversight:** Review process available
- **Limitations:** Disclaimers explain AI's constraints

---

## Troubleshooting

### No posts being generated?

**Check:**
1. GitHub Actions is enabled
2. `ANTHROPIC_API_KEY` secret is set correctly
3. Workflow logs for errors: https://github.com/PeteSumners/eastbound/actions

### AI generating low-quality content?

**Solutions:**
1. Edit the `ANALYSIS_PROMPT` for more specific instructions
2. Switch to Claude Opus (higher quality, more expensive)
3. Add human review step (set `auto_publish: false`)
4. Supplement AI posts with manual posts

### API costs too high?

**Options:**
1. Reduce frequency (weekly instead of daily)
2. Use Claude Haiku (cheaper model)
3. Generate drafts only, publish selectively
4. Implement cost caps in Claude console

---

## Future Enhancements

Potential improvements:

- [ ] Sentiment analysis of Russian coverage
- [ ] Comparison with Western sources (via web search)
- [ ] Trend tracking over time
- [ ] Multi-language support
- [ ] Fact-checking integration
- [ ] Human review queue UI
- [ ] Quality scoring system
- [ ] A/B testing different prompts

---

## Support

**Questions? Issues?**
- Check workflow logs: https://github.com/PeteSumners/eastbound/actions
- Open an issue: https://github.com/PeteSumners/eastbound/issues
- Review the code: All scripts are open source!

---

**Disclaimer:** This is an experimental system. AI-generated content should be treated as preliminary analysis requiring human verification. Eastbound Reports maintains full transparency about the use of AI in content generation.
