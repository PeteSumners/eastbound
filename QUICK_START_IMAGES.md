# Quick Start: Adding Real Photos to Eastbound Reports

## 🚀 5-Minute Setup

### Step 1: Get Unsplash API Key (Free!)

1. Go to https://unsplash.com/developers
2. Sign up (free)
3. Click "New Application"
4. Accept terms
5. Fill in:
   - **Name**: Eastbound Reports
   - **Description**: Media analysis and translation
6. Copy your **Access Key**

### Step 2: Add to GitHub Secrets

1. Go to your repo: Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `UNSPLASH_ACCESS_KEY`
4. Value: Paste your Access Key
5. Click "Add secret"

### Step 3: Test Locally (Optional)

```bash
# Windows
set UNSPLASH_ACCESS_KEY=your_key_here

# Mac/Linux
export UNSPLASH_ACCESS_KEY=your_key_here

# Test it
cd scripts
python fetch_images.py --source unsplash --query "kremlin moscow" --output ../images/
```

---

## 📸 How to Use

### Option 1: Automatic (Best Option)

Edit `.github/workflows/daily-content.yml` and add the `--fetch-images` flag:

```yaml
- name: Generate visualizations
  run: |
    python scripts/generate_visuals.py \
      --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
      --output "images/" \
      --fetch-images  # <-- Add this flag
```

**What it does**: Automatically fetches a relevant image based on your top trending topic!

### Option 2: Manual for Specific Topics

```bash
# Fetch a specific topic image
python scripts/fetch_images.py \
  --source unsplash \
  --query "vladimir putin" \
  --output images/

# Or use Wikipedia (no API key needed!)
python scripts/fetch_images.py \
  --source wikipedia \
  --query "Vladimir Putin" \
  --output images/
```

### Option 3: Add to Existing Post

```bash
python scripts/add_sentiment_and_images.py \
  --briefing research/2025-11-05-briefing.json \
  --post content/drafts/my-post.md \
  --topic "kremlin"
```

---

## 🎯 What Images to Fetch

### ✅ Good Topics for Unsplash

- "kremlin moscow"
- "russia politics"
- "ukraine conflict"
- "russian military"
- "red square moscow"
- "diplomatic meeting"
- "european politics"

### ✅ Good Topics for Wikipedia

- "Vladimir Putin"
- "Moscow Kremlin"
- "Ukraine"
- "NATO"
- "Volodymyr Zelenskyy"
- "Red Square"
- "Russian Armed Forces"

---

## 📊 Image Types

### Your System Now Supports:

1. **Charts (you make these)** ✓
   - Keyword trends
   - Source distribution
   - Featured cards
   - Stats cards
   - Timeline charts
   - Sentiment charts

2. **Unsplash Photos** ✓
   - High-quality stock photos
   - 100% free to use
   - No attribution required
   - Professional

3. **Wikipedia Images** ✓
   - Specific people/places
   - Public domain
   - Free to use
   - Educational

4. **Article Thumbnails** ⚠️
   - Use ONLY for specific article analysis
   - Requires fair use statement
   - Higher legal risk

---

## 🎨 Sample Output

When you run with `--fetch-images`, your post will have:

```markdown
---
layout: post
title: "Russian Media Digest"
image: /images/2025-11-05-featured.png  # Your generated card
---

![Featured](/images/2025-11-05-featured.png)

## Article Content Here...

![Kremlin](images/unsplash-abc123.jpg)
*Photo by Ivan Petrov on Unsplash*

## Data Visualizations

![Keyword Trends](/images/2025-11-05-keywords.png)
![Sources](/images/2025-11-05-sources.png)
![Stats](/images/2025-11-05-stats.png)
```

**Result**: Professional post with 4-5 images, all legal to use!

---

## 🔒 Legal Status

| Source | Legal | Attribution | Commercial Use |
|--------|-------|-------------|----------------|
| Your charts | ✅ 100% safe | Not required | ✅ Yes |
| Unsplash | ✅ 100% safe | Optional | ✅ Yes |
| Wikipedia | ✅ 100% safe | Required* | ✅ Yes |
| Article thumbnails | ⚠️ Fair use only | Required | ⚠️ Limited |

*Public domain images don't require attribution, but CC images do. Script tracks this automatically.

---

## 🤖 Adding Sentiment Analysis

Want the sentiment timeline chart I showed you?

### Step 1: Set Up API Key

You already have this for content generation! Just make sure `ANTHROPIC_API_KEY` is set.

### Step 2: Run Analysis

```bash
python scripts/add_sentiment_and_images.py \
  --briefing research/2025-11-05-briefing.json \
  --output-dir images/
```

### Step 3: Get Results

This creates:
- `research/2025-11-05-sentiment.json` - Sentiment data
- `images/2025-11-05-sentiment-timeline.png` - Beautiful chart!

### Step 4: Add to Post

```markdown
### Sentiment Analysis

![Sentiment Over Time](/images/2025-11-05-sentiment-timeline.png)

Analysis shows sentiment shifting from positive (early week)
to negative (late week) as military operations intensified...
```

---

## 💡 Pro Tips

1. **Cache is your friend**: Images are cached locally. Once fetched, they're reused automatically. No re-downloading!

2. **Mix sources**: Use Unsplash for generic topics, Wikipedia for specific people/places, your charts for data.

3. **Attribution is automatic**: The system tracks attribution in `images/cache/image_metadata.json`

4. **Test before committing**: Run locally first to see what images you get:
   ```bash
   python scripts/generate_visuals.py --briefing research/latest.json --output images/ --fetch-images
   ```

5. **Fallback behavior**: If image fetch fails, your charts still work. System is resilient!

---

## 🚨 Common Issues

### "No Unsplash images found"
- Check your API key is correct
- Try a different query (more generic)
- Check rate limits (50 requests/hour on free tier)

### "Wikipedia fetch failed"
- Check spelling of article title (case-sensitive!)
- Try the English title (not Russian)
- Some pages don't have images

### "Attribution not showing"
- Check `images/cache/image_metadata.json` exists
- Verify image path matches exactly
- Re-run fetch if metadata missing

---

## 📈 Workflow Integration

### Fully Automated Daily Workflow:

```yaml
# .github/workflows/daily-content.yml

- name: Monitor media
  run: python scripts/monitor_russian_media.py --output research/briefing.json

- name: Generate visuals with images
  env:
    UNSPLASH_ACCESS_KEY: ${{ secrets.UNSPLASH_ACCESS_KEY }}
  run: |
    python scripts/generate_visuals.py \
      --briefing research/briefing.json \
      --output images/ \
      --fetch-images

- name: Analyze sentiment
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    python scripts/add_sentiment_and_images.py \
      --briefing research/briefing.json \
      --output-dir images/

- name: Generate AI draft
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: python scripts/generate_ai_draft.py --briefing research/briefing.json

- name: Commit all content
  run: |
    git add images/ research/ content/
    git commit -m "Automated content with images"
    git push
```

**Result**: Fully automated posts with charts, photos, and sentiment analysis!

---

## ✅ Checklist

Before your first automated run:

- [ ] Unsplash API key added to GitHub Secrets
- [ ] `--fetch-images` flag added to workflow
- [ ] Tested locally to verify images fetch correctly
- [ ] Reviewed `IMAGE_LEGAL_GUIDE.md` for compliance
- [ ] Cache directory (`images/cache/`) in `.gitignore` (optional)

---

## 📚 Further Reading

- **Full legal guide**: `IMAGE_LEGAL_GUIDE.md`
- **Visualization guide**: `AI_VISUALIZATION_GUIDE.md`
- **Technical changelog**: `VISUALIZATION_CHANGELOG.md`
- **Image module code**: `scripts/fetch_images.py`
- **Sentiment + images**: `scripts/add_sentiment_and_images.py`

---

## 🎉 You're Done!

Your system now:
- ✅ Generates 4 professional charts automatically
- ✅ Fetches legal stock photos from Unsplash
- ✅ Pulls encyclopedic images from Wikipedia
- ✅ Tracks attribution automatically
- ✅ Analyzes sentiment over time
- ✅ Creates sentiment timeline charts
- ✅ All 100% legal and automated

**Every post gets 5-6 professional images with zero manual work!**
