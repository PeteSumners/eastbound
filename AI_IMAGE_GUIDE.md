# AI-Generated Images for Eastbound Reports

## Why AI-Generated Images?

**Advantages over stock photos:**
- ✅ **Specific to your content** - Generated based on actual topics
- ✅ **No stock photo feel** - Unique, never seen before
- ✅ **100% legal ownership** - You own the generated images
- ✅ **No attribution required** - They're yours
- ✅ **Editorial style** - Can match news photography aesthetic
- ✅ **Consistent branding** - Same AI = consistent style

**Cost:** $0.01-0.04 per image (one-time, then cached forever)

---

## Quick Start (5 Minutes)

### Option 1: DALL-E 3 (Recommended)

**Best for:** Highest quality, photorealistic images

**Setup:**

1. Get API key at https://platform.openai.com/api-keys
2. Add credit ($5-10 is enough for hundreds of images)
3. Add to environment:

```bash
# Windows
set OPENAI_API_KEY=sk-...your_key_here

# Mac/Linux
export OPENAI_API_KEY=sk-...your_key_here

# Or add to GitHub Secrets:
# Settings → Secrets → Actions → New secret
# Name: OPENAI_API_KEY
# Value: sk-...your_key_here
```

4. Generate your first image:

```bash
python scripts/generate_ai_images.py \
  --prompt "Moscow Kremlin at sunset, editorial photography" \
  --output images/ \
  --provider dalle3
```

**Pricing:** $0.04 per 1024x1024 image ($0.08 for HD)

---

### Option 2: Stability AI

**Best for:** Lower cost, still good quality

**Setup:**

1. Get API key at https://platform.stability.ai/
2. Add $10 credit
3. Add to environment:

```bash
set STABILITY_API_KEY=sk-...your_key_here
```

4. Generate:

```bash
python scripts/generate_ai_images.py \
  --prompt "Editorial photograph of Russian government building" \
  --output images/ \
  --provider stability
```

**Pricing:** $0.01 per 1024x1024 image

---

## Automatic Generation

The best part? It works automatically with your briefings!

```bash
# Auto-generate image based on top trending topic
python scripts/generate_ai_images.py \
  --briefing research/2025-11-05-briefing.json \
  --output images/ \
  --provider dalle3 \
  --auto
```

**What it does:**
1. Reads your briefing
2. Identifies top trending topic
3. Creates an appropriate prompt
4. Generates a relevant image
5. Caches it for reuse

---

## Integration with Workflow

Update your `generate_visuals.py` to include AI images:

```python
# In generate_visuals.py, add after other charts:

# Optional: Generate AI image
if args.generate_ai_image:
    from generate_ai_images import generate_for_briefing

    ai_img = generate_for_briefing(
        Path(args.briefing),
        output_dir,
        provider='dalle3'  # or 'stability'
    )

    if ai_img:
        print(f"  [OK] AI-generated image: {ai_img.name}")
        generated.append(ai_img)
```

Or add to GitHub workflow:

```yaml
- name: Generate AI image
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python scripts/generate_ai_images.py \
      --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
      --output "images/" \
      --provider dalle3 \
      --auto
```

---

## Prompt Engineering

### Built-In Smart Prompts

The system automatically creates prompts based on your topic:

| Topic | Generated Prompt |
|-------|------------------|
| Ukraine | "Editorial photograph of Ukrainian flag with architectural elements, professional news photography" |
| Kremlin | "The Moscow Kremlin at golden hour, editorial photography, dramatic clouds" |
| Putin | "Russian government building with flag, editorial style, professional news photography" |
| Military | "Military equipment in abstract editorial style, professional photojournalism" |
| NATO | "NATO headquarters building, editorial photography, dramatic sky" |

### Custom Prompts

For more control, create custom prompts:

```bash
python scripts/generate_ai_images.py \
  --prompt "Editorial photograph of international diplomatic summit, \
            professional news photography, dramatic lighting, \
            photojournalistic style, modern architecture background" \
  --output images/
```

### Prompt Tips

**✅ Good prompts include:**
- "Editorial photography" or "photojournalistic style"
- "Professional news photography"
- "Dramatic lighting"
- Specific architectural or visual elements
- "No text or logos"

**❌ Avoid:**
- Specific recognizable people (may violate policies)
- Copyrighted logos or brands
- Text in images (often garbled)
- Overly violent or disturbing content

**Example prompts:**

```
"European Union parliament building, editorial photography,
modern architecture, professional news style"

"Oil pipeline through winter landscape, editorial photography,
industrial infrastructure, dramatic sky, photojournalistic style"

"International flags arranged in diplomatic setting,
editorial photography, professional news style, clean composition"

"Russian Orthodox church architecture, editorial photography,
golden domes, dramatic lighting, cultural documentation"
```

---

## Legal & Ownership

### DALL-E 3 (OpenAI)

**License:** You own the images you generate

From OpenAI Terms:
> "Subject to your compliance with these Terms, OpenAI hereby assigns to you all its right, title and interest in and to Output."

**What you can do:**
- ✅ Use commercially
- ✅ Modify and adapt
- ✅ No attribution required
- ✅ Sell or distribute
- ✅ Use in any media

**What you can't do:**
- ❌ Generate images that violate OpenAI policies
- ❌ Use to mislead or deceive
- ❌ Generate NSFW content

---

### Stability AI

**License:** You own the images (with Membership)

From Stability AI Terms:
> "You own all Output you create with the Services."

**What you can do:**
- ✅ Use commercially
- ✅ Modify and adapt
- ✅ No attribution required
- ✅ Sell or distribute

**What you can't do:**
- ❌ Generate illegal content
- ❌ Generate NSFW content
- ❌ Violate third-party rights

---

## Cost Management

### Caching

Images are automatically cached! Once generated, never pay again:

```python
# First time: Costs $0.04
generate_ai_images.py --prompt "Kremlin at sunset" --output images/

# Second time: Free (cached)
generate_ai_images.py --prompt "Kremlin at sunset" --output images/
# [OK] Using cached AI-generated image
```

Cache is stored in `images/ai_generated/ai_image_metadata.json`

### Budget Control

**For 100 daily posts:**
- DALL-E 3: 100 images × $0.04 = $4.00/day = $120/month
- Stability: 100 images × $0.01 = $1.00/day = $30/month

**With caching (topics repeat):**
- Month 1: $120 (100 unique images)
- Month 2: $30 (only 25 new topics)
- Month 3: $15 (only 12 new topics)
- **Average: $20-40/month after initial period**

### Free Alternatives

If cost is a concern:

1. **Use only for featured images** (1 per post)
2. **Rely on your charts** for most visuals
3. **Cache aggressively** (topics repeat often)
4. **Use Stability AI** instead of DALL-E ($0.01 vs $0.04)

---

## Examples

### Generated vs Stock Photos

**Stock photo problem:**
- Generic "businessman at desk" vibe
- Recognizable as stock
- Not specific to your content
- Overused images

**AI-generated solution:**
- "Kremlin during winter evening, editorial photography"
- "European parliament session, photojournalistic style"
- "Oil refinery at industrial scale, dramatic sky"
- Unique, never-before-seen, perfectly relevant

---

## Attribution

**Do you need to attribute AI-generated images?**

**No!** You own them. But you *can* add for transparency:

```markdown
![Kremlin](/images/2025-11-05-ai-generated.png)
*AI-generated image for editorial use*
```

Or be more specific:

```markdown
*Editorial image generated using DALL-E 3 for this analysis*
```

This builds trust with your audience and demonstrates transparency.

---

## Workflow Comparison

### Before (Stock Photos):
```
1. Find stock photo on Unsplash
2. Download
3. Check license
4. Add attribution
5. Hope it's relevant
6. Everyone recognizes it as stock
```

### After (AI-Generated):
```
1. Read briefing
2. Auto-generate perfect image
3. You own it
4. Unique and relevant
5. Cached for future use
6. Professional editorial look
```

---

## Technical Details

### Image Specifications

**DALL-E 3:**
- Size: 1024x1024, 1024x1792, or 1792x1024
- Format: PNG
- Quality: Standard ($0.04) or HD ($0.08)
- Speed: 10-30 seconds
- Style: More photorealistic

**Stability AI:**
- Size: 1024x1024 (configurable)
- Format: PNG
- Quality: High
- Speed: 5-15 seconds
- Style: More artistic

### Metadata Tracking

All generated images are tracked in `images/ai_generated/ai_image_metadata.json`:

```json
{
  "abc123": {
    "source": "dall-e-3",
    "prompt": "Kremlin at sunset, editorial photography",
    "path": "images/2025-11-05-ai-generated.png",
    "generated_at": "2025-11-05T14:30:00",
    "model": "dall-e-3",
    "license": "OpenAI - you own generated images"
  }
}
```

---

## FAQ

**Q: Can I generate images of specific people?**
A: No, both DALL-E and Stability have policies against generating images of public figures. Use Wikipedia images for this instead.

**Q: What about Russian text/Cyrillic in images?**
A: AI models struggle with text. For images with text, use your own charts or real photos.

**Q: Can I edit AI-generated images?**
A: Yes! You own them. Edit in Photoshop, add overlays, crop, etc.

**Q: Will images look obviously AI-generated?**
A: Modern models (DALL-E 3, SDXL) are very photorealistic. Most people can't tell.

**Q: How do I prevent weird/inappropriate images?**
A: Use detailed prompts like "professional editorial photography" and avoid vague descriptions.

**Q: Can I combine with my charts?**
A: Absolutely! Use AI images for headers/features, your charts for data visualization.

---

## Best Practices

1. **Use AI for headers/features, charts for data**
   - Featured image: AI-generated
   - Data visualization: Your charts
   - Result: Professional + data-driven

2. **Cache aggressively**
   - Same topic = same image
   - Saves money and time

3. **Iterate on prompts**
   - First generation not perfect? Tweak prompt
   - Add "editorial photography" for news style
   - Add "photojournalistic" for authenticity

4. **Be transparent**
   - Optional: Label as AI-generated
   - Builds trust with audience

5. **Test locally first**
   - Generate a few images manually
   - See what style works best
   - Then automate

---

## Integration Example

Complete automated workflow with AI images:

```yaml
# .github/workflows/daily-content.yml

- name: Generate AI image
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python scripts/generate_ai_images.py \
      --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
      --output "images/" \
      --provider dalle3 \
      --auto

- name: Generate charts
  run: |
    python scripts/generate_visuals.py \
      --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
      --output "images/"

- name: Generate draft (includes all images)
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    python scripts/generate_ai_draft.py \
      --briefing "research/$(date -u +%Y-%m-%d)-briefing.json" \
      --output "content/drafts/"
```

**Result:** Every post has:
- 1 AI-generated featured image (topic-specific)
- 4 data visualization charts (your creation)
- All 100% legal, owned by you, professionally styled

---

## Summary

| Feature | Stock Photos | AI-Generated |
|---------|--------------|--------------|
| Cost | Free | $0.01-0.04 per image (one-time) |
| Relevance | Generic | Specific to content |
| Uniqueness | Overused | Unique |
| Legal | Requires attribution | You own it |
| Quality | Professional | Professional |
| Speed | Instant | 5-30 seconds |
| Caching | N/A | Free after first generation |
| **Best for** | Never use | Use for everything! |

---

**Bottom line:** AI-generated images are better in every way except initial cost. With caching, cost becomes negligible. Use AI images instead of stock photos.

🎨 **Start now:** Get an OpenAI API key and try it!
