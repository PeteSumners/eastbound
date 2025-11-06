#!/usr/bin/env python3
"""
Centralized configuration for Eastbound Reports.

This module provides consistent URLs, paths, and settings across all scripts.
"""

import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# SITE URLS
# ============================================================================

SITE_BASE_URL = "https://petesumners.github.io/eastbound"
SITE_BASEURL = "/eastbound"  # For Jekyll asset paths

def generate_post_url(filename: str) -> str:
    """
    Generate the canonical post URL from a filename.

    Args:
        filename: Post filename in format YYYY-MM-DD-slug.md

    Returns:
        Full URL to the published post (e.g., https://petesumners.github.io/eastbound/2025/11/06/ukraine.html)

    Example:
        >>> generate_post_url("2025-11-06-ukraine.md")
        'https://petesumners.github.io/eastbound/2025/11/06/ukraine.html'
    """
    # Extract filename without extension
    if isinstance(filename, Path):
        filename = filename.stem
    else:
        filename = os.path.basename(filename).replace('.md', '')

    # Parse date parts: YYYY-MM-DD-slug.md -> /YYYY/MM/DD/slug.html
    parts = filename.split('-', 3)

    if len(parts) >= 4:
        year, month, day = parts[0], parts[1], parts[2]
        slug = parts[3]
        return f"{SITE_BASE_URL}/{year}/{month}/{day}/{slug}.html"
    else:
        # Fallback to homepage if filename doesn't match expected format
        return SITE_BASE_URL


def generate_image_path(today: str, image_type: str) -> str:
    """
    Generate Jekyll-compatible image path.

    Args:
        today: Date string in YYYY-MM-DD format
        image_type: Image type (e.g., 'keywords', 'sources', 'stats', 'featured')

    Returns:
        Jekyll asset path (e.g., /eastbound/images/2025-11-06-keywords.png)
    """
    return f"{SITE_BASEURL}/images/{today}-{image_type}.png"


# ============================================================================
# DIRECTORY PATHS
# ============================================================================

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Content directories
RESEARCH_DIR = PROJECT_ROOT / "research"
DRAFTS_DIR = PROJECT_ROOT / "content" / "drafts"
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "images"
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

# ============================================================================
# AI CONFIGURATION
# ============================================================================

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

# Anti-hallucination system
ANTI_HALLUCINATION_ENABLED = True
REQUIRE_SOURCE_CITATIONS = True

# ============================================================================
# SOCIAL MEDIA
# ============================================================================

TWITTER_HASHTAGS = "#Russia #MediaAnalysis #Geopolitics"
LINKEDIN_HASHTAGS = "#RussianMedia #MediaAnalysis #Geopolitics #EastboundReports"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_today_string() -> str:
    """Get today's date as YYYY-MM-DD string."""
    return datetime.now().strftime("%Y-%m-%d")


def get_briefing_path(date: str = None) -> Path:
    """Get path to briefing file for a given date (defaults to today)."""
    if date is None:
        date = get_today_string()
    return RESEARCH_DIR / f"{date}-briefing.json"


def get_draft_path(date: str = None) -> Path:
    """Get path to draft file for a given date (defaults to today)."""
    if date is None:
        date = get_today_string()
    # Drafts use pattern: YYYY-MM-DD-*.md (slug varies)
    # Return directory - caller must search for file
    return DRAFTS_DIR


def get_post_path(filename: str) -> Path:
    """Get full path to a post file."""
    return POSTS_DIR / filename
