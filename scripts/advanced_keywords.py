#!/usr/bin/env python3
"""
Advanced keyword extraction using TF-IDF (Term Frequency-Inverse Document Frequency).

More sophisticated than simple word counting - identifies terms that are:
- Frequent in a document (TF)
- Rare across all documents (IDF)

This catches important specific terms while filtering generic common words.

ENHANCED VERSION:
- Named Entity Recognition (people, places, organizations)
- Multi-word phrase extraction
- Geopolitical term boosting
- Keyword clustering

Usage:
    from advanced_keywords import extract_enhanced_keywords
    keywords = extract_enhanced_keywords(articles)
"""

import re
import math
from collections import Counter, defaultdict

# Try to import spaCy for NER (optional but recommended)
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        NER_AVAILABLE = True
    except OSError:
        # Model not downloaded
        NER_AVAILABLE = False
        nlp = None
except ImportError:
    NER_AVAILABLE = False
    nlp = None


def tokenize(text):
    """Extract words from text, removing HTML and URLs."""
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Remove URLs (http, https, www)
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'www\.\S+', ' ', text)

    # Remove HTML entities
    text = re.sub(r'&\w+;', ' ', text)

    # Extract words (4+ characters)
    words = re.findall(r'\b\w{4,}\b', text)
    return words


def extract_tfidf_keywords(articles, top_n=50, min_df=2):
    """
    Extract keywords using TF-IDF scoring.

    Args:
        articles: List of article dicts with 'title' and 'summary'
        top_n: Number of top keywords to return
        min_df: Minimum number of documents a term must appear in

    Returns:
        List of (keyword, score) tuples, sorted by score descending
    """
    # Stopwords
    stopwords = {
        'this', 'that', 'with', 'from', 'have', 'been', 'will', 'said', 'says',
        'more', 'about', 'after', 'their', 'which', 'when', 'where', 'there',
        'what', 'some', 'than', 'into', 'very', 'just', 'over', 'also', 'only',
        'many', 'most', 'such', 'other', 'would', 'could', 'should', 'these',
        'those', 'them', 'then', 'both', 'each', 'does', 'were', 'make', 'made',
        'russia', 'russian', 'moscow', 'kremlin', 'media', 'tass', 'reported',
        'reports', 'according', 'statement', 'official', 'officials', 'news',
        'world', 'national', 'international', 'chief', 'head', 'minister',
        'president', 'government', 'country', 'state', 'says', 'told', 'plan',
        'plans', 'year', 'years', 'talks', 'meeting', 'held', 'announced',
        'military', 'report', 'full', 'political', 'economic', 'social',
        'foreign', 'domestic', 'federal', 'regional', 'local', 'global',
        # News-specific stopwords
        'article', 'articles', 'story', 'stories', 'read', 'preview', 'https',
        'http', 'link', 'click', 'here', 'view', 'watch', 'video', 'photo',
        'image', 'source', 'sources', 'details', 'information', 'update',
        'updates', 'breaking', 'latest', 'continue', 'reading', 'part'
    }

    # Build document collection
    documents = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        words = [w for w in tokenize(text) if w not in stopwords]

        # Filter years and numbers
        words = [w for w in words if not re.match(r'^(19|20)\d{2}$', w)]
        words = [w for w in words if not w.isdigit()]

        documents.append(words)

    if not documents:
        return []

    # Calculate document frequency (how many docs contain each term)
    df = defaultdict(int)
    for doc in documents:
        for word in set(doc):
            df[word] += 1

    # Filter by minimum document frequency
    df = {word: count for word, count in df.items() if count >= min_df}

    if not df:
        return []

    # Calculate TF-IDF scores
    tfidf_scores = defaultdict(float)
    num_docs = len(documents)

    for doc in documents:
        # Term frequency in this document
        tf = Counter(doc)

        for word, count in tf.items():
            if word in df:
                # TF * IDF
                term_freq = count / len(doc) if len(doc) > 0 else 0
                inverse_doc_freq = math.log(num_docs / df[word])
                tfidf_scores[word] += term_freq * inverse_doc_freq

    # Sort by score
    ranked = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)

    return ranked[:top_n]


def extract_bigram_tfidf(articles, top_n=30, min_df=2):
    """Extract bi-grams (2-word phrases) using TF-IDF."""
    stopwords = {
        'this', 'that', 'with', 'from', 'have', 'been', 'will', 'said', 'says',
        'more', 'about', 'after', 'their', 'which', 'when', 'where', 'there',
        'russia', 'russian', 'moscow', 'kremlin', 'media', 'tass', 'reported',
        'military', 'report', 'political', 'official',
        'article', 'articles', 'story', 'stories', 'read', 'preview', 'https',
        'http', 'link', 'click', 'here', 'view', 'watch', 'full', 'continue'
    }

    # Build bigram collection
    documents = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        words = [w for w in tokenize(text)]

        # Generate bigrams
        bigrams = []
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i+1]

            # Skip if either word is stopword
            if w1 in stopwords or w2 in stopwords:
                continue

            # Skip years/numbers
            if re.match(r'^(19|20)\d{2}$', w1) or re.match(r'^(19|20)\d{2}$', w2):
                continue
            if w1.isdigit() or w2.isdigit():
                continue

            bigrams.append(f"{w1} {w2}")

        documents.append(bigrams)

    if not documents:
        return []

    # Calculate DF
    df = defaultdict(int)
    for doc in documents:
        for bigram in set(doc):
            df[bigram] += 1

    df = {bigram: count for bigram, count in df.items() if count >= min_df}

    if not df:
        return []

    # Calculate TF-IDF
    tfidf_scores = defaultdict(float)
    num_docs = len(documents)

    for doc in documents:
        tf = Counter(doc)

        for bigram, count in tf.items():
            if bigram in df:
                term_freq = count / len(doc) if len(doc) > 0 else 0
                inverse_doc_freq = math.log(num_docs / df[bigram])
                tfidf_scores[bigram] += term_freq * inverse_doc_freq

    ranked = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)

    return ranked[:top_n]


def extract_named_entities(articles):
    """
    Extract named entities (people, places, organizations) using spaCy NER.

    Returns:
        Counter of entity_text: count
    """
    if not NER_AVAILABLE:
        return Counter()

    entities = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}"

        # Remove HTML
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'https?://\S+', ' ', text)

        try:
            doc = nlp(text[:10000])  # Limit text length for performance
            for ent in doc.ents:
                # Focus on geopolitically relevant entity types
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'NORP', 'EVENT']:
                    # Clean and normalize
                    entity_text = ent.text.strip()
                    if len(entity_text) > 3 and not entity_text.isdigit():
                        entities.append(entity_text.lower())
        except:
            pass  # Skip if NER fails on this article

    return Counter(entities)


def extract_enhanced_keywords(articles, top_n=15):
    """
    Enhanced keyword extraction combining multiple techniques:
    1. Named Entity Recognition (people, places, orgs)
    2. TF-IDF keywords
    3. Meaningful bigrams
    4. Geopolitical term boosting

    Returns:
        List of (keyword, score, source) tuples
        source indicates: 'entity', 'keyword', or 'phrase'
    """
    results = []

    # 1. Extract named entities (if available)
    if NER_AVAILABLE:
        entities = extract_named_entities(articles)
        # Boost entities - they're often the most relevant
        for entity, count in entities.most_common(20):
            if count >= 2:  # Must appear in at least 2 articles
                score = count * 2.0  # Boost entity scores
                results.append((entity, score, 'entity'))

    # 2. Extract TF-IDF keywords
    tfidf_keywords = extract_tfidf_keywords(articles, top_n=30, min_df=2)
    for keyword, score in tfidf_keywords:
        # Boost geopolitically relevant terms
        boost = 1.0
        geopolitical_terms = {
            'ukraine', 'ukrainian', 'zelensky', 'biden', 'trump', 'putin',
            'nato', 'sanctions', 'military', 'diplomatic', 'treaty',
            'nuclear', 'alliance', 'summit', 'conflict', 'peace', 'war',
            'china', 'chinese', 'beijing', 'washington', 'europe', 'european'
        }
        if keyword in geopolitical_terms:
            boost = 1.5

        results.append((keyword, score * boost, 'keyword'))

    # 3. Extract meaningful bigrams/phrases
    bigrams = extract_bigram_tfidf(articles, top_n=20, min_df=2)
    for bigram, score in bigrams:
        # Only keep phrases that look meaningful
        words = bigram.split()
        if len(words) == 2:
            # Skip if either word is too common
            common_words = {'government', 'minister', 'president', 'officials'}
            if not any(w in common_words for w in words):
                results.append((bigram, score * 1.2, 'phrase'))

    # Combine and deduplicate
    keyword_scores = defaultdict(lambda: {'score': 0, 'sources': []})
    for keyword, score, source in results:
        keyword_scores[keyword]['score'] += score
        keyword_scores[keyword]['sources'].append(source)

    # Rank by combined score
    ranked = []
    for keyword, data in keyword_scores.items():
        # Bonus for appearing in multiple extraction methods
        diversity_bonus = 1.0 + (len(set(data['sources'])) - 1) * 0.3
        final_score = data['score'] * diversity_bonus
        primary_source = data['sources'][0]
        ranked.append((keyword, final_score, primary_source))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:top_n]


def main():
    """Test TF-IDF extraction."""
    # Example usage
    articles = [
        {'title': 'Putin announces military operation in Ukraine', 'summary': 'Russian president declares special military operation'},
        {'title': 'Ukraine resists Russian invasion', 'summary': 'Ukrainian forces defend against Russian military'},
        {'title': 'NATO condemns Russian aggression', 'summary': 'Alliance responds to Ukraine invasion'},
    ]

    print("TF-IDF Keywords:")
    keywords = extract_tfidf_keywords(articles, top_n=10)
    for word, score in keywords:
        print(f"  {word}: {score:.4f}")

    print("\nTF-IDF Bigrams:")
    bigrams = extract_bigram_tfidf(articles, top_n=10)
    for bigram, score in bigrams:
        print(f"  {bigram}: {score:.4f}")


if __name__ == '__main__':
    main()
