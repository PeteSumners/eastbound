# AI Visualization Guide for Eastbound Reports

**Audience:** Future AI instances (Claude Code, ChatGPT, etc.) working on this codebase

**Purpose:** This guide helps you (an AI assistant) add new visualization types to Eastbound Reports quickly and correctly.

---

## Quick Start: Adding a New Chart Type

### Step 1: Understand the Framework

Location: `scripts/visualization_framework.py`

All charts inherit from `BaseChart` and implement the `generate()` method:

```python
class MyNewChart(BaseChart):
    def generate(self, data, output_path):
        # 1. Setup figure
        self._setup_figure()

        # 2. Create visualization
        # ... your matplotlib code here ...

        # 3. Apply Eastbound styling
        self._apply_style()

        # 4. Save and return
        return self._save_and_close(output_path)
```

### Step 2: Use Eastbound Brand Colors

```python
from visualization_framework import COLORS

COLORS['primary']    # #c74440 - Eastbound red
COLORS['secondary']  # #e57373 - Light red
COLORS['dark']       # #1a1a1a - Almost black
COLORS['light']      # #f5f5f5 - Off-white
COLORS['text']       # #333333 - Dark gray
```

### Step 3: Register Your Chart

Add to `CHART_REGISTRY` in `visualization_framework.py`:

```python
CHART_REGISTRY = {
    'keyword_trend': KeywordTrendChart,
    'my_new_chart': MyNewChart,  # <-- Add here
}
```

### Step 4: Use It

```python
from visualization_framework import create_chart

chart = create_chart('my_new_chart')
chart.generate(data={'foo': 'bar'}, output_path='images/test.png')
```

---

## Common Chart Types to Add

### 1. Sentiment Timeline

**What:** Line chart showing tone (positive/negative) over time
**Why:** Track emotional framing shifts
**Data:** `[{'date': '2025-01-01', 'sentiment': 0.5}, ...]`
**Code hint:**
```python
class SentimentTimeline(BaseChart):
    def generate(self, data, output_path):
        self._setup_figure()
        dates = [item['date'] for item in data]
        sentiments = [item['sentiment'] for item in data]

        self.ax.plot(dates, sentiments, color=COLORS['primary'], linewidth=2)
        self.ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        self.ax.fill_between(dates, 0, sentiments,
                            where=[s > 0 for s in sentiments],
                            alpha=0.3, color='green', label='Positive')
        self.ax.fill_between(dates, 0, sentiments,
                            where=[s < 0 for s in sentiments],
                            alpha=0.3, color='red', label='Negative')

        self.title = 'Sentiment Over Time'
        self._apply_style()
        return self._save_and_close(output_path)
```

### 2. Geographic Heatmap

**What:** Map showing which countries are mentioned
**Why:** Visualize geopolitical focus
**Data:** `{'Ukraine': 50, 'USA': 30, 'China': 25, ...}`
**Requires:** `pip install geopandas`

### 3. Narrative Network Graph

**What:** Graph showing connected topics/narratives
**Why:** Show how Russian media links concepts
**Data:** `{'nodes': [...], 'edges': [...]}`
**Requires:** `pip install networkx`

### 4. Comparison Bar Chart

**What:** Side-by-side comparison of Russian vs Western coverage
**Why:** Show framing differences
**Data:** `{'topics': [...], 'russian_coverage': [...], 'western_coverage': [...]}`

---

## Data Access Patterns

### From Briefing JSON

```python
# Load briefing
with open('research/2025-11-06-briefing.json') as f:
    briefing = json.load(f)

# Access trending stories
trending = briefing['trending_stories']  # List of dicts

# Access all articles
articles = briefing['all_articles']  # List of dicts

# Get article counts by source
from collections import Counter
source_counts = Counter(a['source'] for a in articles)
```

### From Historical Digests

```python
from pathlib import Path

posts_dir = Path('_posts')
recent_posts = sorted(posts_dir.glob('*.md'))[-7:]  # Last 7

# Parse post frontmatter and content
# Extract dates, topics, sentiment, etc.
```

### From Knowledge Base

```python
from scripts.query_knowledge_base import KnowledgeBase

kb = KnowledgeBase(Path('knowledge_base'))
entries = kb.search(keywords=['ukraine'], limit=10)

# Extract dates for timeline
dates = [entry['date'] for entry in entries if entry['date'] != 'ongoing']
```

---

## Styling Best Practices

### Colors

- **Primary (red):** Main data series, emphasis
- **Secondary (light red):** Supporting data
- **Dark:** Backgrounds for social cards
- **Light:** Backgrounds for infographics

### Fonts

```python
# Title
fontsize=14, fontweight='bold', color=COLORS['text']

# Labels
fontsize=12, fontweight='bold'

# Values
fontsize=10
```

### Sizing

```python
# Social media cards
figsize=(12, 6)  # 2:1 ratio for Twitter/LinkedIn

# Data charts
figsize=(10, 6)  # Standard

# Infographics
figsize=(8, 10)  # Portrait for Instagram/mobile
```

---

## Integration Points

### 1. Add to Workflow

Edit `.github/workflows/daily-content.yml`:

```yaml
- name: Generate visualizations
  run: |
    python scripts/generate_visuals.py \
      --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
      --output "images/" \
      --charts "keyword_trend,source_dist,my_new_chart"  # Add yours
```

### 2. Add to Post

Edit `scripts/generate_ai_draft.py`:

```python
## Data Visualizations

### My New Chart Title
![My Chart](/images/{today}-my-chart.png)
```

### 3. Document

Update this file (`AI_VISUALIZATION_GUIDE.md`) with:
- What the chart shows
- Why it's useful
- Data format required
- Example output description

---

## Advanced: Fetching Internet Images

See `scripts/fetch_images.py` for automated image fetching from multiple sources.

### Available Sources

**1. Unsplash** (Free stock photos):
```python
from fetch_images import fetch_unsplash_image

img_path = fetch_unsplash_image(
    query='ukraine war',
    output_dir='images/',
    orientation='landscape'  # or 'portrait', 'squarish'
)
# Returns: images/unsplash-abc123.jpg
```

**Setup**: Get free API key at https://unsplash.com/developers
- Set environment variable: `UNSPLASH_ACCESS_KEY=your_key`
- Or pass `api_key` parameter

**2. Wikipedia** (Public domain images):
```python
from fetch_images import fetch_wikipedia_image

img_path = fetch_wikipedia_image(
    article_title='Vladimir Putin',
    output_dir='images/'
)
# Returns: images/wikipedia-abc123.jpg
```

No API key required!

**3. Article Thumbnails** (Extract from URLs):
```python
from fetch_images import fetch_article_thumbnail

img_path = fetch_article_thumbnail(
    url='https://tass.com/politics/...',
    output_dir='images/'
)
# Returns: images/article-abc123.jpg
```

Extracts Open Graph and Twitter Card images from article HTML.

**4. Smart Fetcher** (Tries multiple sources):
```python
from fetch_images import fetch_relevant_image

# Automatically picks best source based on briefing data
img_path = fetch_relevant_image(briefing_data, 'images/')
```

Strategy:
- If top keyword is a known person → Wikipedia
- If top keyword is a location → Wikipedia
- Otherwise → Unsplash with contextual query

### Image Caching

All fetched images are cached locally in `images/cache/` to avoid re-fetching:
- Cache key: MD5 hash of source + query
- Metadata stored in `images/cache/image_metadata.json`
- Includes attribution info for proper credit

### Attribution

Get attribution text for any fetched image:
```python
from fetch_images import get_image_attribution

attribution = get_image_attribution(img_path)
# Returns: "Photo by John Doe on Unsplash"
```

### Integration with generate_visuals.py

Enable automatic image fetching:
```bash
python scripts/generate_visuals.py \
  --briefing research/2025-11-05-briefing.json \
  --output images/ \
  --fetch-images
```

### Best Practices

1. **Unsplash**: Best for generic concepts (war, diplomacy, politics)
2. **Wikipedia**: Best for specific people and places
3. **Article thumbnails**: Use sparingly (may have copyright restrictions)
4. **Always attribute**: Include attribution in posts or image captions

### Error Handling

All fetch functions return `None` if they fail:
```python
img = fetch_unsplash_image('query')
if img:
    print(f"Success: {img}")
else:
    print("Failed, using fallback")
```

Failures are logged but don't crash the pipeline

---

## Testing Your Visualization

```bash
# 1. Create test data
echo '{"trending_stories": [{"keyword": "test", "source_count": 5}]}' > test.json

# 2. Generate chart
python -c "
from visualization_framework import create_chart
chart = create_chart('your_chart_type')
chart.generate(data, 'test-output.png')
"

# 3. View output
open test-output.png  # macOS
# or
start test-output.png  # Windows
```

---

## Common Mistakes to Avoid

### ❌ Don't Hardcode Colors
```python
# Bad
ax.plot(x, y, color='red')

# Good
ax.plot(x, y, color=COLORS['primary'])
```

### ❌ Don't Forget to Close Figures
```python
# Bad
plt.savefig(path)
# (leaves figure in memory)

# Good
return self._save_and_close(output_path)
```

### ❌ Don't Use Interactive Backend
```python
# Bad
import matplotlib.pyplot as plt  # Default backend

# Good
import matplotlib
matplotlib.use('Agg')  # Non-interactive (for CI/CD)
import matplotlib.pyplot as plt
```

---

## Visualization Ideas by Use Case

### For Social Media Engagement
- Bold, simple designs
- Large text
- High contrast
- 12:6 or 1:1 aspect ratios

**Ideas:**
- Quote cards (key Putin/Lavrov quotes)
- "Did you know?" fact cards
- Before/after comparisons
- Number-focused infographics

### For In-Depth Analysis
- Detailed charts
- Multiple data series
- Annotations
- Standard sizes

**Ideas:**
- Trend lines (keywords over weeks/months)
- Correlation matrices (which topics appear together)
- Network graphs (narrative connections)
- Heatmaps (coverage intensity by source/topic)

### For Reports/PDFs
- Professional styling
- High DPI (300)
- Grayscale-friendly
- Clear labels

**Ideas:**
- Executive summaries (1-page dashboards)
- Comparative analysis (side-by-side charts)
- Timeline views (major events)
- Statistical breakdowns

---

## Example: Full Chart Implementation

```python
class TopicCorrelationMatrix(BaseChart):
    """
    Heatmap showing which topics appear together in articles.

    Data format: Dict of dicts with correlation scores
    Example: {'ukraine': {'nato': 0.8, 'sanctions': 0.6}, ...}
    """

    def __init__(self):
        super().__init__(figsize=(10, 8))

    def generate(self, data, output_path):
        import numpy as np
        import seaborn as sns

        self._setup_figure()

        # Convert dict to matrix
        topics = list(data.keys())
        matrix = np.array([[data[t1].get(t2, 0)
                           for t2 in topics]
                          for t1 in topics])

        # Create heatmap
        sns.heatmap(matrix, annot=True, fmt='.2f',
                   xticklabels=topics, yticklabels=topics,
                   cmap='Reds', cbar_kws={'label': 'Correlation'},
                   ax=self.ax)

        self.title = 'Topic Correlation Matrix'
        self.ax.set_title(self.title, fontsize=14,
                         fontweight='bold', pad=20)

        return self._save_and_close(output_path)

# Register it
CHART_REGISTRY['topic_correlation'] = TopicCorrelationMatrix
```

---

## Questions to Ask Yourself

Before implementing a new chart, consider:

1. **What insight does this reveal?**
   - If it's just "looks cool" without analytical value, reconsider

2. **Can users understand it in 5 seconds?**
   - Simpler is better for social media
   - Complex is OK for detailed analysis

3. **Does it work in grayscale?**
   - Test by converting to grayscale
   - Use patterns/shapes if colors aren't enough

4. **Is the data available?**
   - Check briefing JSON structure
   - Check Knowledge Base structure
   - May need to add data collection first

5. **Will it scale?**
   - What if there are 100 keywords instead of 10?
   - What if date range is 2 years instead of 2 weeks?

---

## Resources

- Matplotlib gallery: https://matplotlib.org/stable/gallery/
- Seaborn examples: https://seaborn.pydata.org/examples/
- Color theory: Use reds/neutrals to match brand
- Chart selection guide: https://datavizcatalogue.com/

---

## Final Checklist

Before submitting a new chart type:

- [ ] Inherits from `BaseChart`
- [ ] Uses `COLORS` constants
- [ ] Implements `generate(data, output_path)`
- [ ] Registered in `CHART_REGISTRY`
- [ ] Documented in this file
- [ ] Tested with sample data
- [ ] Added to `generate_visuals.py` if appropriate
- [ ] Works in CI/CD (non-interactive backend)

---

**Remember:** The goal is insight, not decoration. Every chart should answer a question or reveal a pattern.

**Pro tip:** Look at existing charts in `visualization_framework.py` as templates. Copy structure, modify logic.

**You got this!** 🎨📊📈
