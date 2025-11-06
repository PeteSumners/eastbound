# Eastbound Reports

**Russian media analysis and translation for English-speaking audiences**

[![Website](https://img.shields.io/badge/website-live-brightgreen)](https://petesumners.github.io/eastbound)
[![Twitter](https://img.shields.io/twitter/follow/eastboundreport?style=social)](https://twitter.com/eastboundreport)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## About

Eastbound Reports provides accurate translations, context, and analysis of Russian media sources. We help English-speaking audiences understand Russian perspectives, compare them with Western coverage, and navigate the complex information landscape.

**Core Principles:**
- ✅ Completely independent and transparent
- ✅ Open source everything
- ✅ Objective reporting without partisan positions
- ✅ Only public, open-source information

---

## The System

This is a **fully automated, open-source publishing platform** that runs entirely on GitHub:

```
Create draft → Edit content → Schedule → Publish
                                           ↓
                        Website updates automatically
                                           ↓
                        Twitter thread posts automatically
```

**Cost: $0/month** | **Hosting: GitHub Pages** | **Automation: GitHub Actions**

---

## Features

### 🤖 Fully Automated
- Create drafts via GitHub Actions or locally
- Schedule posts with date/time
- Automatic publishing when scheduled time arrives
- Auto-generates Twitter threads from content
- Website rebuilds automatically on publish

### 🌐 Self-Hosted Website
- Clean, fast Jekyll site on GitHub Pages
- Responsive design
- RSS feed built-in
- SEO optimized
- Custom domain support

### 📱 Social Integration
- Auto-posts Twitter threads with key quotes
- Configurable thread generation
- Links back to website

### 📝 Content Templates
- Weekly analysis template (1000-1500 words)
- Translation template (with context/analysis)
- Structured frontmatter for metadata

### 📊 Data Visualizations
- Automated chart generation for every post
- 6 chart types with extensible framework
- Internet image fetching (Unsplash, Wikipedia)
- AI-friendly documentation for adding new charts
- See: [AI_VISUALIZATION_GUIDE.md](AI_VISUALIZATION_GUIDE.md)

---

## Quick Start

### 1. Fork This Repository

Click "Fork" in the top right to create your own copy.

### 2. Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. **Source:** Deploy from a branch
3. **Branch:** `main` → `/ (root)`
4. Click **Save**

Your site will be live at: `https://YOUR_USERNAME.github.io/eastbound`

### 3. Configure Secrets (Optional)

For Twitter automation, add these secrets in **Settings** → **Secrets** → **Actions**:

- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`

Get credentials at: https://developer.twitter.com/en/portal/dashboard

### 4. Create Your First Post

**Via GitHub Web:**
1. Go to **Actions** → **Create New Draft**
2. Fill in title and type
3. Edit the draft in `content/drafts/`
4. Move to `content/scheduled/` when ready
5. Change `status: draft` to `status: scheduled`

**Locally:**
```bash
git clone https://github.com/YOUR_USERNAME/eastbound.git
cd eastbound
pip install -r requirements.txt

python scripts/create_draft.py --type weekly-analysis --title "Your Title"
# Edit content/drafts/your-file.md
# Move to content/scheduled/ and change status
git add content/
git commit -m "New post"
git push
```

---

## Documentation

- **[Quick Reference](QUICK_REFERENCE.md)** - Common tasks and commands
- **[Automation Setup](AUTOMATION_SETUP.md)** - Technical details
- **[Phase 1 Game Plan](PHASE1_GAMEPLAN.md)** - Strategy and goals

---

## Content Structure

```
eastbound/
├── content/
│   ├── drafts/          # Work in progress
│   ├── scheduled/       # Ready to publish
│   └── published/       # Live on website
├── images/              # Generated visualizations
├── templates/
│   ├── weekly-analysis.md
│   └── translation.md
├── scripts/
│   ├── create_draft.py
│   ├── post_to_twitter.py
│   ├── visualization_framework.py  # Chart library
│   ├── generate_visuals.py         # Generate all charts
│   ├── fetch_images.py             # Internet image fetching
│   └── example_charts.py           # Examples for AI
├── _layouts/            # Jekyll templates
├── .github/workflows/   # Automation
├── AI_VISUALIZATION_GUIDE.md  # Guide for future AI
└── _config.yml         # Site configuration
```

---

## Workflow

### Publishing Flow

```
1. Create draft (GitHub Actions or locally)
   ↓
2. Edit content
   ↓
3. Set date/time, change status to "scheduled"
   ↓
4. Move to content/scheduled/
   ↓
5. Automation checks hourly (at :00)
   ↓
6. When time arrives:
   - Moves to content/published/
   - Website rebuilds automatically
   - Twitter thread posts (if enabled)
   - Commits changes to git
```

### Manual Publishing

For immediate publishing:
1. **Actions** → **Manual Publish Post**
2. Enter filename
3. Choose whether to skip Twitter
4. Publishes instantly

---

## Customization

### Change Site Name/Description

Edit `_config.yml`:
```yaml
title: Your Site Name
description: Your description
url: "https://yourusername.github.io/eastbound"
twitter_username: your_handle
```

### Custom Domain

1. Add `CNAME` file with your domain
2. Configure DNS with your provider
3. Update `url` in `_config.yml`

See: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site

### Modify Design

Edit files in `_layouts/` and `assets/css/` to customize the look and feel.

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

## Tech Stack

- **Content:** Markdown with YAML frontmatter
- **Website:** Jekyll static site generator
- **Hosting:** GitHub Pages (free)
- **Automation:** GitHub Actions
- **Social:** Twitter API v2 via Tweepy
- **Visualizations:** Matplotlib, Seaborn
- **Image Sources:** Unsplash API, Wikipedia API
- **Languages:** Python, Ruby, Liquid templates

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

## Roadmap

- [x] Automated publishing system
- [x] Jekyll website on GitHub Pages
- [x] Twitter automation
- [x] RSS feed
- [x] Data visualization framework
- [x] Automated chart generation
- [x] Internet image fetching
- [ ] Email newsletter integration
- [ ] Search functionality
- [ ] Archive by topic/date
- [ ] Analytics integration
- [ ] Custom domain
- [ ] Advanced charts (sentiment timeline, heatmaps)

---

**Built with transparency. Powered by open source.** 🚀

*Questions? Open an issue or reach out on Twitter!*
