# Quick Start Guide

Get up and running with Eastbound in minutes.

## 🎯 Choose Your Path

### Path 1: Just Monitor News (2 minutes)

**What you get:** JSON briefing files with articles, keywords, and sentiment

```bash
# Install
pip install feedparser pyyaml

# Run
python scripts/monitor_russian_media.py --output daily.json

# Output: daily.json with 200-400 articles
```

**Use case:** You just want the data, you'll analyze it yourself

---

### Path 2: Automated Analysis (10 minutes setup, 5-10 min per run)

**What you get:** Complete analysis posts automatically generated and published

```powershell
# Install
pip install -r requirements.txt

# Setup daily automation (Windows)
.\setup_simple_task.ps1

# Or run manually
.\run_simple_automation.ps1
```

**Pipeline:**
1. Monitor Russian media → JSON briefing
2. Claude CLI analysis → Markdown post
3. Git commit & push → GitHub Pages

**Use case:** You want fully automated daily reports

---

### Path 3: Custom Pipeline (Variable)

**What you get:** Exactly what you build

**See:** [COMPONENT_REGISTRY.md](COMPONENT_REGISTRY.md) for component catalog

**Use case:** You want specific features, custom workflow

---

## 📦 Installation

### Minimal (News Only)
```bash
pip install feedparser pyyaml
```

### Standard (News + Analysis)
```bash
pip install -r requirements.txt
```

### Full (All Features)
```bash
pip install -r requirements.txt
pip install -r requirements-images.txt  # Image generation (heavy, ~2GB)
python -m spacy download en_core_web_sm  # NER (optional)
```

---

## 🚀 First Run

### Test Media Monitoring

```bash
python scripts/monitor_russian_media.py --output test-briefing.json --parallel
```

**Expected output:**
- `test-briefing.json` with 200-400 articles
- Console shows progress: "Fetching from TASS...", etc.
- Duration: ~2-5 minutes

**Verify:**
```bash
python -m json.tool test-briefing.json | head -20
```

Should show JSON with `articles`, `trending_stories`, `keywords`

---

### Test Claude CLI Integration

```bash
echo "What is 2+2?" | claude --print
```

**Expected output:** `4`

**Test JSON mode:**
```bash
echo "List 3 countries" | claude --print --output-format json
```

Should return JSON with `result`, `session_id`, `total_cost_usd`

---

### Test Simple Automation

```powershell
# Windows
.\run_simple_automation.ps1

# Linux/Mac
bash scripts/local_dev.sh
```

**Expected output:**
- Briefing JSON created
- Analysis post in `_posts/YYYY-MM-DD-analysis.md`
- Git commit created
- Duration: ~5-10 minutes

---

## 🔧 Configuration

### Optional: Social Media

Create `.env` file:

```bash
# Twitter/X
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
TWITTER_BEARER_TOKEN=your_bearer

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_USER_URN=your_urn
```

### Optional: East Asian Sources

```bash
python scripts/monitor_russian_media.py --output daily.json --east-asian
```

Adds 10 sources: China Daily, Xinhua, Yomiuri, Asahi, etc.

---

## ✅ Health Check

Verify everything is working:

```bash
python scripts/health_check.py
```

**Checks:**
- RSS feed accessibility
- Recent briefings exist
- Drafts created
- Knowledge base populated
- Published posts

**Exit codes:**
- 0 = All healthy ✅
- 1 = Issues found ⚠️

---

## 📚 Next Steps

### Learn the Components
→ [COMPONENT_REGISTRY.md](COMPONENT_REGISTRY.md)

### Integrate Claude CLI
→ [CLAUDE_CLI_API.md](CLAUDE_CLI_API.md)

### Understand the Data
→ [briefing-database-structure.md](briefing-database-structure.md)

### Build Custom Pipeline
→ [content-generation-pipeline.md](content-generation-pipeline.md)

---

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "claude: command not found"
- Windows: Use `claude.cmd` instead of `claude`
- Linux/Mac: Ensure Claude Code is in PATH
- Check: `claude --version`

### "Insufficient articles" (<50 fetched)
- Check internet connection
- Try `--east-asian` flag for more sources
- Some feeds may be geo-blocked

### "Permission denied" (Git)
```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

### "CUDA error" (Image generation)
- Optional feature, can skip
- Requires NVIDIA GPU with CUDA
- Or use CPU mode (much slower)

---

## 💡 Tips

### Development Workflow

```bash
# 1. Create test briefing
python scripts/monitor_russian_media.py --output test.json

# 2. Test individual components
python scripts/advanced_keywords.py  # Test keyword extraction
python scripts/create_draft.py --title "Test"  # Test draft creation

# 3. Review output
cat content/drafts/test.md
```

### Cost Optimization

- **Minimal setup:** $0/month (just news monitoring)
- **Simple automation:** $0/month (Claude CLI is free)
- **Full automation:** ~$5/month (electricity for image gen)

### Performance Tuning

```bash
# Fast: Haiku model
echo "prompt" | claude --print --model haiku

# Balanced: Sonnet (default)
echo "prompt" | claude --print --model sonnet

# Best: Opus
echo "prompt" | claude --print --model opus
```

---

## 📖 Command Cheat Sheet

```bash
# Monitor news
python scripts/monitor_russian_media.py --output daily.json --parallel

# Create draft
python scripts/create_draft.py --type weekly-analysis --title "Title"

# Post to Twitter
python scripts/post_to_twitter.py --file _posts/post.md --dry-run

# Post to LinkedIn
python scripts/post_to_linkedin.py --file _posts/post.md

# Health check
python scripts/health_check.py

# Query knowledge base
python scripts/query_knowledge_base.py --keywords "topic"

# Load historical context
python scripts/load_historical_context.py --output context.json
```

---

## 🎓 Learning Resources

### Beginner
1. Run Path 1 (news monitoring only)
2. Examine JSON output
3. Read [COMPONENT_REGISTRY.md](COMPONENT_REGISTRY.md)

### Intermediate
1. Run Path 2 (simple automation)
2. Review generated posts
3. Read [CLAUDE_CLI_API.md](CLAUDE_CLI_API.md)

### Advanced
1. Build custom pipeline
2. Create new components
3. Read [briefing-database-structure.md](briefing-database-structure.md)

---

## 🆘 Getting Help

1. **Component-specific:** `python scripts/<script>.py --help`
2. **Claude CLI:** `claude --help`
3. **Documentation:** See [INDEX.md](INDEX.md)
4. **GitHub Issues:** Report bugs

---

**Ready to start?** Pick a path above and follow the steps!

**Questions?** Check [COMPONENT_REGISTRY.md](COMPONENT_REGISTRY.md) or [INDEX.md](INDEX.md)
