#!/usr/bin/env python3
"""
Example Chart Implementations for Future AI Instances

This file contains complete, working examples of how to add new chart types
to the Eastbound visualization framework. Copy these patterns when creating
new charts.

HOW TO USE THESE EXAMPLES:
1. Copy the chart class you want to implement
2. Modify the generate() method for your specific data
3. Add your chart to CHART_REGISTRY in visualization_framework.py
4. Test with sample data
5. Document in AI_VISUALIZATION_GUIDE.md

Each example is fully functional and can be imported directly.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import Counter
import numpy as np

# Import base class and colors
from visualization_framework import BaseChart, COLORS


# ============================================================================
# EXAMPLE 1: Simple Line Chart - Sentiment Timeline
# ============================================================================

class SentimentTimelineChart(BaseChart):
    """
    Line chart showing sentiment (positive/negative) over time.

    Use case: Track emotional framing shifts in Russian media coverage
    Data format: List of dicts with 'date' and 'sentiment' keys
        [
            {'date': '2025-01-01', 'sentiment': 0.3},
            {'date': '2025-01-02', 'sentiment': -0.2},
            ...
        ]
    Sentiment scale: -1.0 (very negative) to +1.0 (very positive)

    IMPLEMENTATION NOTES:
    - Uses fill_between() for visual impact
    - Axhline at y=0 shows neutral line
    - Date parsing with datetime
    - Green fill for positive, red for negative
    """

    def __init__(self):
        super().__init__(figsize=(12, 6))

    def generate(self, data, output_path):
        self._setup_figure()

        # Parse data
        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in data]
        sentiments = [item['sentiment'] for item in data]

        # Main line
        self.ax.plot(dates, sentiments, color=COLORS['primary'],
                    linewidth=2.5, marker='o', markersize=4)

        # Zero line (neutral)
        self.ax.axhline(y=0, color=COLORS['text'], linestyle='--',
                       alpha=0.3, linewidth=1)

        # Fill positive area (green)
        self.ax.fill_between(dates, 0, sentiments,
                            where=[s > 0 for s in sentiments],
                            alpha=0.2, color='green', interpolate=True)

        # Fill negative area (red)
        self.ax.fill_between(dates, 0, sentiments,
                            where=[s < 0 for s in sentiments],
                            alpha=0.2, color=COLORS['primary'], interpolate=True)

        # Labels
        self.ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Sentiment Score', fontsize=12, fontweight='bold')
        self.ax.set_ylim(-1.1, 1.1)

        # Add text labels
        self.ax.text(0.02, 0.98, 'Positive', transform=self.ax.transAxes,
                    fontsize=10, va='top', color='green')
        self.ax.text(0.02, 0.02, 'Negative', transform=self.ax.transAxes,
                    fontsize=10, va='bottom', color=COLORS['primary'])

        self.title = 'Sentiment Over Time'
        self._apply_style()
        return self._save_and_close(output_path)


# ============================================================================
# EXAMPLE 2: Grouped Bar Chart - Comparison
# ============================================================================

class ComparisonBarChart(BaseChart):
    """
    Side-by-side bar chart comparing two data series.

    Use case: Compare Russian vs Western media coverage of topics
    Data format: Dict with topics and two value lists
        {
            'topics': ['Ukraine', 'NATO', 'Economy', ...],
            'russian_coverage': [45, 30, 15, ...],
            'western_coverage': [60, 25, 10, ...]
        }

    IMPLEMENTATION NOTES:
    - Uses np.arange() for x-positions
    - Width of 0.35 leaves gap between groups
    - Legend shows what each color represents
    """

    def __init__(self):
        super().__init__(figsize=(10, 6))

    def generate(self, data, output_path):
        self._setup_figure()

        topics = data['topics']
        russian = data['russian_coverage']
        western = data['western_coverage']

        # Bar positions
        x = np.arange(len(topics))
        width = 0.35

        # Create bars
        bars1 = self.ax.bar(x - width/2, russian, width,
                           label='Russian Media', color=COLORS['primary'])
        bars2 = self.ax.bar(x + width/2, western, width,
                           label='Western Media', color=COLORS['text_light'])

        # Labels
        self.ax.set_xlabel('Topic', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Article Count', fontsize=12, fontweight='bold')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(topics, rotation=45, ha='right')
        self.ax.legend()

        self.title = 'Coverage Comparison: Russian vs Western Media'
        self._apply_style()
        return self._save_and_close(output_path)


# ============================================================================
# EXAMPLE 3: Stacked Area Chart - Topic Evolution
# ============================================================================

class TopicEvolutionChart(BaseChart):
    """
    Stacked area chart showing how topic prevalence changes over time.

    Use case: Show shifting focus in Russian media narratives
    Data format: Dict with dates and topic counts
        {
            'dates': ['2025-01-01', '2025-01-02', ...],
            'topics': {
                'Ukraine': [10, 12, 15, ...],
                'NATO': [5, 6, 4, ...],
                'Economy': [3, 3, 5, ...],
            }
        }

    IMPLEMENTATION NOTES:
    - stackplot() automatically handles stacking
    - Use color palette for multiple topics
    - Legend placement can be tricky with many topics
    """

    def __init__(self):
        super().__init__(figsize=(12, 6))

    def generate(self, data, output_path):
        self._setup_figure()

        dates = [datetime.strptime(d, '%Y-%m-%d') for d in data['dates']]
        topics = data['topics']

        # Prepare data for stackplot
        topic_names = list(topics.keys())
        values = [topics[name] for name in topic_names]

        # Create stacked area
        from visualization_framework import PALETTE
        self.ax.stackplot(dates, *values, labels=topic_names,
                         colors=PALETTE[:len(topic_names)], alpha=0.8)

        # Labels
        self.ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
        self.ax.legend(loc='upper left', fontsize=10)

        self.title = 'Topic Evolution Over Time'
        self._apply_style()
        return self._save_and_close(output_path)


# ============================================================================
# EXAMPLE 4: Simple Scatter - Keyword Importance
# ============================================================================

class KeywordImportanceScatter(BaseChart):
    """
    Scatter plot showing keyword frequency vs recency.

    Use case: Identify hot topics (frequent AND recent)
    Data format: List of dicts with keyword, count, and days_since_first
        [
            {'keyword': 'Ukraine', 'count': 45, 'days_ago': 1},
            {'keyword': 'sanctions', 'count': 30, 'days_ago': 3},
            ...
        ]

    IMPLEMENTATION NOTES:
    - Size represents importance (bubble chart)
    - Color intensity could represent sentiment
    - Annotate top keywords with text labels
    """

    def __init__(self):
        super().__init__(figsize=(10, 8))

    def generate(self, data, output_path):
        self._setup_figure()

        keywords = [item['keyword'] for item in data]
        counts = [item['count'] for item in data]
        recency = [item['days_ago'] for item in data]

        # Size bubbles by frequency
        sizes = [count * 10 for count in counts]

        # Scatter plot
        scatter = self.ax.scatter(recency, counts, s=sizes,
                                 color=COLORS['primary'], alpha=0.6,
                                 edgecolors=COLORS['dark'], linewidth=1)

        # Annotate top 5 keywords
        for i, (keyword, x, y) in enumerate(zip(keywords[:5], recency[:5], counts[:5])):
            self.ax.annotate(keyword, (x, y), xytext=(5, 5),
                           textcoords='offset points', fontsize=9,
                           color=COLORS['text'])

        # Labels
        self.ax.set_xlabel('Days Since First Mention', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Mention Count', fontsize=12, fontweight='bold')

        # Quadrant lines (optional)
        median_x = np.median(recency)
        median_y = np.median(counts)
        self.ax.axvline(median_x, color=COLORS['grid'], linestyle='--', alpha=0.3)
        self.ax.axhline(median_y, color=COLORS['grid'], linestyle='--', alpha=0.3)

        # Quadrant labels
        self.ax.text(0.95, 0.95, 'Hot Topics\n(New & Frequent)',
                    transform=self.ax.transAxes, ha='right', va='top',
                    fontsize=9, color=COLORS['primary'], fontweight='bold')

        self.title = 'Keyword Importance: Frequency vs Recency'
        self._apply_style()
        return self._save_and_close(output_path)


# ============================================================================
# EXAMPLE 5: Horizontal Bar with Custom Styling - Source Credibility
# ============================================================================

class SourceCredibilityChart(BaseChart):
    """
    Horizontal bar chart with diverging colors for credibility ratings.

    Use case: Show how credible different Russian media sources are
    Data format: List of dicts with source name and credibility score
        [
            {'source': 'TASS', 'credibility': 0.7},
            {'source': 'RT', 'credibility': 0.3},
            ...
        ]
    Credibility: 0.0 (low) to 1.0 (high)

    IMPLEMENTATION NOTES:
    - Different colors for high/low credibility
    - Horizontal bars are easier to read with long labels
    - Add value labels for exact scores
    """

    def __init__(self):
        super().__init__(figsize=(10, 6))

    def generate(self, data, output_path):
        self._setup_figure()

        sources = [item['source'] for item in data]
        scores = [item['credibility'] for item in data]

        y_pos = range(len(sources))

        # Color bars based on score
        colors_list = [COLORS['primary'] if score >= 0.5 else COLORS['text_light']
                      for score in scores]

        bars = self.ax.barh(y_pos, scores, color=colors_list)

        # Customize
        self.ax.set_yticks(y_pos)
        self.ax.set_yticklabels(sources)
        self.ax.invert_yaxis()
        self.ax.set_xlabel('Credibility Score', fontsize=12, fontweight='bold')
        self.ax.set_xlim(0, 1.0)

        # Value labels
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            self.ax.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                        f'{score:.2f}', ha='left', va='center',
                        fontweight='bold', color=COLORS['text'])

        # Reference line at 0.5
        self.ax.axvline(0.5, color=COLORS['text'], linestyle='--',
                       alpha=0.3, linewidth=1)

        self.title = 'Source Credibility Ratings'
        self._apply_style()
        return self._save_and_close(output_path)


# ============================================================================
# HOW TO ADD THESE TO THE FRAMEWORK
# ============================================================================

"""
To add any of these charts to the main framework:

1. Copy the class to visualization_framework.py (or import from here)

2. Add to CHART_REGISTRY in visualization_framework.py:

   CHART_REGISTRY = {
       'keyword_trend': KeywordTrendChart,
       'source_distribution': SourceDistributionChart,
       'social_card': SocialMediaCard,
       'stats_card': StatsCard,
       'timeline': TimelineChart,
       'word_cloud': WordCloudChart,

       # New charts from examples:
       'sentiment_timeline': SentimentTimelineChart,
       'comparison_bar': ComparisonBarChart,
       'topic_evolution': TopicEvolutionChart,
       'keyword_importance': KeywordImportanceScatter,
       'source_credibility': SourceCredibilityChart,
   }

3. Use it:

   from visualization_framework import create_chart

   chart = create_chart('sentiment_timeline')
   chart.generate(data, 'output.png')

4. Document in AI_VISUALIZATION_GUIDE.md under "Common Chart Types to Add"
"""


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("Example Charts Module")
    print("=" * 50)
    print("\nAvailable example charts:")
    print("  1. SentimentTimelineChart")
    print("  2. ComparisonBarChart")
    print("  3. TopicEvolutionChart")
    print("  4. KeywordImportanceScatter")
    print("  5. SourceCredibilityChart")
    print("\nTo test an example:")
    print("  python example_charts.py")
    print("\nTo use in production:")
    print("  1. Copy class to visualization_framework.py")
    print("  2. Add to CHART_REGISTRY")
    print("  3. Document in AI_VISUALIZATION_GUIDE.md")
    print("\n" + "=" * 50)

    # Generate sample data and test one chart
    print("\nGenerating sample sentiment timeline...")

    # Sample data
    from datetime import date
    sample_data = []
    for i in range(30):
        d = date.today() - timedelta(days=30-i)
        sentiment = np.sin(i / 5) * 0.7  # Oscillating sentiment
        sample_data.append({
            'date': d.strftime('%Y-%m-%d'),
            'sentiment': sentiment
        })

    # Generate chart
    chart = SentimentTimelineChart()
    output = 'test-sentiment-timeline.png'
    chart.generate(sample_data, output)
    print(f"[OK] Test chart created: {output}")
    print("Open the file to view the result.")
