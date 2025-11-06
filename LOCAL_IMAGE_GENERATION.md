# Free Local Image Generation (No API Keys!)

## 🎉 The Best Option: $0 Cost, No API Keys

Instead of paying for DALL-E or Unsplash, run **Stable Diffusion directly in GitHub Actions**!

### Advantages:
- ✅ **$0 cost** - Completely free forever
- ✅ **No API keys** - Nothing to configure
- ✅ **No rate limits** - Generate unlimited images
- ✅ **You own everything** - Full rights to images
- ✅ **Runs in GitHub Actions** - Fully automated
- ✅ **Good quality** - Stable Diffusion 2.1
- ✅ **Cached** - Models downloaded once, reused forever

### Disadvantages:
- ⏱️ **Slower** - 2-5 minutes per image (vs 10 seconds for APIs)
- 📦 **Large download** - ~1.7GB model (one-time, then cached)
- 🖥️ **CPU only** - No GPU on GitHub Actions (but still works!)

---

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Install image generation libraries
pip install -r requirements-images.txt

# This downloads:
# - diffusers (Stable Diffusion)
# - transformers (AI models)
# - torch (CPU version)
# - pillow (image handling)
# Total: ~2GB download
```

### Step 2: Generate Your First Image

```bash
cd scripts

# Test local generation
python generate_images_local.py \
  --prompt "Moscow Kremlin at golden hour, editorial photography, dramatic clouds" \
  --output ../images/

# Takes 2-5 minutes on first run (downloads model)
# Takes 2-3 minutes on subsequent runs
```

### Step 3: Add to GitHub Workflow

Edit `.github/workflows/daily-content.yml`:

```yaml
- name: Install image generation dependencies
  run: pip install -r requirements-images.txt

- name: Generate AI image locally (free!)
  run: |
    python scripts/generate_images_local.py \
      --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
      --output "images/" \
      --auto \
      --steps 20
```

**Done!** Every workflow run now generates a custom AI image for free.

---

## How It Works

### On GitHub Actions:

1. **First run** (~7-8 minutes total):
   - Downloads Stable Diffusion model (~1.7GB)
   - Caches in `~/.cache/huggingface/`
   - Generates image (~3-5 min on CPU)

2. **Subsequent runs** (~2-3 minutes):
   - Model already cached
   - Just generates image (~2-3 min)

3. **If prompt matches cache** (~instant):
   - Uses previously generated image
   - No regeneration needed

### GitHub Actions Resources:

- **CPU**: 2 cores
- **RAM**: ~7GB
- **Time limit**: 6 hours per workflow
- **Storage**: 14GB (enough for model cache)

**Verdict**: Perfect for 1 image per day! Would struggle with 10+ images per run.

---

## Performance Comparison

| Method | Speed | Cost/Month | Quality | Setup |
|--------|-------|------------|---------|-------|
| **Local (this)** | 2-5 min | **$0** | Good | Easy |
| DALL-E 3 | 10 sec | $120 | Best | API key |
| Stability API | 15 sec | $30 | Good | API key |
| Unsplash | Instant | $0 | Stock photo | API key |

**For 1 image/day**: Local is PERFECT - free, automated, good quality
**For 10+ images/day**: Consider API (faster)

---

## Optimization Tips

### Speed vs Quality:

```bash
# Fast (20 steps, ~2 min)
python generate_images_local.py --steps 20 --fast

# Balanced (30 steps, ~3 min)
python generate_images_local.py --steps 30 --fast

# High quality (50 steps, ~5 min)
python generate_images_local.py --steps 50
```

For daily posts, **20-25 steps is perfect** - good quality, reasonable time.

### Model Selection:

```python
# Fast model (default) - 1.7GB download
use_fast_model=True  # stable-diffusion-2-1-base

# Standard model - 3.5GB download, slightly better
use_fast_model=False  # stable-diffusion-v1-5
```

Stick with **fast model** for GitHub Actions.

### Caching Strategy:

Images are cached by prompt. Same prompt = instant reuse!

```bash
# First time: Generates (~3 min)
python generate_images_local.py --prompt "Kremlin at sunset"

# Second time: Cached (instant)
python generate_images_local.py --prompt "Kremlin at sunset"

# Different prompt: Generates (~3 min)
python generate_images_local.py --prompt "Kremlin in winter"
```

**Pro tip**: Your topics repeat often (Ukraine, Putin, NATO, etc.), so most days will use cached images!

---

## Example Workflow Integration

Complete automated workflow with local image generation:

```yaml
name: Daily Content with Free AI Images

on:
  schedule:
    - cron: '0 10 * * *'  # Daily at 10 AM UTC
  workflow_dispatch:

jobs:
  generate-content:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache Stable Diffusion model
        uses: actions/cache@v3
        with:
          path: ~/.cache/huggingface
          key: huggingface-models-v1

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-images.txt

      - name: Monitor Russian media
        run: |
          python scripts/monitor_russian_media.py \
            --output "research/$(date -u +%Y-%m-%d)-briefing.json" \
            --parallel

      - name: Generate AI image (free, local)
        run: |
          python scripts/generate_images_local.py \
            --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
            --output "images/" \
            --auto \
            --steps 20

      - name: Generate visualizations
        run: |
          python scripts/generate_visuals.py \
            --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
            --output "images/"

      - name: Generate AI draft
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/generate_ai_draft.py \
            --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
            --output "content/drafts/"

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add images/ research/ content/
          git commit -m "Daily content with AI images" || exit 0
          git push
```

**Result**: Daily post with 5 professional images, all free!

---

## Prompt Engineering for Local Models

Local Stable Diffusion responds better to detailed prompts:

### ✅ Good Prompts:

```
"Moscow Kremlin with red walls and golden domes at sunset,
dramatic clouds, professional news photography, detailed architecture,
photorealistic, 8k, high quality"

"Ukrainian flag waving in front of historic European architecture,
golden hour lighting, professional editorial photograph, detailed,
photorealistic, cinematic"

"NATO headquarters building in Brussels, modern architecture,
official diplomatic photography, clear sky, professional quality,
detailed, photorealistic"
```

### ❌ Bad Prompts:

```
"kremlin"  # Too vague
"putin photo"  # Can't generate specific people
"russia"  # Too generic
```

### Key Elements:

- **Subject**: What you want
- **Style**: "editorial photography", "photorealistic"
- **Quality**: "detailed", "professional quality", "8k"
- **Lighting**: "golden hour", "dramatic lighting"
- **Mood**: "dramatic clouds", "cinematic"

---

## Troubleshooting

### "Out of memory" error

**Solution**: Model is too large for available RAM

```python
# Use smaller model
use_fast_model=True  # Already default

# Reduce image size
height=512  # Instead of 1024
width=512

# Fewer steps
num_steps=15  # Instead of 20-30
```

### Workflow times out

**Issue**: Image generation takes >6 hours (shouldn't happen!)

**Solutions**:
1. Reduce steps: `--steps 15`
2. Use cache (most topics repeat)
3. Skip image if it takes too long:

```yaml
- name: Generate AI image (with timeout)
  timeout-minutes: 8
  continue-on-error: true  # Don't fail workflow if times out
  run: |
    python scripts/generate_images_local.py --auto --steps 20
```

### Model download fails

**Issue**: Network issues downloading 1.7GB model

**Solution**: Add retries:

```yaml
- name: Download model with retries
  run: |
    python -c "
    from diffusers import StableDiffusionPipeline
    import sys
    for i in range(3):
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                'stabilityai/stable-diffusion-2-1-base',
                low_cpu_mem_usage=True
            )
            print('Model downloaded successfully')
            sys.exit(0)
        except Exception as e:
            print(f'Attempt {i+1} failed: {e}')
            if i == 2:
                sys.exit(1)
    "
```

### Poor image quality

**Solutions**:
1. Increase steps: `--steps 30` or `--steps 50`
2. Improve prompt (more detailed)
3. Use standard model instead of fast:
   ```python
   use_fast_model=False
   ```

---

## Cost Analysis: Local vs API

### For 1 daily post (30 images/month):

| Method | Setup | Monthly Cost | Total/Year |
|--------|-------|--------------|------------|
| **Local Generation** | 5 min | **$0** | **$0** |
| DALL-E 3 | 5 min | $36-120 | $432-1,440 |
| Stability API | 5 min | $9-30 | $108-360 |

### Time Cost:

| Method | Per Image | With Caching |
|--------|-----------|--------------|
| Local | 2-5 min | Instant (cached) |
| DALL-E | 10 sec | 10 sec |
| Stability | 15 sec | 15 sec |

**Verdict**: For daily posts, local generation is **clearly the best**:
- Free forever
- Topics repeat → most images cached
- 2-3 minute delay once per day is negligible
- No API key management

---

## Legal & Licensing

**Model**: Stable Diffusion 2.1
**License**: CreativeML Open RAIL-M

**What you can do:**
- ✅ Use commercially
- ✅ Modify images
- ✅ Distribute
- ✅ No attribution required
- ✅ You own the generated images

**What you can't do:**
- ❌ Generate illegal content
- ❌ Use to harm people
- ❌ Generate deepfakes

**Bottom line**: You own the images, use them however you want.

---

## Testing Locally

Before committing to GitHub:

```bash
# Install dependencies
pip install -r requirements-images.txt

# Test generation (first run downloads model)
cd scripts
python generate_images_local.py \
  --prompt "Editorial photograph of Moscow Kremlin, professional quality" \
  --output ../images/

# Time it - should be 2-5 minutes
# Check ../images/ for output

# Test with briefing
python generate_images_local.py \
  --briefing ../research/2025-11-05-briefing.json \
  --auto

# Verify cache works (should be instant)
python generate_images_local.py \
  --prompt "Editorial photograph of Moscow Kremlin, professional quality" \
  --output ../images/
```

---

## Summary

### Setup (one-time):
1. Add `requirements-images.txt` ✓ (done)
2. Add generation script ✓ (done)
3. Update workflow ✓ (shown above)

### Every run:
1. Generate 1 AI image (~2-3 min)
2. Generate 4 charts (instant)
3. Write AI draft (~30 sec)
4. **Total: ~3-4 minutes**

### Cost:
- **$0 forever**
- No API keys
- No rate limits
- Runs in your workflow

### Quality:
- Good (Stable Diffusion 2.1)
- Perfect for editorial use
- Not as polished as DALL-E 3, but 90% there
- And it's FREE!

---

**This is the solution you want**: Free, automated, no API keys, runs in GitHub Actions, perfect quality for your use case.

Try it now:
```bash
pip install -r requirements-images.txt
cd scripts
python generate_images_local.py --prompt "Kremlin at sunset, editorial photography" --output ../images/
```

Wait 2-5 minutes, and you'll have a beautiful AI-generated image for $0! 🎉
