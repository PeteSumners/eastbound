# Enhanced Keyword Extraction

The system now supports **enhanced keyword extraction** with multiple improvements:

## Features

### 1. **Named Entity Recognition (NER)** [Optional, requires spaCy]
- Automatically extracts people, places, organizations
- Example: "Zelens", "Trump", "White House", "NATO", "Ukraine"
- Entities are boosted in scoring (most relevant terms)

### 2. **Geopolitical Term Boosting**
- Key geopolitical terms get 1.5x score boost
- Terms include: ukraine, nato, sanctions, military, trump, biden, putin, etc.
- Ensures important geopolitical topics rise to the top

### 3. **Meaningful Phrase Extraction**
- Extracts 2-word phrases using TF-IDF
- Filters out generic phrases
- Example: "white house", "european union", "peace talks"

### 4. **Multi-Method Combination**
- Combines keywords from multiple extraction methods
- Gives diversity bonus for terms appearing in multiple methods
- Deduplicates and ranks by combined score

### 5. **Better Filtering**
- Strips HTML tags and URLs before processing
- Enhanced stopword list for news content
- Filters generic terms like "article", "source", "preview"

## Installation

### Basic (Current - TF-IDF only)
No installation needed - works out of the box!

### Enhanced (With NER - Recommended)
Run this once to enable Named Entity Recognition:

```bash
scripts\install_spacy.bat
```

This installs:
- `spacy` - NLP library
- `en_core_web_sm` - Small English language model (~15MB)

## Usage

The enhanced keywords are **automatically** used in the monitoring script.

### Manual Testing
```python
from advanced_keywords import extract_enhanced_keywords

keywords = extract_enhanced_keywords(articles, top_n=15)
for keyword, score, source in keywords:
    print(f"{keyword} ({source}): {score}")
```

## Examples

### Before (Old TF-IDF)
```
1. ukraine
2. ukrainian
3. trump
4. white
5. house
6. https          ← Generic/noise
7. article        ← Generic/noise
8. preview        ← Generic/noise
9. full           ← Generic/noise
10. sanctions
```

### After (Enhanced)
```
1. zelensky [ENTITY]       ← Named entity
2. ukraine [KEYWORD]       ← Boosted geopolitical term
3. trump [ENTITY]          ← Named entity
4. white house [PHRASE]    ← Meaningful phrase
5. nato [KEYWORD]          ← Boosted geopolitical term
6. ukrainian [KEYWORD]
7. sanctions [KEYWORD]     ← Boosted geopolitical term
8. european union [PHRASE] ← Meaningful phrase
9. biden [ENTITY]          ← Named entity
10. military [KEYWORD]     ← Boosted geopolitical term
```

## How It Works

1. **Extract named entities** (people, places, orgs) using spaCy NER
2. **Extract TF-IDF keywords** with geopolitical term boosting
3. **Extract meaningful phrases** (bigrams/trigrams) using TF-IDF
4. **Combine & deduplicate** all keywords
5. **Rank by combined score** with diversity bonus
6. **Return top N** most relevant keywords

## Benefits

- **More meaningful keywords** - Actual people/places/topics vs generic terms
- **Better context** - Phrases provide more context than single words
- **Geopolitically relevant** - Boosts important terms in Russian media analysis
- **Automatic** - Works with existing automation system
- **Fast** - Processes 300+ articles in seconds

## Technical Details

**File**: `scripts/advanced_keywords.py`
**Function**: `extract_enhanced_keywords(articles, top_n=15)`
**Dependencies**:
- Required: None (works with TF-IDF only)
- Optional: `spacy` + `en_core_web_sm` (for NER)

**Scoring**:
- Base TF-IDF score
- Geopolitical boost (1.5x)
- Entity boost (2.0x)
- Diversity bonus (up to 1.6x for appearing in multiple methods)
