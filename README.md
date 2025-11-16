# Eastbound Reports

**Russian and East Asian media analysis for English-speaking audiences**

[![Website](https://img.shields.io/badge/website-live-brightgreen)](https://eastboundreports.github.io/Eastbound)
[![Twitter](https://img.shields.io/twitter/follow/eastboundreport?style=social)](https://twitter.com/eastboundreport)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Automation](https://img.shields.io/badge/automation-modular-success)](Docs/COMPONENT_REGISTRY.md)

---

## 🎯 About

Eastbound Reports is a **modular automation system** that monitors Russian (and optionally East Asian) news sources, generates AI-powered analysis, and publishes insights—all running **locally for FREE**.

**What makes us unique:**
- 🧩 **Modular design** - Pick and choose components you need
- 💰 **$0/month cost** - No API fees, uses Claude Code CLI (free)
- 🔍 **Multi-source verification** - Requires 3+ sources before flagging trends
- 📊 **Data-driven analysis** - TF-IDF keyword extraction, sentiment analysis
- 🤖 **Claude CLI integration** - Use Claude Code as a programmable API
- 🚀 **Flexible automation** - From simple news monitoring to full publishing pipeline

**Core Principles:**
- ✅ Modular and extensible architecture
- ✅ Open source everything (MIT License)
- ✅ Choose your own level of automation
- ✅ Only public, open-source information
- ✅ Independent and transparent

---

## 📚 Documentation

**→ [Docs/INDEX.md](Docs/INDEX.md)** - Complete documentation index

**→ [Docs/COMPONENT_REGISTRY.md](Docs/COMPONENT_REGISTRY.md)** - **Start here!** Component catalog

**→ [Docs/CLAUDE_CLI_API.md](Docs/CLAUDE_CLI_API.md)** - Claude Code CLI integration

---

## ⚡ Quick Start

### Minimal Setup (News Monitoring Only)

```bash
# Clone repository
git clone https://github.com/eastboundreports/Eastbound.git
cd Eastbound

# Install minimal dependencies
pip install feedparser pyyaml

# Monitor news
python scripts/monitor_russian_media.py --output daily.json
```

**What you get:** JSON briefing with articles, keywords, sentiment scores

---

### Simple Automation (Recommended)

```powershell
# Install dependencies
pip install -r requirements.txt

# Run simple automation (5-10 minutes)
.\run_simple_automation.ps1
```

**What happens:**
1. ✅ Monitors Russian media sources
2. ✅ Generates analysis with Claude Code CLI (FREE)
3. ✅ Commits to git
4. ✅ GitHub Pages auto-deploys

**Cost: $0** | **Time: 5-10 min** | **Human effort: 0 min**

---

### Full Custom Pipeline

Mix and match components as needed. See **[Docs/COMPONENT_REGISTRY.md](Docs/COMPONENT_REGISTRY.md)** for:
- 20+ modular components
- Pick-and-choose examples
- Custom pipeline configurations

---

## 🏗️ Modular Architecture

Pick and choose components to build your own automation pipeline:

```
┌──────────────────────────────────────────────────────┐
│              MODULAR COMPONENT SYSTEM                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  📡 Media Monitoring    →  RSS feeds, TF-IDF       │
│                            Multi-source verification │
│                            13-23 sources             │
│                                                      │
│  🤖 Content Generation  →  Claude CLI integration   │
│                            Template system           │
│                            Anti-hallucination        │
│                                                      │
│  📊 Visualization       →  Chart framework          │
│                            Extensible system         │
│                            Brand styling             │
│                                                      │
│  📢 Publishing          →  Twitter, LinkedIn        │
│                            GitHub Pages              │
│                            Git automation            │
│                                                      │
│  📚 Knowledge Base      →  Historical context       │
│                            Search system             │
│                            7 categories              │
│                                                      │
│  🎨 Image Gen (Optional)→  SDXL, LoRA models       │
│                            Local generation          │
│                            CPU/GPU support           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**See:** [Component Registry](Docs/COMPONENT_REGISTRY.md) for complete catalog

---

## ✨ Key Features

### 🤖 Claude CLI Integration
- **FREE AI integration** - Uses Claude Code CLI (no API costs)
- **Programmable API** - Call from Python, PowerShell, Bash
- **JSON output** - Structured responses with metadata
- 📖 See: [Claude CLI API Guide](Docs/CLAUDE_CLI_API.md)

### 📡 Media Monitoring
- **13 Russian sources** - TASS, RT, Kommersant, RIA, etc.
- **+10 East Asian sources** (optional) - China, Japan, Korea, Taiwan
- **TF-IDF keyword extraction** - Statistical topic identification
- **Multi-source verification** - Requires 3+ sources for trends
- 📖 See: [Component Registry](Docs/COMPONENT_REGISTRY.md#media-monitoring)

### 📊 Data & Analysis
- **Anti-hallucination system** - Verified sources only
- **Knowledge base** - Historical context (7 categories)
- **Visualization framework** - Extensible chart system
- **Sentiment analysis** - Keyword-based scoring
- 📖 See: [Briefing Structure](Docs/briefing-database-structure.md)

### 🚀 Flexible Automation
- **Modular components** - Use what you need
- **Simple pipeline** - 5-10 minute automation
- **Full customization** - Mix and match features
- **Windows/Linux support** - Cross-platform scripts
- 📖 See: [Content Pipeline](Docs/content-generation-pipeline.md)

### 🌐 Publishing Options
- **GitHub Pages** - Free static site hosting
- **Twitter/LinkedIn** - Social media integration
- **Git automation** - Auto-commit and push
- **Jekyll templating** - Customizable themes
- 🌐 Visit: [eastboundreports.github.io/Eastbound](https://eastboundreports.github.io/Eastbound)

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
git clone https://github.com/eastboundreports/Eastbound.git
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

Read more: [About Page](https://eastboundreports.github.io/eastbound/about)

---

## License

- **Code:** MIT License
- **Content:** CC BY-NC 4.0

See [LICENSE](LICENSE) for details.

---

## Links

- **Website:** https://eastboundreports.github.io/eastbound
- **Twitter:** https://twitter.com/eastboundreport
- **GitHub:** https://github.com/eastboundreports/eastbound

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
