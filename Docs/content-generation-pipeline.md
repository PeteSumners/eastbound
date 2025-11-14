# Content Generation Pipeline

## Overview

The Eastbound content generation pipeline is a fully automated system that monitors Russian media, generates analysis, creates visualizations, and publishes content—all running locally for FREE.

## Daily Automation Flow

**Script:** `scripts/run_daily_automation.py`
**Trigger:** Windows Task Scheduler (6:00 AM daily)
**Total Runtime:** ~30-40 minutes
**Cost:** $0 (no API fees, no GitHub Actions minutes)

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 1: Media Monitoring                     │
│  Monitor Russian RSS feeds → Generate briefing JSON              │
│  Runtime: ~2-5 minutes                                          │
│  Output: research/YYYY-MM-DD-briefing.json (~200-400 articles)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 2: SDXL Image Generation (LOCAL)              │
│  Stable Diffusion XL generates news illustration                 │
│  Runtime: ~15-20 minutes                                         │
│  Output: images/YYYY-MM-DD-generated.png                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           STAGE 3: Data Visualization Generation                 │
│  Create charts: trending keywords, source distribution, stats    │
│  Runtime: ~30-60 seconds                                        │
│  Output: images/YYYY-MM-DD-{keywords,sources,stats}.png         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         STAGE 4: AI Content Generation (Claude Code)             │
│  FREE Claude Code CLI generates 1000-1500 word analysis          │
│  Runtime: ~2-3 minutes                                          │
│  Output: content/drafts/YYYY-MM-DD-analysis.md                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 5: Auto-Publish & Git Push                    │
│  Move draft to _posts/, commit, and push to GitHub Pages        │
│  Runtime: ~30 seconds                                           │
│  Output: Site live at petesandwich.github.io/Eastbound          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            STAGE 6: Social Media Distribution                    │
│  Post to Twitter/X and LinkedIn with excerpt                     │
│  Runtime: ~10 seconds                                           │
│  Output: Social posts with link back to site                    │
└─────────────────────────────────────────────────────────────────┘
```

## Stage 1: Media Monitoring

### Script
`scripts/monitor_russian_media.py --output research/YYYY-MM-DD-briefing.json --parallel`

### What It Does

1. **Fetch RSS Feeds** (parallel mode, ~13 sources simultaneously)
   - TASS (main + politics + economy + world)
   - RT (main + news + Russia + business)
   - RIA Novosti
   - Interfax
   - Kommersant (main + politics + economics)

2. **Deduplicate Articles**
   - Remove exact URL duplicates
   - Fuzzy match titles (85% similarity threshold)
   - Typical: 400 raw → 250 unique articles

3. **TF-IDF Keyword Extraction**
   - Extract statistically significant terms (unigrams + bigrams)
   - Score by importance and rarity
   - Filter generic media language

4. **Identify Trending Stories**
   - Find keywords appearing in 3+ different sources
   - Calculate combined score: `tfidf_score × source_count`
   - Select top 10 trending topics

5. **Generate Briefing JSON**
   - trending_stories: Top 10 multi-source topics
   - top_headlines: Most recent 50 articles
   - all_articles: Complete dataset (200-400 articles)

### Quality Thresholds

- **Minimum viable dataset:** 50 unique articles (automation fails if not met)
- **Multi-source verification:** Keywords need 3+ sources to qualify as "trending"
- **Deduplication:** Ensures high signal-to-noise ratio

### Output Format

See [Briefing Database Structure](briefing-database-structure.md) for complete schema documentation.

## Stage 2: SDXL Image Generation

### Script
`scripts/generate_images_local.py --briefing research/YYYY-MM-DD-briefing.json --output images/ --auto --steps 50`

### What It Does

1. **Read Briefing** and extract top trending keywords
2. **Generate Prompt** for news illustration
3. **Run Stable Diffusion XL** locally (15-20 minutes on consumer GPU)
4. **Save Output** as `images/YYYY-MM-DD-generated.png`

### Model Details

- **Base Model:** Stable Diffusion XL (SDXL)
- **Runtime:** 50 inference steps (~15-20 min on RTX 3060/3070)
- **Resolution:** 1024x1024 or 1024x768
- **Cost:** $0 (local generation)

### Future Enhancement: LoRA Finetunes

**Planned:** Fine-tune SDXL on news/photojournalism datasets
- **Candidates:** Realistic Vision, DreamShaper, news-specific LoRAs
- **License check:** Must be commercial-friendly (CC-BY-4.0, OpenRAIL, Apache 2.0)
- **Goal:** More consistent news-appropriate aesthetic

### Why Image Gen Happens Early

**Current flow:** Image → Content
**Planned change:** Content → Image (allows image prompt to use actual article title/themes)

See tracked issue in [Features Roadmap](#).

## Stage 3: Data Visualization Generation

### Script
`scripts/generate_visuals.py --briefing research/YYYY-MM-DD-briefing.json --output images/`

### What It Creates

**1. Trending Topics Chart** (`YYYY-MM-DD-keywords.png`)
- Horizontal bar chart of top 10 keywords
- X-axis: Combined score (TF-IDF × source count)
- Color-coded by score intensity

**2. Source Distribution** (`YYYY-MM-DD-sources.png`)
- Pie chart showing article distribution by source
- Shows which outlets published most content that day

**3. Statistics Panel** (`YYYY-MM-DD-stats.png`)
- Total articles scanned
- Unique sources
- Trending topics count
- Date and timestamp

### Technology

- **Library:** matplotlib + seaborn
- **Style:** Clean, professional, web-optimized
- **Format:** PNG with transparency support
- **Size:** Optimized for web (<200KB each)

## Stage 4: AI Content Generation

### Script
Claude Code CLI (FREE tier, no API costs)

### The Prompt

The automation generates a detailed prompt instructing Claude Code to:

**Read briefing JSON and:**
1. Analyze top trending stories
2. Provide cultural/political context
3. Compare with Western media coverage
4. Write 1000-1500 word analysis

**Output structured Jekyll post with:**
- Frontmatter (title, date, categories, tags, excerpt, image)
- Opening context paragraph
- Main analysis sections
- "Data Visualizations" section with embedded charts
- "Stakeholder Perspectives" section with 3-5 random personas
- "Key Articles Referenced" section with source links

### Content Guidelines

Defined in `CLAUDE.md`:
- Objective, analytical tone
- Report both Russian and Western perspectives
- Acknowledge biases in sources
- Focus on journalism, not intelligence analysis
- Transparency about being public open-source research

### Anti-Hallucination System

**Source verification:**
- All article URLs come from briefing JSON (not AI-generated)
- Quotes attributed to named sources
- Dates and details preserved from original articles

**Fact checking:**
- Historical context from `knowledge_base/` JSON files
- Cross-reference with multiple sources
- Flag uncertainty when details conflict

### Output Location

`content/drafts/YYYY-MM-DD-analysis.md`

## Stage 5: Auto-Publish & Git Push

### What It Does

1. **Find Latest Draft** in `content/drafts/`
2. **Update Frontmatter:** Change `status: draft` → `status: published`
3. **Move to `_posts/`** directory (Jekyll convention)
4. **Git Commit:** `"AI content: YYYY-MM-DD [automated - local]"`
5. **Git Push:** Triggers GitHub Pages rebuild (~2 minutes)

### Site Publication

- **Hosting:** GitHub Pages (FREE)
- **URL:** https://petesandwich.github.io/Eastbound
- **Rebuild time:** ~2 minutes after push
- **SSL:** Automatic HTTPS via GitHub

## Stage 6: Social Media Distribution

### Twitter/X Post
`scripts/post_to_twitter.py --file _posts/YYYY-MM-DD-analysis.md`

**What it posts:**
- Article title
- Excerpt (first 200 chars)
- Link to published article
- Auto-generated hashtags from article tags

### LinkedIn Post
`scripts/post_to_linkedin.py --file _posts/YYYY-MM-DD-analysis.md`

**What it posts:**
- Article title
- Full excerpt from frontmatter
- Link to published article
- Professional framing for business audience

### API Keys Required

Set in `.env` file:
- `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`
- `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_USER_URN`

**Graceful degradation:** If keys not set, automation continues without social posting.

## Command-Line Options

```bash
# Full automation (default)
python scripts/run_daily_automation.py

# Skip image generation (if already generated)
python scripts/run_daily_automation.py --skip-image

# Skip data visualizations
python scripts/run_daily_automation.py --skip-visuals

# Create draft only, don't publish
python scripts/run_daily_automation.py --draft-only

# Skip social media posting
python scripts/run_daily_automation.py --skip-social

# Verbose output with real-time streaming
python scripts/run_daily_automation.py --verbose
```

## Error Handling

### Stage Failures

**Media monitoring fails:**
- Check RSS feed availability
- Check internet connection
- Review `RSS_SOURCES` dict in `monitor_russian_media.py`

**Image generation fails:**
- Logged as warning, automation continues
- Check GPU availability and CUDA setup
- Review `generate_images_local.py` for SDXL dependencies

**Content generation fails:**
- Check Claude Code CLI is installed: `claude --version`
- Check briefing JSON is valid
- Review prompt template in automation script

**Social media fails:**
- Logged as warning, automation continues
- Check API keys in `.env`
- Check rate limits and account status

### Monitoring

Check daily automation health:
```bash
# View recent git commits (should see daily automated commits)
git log --oneline -10

# Check for generated files
ls research/ | tail -5
ls _posts/ | tail -5
ls images/ | tail -10
```

## Manual Overrides

### Generate Briefing Only
```bash
python scripts/monitor_russian_media.py --output research/test-briefing.json --parallel
```

### Generate Content Only
```bash
# Create custom prompt file, then:
claude --print --output-format text --tools Read,Write,Glob < your_prompt.txt
```

### Publish Existing Draft
```bash
# Manually move draft and push
mv content/drafts/YYYY-MM-DD-analysis.md _posts/
git add _posts/ && git commit -m "Publish: YYYY-MM-DD" && git push
```

## Costs Breakdown

| Component | Technology | Cost |
|-----------|------------|------|
| Media Monitoring | Python + RSS | $0 |
| Image Generation | SDXL (local GPU) | $0 (electricity only) |
| Data Visualization | matplotlib | $0 |
| Content Generation | Claude Code CLI (free tier) | $0 |
| Hosting | GitHub Pages | $0 |
| Social Media APIs | Twitter/X + LinkedIn | $0 (free tier) |
| **TOTAL** | | **$0/month** |

**No GitHub Actions minutes used** - everything runs locally on your machine!

## Related Documentation

- [Briefing Database Structure](briefing-database-structure.md) - How the briefing JSON works
- [Stakeholder Perspective System](stakeholder-perspective-system.md) - Persona generation explained
- [Anti-Hallucination System](anti-hallucination.md) - How we prevent AI fabrication
- [TF-IDF Algorithm](tfidf-algorithm.md) - Keyword extraction deep dive
