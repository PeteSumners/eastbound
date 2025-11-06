#!/usr/bin/env python3
"""
Internet Image Fetching Module for Eastbound Reports

Fetches relevant images from various online sources:
- Unsplash: Free stock photos (requires API key)
- Wikipedia: Public domain images (no key required)
- URL thumbnails: Extract images from article URLs
- Custom search: Generic image search with caching

USAGE:
    from fetch_images import fetch_unsplash_image, fetch_wikipedia_image

    img_path = fetch_unsplash_image('ukraine war', output_dir='images/')
    img_path = fetch_wikipedia_image('Vladimir Putin', output_dir='images/')

SETUP:
    1. Get free Unsplash API key: https://unsplash.com/developers
    2. Set environment variable: UNSPLASH_ACCESS_KEY=your_key_here
    3. Or pass api_key parameter to functions

For future AI instances:
- Images are cached locally to avoid re-fetching
- All functions return local file path or None
- Respect rate limits and attribution requirements
"""

import os
import hashlib
import requests
import json
from pathlib import Path
from urllib.parse import quote, urljoin
from typing import Optional, Dict, List
import time


# Cache directory for downloaded images
CACHE_DIR = Path('images/cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Metadata cache for tracking sources and attribution
METADATA_FILE = CACHE_DIR / 'image_metadata.json'


def _load_metadata() -> Dict:
    """Load image metadata cache."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_metadata(metadata: Dict):
    """Save image metadata cache."""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


def _get_cache_key(source: str, query: str) -> str:
    """Generate cache key for query."""
    return hashlib.md5(f"{source}:{query}".encode()).hexdigest()


def _download_image(url: str, output_path: Path, timeout: int = 10) -> Optional[Path]:
    """
    Download image from URL to local path.

    Args:
        url: Image URL
        output_path: Where to save
        timeout: Request timeout in seconds

    Returns:
        Path to saved image or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Eastbound Reports/1.0 (Educational Media Analysis)'
        }

        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        # Check if content is actually an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"[WARNING] URL does not return an image: {content_type}")
            return None

        # Write to file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] Downloaded image: {output_path.name}")
        return output_path

    except Exception as e:
        print(f"[ERROR] Failed to download image: {e}")
        return None


def fetch_unsplash_image(query: str, output_dir: str = 'images/',
                         api_key: Optional[str] = None,
                         orientation: str = 'landscape') -> Optional[Path]:
    """
    Fetch a relevant stock photo from Unsplash.

    Args:
        query: Search query (e.g., 'ukraine war', 'kremlin', 'russian politics')
        output_dir: Directory to save image
        api_key: Unsplash API access key (or set UNSPLASH_ACCESS_KEY env var)
        orientation: 'landscape', 'portrait', or 'squarish'

    Returns:
        Path to downloaded image or None if failed

    Setup:
        Get free API key at https://unsplash.com/developers
        Set environment variable: UNSPLASH_ACCESS_KEY=your_key
    """
    # Get API key
    if not api_key:
        api_key = os.getenv('UNSPLASH_ACCESS_KEY')

    if not api_key:
        print("[WARNING] No Unsplash API key found. Set UNSPLASH_ACCESS_KEY env var.")
        return None

    # Check cache
    cache_key = _get_cache_key('unsplash', query)
    metadata = _load_metadata()

    if cache_key in metadata:
        cached_path = Path(metadata[cache_key]['path'])
        if cached_path.exists():
            print(f"[OK] Using cached Unsplash image: {cached_path.name}")
            return cached_path

    # Search Unsplash
    try:
        search_url = 'https://api.unsplash.com/search/photos'
        params = {
            'query': query,
            'per_page': 1,
            'orientation': orientation
        }
        headers = {
            'Authorization': f'Client-ID {api_key}'
        }

        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data['results']:
            print(f"[WARNING] No Unsplash images found for: {query}")
            return None

        # Get first result
        photo = data['results'][0]
        image_url = photo['urls']['regular']  # 1080px width
        photographer = photo['user']['name']
        photo_id = photo['id']

        # Download image
        output_path = Path(output_dir) / f'unsplash-{cache_key[:12]}.jpg'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        downloaded = _download_image(image_url, output_path)

        if downloaded:
            # Save metadata for attribution
            metadata[cache_key] = {
                'source': 'unsplash',
                'query': query,
                'path': str(output_path),
                'photographer': photographer,
                'photo_id': photo_id,
                'attribution': f'Photo by {photographer} on Unsplash',
                'url': f'https://unsplash.com/photos/{photo_id}'
            }
            _save_metadata(metadata)

            print(f"[OK] Fetched Unsplash image: {photographer}")
            return output_path

    except Exception as e:
        print(f"[ERROR] Unsplash fetch failed: {e}")
        return None


def fetch_wikipedia_image(article_title: str, output_dir: str = 'images/') -> Optional[Path]:
    """
    Fetch the main image from a Wikipedia article.

    Args:
        article_title: Wikipedia article title (e.g., 'Vladimir Putin', 'Kremlin')
        output_dir: Directory to save image

    Returns:
        Path to downloaded image or None if failed

    Note:
        Wikipedia images are public domain or freely licensed.
        No API key required.
    """
    # Check cache
    cache_key = _get_cache_key('wikipedia', article_title)
    metadata = _load_metadata()

    if cache_key in metadata:
        cached_path = Path(metadata[cache_key]['path'])
        if cached_path.exists():
            print(f"[OK] Using cached Wikipedia image: {cached_path.name}")
            return cached_path

    try:
        # Use Wikipedia API to get page info
        api_url = 'https://en.wikipedia.org/w/api.php'
        params = {
            'action': 'query',
            'titles': article_title,
            'prop': 'pageimages',
            'format': 'json',
            'pithumbsize': 1000  # Max width
        }

        headers = {
            'User-Agent': 'Eastbound Reports/1.0 (https://github.com/PeteSumners/eastbound; Educational Media Analysis)',
            'Accept': 'application/json'
        }

        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        pages = data['query']['pages']
        page_id = list(pages.keys())[0]

        if page_id == '-1':
            print(f"[WARNING] Wikipedia article not found: {article_title}")
            return None

        page = pages[page_id]

        if 'thumbnail' not in page:
            print(f"[WARNING] No image found for Wikipedia article: {article_title}")
            return None

        image_url = page['thumbnail']['source']

        # Download image
        output_path = Path(output_dir) / f'wikipedia-{cache_key[:12]}.jpg'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        downloaded = _download_image(image_url, output_path)

        if downloaded:
            # Save metadata
            metadata[cache_key] = {
                'source': 'wikipedia',
                'article': article_title,
                'path': str(output_path),
                'attribution': f'Image from Wikipedia: {article_title}',
                'url': f'https://en.wikipedia.org/wiki/{quote(article_title)}'
            }
            _save_metadata(metadata)

            print(f"[OK] Fetched Wikipedia image for: {article_title}")
            return output_path

    except Exception as e:
        print(f"[ERROR] Wikipedia fetch failed: {e}")
        return None


def fetch_article_thumbnail(url: str, output_dir: str = 'images/') -> Optional[Path]:
    """
    Extract thumbnail/featured image from article URL using Open Graph tags.

    Args:
        url: Article URL
        output_dir: Directory to save image

    Returns:
        Path to downloaded image or None if failed
    """
    # Check cache
    cache_key = _get_cache_key('article', url)
    metadata = _load_metadata()

    if cache_key in metadata:
        cached_path = Path(metadata[cache_key]['path'])
        if cached_path.exists():
            print(f"[OK] Using cached article thumbnail: {cached_path.name}")
            return cached_path

    try:
        # Fetch HTML
        headers = {
            'User-Agent': 'Eastbound Reports/1.0 (Educational Media Analysis)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        html = response.text

        # Look for Open Graph image tag
        import re
        og_image = re.search(r'<meta property="og:image" content="([^"]+)"', html)

        if not og_image:
            # Try Twitter card
            og_image = re.search(r'<meta name="twitter:image" content="([^"]+)"', html)

        if not og_image:
            print(f"[WARNING] No thumbnail found in article: {url}")
            return None

        image_url = og_image.group(1)

        # Make absolute URL if needed
        if not image_url.startswith('http'):
            image_url = urljoin(url, image_url)

        # Download image
        output_path = Path(output_dir) / f'article-{cache_key[:12]}.jpg'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        downloaded = _download_image(image_url, output_path)

        if downloaded:
            # Save metadata
            metadata[cache_key] = {
                'source': 'article',
                'url': url,
                'path': str(output_path),
                'image_url': image_url
            }
            _save_metadata(metadata)

            print(f"[OK] Fetched article thumbnail")
            return output_path

    except Exception as e:
        print(f"[ERROR] Article thumbnail fetch failed: {e}")
        return None


def get_image_attribution(image_path: Path) -> Optional[str]:
    """
    Get attribution text for a downloaded image.

    Args:
        image_path: Path to image file

    Returns:
        Attribution string or None
    """
    metadata = _load_metadata()

    # Find metadata for this image
    for cache_key, info in metadata.items():
        if Path(info['path']) == image_path:
            return info.get('attribution')

    return None


def fetch_relevant_image(briefing_data: Dict, output_dir: str = 'images/') -> Optional[Path]:
    """
    Smart fetcher that tries multiple sources to get a relevant image.

    Args:
        briefing_data: Briefing JSON with trending stories
        output_dir: Directory to save image

    Returns:
        Path to downloaded image or None if all sources fail

    Strategy:
        1. If top keyword is a person, try Wikipedia
        2. If top keyword is a location, try Wikipedia
        3. Fall back to Unsplash with generic query
    """
    if not briefing_data.get('trending_stories'):
        return None

    top_keyword = briefing_data['trending_stories'][0]['keyword']

    # List of known entities that have Wikipedia articles
    people = ['putin', 'zelensky', 'lavrov', 'biden', 'trump', 'medvedev']
    places = ['ukraine', 'russia', 'kremlin', 'moscow', 'kyiv', 'donbas']

    # Try Wikipedia for known entities
    if top_keyword.lower() in people:
        capitalized = top_keyword.capitalize()
        img = fetch_wikipedia_image(capitalized, output_dir)
        if img:
            return img

    if top_keyword.lower() in places:
        capitalized = top_keyword.capitalize()
        img = fetch_wikipedia_image(capitalized, output_dir)
        if img:
            return img

    # Fall back to Unsplash
    query = f"{top_keyword} russia news"
    return fetch_unsplash_image(query, output_dir, orientation='landscape')


if __name__ == '__main__':
    # Demo
    import argparse

    parser = argparse.ArgumentParser(description='Fetch images from the internet')
    parser.add_argument('--source', choices=['unsplash', 'wikipedia', 'article'],
                       default='unsplash', help='Image source')
    parser.add_argument('--query', required=True, help='Search query or article title/URL')
    parser.add_argument('--output', default='images/', help='Output directory')

    args = parser.parse_args()

    if args.source == 'unsplash':
        result = fetch_unsplash_image(args.query, args.output)
    elif args.source == 'wikipedia':
        result = fetch_wikipedia_image(args.query, args.output)
    elif args.source == 'article':
        result = fetch_article_thumbnail(args.query, args.output)

    if result:
        print(f"\n[SUCCESS] Image saved: {result}")
        attribution = get_image_attribution(result)
        if attribution:
            print(f"[INFO] Attribution: {attribution}")
    else:
        print("\n[FAILED] Could not fetch image")
