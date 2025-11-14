# Eastbound Reports

**Russian and East Asian media analysis for English-speaking audiences**

[![Website](https://img.shields.io/badge/website-live-brightgreen)](https://petesandwich.github.io/Eastbound)
[![Twitter](https://img.shields.io/twitter/follow/eastboundreport?style=social)](https://twitter.com/eastboundreport)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Automation](https://img.shields.io/badge/automation-100%25-success)](Docs/content-generation-pipeline.md)

---

## 🎯 About

Eastbound Reports is a **fully automated media analysis platform** that monitors Russian (and optionally East Asian) news sources, generates AI-powered analysis, and publishes daily insights—all running **locally for FREE**.

**What makes us unique:**
- 🤖 **100% automated** - Runs daily without manual intervention
- 💰 **$0/month cost** - No API fees, no cloud hosting charges
- 🔍 **Multi-source verification** - Requires 3+ sources before flagging trends
- 🌍 **Global stakeholder perspectives** - Shows how narratives affect real people worldwide
- 📊 **Data-driven analysis** - TF-IDF keyword extraction, sentiment analysis, visualizations
- 🎨 **Local AI image generation** - SDXL creates news illustrations (no API costs)

**Core Principles:**
- ✅ Completely independent and transparent
- ✅ Open source everything (MIT License)
- ✅ Objective reporting without partisan positions
- ✅ Only public, open-source information
- ✅ Journalism/research, NOT intelligence work

---

## ⚡ Quick Start (3 Steps)

### Option 1: Use the Automation (Recommended)

```bash
# Clone repository
git clone https://github.com/PeteSandwich/Eastbound.git
cd Eastbound

# Install dependencies
pip install -r requirements.txt

# Run daily automation (30-40 minutes)
python scripts/run_daily_automation.py
```

**What happens:**
1. ✅ Monitors 13 Russian media sources (or 23+ with `--include-asia`)
2. ✅ Generates data visualizations
3. ✅ Creates 1000-1500 word analysis with Claude Code (FREE)
4. ✅ Generates SDXL image based on article title
5. ✅ Auto-publishes to GitHub Pages
6. ✅ Posts to Twitter/X and LinkedIn

**Cost: $0** | **Time: 30-40 min** | **Human effort: 0 min**

### Option 2: Manual Content Creation

```bash
# Create a draft
python scripts/create_draft.py --type analysis --title "Your Title"

# Edit the draft
# Edit file in content/drafts/

# Move to _posts when ready
mv content/drafts/YYYY-MM-DD-your-title.md _posts/

# Commit and push
git add . && git commit -m "New post" && git push
```

---

## 🏗️ The System

This is a **fully automated, open-source publishing platform** that runs **entirely on your local machine**:

```
┌─────────────────────────────────────────────────────────────┐
│              AUTOMATED PIPELINE (6 STAGES)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Monitor Media      →  13-23 RSS feeds (parallel)       │
│                           TF-IDF keyword extraction         │
│                           Multi-source verification         │
│                           ~5 minutes                        │
│                                                             │
│  2. Data Visuals       →  Keywords, sources, stats charts  │
│                           Matplotlib + Seaborn              │
│                           ~30 seconds                       │
│                                                             │
│  3. AI Content         →  Claude Code (FREE!)              │
│                           1000-1500 word analysis           │
│                           Stakeholder perspectives          │
│                           ~2-3 minutes                      │
│                                                             │
│  4. SDXL Image         →  Stable Diffusion XL (local GPU)  │
│                           Based on article title            │
│                           ~15-20 minutes                    │
│                                                             │
│  5. Auto-Publish       →  Move to _posts/                  │
│                           Git commit & push                 │
│                           GitHub Pages rebuild              │
│                           ~30 seconds                       │
│                                                             │
│  6. Social Media       →  Twitter/X + LinkedIn posting     │
│                           Auto-generated excerpts           │
│                           ~10 seconds                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Total Runtime:** ~30-40 minutes | **Cost:** $0/month | **Hosting:** GitHub Pages (free)

---

## ✨ Features

### 🤖 AI-Powered Content Generation
- **Multi-source monitoring:** 13 Russian media sources (TASS, RT, Kommersant, etc.)
- **Optional East Asian sources:** +10 sources (China, Japan, NK, SK, Taiwan)
- **Claude Code integration:** FREE AI content generation (no API costs!)
- **TF-IDF keyword extraction:** Statistically identifies significant topics
- **Multi-source verification:** Requires 3+ sources to flag trending stories
- **Anti-hallucination system:** All article URLs extracted from briefing JSON (not AI-generated)
- **Knowledge base grounding:** 17+ historical context files prevent AI fabrication
- **Article structure:** 1000-1500 words with sources, context, Western comparison
- 📖 See: [Content Generation Pipeline](Docs/content-generation-pipeline.md)

### 👥 Stakeholder Perspective System
- **Random persona generation:** 100+ occupations, 40+ countries, 10 global regions
- **Topic-aware stakes:** Ukraine → refugees, Energy → oil workers, NATO → military families
- **Humanizes geopolitics:** Shows how Russian narratives affect real people worldwide
- **4 personas per article** with individualized analysis tied to that day's stories
- **NOT opinion polls** - Concrete examples of material stakes, not representative samples
- 📖 See: [Stakeholder System Documentation](Docs/stakeholder-perspective-system.md)

### 📊 Data Visualizations
- **Trending topics chart:** Top 10 keywords by TF-IDF × source count
- **Source distribution:** Pie chart showing which outlets published most
- **Statistics panel:** Total articles, sources, trending topics
- **All charts auto-generated:** Matplotlib + Seaborn, embedded in every article
- **Local SDXL image generation:** Stable Diffusion XL creates news illustrations
- **Article-aware prompts:** Images generated from article title (not generic keywords)
- 📖 See: [Visualization Framework](scripts/generate_visuals.py)

### 📚 Knowledge Base System
- **17+ comprehensive entries** across events, figures, policies, narratives
- **Dual perspectives:** Russian AND Western viewpoints documented
- **Prevents hallucinations:** AI references verified historical facts
- **Examples:** 2022 Ukraine invasion, Putin worldview, NATO expansion narrative
- **Narrative tracking:** How Russian messaging evolves over time
- 📖 See: [Knowledge Base](knowledge_base/)

### 🚀 Fully Automated Local Pipeline
- **Windows Task Scheduler:** Runs daily at 6:00 AM (or on-demand)
- **Parallel RSS fetching:** 8 workers, monitors 13-23 sources in 5-15 min
- **Zero API costs:** Claude Code CLI (free tier), local SDXL (no cloud fees)
- **Auto-publishing:** Moves drafts to `_posts/`, commits, pushes to GitHub
- **Social media posting:** Twitter/X + LinkedIn with auto-generated excerpts
- **Graceful error handling:** Continues on failures (e.g., image gen timeout)
- 📖 See: [Pipeline Documentation](Docs/content-generation-pipeline.md)

### 🌐 Self-Hosted Website
- **Jekyll static site** on GitHub Pages (free hosting)
- **Responsive design** with SEO optimization
- **RSS feed** built-in for subscribers
- **Custom domain support** (optional)
- **Automatic rebuilds** on git push (~2 minutes)
- **Cost:** $0/month (GitHub Pages is free)
- 🌐 Visit: [petesandwich.github.io/Eastbound](https://petesandwich.github.io/Eastbound)

### 📱 Social Media Integration
- **Twitter/X threads:** Auto-generated with article excerpts
- **LinkedIn posts:** Professional framing for business audiences
- **Configurable:** Skip social posting with `--skip-social` flag
- **Graceful degradation:** Continues without API keys
- **Direct links:** Posts link back to full analysis on website
- 📖 See: [Social Media Scripts](scripts/)

---

## 📋 Setup Guide

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/PeteSandwich/Eastbound.git
cd Eastbound
pip install -r requirements.txt
```

**Required dependencies:**
- Python 3.8+
- feedparser (RSS parsing)
- scikit-learn (TF-IDF)
- matplotlib, seaborn (charts)
- diffusers, torch (SDXL)
- tweepy (Twitter API, optional)
- python-dotenv (.env support)

### 2. Install Claude Code CLI

```bash
# Install Claude Code (free tier)
# Visit: https://claude.ai/code for installation instructions
claude --version
```

### 3. Configure Environment Variables (Optional)

Create `.env` file for social media posting:

```bash
# Twitter/X (optional)
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret

# LinkedIn (optional)
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_USER_URN=your_urn
```

**Note:** Automation works without API keys (skips social posting gracefully)

### 4. Enable GitHub Pages

1. Fork this repository
2. Go to **Settings** → **Pages**
3. **Source:** Deploy from a branch → `main` → `/` (root)
4. Click **Save**

Your site will be live at: `https://YOUR_USERNAME.github.io/Eastbound`

### 5. Set Up Windows Task Scheduler (Optional)

For daily automation at 6:00 AM:

```powershell
# Open Task Scheduler → Create Basic Task
# Name: "Eastbound Daily Automation"
# Trigger: Daily at 6:00 AM
# Action: Start a program
#   Program: python
#   Arguments: scripts/run_daily_automation.py
#   Start in: C:\Path\To\Eastbound
```

---

## 📖 Documentation

**Core System Docs** (in `Docs/` folder):
- **[README.md](Docs/README.md)** - Complete system overview & command reference
- **[Content Generation Pipeline](Docs/content-generation-pipeline.md)** - 6-stage automation explained
- **[Briefing Database](Docs/briefing-database-structure.md)** - How the 200-400 article database works
- **[Stakeholder System](Docs/stakeholder-perspective-system.md)** - Random persona generation philosophy
- **[SDXL LoRA Recommendations](Docs/sdxl-lora-recommendations.md)** - Image quality enhancements

**Legacy Docs** (older GitHub Actions approach):
- [Quick Reference](QUICK_REFERENCE.md) - Common tasks (may be outdated)
- [Automation Setup](AUTOMATION_SETUP.md) - GitHub Actions setup (deprecated)
- [Phase 1 Game Plan](PHASE1_GAMEPLAN.md)** - Original strategy

---

## 📁 Project Structure

```
Eastbound/
├── Docs/                           # 📚 System documentation
│   ├── README.md                   # Complete overview
│   ├── content-generation-pipeline.md
│   ├── briefing-database-structure.md
│   ├── stakeholder-perspective-system.md
│   └── sdxl-lora-recommendations.md
│
├── scripts/                        # 🤖 Automation scripts
│   ├── run_daily_automation.py     # Main orchestrator (6 stages)
│   ├── monitor_russian_media.py    # RSS + TF-IDF extraction
│   ├── generate_images_local.py    # SDXL image generation
│   ├── generate_visuals.py         # Data visualization charts
│   ├── generate_stakeholder_personas.py  # Random personas
│   ├── post_to_twitter.py          # Twitter/X posting
│   ├── post_to_linkedin.py         # LinkedIn posting
│   └── config.py                   # Configuration
│
├── research/                       # 📊 Daily briefing JSON files
│   └── YYYY-MM-DD-briefing.json    # 200-400 articles + trending analysis
│
├── images/                         # 🎨 Generated images
│   ├── YYYY-MM-DD-generated.png    # SDXL hero image
│   ├── YYYY-MM-DD-keywords.png     # Trending topics chart
│   ├── YYYY-MM-DD-sources.png      # Source distribution
│   └── YYYY-MM-DD-stats.png        # Statistics panel
│
├── content/drafts/                 # ✏️ Draft articles (pre-publishing)
├── _posts/                         # 📰 Published articles (Jekyll)
│
├── knowledge_base/                 # 🧠 Historical context
│   ├── events/*.json               # Historical events
│   ├── figures/*.json              # Key political figures
│   ├── narratives/*.json           # Russian narrative themes
│   └── policies/*.json             # Policy backgrounds
│
├── _layouts/                       # 🎨 Jekyll templates
├── assets/css/                     # Stylesheets
├── _config.yml                     # Jekyll configuration
├── CLAUDE.md                       # AI content guidelines
└── README.md                       # This file
```

---

## ⚙️ Command Reference

### Full Automation (Recommended)
```bash
# Run complete pipeline (30-40 min)
python scripts/run_daily_automation.py

# Include East Asian sources (15 min longer)
python scripts/run_daily_automation.py --include-asia

# Skip image generation (save 15-20 min)
python scripts/run_daily_automation.py --skip-image

# Draft only (don't publish)
python scripts/run_daily_automation.py --draft-only

# Skip social media posting
python scripts/run_daily_automation.py --skip-social

# Verbose output with real-time streaming
python scripts/run_daily_automation.py --verbose
```

### Individual Components
```bash
# 1. Monitor media only
python scripts/monitor_russian_media.py --output research/briefing.json --parallel
python scripts/monitor_russian_media.py --output research/briefing.json --parallel --include-asia

# 2. Generate visualizations only
python scripts/generate_visuals.py --briefing research/2025-11-13-briefing.json --output images/

# 3. Generate stakeholder personas
python scripts/generate_stakeholder_personas.py --briefing research/briefing.json --count 4

# 4. Generate SDXL image only
python scripts/generate_images_local.py --briefing research/briefing.json --output images/ --auto --steps 50
python scripts/generate_images_local.py --prompt "Your custom prompt" --output images/test.png --steps 50

# 5. Post to social media
python scripts/post_to_twitter.py --file _posts/2025-11-13-analysis.md
python scripts/post_to_linkedin.py --file _posts/2025-11-13-analysis.md
```

### Manual Content Creation
```bash
# Create custom draft
python scripts/create_draft.py --type analysis --title "Your Title"

# Edit draft
# Edit file in content/drafts/

# Publish manually
mv content/drafts/YYYY-MM-DD-title.md _posts/
git add . && git commit -m "New post" && git push
```

---

## 🎨 Customization

### Change Site Name/Description

Edit `_config.yml`:
```yaml
title: Your Site Name
description: Your description
url: "https://yourusername.github.io/Eastbound"
twitter_username: your_handle
baseurl: "/Eastbound"
```

### Customize Content Guidelines

Edit `CLAUDE.md` to change AI content generation instructions:
- Tone and style
- Article structure
- Source requirements
- Analysis frameworks

### Add New RSS Sources

Edit `scripts/monitor_russian_media.py`:
```python
RSS_SOURCES = {
    'Your Source': 'https://example.com/rss.xml',
}

# Or add to East Asian sources
EAST_ASIA_SOURCES = {
    'Your Asian Source': 'https://example.com/rss.xml',
}
```

### Custom Domain

1. Add `CNAME` file with your domain
2. Configure DNS with your provider
3. Update `url` in `_config.yml`

See: [GitHub Pages Custom Domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

### Modify Design

Edit files in `_layouts/` and `assets/css/` to customize appearance.

---

## Content Guidelines

### Weekly Analysis Posts

1. **Hook:** What happened and why it matters
2. **Russian Perspective:** Multiple sources, key quotes
3. **Context:** Background Western audiences miss
4. **Comparison:** How Western media differs
5. **Implications:** For policy, business, culture
6. **Sources:** Full citations with links

### Translation Posts

1. **Introduction:** Who, when, why it matters
2. **Translation:** Full accurate translation
3. **Translator's Notes:** Cultural/linguistic context
4. **Analysis:** What this reveals
5. **Sources:** Links to originals

---

## 🛠️ Tech Stack

**Core Technologies:**
- **Content:** Markdown with YAML frontmatter
- **Website:** Jekyll static site generator (Ruby)
- **Hosting:** GitHub Pages (free, automatic SSL)
- **Automation:** Python + Windows Task Scheduler (local)

**AI & Machine Learning:**
- **Content generation:** Claude Code CLI (free tier, no API costs)
- **Image generation:** Stable Diffusion XL (local GPU, 15-20 min/image)
- **Keyword extraction:** TF-IDF via scikit-learn
- **Future:** LoRA finetunes for news-appropriate aesthetics

**Data Processing:**
- **RSS parsing:** feedparser (parallel fetching, 8 workers)
- **Visualizations:** Matplotlib + Seaborn
- **Deduplication:** Fuzzy string matching (85% threshold)
- **Anti-hallucination:** JSON-based knowledge base

**Social Media:**
- **Twitter/X:** Tweepy (v2 API)
- **LinkedIn:** Direct API integration

**Languages:**
- Python 3.8+ (automation scripts)
- Ruby (Jekyll backend)
- Liquid (templating)
- Bash/PowerShell (task scheduling)

---

## Contributing

Contributions welcome! This is an open-source project.

**Ways to contribute:**
- Improve documentation
- Enhance automation scripts
- Suggest features
- Report bugs
- Share content ideas

**To contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Ethics & Independence

**We are:**
- ✅ Completely independent
- ✅ Transparent in our methods
- ✅ Using only public information
- ✅ Objective in our analysis

**We are NOT:**
- ❌ Affiliated with any government
- ❌ Working with intelligence agencies
- ❌ Handling classified information
- ❌ Taking partisan positions

Read more: [About Page](https://petesumners.github.io/eastbound/about)

---

## License

- **Code:** MIT License
- **Content:** CC BY-NC 4.0

See [LICENSE](LICENSE) for details.

---

## Links

- **Website:** https://petesumners.github.io/eastbound
- **Twitter:** https://twitter.com/eastboundreport
- **GitHub:** https://github.com/PeteSumners/eastbound

---

## 🗺️ Roadmap

**✅ Phase 1 Complete (MVP - Q4 2024)**
- [x] Local automation pipeline (6 stages, $0 cost)
- [x] Jekyll website on GitHub Pages
- [x] Twitter/X + LinkedIn automation
- [x] RSS feed monitoring (13 Russian sources)
- [x] TF-IDF keyword extraction + multi-source verification
- [x] Data visualization framework (3 chart types)
- [x] Local SDXL image generation
- [x] Claude Code integration (free tier)
- [x] Stakeholder perspective system
- [x] Knowledge base (17+ entries)
- [x] Anti-hallucination validation
- [x] Article-aware image prompts (SDXL after content)
- [x] East Asian source support (10 sources: China, Japan, NK, SK, Taiwan)
- [x] Comprehensive documentation (Docs/ folder)

**🚧 Phase 2 In Progress (Growth - Q1 2025)**
- [ ] SDXL LoRA finetune testing (Touch of Realism, Film Photography)
- [ ] Sentiment analysis per article (positive/negative/neutral)
- [ ] Named entity recognition (people, places, organizations)
- [ ] Historical stakeholder tracking ("What did Elena think last week?")
- [ ] Persistent 200-person persona pool (select subset daily)
- [ ] Article categorization (conflict, energy, politics, economy)
- [ ] Custom domain setup

**📅 Phase 3 Planned (Scale - Q2-Q4 2025)**
- [ ] Enhanced website (Next.js migration for interactivity)
- [ ] Stripe payment processing (premium tier: $20-50/month)
- [ ] Corporate subscriptions ($500-2000/month)
- [ ] Email newsletter integration
- [ ] Advanced charts (sentiment timeline, heatmaps, network graphs)
- [ ] Search functionality
- [ ] Archive by topic/date/source
- [ ] Analytics dashboard
- [ ] Team collaboration tools
- [ ] Custom CMS
- [ ] Train custom LoRA on historical Soviet photography

**🔮 Future Considerations (Years 2-3)**
- Multi-language support (Russian, Chinese, Japanese)
- API for third-party integrations
- Mobile app
- Real-time breaking news alerts
- Comparative analysis dashboard (Russian vs. Western narratives)
- Academic research partnerships

---

**Built with transparency. Powered by open source.** 🚀

*Questions? Open an issue or reach out on Twitter!*
