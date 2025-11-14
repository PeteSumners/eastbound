# Briefing Database Structure

## Overview

The briefing database (`research/YYYY-MM-DD-briefing.json`) is the core data structure that feeds the entire content generation pipeline. It's generated daily by `scripts/monitor_russian_media.py` and contains all source articles, trending analysis, and metadata used by the AI content generation system.

## Generation Process

**Script:** `scripts/monitor_russian_media.py`

**Input:** RSS feeds from 13+ Russian media sources
**Output:** Single JSON file containing ~200-400 articles
**Frequency:** Daily (6:00 AM via scheduled task)

### RSS Sources Monitored

- **TASS** (Russian State News Agency) - Main, Politics, Economy, World
- **RT** (Russia Today) - Main, News, Russia, Business
- **RIA Novosti** (State News Agency)
- **Interfax** (Independent News Agency)
- **Kommersant** (Business Daily) - Main, Politics, Economics

## Database Schema

```json
{
  "date": "YYYY-MM-DD",
  "generated_at": "ISO 8601 timestamp",
  "total_articles_scanned": 297,

  "trending_stories": [
    {
      "keyword": "ukraine",
      "source_count": 5,
      "tfidf_score": 1.0,
      "combined_score": 5.0,
      "articles": [...]
    }
  ],

  "top_headlines": [...],  // Top 50 articles by recency

  "all_articles": [        // ALL articles (200-400 total)
    {
      "source": "TASS",
      "title": "Article headline",
      "link": "https://...",
      "published": "Wed, 04 Jun 2025 14:21:03 +0300",
      "summary": "First 1000 chars of article..."
    }
  ]
}
```

## Key Fields Explained

### trending_stories

**Purpose:** Identifies the most significant topics being covered by multiple Russian media sources.

**Algorithm:**
1. TF-IDF (Term Frequency-Inverse Document Frequency) extracts significant keywords/phrases
2. Cross-source verification - keywords must appear in 3+ different sources
3. Combined scoring: `tfidf_score × source_count`
4. Top 10 trending topics selected

**Why this matters for content generation:**
- These represent coordinated messaging across Russian state media
- Multi-source coverage indicates Kremlin-prioritized narratives
- TF-IDF scoring filters out generic news language to find substantive topics

### source_count

The number of different media outlets covering this keyword. Higher counts indicate:
- State-coordinated messaging campaigns
- Major breaking news events
- Topics of strategic importance to Russian government

### tfidf_score

**Range:** 0.0 to 1.0 (normalized)

**Meaning:** Statistical measure of how "important" and "distinctive" a term is across all articles.
- High score = term is frequent in specific articles but rare overall (indicates topic specificity)
- Low score = term appears everywhere (generic language)

**Technical details:**
- TF (Term Frequency): How often term appears in an article
- IDF (Inverse Document Frequency): How rare the term is across all articles
- Formula: `TF × log(total_docs / docs_containing_term)`

### combined_score

`tfidf_score × source_count`

This prioritizes topics that are both:
1. Statistically significant (high TF-IDF)
2. Widely covered (multiple sources)

### all_articles

**Complete dataset** of every article fetched (200-400 articles/day).

**Why we keep everything:**
- AI can identify patterns humans miss
- Background context enriches analysis
- Minor stories sometimes reveal narrative shifts
- Allows for sentiment analysis across full dataset

## How the AI Uses This Database

### During Content Generation

The Claude Code automation (`run_daily_automation.py`) passes the briefing file to the AI with instructions to:

1. **Analyze trending_stories** - These become the main article topics
2. **Read top_headlines** - Provides recent context and breaking news
3. **Reference all_articles** - Background dataset for comprehensive analysis
4. **Extract article URLs** - Used in "Key Articles Referenced" section
5. **Identify narrative patterns** - AI looks for coordinated messaging themes

### Specific Usage Examples

**For article structure:**
- Top trending story → Main article narrative
- Related trending stories → Supporting sections
- all_articles → Context and background mentions

**For "Key Articles Referenced" section:**
- AI extracts URLs from articles discussed in the text
- Groups by source (TASS, RT, Kommersant)
- Provides direct links for reader verification

**For Data Visualizations:**
- `trending_stories` keywords → Trending Topics chart
- Article `source` field → Source Distribution pie chart
- `total_articles_scanned` → By The Numbers stats panel

## Data Quality & Anti-Hallucination

### Deduplication
Articles are deduplicated by:
- Exact URL matching
- Fuzzy title similarity (85% threshold)

### Minimum Viable Dataset
- Requires minimum 50 unique articles
- Automation fails if threshold not met (prevents low-quality output)

### Source Verification
- Every article includes source URL
- Published timestamps preserved
- Original summaries stored (not AI-generated)

## File Locations

**Generated briefings:** `research/YYYY-MM-DD-briefing.json`
**Historical context:** `knowledge_base/events/*.json`, `knowledge_base/narratives/*.json`
**Generation script:** `scripts/monitor_russian_media.py`

## Related Documentation

- [Content Generation Pipeline](content-generation-pipeline.md)
- [TF-IDF Keyword Extraction](tfidf-algorithm.md)
- [Anti-Hallucination System](anti-hallucination.md)
