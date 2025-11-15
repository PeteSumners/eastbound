# Global Knowledge Crawler System Design

## Vision
Build a comprehensive, automated knowledge ingestion system that collects, processes, and stores information from worldwide sources to inform Eastbound's Russian media analysis with deep global context.

## Current Architecture Analysis

### Existing Data Storage
```
knowledge_base/
├── events/          # Historical geopolitical events (manual)
├── figures/         # Key political figures (manual)
├── policies/        # Government policies (manual)
├── narratives/      # Propaganda patterns (manual)
├── analysis/        # Auto-extracted from published articles ✅ AUTO
└── science/         # Cutting-edge research (manual)
```

### Current Ingestion Pipeline
```
RSS Feeds → Python Parser → JSON Briefing → AI Analysis → Published Article → Knowledge Extraction
```

**Strengths:**
- ✅ RSS-based ingestion already supports parallel fetching
- ✅ TFIDF keyword extraction identifies trending topics
- ✅ Sentiment analysis provides context
- ✅ Knowledge base auto-expands from articles
- ✅ East Asian sources already defined (optional flag)

**Limitations:**
- ⚠️ Only RSS feeds (misses academic papers, databases, APIs)
- ⚠️ Manual curation for science/events/policies
- ⚠️ No systematic web scraping for research
- ⚠️ Limited to news sources

---

## Proposed Global Knowledge Crawler

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│                   GLOBAL KNOWLEDGE CRAWLER                   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    [RSS/News]      [Scientific APIs]    [Databases/Archives]
        │                   │                   │
   ┌────┴────┐         ┌────┴────┐        ┌────┴────┐
   │Regional │         │Research │        │Historical│
   │  News   │         │ Papers  │        │ Archives │
   └────┬────┘         └────┬────┘        └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────┴────────┐
                    │  Processing    │
                    │  Pipeline      │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   [Enrichment]      [Classification]    [Deduplication]
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────┴────────┐
                    │  Knowledge     │
                    │  Base Storage  │
                    └────────────────┘
```

---

## Data Source Categories

### 1. Regional News Media (RSS + Web Scraping)

**Europe:**
- UK: BBC, Guardian, Times, Telegraph, FT
- Germany: DW, Der Spiegel, FAZ
- France: Le Monde, AFP, France24
- Nordic: Sveriges Radio, NRK, YLE, DR
- Eastern Europe: Euronews, Radio Free Europe

**Americas:**
- US: NYT, WaPo, WSJ, Bloomberg, AP, Reuters
- Canada: CBC, Globe & Mail
- Latin America: El País, Clarín

**Asia-Pacific:**
- China: CGTN, Xinhua, Global Times, SCMP
- Japan: NHK, Japan Times, Asahi
- Korea: Yonhap, Arirang
- India: Times of India, Hindustan Times
- Australia: ABC, Sydney Morning Herald

**Middle East:**
- Al Jazeera, Al Arabiya, Times of Israel, Haaretz

**Africa:**
- South Africa: News24, Daily Maverick
- Pan-African: African News

### 2. Scientific & Research Sources

**Academic Papers:**
- arXiv.org (physics, CS, math) - API available
- bioRxiv/medRxiv (biology, medicine) - API available
- PubMed (medical) - NCBI E-utilities API
- SSRN (social sciences) - RSS feeds
- ResearchGate - web scraping

**Research Institutions:**
- DARPA announcements - RSS/web
- NSF awards database - API
- NASA news - RSS
- CERN announcements - RSS
- Max Planck - RSS
- CNRS (France) - RSS

**Technology:**
- Nature, Science - RSS (abstracts)
- MIT Tech Review - RSS
- IEEE Spectrum - RSS
- Ars Technica - RSS

### 3. Government & Policy Sources

**International Organizations:**
- UN News - RSS
- NATO - RSS
- EU Commission - RSS
- World Bank - API
- IMF - API
- OECD - Data APIs

**National Governments:**
- US State Dept - RSS
- UK Gov - RSS
- EU Parliament - RSS
- Kremlin.ru - RSS
- MFA Russia - RSS

**Think Tanks:**
- Carnegie - RSS
- Brookings - RSS
- CSIS - RSS
- RAND - Reports
- Chatham House - RSS

### 4. Specialty Databases

**Space:**
- Space.com - RSS
- NASA JPL - RSS
- ESA - RSS
- SpaceNews - RSS

**Energy:**
- IEA - API
- OPEC - Reports
- EIA (US) - API

**Economics:**
- Trading Economics - API
- World Bank Data - API
- FRED (Federal Reserve) - API

**Climate:**
- NOAA - API
- Copernicus - API
- Climate.gov - Data

---

## Implementation Plan

### Phase 1: Multi-Region News Expansion (Week 1)
```python
# Extend monitor_russian_media.py
scripts/monitor_global_media.py
  ├── Regional configurations
  ├── Parallel RSS fetching (existing)
  ├── Language detection
  ├── Auto-translation summaries (optional)
  └── Save to knowledge_base/news/
```

**Deliverables:**
- `scripts/monitor_global_media.py` - Multi-region RSS crawler
- Configuration: `config/news_sources.json` - Categorized by region
- Storage: `knowledge_base/news/{region}/{date}-briefing.json`
- Scheduler: Daily runs for each region (parallel)

### Phase 2: Scientific Paper Crawler (Week 2)
```python
scripts/crawl_research_papers.py
  ├── arXiv API integration
  ├── bioRxiv/medRxiv scraping
  ├── PubMed API integration
  ├── Keyword-based filtering
  ├── Category classification
  └── Save to knowledge_base/research/
```

**Deliverables:**
- `scripts/crawl_research_papers.py` - Academic paper ingestion
- Storage: `knowledge_base/research/{category}/{year}-{month}/`
- Update frequency: Daily for preprints, weekly for journals
- Focus areas: quantum, AI, biotech, materials, space

### Phase 3: Database API Integration (Week 3)
```python
scripts/ingest_databases.py
  ├── World Bank API
  ├── FRED API (economic data)
  ├── UN Data API
  ├── NASA API
  ├── Trading Economics API
  └── Save to knowledge_base/data/
```

**Deliverables:**
- `scripts/ingest_databases.py` - Structured data ingestion
- Storage: `knowledge_base/data/{source}/{dataset}/`
- Format: JSON with metadata (source, timestamp, fields)
- Update: Weekly or on-demand

### Phase 4: Automated Knowledge Enrichment (Week 4)
```python
scripts/enrich_knowledge_base.py
  ├── Cross-reference entries
  ├── Identify related topics
  ├── Generate summaries (using Claude)
  ├── Extract multi-perspective views
  └── Update knowledge base entries
```

**Deliverables:**
- `scripts/enrich_knowledge_base.py` - AI-powered enrichment
- Auto-linking: Related entries across categories
- Multi-perspective synthesis: US/Russia/China/EU views
- Fact-checking: Cross-reference claims

---

## Enhanced Knowledge Base Structure

```
knowledge_base/
├── analysis/          # Eastbound articles (auto) ✅ EXISTING
├── science/          # Research tracking (manual + auto)
│   ├── physics/
│   ├── biology/
│   ├── chemistry/
│   ├── ai-ml/
│   ├── space/
│   └── materials/
├── news/             # Regional news (auto) 🆕
│   ├── europe/
│   ├── americas/
│   ├── asia/
│   ├── africa/
│   └── middle-east/
├── research/         # Academic papers (auto) 🆕
│   ├── preprints/
│   ├── journals/
│   └── by-topic/
├── data/             # Structured databases (auto) 🆕
│   ├── economic/
│   ├── climate/
│   ├── space/
│   └── energy/
├── events/           # Historical events ✅ EXISTING
├── figures/          # Key people ✅ EXISTING
├── policies/         # Government policies ✅ EXISTING
└── narratives/       # Propaganda patterns ✅ EXISTING
```

---

## Metadata Standard (All Sources)

Every knowledge entry includes:
```json
{
  "id": "unique-identifier",
  "category": "news|research|data|event|figure|policy|narrative|analysis",
  "subcategory": "region|topic|dataset",
  "date": "YYYY-MM-DD",
  "source": {
    "name": "Source Name",
    "url": "https://...",
    "reliability": "high|medium|low",
    "bias": "left|right|center|state-controlled"
  },
  "content": {
    "title": "...",
    "summary": "...",
    "full_text": "..." // optional
  },
  "perspectives": {
    "russian": {...},
    "us": {...},
    "chinese": {...},
    "eu": {...}
  },
  "metadata": {
    "language": "en|ru|zh|...",
    "topics": ["tag1", "tag2"],
    "entities": ["Putin", "NATO"],
    "sentiment": 0.5  // -1.0 to 1.0
  },
  "auto_generated": true,
  "generated_date": "YYYY-MM-DD",
  "related_entries": ["id1", "id2"]
}
```

---

## Query & Analysis Layer

### Enhanced Knowledge Base Query
```python
from query_knowledge_base import KnowledgeBase

kb = KnowledgeBase('knowledge_base/')

# Multi-source query
results = kb.search(
    keywords=['quantum', 'computing'],
    categories=['science', 'news', 'research'],
    regions=['US', 'China', 'EU'],
    date_range=('2024-01-01', '2025-11-15')
)

# Perspective comparison
perspectives = kb.compare_perspectives(
    topic='quantum computing',
    sources=['Russian', 'US', 'Chinese']
)

# Trend analysis
trends = kb.analyze_trends(
    topic='Ukraine',
    time_window='90days',
    sources=['news/europe', 'news/americas', 'analysis']
)
```

### Integration with Article Generation
```python
# AI queries knowledge base for context
context = kb.get_comprehensive_context(
    briefing=russian_briefing,
    include_categories=['news', 'research', 'events', 'analysis'],
    max_entries=20
)

# AI sees:
# - Current Russian narrative
# - How other regions report same event
# - Historical precedents
# - Scientific context (if relevant)
# - Previous Eastbound analysis
```

---

## Automation Schedule

**Daily (8:00 AM):**
- Russian media monitoring ✅ EXISTING
- Global news monitoring 🆕
- arXiv/bioRxiv crawling 🆕
- Article generation + knowledge extraction ✅ EXISTING

**Weekly (Sunday 2:00 AM):**
- Database API ingestion (economic, climate data) 🆕
- Research journal scanning 🆕
- Knowledge base enrichment (cross-linking) 🆕
- Cleanup old entries (archive after 1 year)

**Monthly (1st, 3:00 AM):**
- Full knowledge base re-indexing 🆕
- Generate knowledge base statistics report
- Backup knowledge base to cloud

---

## Storage & Performance

**Estimated Growth:**
- Daily: ~500 news articles × 365 = ~180K/year
- Weekly: ~200 research papers × 52 = ~10K/year
- Monthly: ~50 database snapshots × 12 = ~600/year
- **Total: ~190K entries/year**

**Storage Requirements:**
- JSON entries: ~2KB average = ~380MB/year
- Full text (optional): ~50KB average = ~9.5GB/year
- With compression: ~2-3GB/year total

**Performance Optimization:**
- SQLite for fast querying (optional)
- Elasticsearch for full-text search (future)
- Index by: date, category, keywords, entities
- Cache frequently accessed entries

---

## Key Benefits for Eastbound Analysis

1. **Multi-Perspective Context**
   - Russian narrative vs. US/EU/China/Asia perspectives
   - Identify unique angles Western media misses

2. **Scientific Grounding**
   - Fact-check technical claims (quantum, energy, weapons)
   - Provide context for sci-tech narratives

3. **Historical Precedents**
   - Compare current narratives to past patterns
   - Identify recurring propaganda techniques

4. **Comprehensive World View**
   - Understand global reactions to Russian actions
   - Identify allied vs. opposed narratives

5. **Trend Detection**
   - Track narrative evolution over time
   - Predict future Russian messaging

---

## Next Steps

1. ✅ Review this design document
2. Create `scripts/monitor_global_media.py` (Phase 1)
3. Create `config/news_sources.json` with all RSS feeds
4. Test parallel ingestion with 5-10 sources
5. Verify knowledge base storage format
6. Integrate with existing automation
7. Add to daily scheduler

**Timeline:** 4 weeks to full implementation
**Cost:** $0 (all free sources + local processing)
**Maintenance:** Automated with minimal manual curation
