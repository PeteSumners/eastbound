# Eastbound Component Registry

A modular catalog of all automation components. Pick and choose what you need.

## Quick Start

### Minimal Setup (News Analysis Only)
```bash
# Install dependencies
pip install -r requirements.txt

# Run media monitoring
python scripts/monitor_russian_media.py --output research/2025-11-16-briefing.json

# Generate analysis (manual or with Claude CLI)
# See: Docs/CLAUDE_CLI_API.md
```

### Full Automation
```powershell
# Setup scheduled daily automation
.\setup_simple_task.ps1

# Or run manually
.\run_simple_automation.ps1
```

---

## Component Catalog

### 🔍 Media Monitoring

#### `monitor_russian_media.py`
**Purpose**: Monitor Russian and East Asian media outlets via RSS feeds

**Usage**:
```bash
python scripts/monitor_russian_media.py \
  --output research/2025-11-16-briefing.json \
  --parallel \
  --east-asian
```

**Features**:
- 13 Russian media sources (TASS, RIA, RT, Kommersant, etc.)
- Optional 10 East Asian sources (China, Japan, Korea, Taiwan)
- Sentiment analysis (keyword-based scoring)
- TF-IDF keyword extraction
- Parallel feed fetching

**Output**: JSON briefing with articles, keywords, sentiment scores

**Dependencies**: `feedparser`, `advanced_keywords`

**Standalone**: ✅ Yes - can run independently

---

#### `advanced_keywords.py`
**Purpose**: Extract meaningful keywords using TF-IDF and NER

**Usage**:
```python
from scripts.advanced_keywords import extract_enhanced_keywords

keywords = extract_enhanced_keywords(
    articles=article_list,
    top_n=20,
    use_ner=True  # Requires spacy
)
```

**Features**:
- TF-IDF (Term Frequency-Inverse Document Frequency)
- Bigram extraction (2-word phrases)
- Named Entity Recognition (optional, requires spaCy)
- Geopolitical term boosting

**Dependencies**: `sklearn`, `spacy` (optional)

**Standalone**: ⚠️ Library - imported by other scripts

---

### 📝 Content Creation

#### `create_draft.py`
**Purpose**: Generate draft articles from templates

**Usage**:
```bash
# Weekly analysis
python scripts/create_draft.py \
  --type weekly-analysis \
  --title "Your Title Here"

# Translation post
python scripts/create_draft.py \
  --type translation \
  --title "Translation Title" \
  --schedule 3  # Schedule 3 days ahead
```

**Features**:
- Template-based generation (`templates/weekly-analysis.md`, `templates/translation.md`)
- Auto-slugification (converts title to URL-friendly format)
- YAML frontmatter with metadata
- Scheduling support

**Output**: Markdown file in `content/drafts/YYYY-MM-DD-slug.md`

**Dependencies**: `pyyaml`, `markdown`, `config`

**Standalone**: ✅ Yes

---

#### `validate_and_fix.py`
**Purpose**: Anti-hallucination system for AI-generated content

**Usage**:
```python
from scripts.validate_and_fix import validate_and_fix_content

fixed_content = validate_and_fix_content(
    content=raw_markdown,
    date="2025-11-16"
)
```

**Features**:
- Fixes date hallucinations (wrong years)
- Validates article structure (required sections)
- Warns about potentially fake sources
- Injects verified facts

**Dependencies**: `re`, `datetime`

**Standalone**: ⚠️ Library - imported by other scripts

---

### 📢 Publishing

#### `post_to_twitter.py`
**Purpose**: Post articles to Twitter/X as threads

**Usage**:
```bash
# Post article
python scripts/post_to_twitter.py \
  --file _posts/2025-11-16-analysis.md

# Dry run (preview without posting)
python scripts/post_to_twitter.py \
  --file _posts/2025-11-16-analysis.md \
  --dry-run
```

**Features**:
- Parses markdown frontmatter
- Generates Twitter threads from article sections
- Dry-run mode for testing
- Hashtag support

**Requires**: Twitter API credentials in `.env`
```
TWITTER_API_KEY
TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
TWITTER_BEARER_TOKEN
```

**Dependencies**: `tweepy`, `pyyaml`

**Standalone**: ✅ Yes

---

#### `post_to_linkedin.py`
**Purpose**: Post articles to LinkedIn

**Usage**:
```bash
# Post article
python scripts/post_to_linkedin.py \
  --file _posts/2025-11-16-analysis.md

# Delete post
python scripts/post_to_linkedin.py \
  --delete POST_ID
```

**Features**:
- LinkedIn API v2 integration
- Clean preview text extraction
- Post deletion support

**Requires**: LinkedIn credentials in `.env`
```
LINKEDIN_ACCESS_TOKEN
LINKEDIN_USER_URN
```

**Dependencies**: `requests`, `pyyaml`

**Standalone**: ✅ Yes

---

#### `post_announcement.py`
**Purpose**: Post announcement thread to Twitter

**Usage**:
```bash
python scripts/post_announcement.py
```

**Features**:
- Pre-written 4-tweet announcement thread
- Mission statement
- Tech stack overview
- Coming soon features

**Requires**: Twitter API credentials (same as `post_to_twitter.py`)

**Standalone**: ✅ Yes

---

### 📚 Knowledge Base

#### `query_knowledge_base.py`
**Purpose**: Search historical knowledge base for context

**Usage**:
```bash
# Keyword search
python scripts/query_knowledge_base.py \
  --keywords "ukraine nato sanctions" \
  --output context.json

# Category filter
python scripts/query_knowledge_base.py \
  --keywords "putin" \
  --categories events figures \
  --limit 10
```

**Features**:
- 7 categories: events, figures, policies, narratives, context, analysis, science
- Keyword matching with title/summary bonuses
- Date range filtering
- Ranked results by relevance

**Output**: JSON with relevant knowledge base entries

**Dependencies**: `pathlib`, `json`

**Standalone**: ✅ Yes

---

#### `load_historical_context.py`
**Purpose**: Load historical briefings with temporal decay

**Usage**:
```bash
python scripts/load_historical_context.py \
  --output research/historical_context.json \
  --max-articles 100
```

**Features**:
- Logarithmic temporal decay weighting
- Time buckets: today (100%), last week (75%), month (50%), quarter (25%), year (10%)
- Sampling based on time decay
- Consolidated historical context

**Output**: JSON with sampled historical articles

**Dependencies**: `datetime`, `json`, `config`

**Standalone**: ✅ Yes

---

### 📊 Visualization

#### `visualization_framework.py`
**Purpose**: Modular chart generation framework

**Usage**:
```python
from scripts.visualization_framework import ChartRegistry

# Get chart by name
chart_class = ChartRegistry.get_chart("sentiment_timeline")
chart = chart_class(data=data)
chart.render(output_path="images/2025-11-16-sentiment.png")

# List available charts
charts = ChartRegistry.list_charts()
```

**Features**:
- Base class for extensibility (`BaseChart`)
- Brand color palette (Eastbound red, orange, dark)
- Matplotlib + seaborn styling
- Chart registry for discoverability

**Chart Types** (extend via `example_charts.py`):
- Sentiment Timeline (line chart)
- Source Distribution (pie chart)
- Keyword Trends (bar chart)

**Dependencies**: `matplotlib`, `seaborn`

**Standalone**: ⚠️ Framework - extend with custom charts

---

#### `example_charts.py`
**Purpose**: Reference implementations of chart types

**Usage**:
```python
from scripts.example_charts import SentimentTimelineChart

chart = SentimentTimelineChart(data={
    "dates": ["2025-11-10", "2025-11-11", "2025-11-12"],
    "sentiment_scores": [0.2, -0.3, 0.5]
})
chart.render("images/sentiment.png")
```

**Charts**:
- `SentimentTimelineChart`: Positive/negative fill areas
- `SourceDistributionChart`: Media outlet distribution
- `KeywordsTrendingChart`: Top keywords bar chart

**Dependencies**: `visualization_framework`, `matplotlib`, `seaborn`

**Standalone**: ⚠️ Library - educational examples

---

### 🛠️ Utilities

#### `config.py`
**Purpose**: Centralized configuration for all scripts

**Usage**:
```python
from scripts.config import RESEARCH_DIR, generate_post_url

# Use project paths
briefing_path = RESEARCH_DIR / "2025-11-16-briefing.json"

# Generate URLs
url = generate_post_url("2025-11-16", "analysis")
# Returns: "https://eastboundreports.github.io/2025/11/16/analysis.html"
```

**Constants**:
- Project paths: `RESEARCH_DIR`, `DRAFTS_DIR`, `POSTS_DIR`, `IMAGES_DIR`, `KNOWLEDGE_BASE_DIR`
- Site URL: `SITE_URL`
- Social hashtags: `HASHTAGS`

**Functions**:
- `generate_post_url(date, slug)`
- `generate_image_path(date, image_type)`
- `get_today_string()`
- `get_briefing_path(date)`

**Dependencies**: `pathlib`, `datetime`, `pyyaml`

**Standalone**: ⚠️ Library - imported by all scripts

---

#### `logger.py`
**Purpose**: Centralized logging system

**Usage**:
```python
from scripts.logger import init_script_logging, get_logger

# Initialize logging for your script
init_script_logging("my_script")

# Get logger
logger = get_logger(__name__)
logger.info("Processing started")
logger.error("An error occurred")
```

**Features**:
- Colored console output (cyan, green, yellow, red, magenta)
- Timestamped log files in `logs/` directory
- Both file and console logging

**Dependencies**: `logging`, `pathlib`, `datetime`

**Standalone**: ⚠️ Library - imported by all scripts

---

#### `health_check.py`
**Purpose**: System health verification

**Usage**:
```bash
python scripts/health_check.py
```

**Checks**:
- RSS feed accessibility (3 feeds tested)
- Recent briefing generation (last 7 days)
- Draft creation status (last 7 days)
- Knowledge base population (by category)
- Published posts (last 30 days)

**Output**: Console report + exit code (0 = healthy, 1 = failures)

**Dependencies**: `feedparser`, `json`, `pathlib`, `config`

**Standalone**: ✅ Yes

---

#### `embed_images_base64.py`
**Purpose**: Convert images to base64 data URIs (self-contained posts)

**Usage**:
```bash
# Inline replacement
python scripts/embed_images_base64.py \
  --file _posts/2025-11-16-analysis.md \
  --inline

# Separate output
python scripts/embed_images_base64.py \
  --file _posts/2025-11-16-analysis.md \
  --output _posts/2025-11-16-analysis-embedded.md
```

**Features**:
- PNG, JPG, GIF support
- Inline replacement or separate output
- Appropriate MIME types

**Warning**: Significantly increases file size

**Dependencies**: `base64`, `pathlib`, `re`

**Standalone**: ✅ Yes

---

### 🎨 Image Generation (Optional)

#### `download_loras.py`
**Purpose**: Download SDXL LoRA models for image generation

**Usage**:
```bash
python scripts/download_loras.py
```

**Downloads**:
- Steve McCurry Photography style (HuggingFace)
- Instructions for manual downloads:
  - Touch of Realism v2 (Civitai)
  - Film Photography LoRA (Civitai)

**Storage**: `models/loras/`

**Dependencies**: `huggingface_hub` (optional)

**Standalone**: ✅ Yes

**Note**: Image generation currently disabled in automation (CPU-intensive, 30-40 min per image)

---

## Automation Pipelines

### Simple Pipeline (Recommended)

**File**: `run_simple_automation.ps1`

**Steps**:
1. Monitor Russian media → `research/YYYY-MM-DD-briefing.json`
2. Generate analysis with Claude CLI → `_posts/YYYY-MM-DD-analysis.md`
3. Git commit & push

**Duration**: ~5-10 minutes
**Cost**: Free (Claude Code CLI)

**Setup**:
```powershell
.\setup_simple_task.ps1  # Runs daily at 9:50 AM
```

---

### Manual Execution

**File**: `RUN_AUTOMATION_NOW.bat`

**Usage**:
```bash
.\RUN_AUTOMATION_NOW.bat
```

**Features**:
- Live progress display
- Draft-only mode (review before publish)
- Console stays open

---

### Development Menu (Linux/Mac)

**File**: `scripts/local_dev.sh`

**Usage**:
```bash
bash scripts/local_dev.sh
```

**Menu Options**:
1. Test setup
2. Create draft
3. Preview posts
4. Publish (dry-run)
5. Generate Twitter thread
6. List drafts/scheduled/published posts
7. Install dependencies

---

## Dependency Groups

### Core (Required for Basic Automation)
```bash
pip install pyyaml feedparser requests markdown
```

### Social Media (Optional)
```bash
pip install tweepy  # Twitter
# LinkedIn uses requests (already installed)
```

### Visualization (Optional)
```bash
pip install matplotlib seaborn
```

### Advanced Analysis (Optional)
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### Image Generation (Optional, Heavy)
```bash
pip install -r requirements-images.txt
# Downloads ~2GB+ (PyTorch, Diffusers, etc.)
```

---

## Mix & Match Examples

### Example 1: News Monitoring Only
```bash
# Install
pip install feedparser pyyaml

# Run
python scripts/monitor_russian_media.py --output daily.json
```

---

### Example 2: News + Manual Analysis
```bash
# Install
pip install feedparser pyyaml markdown

# Monitor
python scripts/monitor_russian_media.py --output research/2025-11-16-briefing.json

# Create draft
python scripts/create_draft.py --type weekly-analysis --title "Weekly Roundup"

# Edit manually in content/drafts/, then move to _posts/
```

---

### Example 3: Full Automation with Social
```bash
# Install everything
pip install -r requirements.txt

# Setup credentials in .env
# TWITTER_API_KEY=...
# LINKEDIN_ACCESS_TOKEN=...

# Run automation
.\run_simple_automation.ps1

# Post to socials
python scripts/post_to_twitter.py --file _posts/2025-11-16-analysis.md
python scripts/post_to_linkedin.py --file _posts/2025-11-16-analysis.md
```

---

### Example 4: Custom Visualization Pipeline
```bash
# Install
pip install matplotlib seaborn feedparser pyyaml

# Monitor
python scripts/monitor_russian_media.py --output daily.json

# Generate charts (custom script)
python custom_chart_generator.py --briefing daily.json --output charts/
```

---

## Adding New Components

### 1. Create Your Script
```python
# scripts/my_component.py
from scripts.config import RESEARCH_DIR
from scripts.logger import init_script_logging, get_logger

def main():
    init_script_logging("my_component")
    logger = get_logger(__name__)

    logger.info("Running my component...")
    # Your logic here

if __name__ == "__main__":
    main()
```

### 2. Document in Registry
Add entry to this file under appropriate category.

### 3. Update Dependencies
Add to `requirements.txt` if needed.

---

## Component Dependencies Graph

```
monitor_russian_media.py
├── advanced_keywords.py
├── config.py
└── logger.py

create_draft.py
├── config.py
└── logger.py

post_to_twitter.py
├── config.py
└── logger.py

visualization_framework.py
└── (standalone, base class)

example_charts.py
└── visualization_framework.py

query_knowledge_base.py
├── config.py
└── logger.py

load_historical_context.py
├── config.py
└── logger.py

health_check.py
└── config.py
```

---

## Quick Reference Card

| Task | Component | Command |
|------|-----------|---------|
| Monitor news | `monitor_russian_media.py` | `python scripts/monitor_russian_media.py --output daily.json` |
| Create draft | `create_draft.py` | `python scripts/create_draft.py --type weekly-analysis --title "Title"` |
| Post to Twitter | `post_to_twitter.py` | `python scripts/post_to_twitter.py --file _posts/post.md` |
| Post to LinkedIn | `post_to_linkedin.py` | `python scripts/post_to_linkedin.py --file _posts/post.md` |
| Search knowledge | `query_knowledge_base.py` | `python scripts/query_knowledge_base.py --keywords "topic"` |
| Health check | `health_check.py` | `python scripts/health_check.py` |
| Full automation | `run_simple_automation.ps1` | `.\run_simple_automation.ps1` |
| Dev menu | `local_dev.sh` | `bash scripts/local_dev.sh` |

---

## Support

For component-specific help, run:
```bash
python scripts/<component>.py --help
```

For Claude CLI integration, see: `Docs/CLAUDE_CLI_API.md`
