# Eastbound Knowledge Base

## Overview

This is a **structured knowledge database** that the AI can reference when generating analysis. It includes:

- **Historical Events**: Major world events with dates and Russian media perspectives
- **Key Figures**: Politicians, officials, analysts and their positions over time
- **Economic Data**: Sanctions, trade data, economic indicators
- **Policy Changes**: Government decisions and their impacts
- **Narrative Patterns**: Recurring propaganda themes and techniques
- **Context Database**: Historical/cultural background for current events

## Purpose

When analyzing current Russian media, the AI can:
1. **Reference relevant historical context** automatically
2. **Compare current narratives** to past patterns
3. **Track policy evolution** over time
4. **Fact-check claims** against known data
5. **Identify propaganda techniques** from historical examples

## Structure

```
knowledge_base/
├── events/
│   ├── 2022-ukraine-invasion.json
│   ├── 2014-crimea-annexation.json
│   └── [other major events]
├── figures/
│   ├── putin-vladimir.json
│   ├── lavrov-sergei.json
│   └── [key political figures]
├── policies/
│   ├── sanctions-timeline.json
│   ├── energy-policy.json
│   └── [policy areas]
├── narratives/
│   ├── nato-expansion.json
│   ├── western-decline.json
│   └── [recurring themes]
└── context/
    ├── russian-history.json
    ├── cultural-context.json
    └── [background info]
```

## Entry Format

Each knowledge base entry is a JSON file with:

```json
{
  "id": "unique-identifier",
  "title": "Event/Topic Name",
  "date": "YYYY-MM-DD or date range",
  "category": "event|figure|policy|narrative|context",
  "summary": "Brief description",
  "russian_perspective": {
    "official_narrative": "What Russian gov says",
    "media_framing": "How Russian media covers it",
    "key_quotes": ["quote 1", "quote 2"],
    "evolution": "How narrative changed over time"
  },
  "western_perspective": {
    "official_position": "What Western govs say",
    "media_framing": "How Western media covers it",
    "key_differences": "Main divergences from Russian view"
  },
  "facts": {
    "verified_claims": ["claim 1", "claim 2"],
    "disputed_claims": ["claim 1", "claim 2"],
    "data_points": {
      "economic": {},
      "political": {},
      "military": {}
    }
  },
  "related_entries": ["id1", "id2"],
  "sources": [
    {"title": "Source 1", "url": "https://...", "date": "YYYY-MM-DD"}
  ],
  "last_updated": "YYYY-MM-DD"
}
```

## Usage in AI Analysis

When generating analysis, the AI queries the knowledge base for:

1. **Temporal Context**: What was happening on this date historically?
2. **Narrative Patterns**: Has Russian media used this framing before?
3. **Figure Tracking**: What has this person said previously?
4. **Fact Checking**: Do these claims match known data?
5. **Policy Context**: How does this relate to existing policies?

## Example Entry

See `examples/2022-ukraine-invasion.json` for a complete example.

## Adding Entries

Use the helper script:
```bash
python scripts/add_knowledge_entry.py \
  --category event \
  --title "Major Event Name" \
  --date "2022-02-24" \
  --summary "Brief description"
```

Or manually create JSON files following the format above.

## Querying the Knowledge Base

```python
from knowledge_base import query

# Find relevant context
results = query.search(
    keywords=["ukraine", "nato"],
    date_range=("2014-01-01", "2024-12-31"),
    categories=["event", "narrative"]
)

# Get specific entry
entry = query.get("2022-ukraine-invasion")

# Find related entries
related = query.related("2022-ukraine-invasion")
```

## Integration with AI

The `generate_ai_draft.py` script automatically:
1. Identifies keywords from current briefing
2. Queries knowledge base for relevant entries
3. Includes relevant context in AI prompt
4. Weights by temporal proximity and relevance

## Contributing

To add knowledge base entries:
1. Research the topic thoroughly
2. Collect sources (Russian and Western)
3. Document both perspectives objectively
4. Include verifiable facts and data
5. Link to related entries
6. Update related entries to link back

## Maintenance

- **Weekly**: Review and update active narratives
- **Monthly**: Add major events and policy changes
- **Quarterly**: Audit entries for accuracy and completeness
- **Yearly**: Archive old entries, consolidate patterns

## Example Queries

**"What was Russian media saying about NATO in 2014?"**
→ Returns Crimea annexation entry with NATO expansion narrative

**"How has Putin's rhetoric on Ukraine evolved?"**
→ Returns Putin figure entry with timeline of statements

**"What sanctions were imposed in response to Ukraine invasion?"**
→ Returns sanctions timeline with impact data

**"What are common Russian narratives about Western decline?"**
→ Returns western-decline narrative entry with examples over time

## Future Enhancements

- [ ] Sentiment tracking over time
- [ ] Network graph of related concepts
- [ ] Automated fact extraction from sources
- [ ] ML-based relevance scoring
- [ ] Visual timeline interface
- [ ] API for external querying
