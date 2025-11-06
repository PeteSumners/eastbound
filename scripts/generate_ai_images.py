#!/usr/bin/env python3
"""
AI Image Generation for Eastbound Reports

Generates custom images using AI (DALL-E, Stable Diffusion, etc.)
These images are tailored to your specific content and 100% legal to use.

Supported providers:
- OpenAI DALL-E 3 (best quality, $0.04/image)
- Stability AI (Stable Diffusion, $0.01/image)
- Local Stable Diffusion (free, requires GPU)

Usage:
    python generate_ai_images.py --prompt "Kremlin at sunset, editorial style" --output images/
    python generate_ai_images.py --briefing research/briefing.json --auto
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
import requests
import hashlib
from typing import Optional, Dict


# Cache directory for generated images
CACHE_DIR = Path('images/ai_generated')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Metadata file
METADATA_FILE = CACHE_DIR / 'ai_image_metadata.json'


def _load_metadata() -> Dict:
    """Load AI image metadata cache."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_metadata(metadata: Dict):
    """Save AI image metadata cache."""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


def _get_cache_key(prompt: str) -> str:
    """Generate cache key for prompt."""
    return hashlib.md5(prompt.encode()).hexdigest()


def generate_dalle3_image(prompt: str, output_path: Path, api_key: Optional[str] = None) -> Optional[Path]:
    """
    Generate image using OpenAI DALL-E 3.

    Pricing: $0.04 per image (1024x1024)
    Quality: Best
    Speed: ~10-30 seconds

    Args:
        prompt: Description of image to generate
        output_path: Where to save the image
        api_key: OpenAI API key (or from OPENAI_API_KEY env var)

    Returns:
        Path to generated image or None if failed
    """
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("[ERROR] No OpenAI API key found. Set OPENAI_API_KEY env var.")
        return None

    print(f"[DALL-E] Generating image...")
    print(f"[DALL-E] Prompt: {prompt}")

    try:
        # Call DALL-E 3 API
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'dall-e-3',
                'prompt': prompt,
                'size': '1024x1024',
                'quality': 'standard',  # or 'hd' for $0.08
                'n': 1
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        # Get image URL
        image_url = data['data'][0]['url']

        # Download image
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(img_response.content)

        print(f"[OK] Generated: {output_path.name}")

        # Save metadata
        metadata = _load_metadata()
        cache_key = _get_cache_key(prompt)
        metadata[cache_key] = {
            'source': 'dall-e-3',
            'prompt': prompt,
            'path': str(output_path),
            'generated_at': datetime.now().isoformat(),
            'model': 'dall-e-3',
            'license': 'OpenAI - you own generated images',
            'url': image_url  # Expires after ~1 hour
        }
        _save_metadata(metadata)

        return output_path

    except Exception as e:
        print(f"[ERROR] DALL-E 3 generation failed: {e}")
        return None


def generate_stability_image(prompt: str, output_path: Path, api_key: Optional[str] = None) -> Optional[Path]:
    """
    Generate image using Stability AI (Stable Diffusion).

    Pricing: $0.01-0.02 per image
    Quality: Good
    Speed: ~5-15 seconds

    Args:
        prompt: Description of image to generate
        output_path: Where to save the image
        api_key: Stability AI API key (or from STABILITY_API_KEY env var)

    Returns:
        Path to generated image or None if failed
    """
    if not api_key:
        api_key = os.getenv('STABILITY_API_KEY')

    if not api_key:
        print("[ERROR] No Stability API key found. Set STABILITY_API_KEY env var.")
        return None

    print(f"[STABILITY] Generating image...")
    print(f"[STABILITY] Prompt: {prompt}")

    try:
        # Call Stability AI API
        response = requests.post(
            'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            json={
                'text_prompts': [
                    {'text': prompt, 'weight': 1.0}
                ],
                'cfg_scale': 7,
                'height': 1024,
                'width': 1024,
                'samples': 1,
                'steps': 30,
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        # Get base64 image
        import base64
        image_data = base64.b64decode(data['artifacts'][0]['base64'])

        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(image_data)

        print(f"[OK] Generated: {output_path.name}")

        # Save metadata
        metadata = _load_metadata()
        cache_key = _get_cache_key(prompt)
        metadata[cache_key] = {
            'source': 'stability-ai',
            'prompt': prompt,
            'path': str(output_path),
            'generated_at': datetime.now().isoformat(),
            'model': 'stable-diffusion-xl',
            'license': 'You own generated images'
        }
        _save_metadata(metadata)

        return output_path

    except Exception as e:
        print(f"[ERROR] Stability AI generation failed: {e}")
        return None


def create_prompt_from_briefing(briefing: Dict) -> str:
    """
    Create an image generation prompt from briefing data.

    Args:
        briefing: Briefing JSON with trending stories

    Returns:
        Optimized prompt for image generation
    """
    # Get top keyword
    trending = briefing.get('trending_stories', [])
    if not trending:
        return "Russian government building, editorial photography style"

    top_keyword = trending[0]['keyword']

    # Get context from articles
    articles = trending[0].get('articles', [])
    context = []

    for article in articles[:3]:
        title = article.get('title', '')
        if title:
            context.append(title)

    # Build prompt
    prompt_templates = {
        'ukraine': "Editorial photograph of Ukrainian flag with architectural elements, professional news photography, dramatic lighting, photojournalistic style",
        'kremlin': "The Moscow Kremlin at golden hour, editorial photography, dramatic clouds, professional news photo",
        'putin': "Russian government building with flag, editorial style, professional news photography, dramatic lighting",
        'military': "Military equipment in abstract editorial style, professional photojournalism, dramatic composition",
        'sanctions': "European Union and Russian flags, editorial photography, professional news style",
        'nato': "NATO headquarters building, editorial photography, professional news style, dramatic sky",
        'diplomacy': "International diplomatic meeting room, editorial photography, professional style",
        'energy': "Oil pipeline infrastructure, editorial photography, industrial landscape, dramatic lighting",
    }

    # Find matching template
    keyword_lower = top_keyword.lower()
    for key, template in prompt_templates.items():
        if key in keyword_lower:
            return template

    # Generic fallback
    return f"Editorial photograph related to {top_keyword}, professional news photography, dramatic lighting, photojournalistic style, no text or logos"


def generate_for_briefing(briefing_path: Path, output_dir: Path,
                         provider: str = 'dalle3') -> Optional[Path]:
    """
    Generate an image automatically from briefing.

    Args:
        briefing_path: Path to briefing JSON
        output_dir: Where to save images
        provider: 'dalle3' or 'stability'

    Returns:
        Path to generated image
    """
    # Load briefing
    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    # Create prompt
    prompt = create_prompt_from_briefing(briefing)

    print(f"[INFO] Auto-generated prompt: {prompt}")

    # Check cache
    cache_key = _get_cache_key(prompt)
    metadata = _load_metadata()

    if cache_key in metadata:
        cached_path = Path(metadata[cache_key]['path'])
        if cached_path.exists():
            print(f"[OK] Using cached AI-generated image: {cached_path.name}")
            return cached_path

    # Generate image
    date = briefing.get('date', datetime.now().strftime('%Y-%m-%d'))
    output_path = output_dir / f"{date}-ai-generated.png"

    if provider == 'dalle3':
        return generate_dalle3_image(prompt, output_path)
    elif provider == 'stability':
        return generate_stability_image(prompt, output_path)
    else:
        print(f"[ERROR] Unknown provider: {provider}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Generate AI images for Eastbound Reports')
    parser.add_argument('--prompt', help='Custom prompt for image generation')
    parser.add_argument('--briefing', help='Briefing JSON for auto-generation')
    parser.add_argument('--output', default='images/', help='Output directory')
    parser.add_argument('--provider', choices=['dalle3', 'stability'],
                       default='dalle3', help='AI provider to use')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-generate from briefing')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.auto and args.briefing:
        # Auto-generate from briefing
        img = generate_for_briefing(Path(args.briefing), output_dir, args.provider)
        if img:
            print(f"\n[SUCCESS] Image generated: {img}")
        else:
            print("\n[FAILED] Could not generate image")

    elif args.prompt:
        # Custom prompt
        output_path = output_dir / f"custom-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

        if args.provider == 'dalle3':
            img = generate_dalle3_image(args.prompt, output_path)
        elif args.provider == 'stability':
            img = generate_stability_image(args.prompt, output_path)

        if img:
            print(f"\n[SUCCESS] Image generated: {img}")
        else:
            print("\n[FAILED] Could not generate image")

    else:
        print("[ERROR] Provide either --prompt or --briefing with --auto")
        parser.print_help()


if __name__ == '__main__':
    main()
