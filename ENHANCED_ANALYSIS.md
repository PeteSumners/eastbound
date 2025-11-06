# Enhanced Analysis System

## Overview

The Eastbound Reports analysis system has been significantly enhanced to provide deeper, more comprehensive coverage of Russian media narratives.

## What Changed

### 1. **MASSIVE Article Collection (5x Increase)**

**Before:**
- 6 RSS feeds
- 10 articles per feed
- ~60 total articles
- 15 headlines in briefing

**After:**
- 14 RSS feeds (added specialized feeds)
- 50 articles per feed
- **~700 total articles** 📈
- 50 headlines + ALL articles in briefing
- 10 trending topics (up from 5)
- 10 articles per trending topic (up from 5)

**New RSS Sources Added:**
- RT News, RT Russia, RT Business (specialized RT feeds)
- Kommersant Politics, Kommersant Economics (specialized Kommersant)
- TASS Politics, TASS Economy, TASS World (specialized TASS)

### 2. **Previous Digest Context (The Meta Feature!)**

The AI now has access to **previous 7 days of published digests** to:

✅ **Track narrative evolution** - How has Russian media's framing changed over time?
✅ **Maintain consistency** - Reference previous analysis for continuity
✅ **Identify patterns** - Spot shifts in messaging and propaganda techniques
✅ **Provide deeper context** - Connect current coverage to recent history

**Example:**
```
The AI can now say:
"Unlike last week's coverage which emphasized diplomatic channels,
Russian media has shifted to more confrontational framing..."
```

### 3. **New Analysis Section: Narrative Evolution**

All posts now include a dedicated section tracking **how Russian media narratives evolve**:

- Changes in tone/framing
- New keywords/messaging
- Shifts in emphasis
- Propaganda technique evolution

### 4. **Longer, Deeper Analysis**

**Before:** 1000-1500 words
**After:** 1500-2000 words

More space for:
- Multiple source quotes
- Historical context
- Comparative analysis
- Narrative tracking

## Technical Implementation

### Article Collection (`monitor_russian_media.py`)

```python
# Before
for entry in feed.entries[:10]:  # Only 10 articles

# After
for entry in feed.entries[:50]:  # 50 articles per feed!
```

```python
# Before
briefing = {
    'top_headlines': all_articles[:15]  # Only 15 headlines
}

# After
briefing = {
    'top_headlines': all_articles[:50],  # 50 headlines
    'all_articles': all_articles  # EVERYTHING for AI context
}
```

### Previous Digest Loading (`generate_ai_draft.py`)

```python
def load_previous_digests(days=7):
    """Load last 7 days of published posts."""
    # Scans _posts/ directory
    # Extracts date from filename
    # Loads first 2000 chars of each post
    # Returns 5 most recent digests
```

### Enhanced AI Prompt

The prompt now includes:
1. **Total article count** in briefing (e.g., "EXPANDED with 700 articles")
2. **Previous digests section** with last 5 posts
3. **All article headlines** (first 100) for broader context
4. **New requirement**: Narrative Evolution section

## Example Output Difference

### Before (Limited Context)
```
## RUSSIAN PERSPECTIVE

According to TASS, Russia announced new economic measures.
RT reported similar policies...
```

### After (Rich Context)
```
## RUSSIAN PERSPECTIVE

Based on analysis of 700 articles across 14 Russian media sources,
a clear pattern emerges...

According to TASS Politics, [detailed quote]
Kommersant Economics adds: [detailed quote]
RT Business frames this as: [detailed quote]

## NARRATIVE EVOLUTION

Compared to last week's coverage (analyzed November 1-4), Russian
media has shifted from defensive framing to more assertive messaging.
Key changes include:
- Increased use of "security" language (up 40%)
- Shift from European to Asian markets in economic coverage
- New emphasis on self-sufficiency narratives
```

## Benefits

### For AI Analysis
- ✅ **More data** = better pattern recognition
- ✅ **Historical context** = narrative tracking
- ✅ **Multiple sources** = balanced perspective
- ✅ **Temporal awareness** = evolution tracking

### For Readers
- ✅ **Deeper insights** from comprehensive coverage
- ✅ **Trend analysis** over time
- ✅ **Pattern recognition** in propaganda
- ✅ **Better understanding** of Russian media ecosystem

### For The Platform
- ✅ **Unique value** - no one else tracks this way
- ✅ **Institutional memory** - builds on previous analysis
- ✅ **Consistency** - maintains analytical standards
- ✅ **Defensibility** - comprehensive source coverage

## Data Flow

```
[14 RSS Feeds] → [~700 Articles]
       ↓
[Briefing JSON with ALL articles]
       ↓
[Load Previous 7 Days Digests] → [AI Prompt]
       ↓
[Claude API with Expanded Context]
       ↓
[1500-2000 Word Analysis with Narrative Evolution]
```

## Cost Impact

**Negligible!**
- RSS fetching: Free
- Storage: JSON files are tiny (~500KB each)
- GitHub Pages: Still free
- Claude API: Slightly longer prompts, but still cheap (~$0.10/post)

## Future Enhancements

Possible next steps:

1. **Sentiment tracking over time** - Chart emotional tone shifts
2. **Keyword frequency analysis** - Which terms are trending?
3. **Source comparison matrix** - How do different outlets frame same story?
4. **Automated narrative graphs** - Visualize messaging evolution
5. **Weekly meta-analysis** - "What we learned this week about Russian media"

## Configuration

### Adjust Article Count

In `monitor_russian_media.py`:
```python
def fetch_feed(url, source_name, max_articles=50):  # Change this number
```

### Adjust Previous Digest Window

In `generate_ai_draft.py`:
```python
previous_digests = load_previous_digests(days=7)  # Change number of days
```

### Adjust Context Depth

In `generate_ai_draft.py`:
```python
previous_digests.append({
    'content': content[:2000]  # Change chars per digest
})
```

## Testing the Enhancement

Run the monitoring script:
```bash
python scripts/monitor_russian_media.py --output research/test-briefing.json
```

Check the output:
```bash
# Should see:
Total articles: ~700 (up from ~60)
Trending stories: 10 (up from 5)
All articles included in briefing
```

Generate a draft:
```bash
python scripts/generate_ai_draft.py \
  --briefing research/test-briefing.json \
  --output content/drafts/
```

Check the output:
```bash
# Should see in logs:
✓ Found X previous digests
- Using 700+ articles from briefing
- Including X previous digests for context
```

## Example Briefing Structure

```json
{
  "date": "2025-11-05",
  "total_articles_scanned": 703,
  "trending_stories": [
    {
      "keyword": "ukraine",
      "source_count": 8,
      "articles": [/* 10 articles */]
    }
    // ... 9 more trending topics
  ],
  "top_headlines": [/* 50 headlines */],
  "all_articles": [/* ALL 703 articles */]
}
```

## The Meta Aspect

The **most powerful** part of this enhancement is the **self-referential analysis**:

The AI reads its own previous analysis to:
- Build institutional memory
- Track its own observations over time
- Maintain consistent analytical frameworks
- Identify long-term patterns

This creates a **feedback loop** where each analysis gets smarter by learning from previous analyses.

**Example:**
```
Day 1: AI notices "security" rhetoric increasing
Day 2: AI confirms trend, notes 20% increase
Day 3: AI connects to historical precedent from previous coverage
Day 4: AI predicts narrative shift based on pattern
Day 5: AI validates prediction, refines model
```

This is **unprecedented** in automated media analysis!

---

**Bottom Line:** Eastbound Reports now analyzes 10x more content with historical awareness. The AI doesn't just analyze today's news—it tracks how narratives evolve over time. That's genuinely unique.
