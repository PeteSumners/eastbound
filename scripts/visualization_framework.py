#!/usr/bin/env python3
"""
Eastbound Visualization Framework

A modular system for creating data visualizations for Eastbound Reports.
Designed to be easily extensible by future AI instances or developers.

PHILOSOPHY:
- Every chart type is a class with consistent interface
- New chart types can be added by subclassing BaseChart
- Charts are registered in CHART_REGISTRY for discoverability
- All charts follow same style guide (colors, fonts, layout)

HOW TO ADD A NEW CHART TYPE:
1. Subclass BaseChart
2. Implement generate() method
3. Add to CHART_REGISTRY
4. Document in AI_VISUALIZATION_GUIDE.md

Example:
    class MyNewChart(BaseChart):
        def generate(self, data, output_path):
            # Your visualization logic here
            pass

    CHART_REGISTRY['my_chart'] = MyNewChart

USAGE:
    from visualization_framework import create_chart

    chart = create_chart('keyword_trend', briefing_data)
    chart.generate(output_path='images/chart.png')
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from datetime import datetime
from abc import ABC, abstractmethod


# EASTBOUND BRAND COLORS
COLORS = {
    'primary': '#c74440',      # Eastbound red
    'secondary': '#e57373',    # Light red
    'accent': '#ff6f60',       # Bright red-orange
    'dark': '#1a1a1a',         # Almost black
    'light': '#f5f5f5',        # Off-white
    'text': '#333333',         # Dark gray
    'text_light': '#666666',   # Medium gray
    'grid': '#cccccc',         # Light gray
}

PALETTE = ['#c74440', '#e57373', '#ef5350', '#f44336',
           '#ff6f60', '#ff8a80', '#ffab91', '#ffccbc']


class BaseChart(ABC):
    """
    Base class for all chart types.

    All charts must implement the generate() method.
    Subclasses inherit common styling and utilities.
    """

    def __init__(self, title=None, figsize=(10, 6)):
        self.title = title
        self.figsize = figsize
        self.fig = None
        self.ax = None

    def _setup_figure(self):
        """Create figure and axis with standard settings."""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)

    def _apply_style(self):
        """Apply Eastbound brand styling to the current plot."""
        if self.title:
            self.ax.set_title(self.title, fontsize=14,
                            fontweight='bold', pad=20,
                            color=COLORS['text'])

        # Grid styling
        self.ax.grid(alpha=0.3, linestyle='--', linewidth=0.5)

        # Spine styling
        for spine in self.ax.spines.values():
            spine.set_color(COLORS['grid'])
            spine.set_linewidth(0.5)

    def _save_and_close(self, output_path, dpi=150):
        """Save figure and clean up."""
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(self.fig)
        return output_path

    @abstractmethod
    def generate(self, data, output_path):
        """
        Generate the chart.

        Args:
            data: Chart-specific data (dict, list, etc.)
            output_path: Where to save the PNG

        Returns:
            Path to saved image
        """
        pass


class KeywordTrendChart(BaseChart):
    """
    Horizontal bar chart showing top trending keywords.

    Data format: List of dicts with 'keyword' and 'source_count' keys
    """

    def generate(self, data, output_path):
        self._setup_figure()

        keywords = [item['keyword'] for item in data[:10]]
        counts = [item['source_count'] for item in data[:10]]

        y_pos = range(len(keywords))
        bars = self.ax.barh(y_pos, counts, color=COLORS['primary'])

        self.ax.set_yticks(y_pos)
        self.ax.set_yticklabels(keywords)
        self.ax.invert_yaxis()
        self.ax.set_xlabel('Number of Sources', fontsize=12, fontweight='bold')

        # Value labels on bars
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            self.ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                        f'{count}', ha='left', va='center',
                        fontweight='bold', color=COLORS['text'])

        self.title = 'Top Trending Topics in Russian Media'
        self._apply_style()
        return self._save_and_close(output_path)


class SourceDistributionChart(BaseChart):
    """
    Pie chart showing article distribution across sources.

    Data format: List of article dicts with 'source' key
    """

    def __init__(self):
        super().__init__(figsize=(10, 8))

    def generate(self, data, output_path):
        self._setup_figure()

        # Count articles per source
        source_counts = Counter(article['source'] for article in data)
        top_sources = source_counts.most_common(8)

        # Combine small sources into "Other"
        other_count = sum(count for source, count in source_counts.items()
                         if source not in dict(top_sources))
        if other_count > 0:
            top_sources.append(('Other', other_count))

        sources = [s[0] for s in top_sources]
        counts = [s[1] for s in top_sources]

        # Custom autopct function to hide percentages for very small slices
        def make_autopct(values):
            def my_autopct(pct):
                # Only show percentage if > 5%
                return f'{pct:.1f}%' if pct > 5 else ''
            return my_autopct

        wedges, texts, autotexts = self.ax.pie(
            counts, labels=sources, autopct=make_autopct(counts),
            colors=PALETTE[:len(sources)], startangle=90,
            pctdistance=0.85  # Move percentages closer to center to avoid overlap
        )

        # Style labels (source names)
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
            text.set_color(COLORS['text'])

        # Style percentages
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        self.title = 'Article Distribution by Source'
        self.ax.set_title(self.title, fontsize=14, fontweight='bold',
                         pad=20, color=COLORS['text'])

        return self._save_and_close(output_path)


class SocialMediaCard(BaseChart):
    """
    Featured image card for social media sharing.

    Data format: Dict with 'date', 'total_articles', 'top_keyword'
    """

    def __init__(self):
        super().__init__(figsize=(12, 6))

    def generate(self, data, output_path):
        self._setup_figure()

        self.fig.patch.set_facecolor(COLORS['dark'])
        self.ax.set_facecolor(COLORS['dark'])
        self.ax.axis('off')

        # Title
        self.ax.text(0.5, 0.75, 'EASTBOUND REPORTS',
                    ha='center', va='center', fontsize=32,
                    fontweight='bold', color=COLORS['primary'],
                    transform=self.ax.transAxes)

        # Subtitle
        self.ax.text(0.5, 0.60, 'Russian Media Analysis',
                    ha='center', va='center', fontsize=18,
                    color='white', transform=self.ax.transAxes)

        # Date
        date_formatted = datetime.strptime(data['date'], '%Y-%m-%d').strftime('%B %d, %Y')
        self.ax.text(0.5, 0.45, date_formatted,
                    ha='center', va='center', fontsize=14,
                    color='#aaaaaa', transform=self.ax.transAxes)

        # Stats
        self.ax.text(0.5, 0.30, f"{data['total_articles']} ARTICLES ANALYZED",
                    ha='center', va='center', fontsize=16,
                    fontweight='bold', color='white',
                    transform=self.ax.transAxes)

        # Top keyword
        self.ax.text(0.5, 0.15, f"Top Topic: {data['top_keyword'].upper()}",
                    ha='center', va='center', fontsize=14,
                    color=COLORS['primary'], transform=self.ax.transAxes)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor=COLORS['dark'], edgecolor='none')
        plt.close(self.fig)
        return output_path


class StatsCard(BaseChart):
    """
    Statistics infographic showing key numbers.

    Data format: Dict with 'total_articles', 'sources', 'trending_count', 'date'
    """

    def __init__(self):
        super().__init__(figsize=(8, 10))

    def generate(self, data, output_path):
        self._setup_figure()

        self.fig.patch.set_facecolor(COLORS['light'])
        self.ax.set_facecolor(COLORS['light'])
        self.ax.axis('off')

        # Title
        self.ax.text(0.5, 0.95, 'BY THE NUMBERS',
                    ha='center', va='top', fontsize=24,
                    fontweight='bold', color=COLORS['text'],
                    transform=self.ax.transAxes)

        date_formatted = datetime.strptime(data['date'], '%Y-%m-%d').strftime('%B %d, %Y')
        self.ax.text(0.5, 0.90, date_formatted,
                    ha='center', va='top', fontsize=12,
                    color=COLORS['text_light'], transform=self.ax.transAxes)

        # Stats
        stats = [
            (data['total_articles'], 'Articles Analyzed'),
            (data['sources'], 'Media Sources'),
            (data['trending_count'], 'Trending Topics'),
        ]

        y_start = 0.75
        y_step = 0.20

        for i, (number, label) in enumerate(stats):
            y = y_start - (i * y_step)

            self.ax.text(0.5, y, f'{number}',
                        ha='center', va='center', fontsize=48,
                        fontweight='bold', color=COLORS['primary'],
                        transform=self.ax.transAxes)

            self.ax.text(0.5, y - 0.08, label,
                        ha='center', va='center', fontsize=16,
                        color=COLORS['text'], transform=self.ax.transAxes)

        # Footer
        self.ax.text(0.5, 0.05, 'eastboundreports.com',
                    ha='center', va='bottom', fontsize=12,
                    color=COLORS['text_light'], transform=self.ax.transAxes)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor=COLORS['light'], edgecolor='none')
        plt.close(self.fig)
        return output_path


class TimelineChart(BaseChart):
    """
    Timeline showing narrative evolution over time.

    Data format: List of dicts with 'date', 'event', 'importance' keys

    EXAMPLE FOR FUTURE AI:
        data = [
            {'date': '2022-02-24', 'event': 'Invasion begins', 'importance': 10},
            {'date': '2022-04-01', 'event': 'Kyiv withdrawal', 'importance': 8},
            ...
        ]
    """

    def generate(self, data, output_path):
        self._setup_figure()
        self.fig, self.ax = plt.subplots(figsize=(14, 6))

        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in data]
        events = [item['event'] for item in data]
        importance = [item.get('importance', 5) for item in data]

        # Plot timeline
        self.ax.scatter(dates, [0] * len(dates), s=[imp * 30 for imp in importance],
                       c=importance, cmap='Reds', alpha=0.6, edgecolors='black')

        # Add event labels
        for date, event in zip(dates, events):
            self.ax.annotate(event, xy=(date, 0), xytext=(0, 20),
                           textcoords='offset points', ha='center',
                           fontsize=9, rotation=45)

        self.ax.set_ylim(-1, 1)
        self.ax.set_yticks([])
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)

        self.title = 'Narrative Timeline'
        self._apply_style()
        return self._save_and_close(output_path)


class WordCloudChart(BaseChart):
    """
    Word cloud visualization (requires wordcloud library).

    Data format: Dict mapping words to frequencies

    NOTE: Requires 'pip install wordcloud'
    """

    def generate(self, data, output_path):
        try:
            from wordcloud import WordCloud
        except ImportError:
            print("[ERROR] wordcloud library not installed. Run: pip install wordcloud")
            return None

        self._setup_figure()

        # Generate word cloud
        wc = WordCloud(width=800, height=400,
                      background_color='white',
                      colormap='Reds',
                      max_words=50).generate_from_frequencies(data)

        self.ax.imshow(wc, interpolation='bilinear')
        self.ax.axis('off')

        self.title = 'Most Mentioned Terms'
        if self.title:
            self.ax.set_title(self.title, fontsize=14, fontweight='bold',
                            pad=20, color=COLORS['text'])

        return self._save_and_close(output_path)


# CHART REGISTRY
# Add new chart types here for discoverability
CHART_REGISTRY = {
    'keyword_trend': KeywordTrendChart,
    'source_distribution': SourceDistributionChart,
    'social_card': SocialMediaCard,
    'stats_card': StatsCard,
    'timeline': TimelineChart,
    'word_cloud': WordCloudChart,
}


def create_chart(chart_type, **kwargs):
    """
    Factory function to create chart instances.

    Args:
        chart_type: String key from CHART_REGISTRY
        **kwargs: Arguments passed to chart constructor

    Returns:
        Chart instance

    Example:
        chart = create_chart('keyword_trend')
        chart.generate(data, 'output.png')
    """
    if chart_type not in CHART_REGISTRY:
        raise ValueError(f"Unknown chart type: {chart_type}. "
                        f"Available: {list(CHART_REGISTRY.keys())}")

    chart_class = CHART_REGISTRY[chart_type]
    return chart_class(**kwargs)


def list_available_charts():
    """Print all registered chart types with descriptions."""
    print("Available Chart Types:\n")
    for name, chart_class in CHART_REGISTRY.items():
        print(f"  {name}: {chart_class.__doc__.strip().split(chr(10))[0]}")


if __name__ == '__main__':
    # Demo
    list_available_charts()
