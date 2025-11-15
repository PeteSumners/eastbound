#!/usr/bin/env python3
"""
Verify GitHub Pages deployment and check published article
"""
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

def verify_article_published(date_str, max_wait=300):
    """Verify article is published and accessible on GitHub Pages."""

    # Expected URL pattern based on frontmatter
    base_url = "https://petesumners.github.io/eastbound"

    # Try multiple possible URL patterns
    possible_urls = [
        f"{base_url}/analysis/ukraine/{date_str.replace('-', '/')}/analysis.html",
        f"{base_url}/{date_str.replace('-', '/')}/analysis.html",
        f"{base_url}/posts/{date_str}-analysis.html",
    ]

    print(f"\n[VERIFY] Checking GitHub Pages deployment...", flush=True)
    print(f"[VERIFY] Date: {date_str}", flush=True)

    start_time = time.time()
    attempt = 0

    while time.time() - start_time < max_wait:
        attempt += 1

        for url in possible_urls:
            try:
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    print(f"\n[SUCCESS] Article is live!", flush=True)
                    print(f"[SUCCESS] URL: {url}", flush=True)
                    print(f"[SUCCESS] HTTP Status: {response.status_code}", flush=True)
                    print(f"[SUCCESS] Response size: {len(response.content)} bytes", flush=True)
                    return True, url

            except Exception as e:
                pass  # Try next URL

        # Wait before retrying
        if attempt == 1:
            print(f"[VERIFY] Not published yet, waiting for GitHub Pages build...", flush=True)

        elapsed = int(time.time() - start_time)
        remaining = max_wait - elapsed

        if remaining > 0 and attempt % 6 == 0:  # Every 30 seconds
            print(f"[VERIFY] Still waiting... ({elapsed}s elapsed, {remaining}s remaining)", flush=True)

        time.sleep(5)

    print(f"\n[FAILED] Article not accessible after {max_wait}s", flush=True)
    print(f"[FAILED] Tried URLs:", flush=True)
    for url in possible_urls:
        print(f"  - {url}", flush=True)

    return False, None


def main():
    date = datetime.now().strftime('%Y-%m-%d')

    # Wait for GitHub Pages to build (usually 30-60 seconds)
    print(f"[INFO] Waiting 60 seconds for GitHub Pages to build...", flush=True)
    time.sleep(60)

    success, url = verify_article_published(date, max_wait=240)

    if success:
        print(f"\n[OK] Verification passed!", flush=True)
        return 0
    else:
        print(f"\n[ERROR] Verification failed!", flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
