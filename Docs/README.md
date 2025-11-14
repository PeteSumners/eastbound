# Eastbound System Documentation

Welcome to the comprehensive documentation for the Eastbound automated content generation system.

## What is Eastbound?

Eastbound is a **fully automated** Russian media monitoring and analysis platform that runs entirely locally for FREE. It monitors Russian state media sources, generates AI-powered analysis articles, creates data visualizations, and publishes content to GitHub Pages—all without any API costs or GitHub Actions minutes.

## Quick Start

### Daily Automation (Default Mode)
```bash
python scripts/run_daily_automation.py
```

This single command:
1. Monitors 13+ Russian media RSS feeds
2. Generates SDXL images locally (15-20 min)
3. Creates data visualizations
4. Generates 1000-1500 word analysis with Claude Code (FREE)
5. Auto-publishes to GitHub Pages
6. Posts to Twitter/X and LinkedIn

### With East Asian Sources
```bash
python scripts/monitor_russian_media.py --output research/briefing.json --parallel --include-asia
```

Adds 10 East Asian news sources (China, Japan, NK, SK, Taiwan) for broader regional perspectives.

## Core Documentation

### 📊 [Briefing Database Structure](briefing-database-structure.md)
Learn how the briefing JSON database works, including:
- TF-IDF keyword extraction algorithm
- Trending story identification
- Multi-source verification
- Data quality and anti-hallucination measures

**Key concepts:**
- `trending_stories`: Multi-source verified topics (3+ sources required)
- `tfidf_score`: Statistical measure of term importance/distinctiveness
- `combined_score`: TF-IDF × source count (prioritizes both significance and coverage)
- `all_articles`: Complete dataset of 200-400 articles for comprehensive analysis

### 🏭 [Content Generation Pipeline](content-generation-pipeline.md)
Complete walkthrough of the 6-stage automation pipeline:
1. **Media Monitoring** - RSS feed fetching & TF-IDF analysis (~2-5 min)
2. **SDXL Image Generation** - Local Stable Diffusion XL (~15-20 min)
3. **Data Visualizations** - Charts & graphs (~30-60 sec)
4. **AI Content Generation** - Claude Code CLI article writing (~2-3 min)
5. **Auto-Publish** - Git commit & push to GitHub Pages (~30 sec)
6. **Social Distribution** - Twitter/X & LinkedIn posting (~10 sec)

**Total runtime:** ~30-40 minutes | **Total cost:** $0/month

### 👥 [Stakeholder Perspective System](stakeholder-perspective-system.md)
Understand the random persona generation system:
- Why we use **random selection** instead of targeted analysis
- How personas are generated (100+ occupations, 40+ countries, 10 regions)
- Topic-specific stakes (Ukraine → refugees, Energy → oil workers, etc.)
- Integration with articles (4 personas per article with individualized analysis)

**Philosophy:** These are NOT opinion polls or representative samples. They're concrete examples showing how abstract geopolitics affects real people with real interests.

## Features Overview

### ✅ Implemented Features

**Content Generation:**
- [x] Automated daily Russian media monitoring (13 sources)
- [x] TF-IDF keyword extraction with multi-source verification
- [x] Local SDXL image generation (no API costs)
- [x] Data visualization charts (keywords, sources, stats)
- [x] Claude Code-powered article generation (FREE)
- [x] Jekyll-formatted posts with proper frontmatter
- [x] Stakeholder perspective system (4 random personas per article)
- [x] Automatic source citation with grouped reference links
- [x] GitHub Pages auto-publishing

**East Asian Expansion:**
- [x] Optional East Asian news sources (10 sources: China, Japan, NK, SK, Taiwan)
- [x] Asian country support in stakeholder system (cities, names, perspectives)
- [x] Regional diversity in persona generation

**Infrastructure:**
- [x] Windows Task Scheduler integration (6:00 AM daily)
- [x] Parallel RSS feed fetching (8 workers)
- [x] Article deduplication (URL + fuzzy title matching)
- [x] Minimum viable dataset thresholds (50 articles minimum)
- [x] Graceful error handling and fallbacks
- [x] Social media posting (Twitter/X + LinkedIn)

### 🚧 Planned Features

**Phase 1 (Near-term):**
- [ ] Move SDXL generation AFTER content completion (better prompt coherence)
- [ ] SDXL LoRA finetunes for news-appropriate aesthetics
- [ ] Sentiment analysis per article (positive/negative/neutral)
- [ ] Named entity recognition (people, places, organizations)

**Phase 2 (Medium-term):**
- [ ] Historical stakeholder tracking ("What did Elena think last week vs. today?")
- [ ] Persistent 200-person persona pool (select subset daily)
- [ ] Article categorization (conflict, energy, politics, economy, etc.)
- [ ] Trend tracking over time (week-over-week narrative shifts)

**Phase 3 (Long-term):**
- [ ] Custom CMS for content management
- [ ] Team collaboration tools
- [ ] Analytics dashboard
- [ ] Premium tier content ($20-50/month)
- [ ] Corporate subscriptions ($500-2000/month)

## System Requirements

**Software:**
- Python 3.8+
- Claude Code CLI (free tier)
- Git
- CUDA-capable GPU (for SDXL image generation)

**Python Dependencies:**
- feedparser (RSS parsing)
- scikit-learn (TF-IDF)
- matplotlib, seaborn (visualizations)
- diffusers, torch (SDXL)
- tweepy (Twitter API)
- python-dotenv (.env file support)

**Optional:**
- Twitter/X API credentials (social posting)
- LinkedIn API credentials (social posting)

## Configuration

### Environment Variables (.env)
```bash
# Social Media (optional)
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret

LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_USER_URN=your_urn

# Claude API (if using external API instead of CLI)
ANTHROPIC_API_KEY=your_key
```

### Windows Task Scheduler
Set to run daily at 6:00 AM:
```powershell
# Task: "Eastbound Daily Automation"
# Trigger: Daily at 6:00 AM
# Action: Run python scripts/run_daily_automation.py
# Working directory: C:\Users\YourUser\Desktop\Eastbound
```

## Command Reference

### Media Monitoring
```bash
# Russian sources only (default)
python scripts/monitor_russian_media.py --output research/briefing.json --parallel

# Include East Asian sources
python scripts/monitor_russian_media.py --output research/briefing.json --parallel --include-asia
```

### Image Generation
```bash
# Auto-generate from briefing
python scripts/generate_images_local.py --briefing research/2025-11-13-briefing.json --output images/ --auto --steps 50

# Skip image generation in automation
python scripts/run_daily_automation.py --skip-image
```

### Stakeholder Personas
```bash
# Generate 4 personas from briefing
python scripts/generate_stakeholder_personas.py --briefing research/2025-11-13-briefing.json --count 4

# Save to JSON
python scripts/generate_stakeholder_personas.py --count 5 --output personas.json
```

### Data Visualizations
```bash
python scripts/generate_visuals.py --briefing research/2025-11-13-briefing.json --output images/
```

### Social Media Posting
```bash
# Post to Twitter
python scripts/post_to_twitter.py --file _posts/2025-11-13-analysis.md

# Post to LinkedIn
python scripts/post_to_linkedin.py --file _posts/2025-11-13-analysis.md
```

### Full Automation Options
```bash
# Full automation
python scripts/run_daily_automation.py

# Draft only (don't publish)
python scripts/run_daily_automation.py --draft-only

# Skip social media
python scripts/run_daily_automation.py --skip-social

# Skip images and visualizations
python scripts/run_daily_automation.py --skip-image --skip-visuals

# Verbose output (real-time streaming)
python scripts/run_daily_automation.py --verbose
```

## File Structure

```
Eastbound/
├── Docs/                           # System documentation (you are here!)
│   ├── README.md                   # This file
│   ├── briefing-database-structure.md
│   ├── content-generation-pipeline.md
│   └── stakeholder-perspective-system.md
│
├── scripts/                        # Automation scripts
│   ├── run_daily_automation.py     # Main automation orchestrator
│   ├── monitor_russian_media.py    # RSS monitoring & TF-IDF
│   ├── generate_images_local.py    # SDXL image generation
│   ├── generate_visuals.py         # Data visualization charts
│   ├── generate_stakeholder_personas.py  # Random persona generation
│   ├── post_to_twitter.py          # Twitter API posting
│   └── post_to_linkedin.py         # LinkedIn API posting
│
├── research/                       # Daily briefing JSON files
│   └── YYYY-MM-DD-briefing.json    # 200-400 articles, trending analysis
│
├── images/                         # Generated images
│   ├── YYYY-MM-DD-generated.png    # SDXL hero image
│   ├── YYYY-MM-DD-keywords.png     # Trending topics chart
│   ├── YYYY-MM-DD-sources.png      # Source distribution pie chart
│   └── YYYY-MM-DD-stats.png        # Statistics panel
│
├── content/drafts/                 # Draft articles (before publishing)
│   └── YYYY-MM-DD-analysis.md
│
├── _posts/                         # Published articles (Jekyll)
│   └── YYYY-MM-DD-analysis.md
│
├── knowledge_base/                 # Historical context (anti-hallucination)
│   ├── events/*.json               # Historical events
│   ├── figures/*.json              # Key political figures
│   ├── narratives/*.json           # Russian narrative themes
│   └── policies/*.json             # Policy backgrounds
│
└── CLAUDE.md                       # Content guidelines for AI
```

## Troubleshooting

### "Insufficient articles" error
**Problem:** Fewer than 50 articles fetched
**Solutions:**
- Check internet connection
- Check if RSS feeds are accessible (some may be geo-blocked)
- Try `--include-asia` flag to expand source pool

### SDXL generation fails
**Problem:** GPU out of memory or CUDA errors
**Solutions:**
- Reduce `--steps` parameter (try 30 instead of 50)
- Check GPU availability: `nvidia-smi`
- Skip image generation: `--skip-image`

### Claude Code fails
**Problem:** Content generation errors
**Solutions:**
- Check Claude Code is installed: `claude --version`
- Verify briefing JSON is valid: `python -m json.tool research/briefing.json`
- Check file permissions for `content/drafts/`

### Social media posting fails
**Problem:** API authentication errors
**Solutions:**
- Verify `.env` file exists with correct credentials
- Check API rate limits
- Use `--skip-social` flag to bypass

### Git push fails
**Problem:** GitHub authentication or merge conflicts
**Solutions:**
- Check GitHub credentials: `git config --list`
- Pull latest changes: `git pull origin main`
- Check GitHub Pages is enabled in repository settings

## Contributing

### Adding New RSS Sources
Edit `scripts/monitor_russian_media.py`:
```python
RSS_SOURCES = {
    'New Source': 'https://example.com/rss.xml',
}
```

### Adding New Countries to Stakeholder System
Edit `scripts/generate_stakeholder_personas.py`:
```python
REGIONS = {
    'New Region': ['Country1', 'Country2'],
}

CITIES = {
    'Country1': ['City1', 'City2'],
}

names_by_region = {
    'Country1': ['Name1', 'Name2'],
}
```

### Customizing Content Guidelines
Edit `CLAUDE.md` with project-specific instructions for the AI.

## Cost Breakdown

| Component | Technology | Monthly Cost |
|-----------|------------|--------------|
| Media Monitoring | Python RSS | $0 |
| Image Generation | SDXL (local) | ~$5 electricity |
| Content Generation | Claude Code CLI | $0 |
| Hosting | GitHub Pages | $0 |
| Social APIs | Twitter + LinkedIn | $0 |
| **TOTAL** | | **~$5/month** |

## Future Documentation

Coming soon:
- [ ] Anti-Hallucination System deep dive
- [ ] TF-IDF Algorithm technical explanation
- [ ] SDXL Prompt Engineering guide
- [ ] Jekyll Theme Customization
- [ ] Analytics & Metrics tracking
- [ ] Premium Features roadmap

## Support & Feedback

**Issues:** Report bugs at [GitHub Issues](https://github.com/petesandwich/Eastbound/issues)
**Discussions:** Join conversations at [GitHub Discussions](https://github.com/petesandwich/Eastbound/discussions)

## License

This project is open-source under the MIT License. See LICENSE file for details.

---

*Last Updated: 2025-11-13*
*Documentation Version: 1.0*
