#!/usr/bin/env python3
"""
Advanced keyword extraction using TF-IDF (Term Frequency-Inverse Document Frequency).

More sophisticated than simple word counting - identifies terms that are:
- Frequent in a document (TF)
- Rare across all documents (IDF)

This catches important specific terms while filtering generic common words.

Usage:
    from advanced_keywords import extract_tfidf_keywords
    keywords = extract_tfidf_keywords(articles)
"""

import re
import math
from collections import Counter, defaultdict


def tokenize(text):
    """Extract words from text."""
    text = text.lower()
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
