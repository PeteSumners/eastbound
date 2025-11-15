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

## Current Entries (19+ Total, Auto-Expanding)

### Events (6) - Manual entries
- `2022-ukraine-invasion.json` - Full-scale invasion of Ukraine
- `crimea-annexation-2014.json` - Annexation of Crimea
- `euromaidan-2014.json` - Ukrainian revolution
- `georgia-war-2008.json` - Russia-Georgia war
- `donbas-conflict.json` - Donbas war 2014-present
- `prigozhin-mutiny-2023.json` - Wagner rebellion

### Figures (2) - Manual entries
- `putin-worldview.json` - Vladimir Putin's ideology and statements
- `wagner-prigozhin.json` - Wagner Group and Yevgeny Prigozhin

### Policies (2) - Manual entries
- `western-sanctions-russia.json` - Sanctions timeline and impact
- `russian-energy-gas-policy.json` - Energy as geopolitical tool

### Narratives (5) - Manual entries
- `nato-expansion.json` - NATO expansion narrative
- `russian-nuclear-rhetoric.json` - Nuclear threat rhetoric
- `domestic-opposition.json` - Suppression of dissent narrative
- `soviet-collapse-trauma.json` - USSR collapse as trauma
- `multipolar-world.json` - Multipolar world order vision

### Analysis (Auto-Generated) - Grows daily
- `analysis-YYYY-MM-DD.json` - Extracted from each published article
- Captures Russian media narratives, quotes, sources, framing patterns
- Enables AI to reference its own previous analysis
- Auto-updates via `scripts/extract_knowledge_from_posts.py`

### Science (4+ entries) - Research tracking
- `quantum-computing-2024-2025.json` - DARPA QBI, quantum error correction
- `psi-research-parapsychology.json` - CIA Stargate, DARPA brain-computer interfaces
- `crispr-gene-editing-2024-2025.json` - Gene therapy breakthroughs
- `superconductor-materials-science-2024-2025.json` - Room-temperature superconductor research
- Expandable with new scientific developments

## Structure

```
knowledge_base/
├── events/          # 6 major historical events (manual)
├── figures/         # 2 key figures and organizations (manual)
├── policies/        # 2 policy areas (manual)
├── narratives/      # 5 recurring themes (manual)
├── analysis/        # Auto-generated from published articles (grows daily)
├── science/         # Cutting-edge research tracking (manual + auto)
└── examples/        # Reference examples
```

## Entry Format

Each knowledge base entry is a JSON file with multiple perspectives:

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
    "official_position": "What Western govs say (general)",
    "media_framing": "How Western media covers it",
    "key_differences": "Main divergences from Russian view"
  },

  "us_perspective": {
    "official_position": "US government position",
    "key_actions": ["action 1", "action 2"],
    "political_divisions": "Internal debates",
    "concerns": ["concern 1", "concern 2"]
  },

  "eu_perspective": {
    "official_position": "European Union position",
    "key_actions": ["action 1", "action 2"],
    "internal_divisions": "Member state disagreements",
    "concerns": ["concern 1", "concern 2"]
  },

  "chinese_perspective": {
    "official_position": "Chinese government position",
    "key_statements": ["statement 1", "statement 2"],
    "actions": ["action 1", "action 2"],
    "motivations": ["motivation 1", "motivation 2"]
  },

  "indian_perspective": {
    "official_position": "Indian government position",
    "key_actions": ["action 1", "action 2"],
    "rationale": ["reason 1", "reason 2"],
    "internal_debate": "Domestic perspectives"
  },

  "global_south_perspective": {
    "positions_vary": "Overview of diversity",
    "major_views": {
      "africa": "African perspective",
      "middle_east": "Middle Eastern perspective",
      "latin_america": "Latin American perspective"
    },
    "common_themes": ["theme 1", "theme 2"]
  },

  "facts": {
    "verified_claims": ["claim 1", "claim 2"],
    "disputed_claims": ["claim 1", "claim 2"],
    "data_points": {}
  },

  "related_entries": ["id1", "id2"],
  "sources": [
    {"title": "Source 1", "url": "https://...", "date": "YYYY-MM-DD"}
  ]
}
```

**Note:** Not all entries need all perspectives. Add perspectives that are relevant to the specific event/topic. Russian and Western perspectives are standard; add others as appropriate (US, EU, China, India, Global South, Japan, Turkey, etc.).

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
