#!/usr/bin/env python3
"""
Local/CPU Image Generation for GitHub Actions

Runs Stable Diffusion locally without any API keys or costs.
Optimized for GitHub Actions runners (CPU-only, ~7GB RAM available).

Uses Hugging Face's diffusers library with smaller, faster models.

Installation:
    pip install diffusers transformers accelerate pillow

Usage:
    python generate_images_local.py --prompt "Kremlin at sunset" --output images/
    python generate_images_local.py --briefing research/briefing.json --auto
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Optional, Dict
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


# Cache directory
CACHE_DIR = Path('images/local_generated')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

METADATA_FILE = CACHE_DIR / 'local_image_metadata.json'


def _load_metadata() -> Dict:
    """Load metadata cache."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _save_metadata(metadata: Dict):
    """Save metadata cache."""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


def _get_cache_key(prompt: str) -> str:
    """Generate cache key."""
    return hashlib.md5(prompt.encode()).hexdigest()


def generate_image_cpu(prompt: str, output_path: Path,
                       num_steps: int = 20,
                       use_fast_model: bool = True) -> Optional[Path]:
    """
    Generate image using Stable Diffusion on CPU.

    Optimized for GitHub Actions:
    - Uses smaller, faster model
    - Reduced inference steps for speed
    - CPU-only (no GPU required)
    - ~2-5 minutes per image on GitHub runners

    Args:
        prompt: Description of image
        output_path: Where to save
        num_steps: Inference steps (lower = faster, 20-30 recommended)
        use_fast_model: Use faster model optimized for CPU

    Returns:
        Path to generated image or None if failed
    """
    try:
        print(f"[LOCAL-GEN] Generating image on CPU...")
        print(f"[LOCAL-GEN] Prompt: {prompt}")
        print(f"[LOCAL-GEN] Steps: {num_steps} (lower = faster)")

        # Import here to avoid slow startup if not needed
        from diffusers import StableDiffusionPipeline
        import torch

        # Force CPU mode
        device = "cpu"
        torch_dtype = torch.float32  # CPU needs float32

        # Choose model
        if use_fast_model:
            # Smaller, faster model - optimized for CPU
            # ~1.7GB download, ~2-3 min generation on GitHub Actions
            model_id = "stabilityai/stable-diffusion-2-1-base"
            print(f"[LOCAL-GEN] Using fast model: {model_id}")
        else:
            # Higher quality but slower
            # ~3.5GB download, ~5-7 min generation
            model_id = "runwayml/stable-diffusion-v1-5"
            print(f"[LOCAL-GEN] Using standard model: {model_id}")

        print(f"[LOCAL-GEN] Loading model... (first run downloads ~1.7GB)")

        # Load pipeline with CPU optimizations
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )

        pipe = pipe.to(device)

        # Enable CPU optimizations
        # These reduce memory usage for GitHub Actions
        pipe.enable_attention_slicing()

        print(f"[LOCAL-GEN] Model loaded, starting generation...")
        print(f"[LOCAL-GEN] This will take 2-5 minutes on CPU...")

        # Generate image
        with torch.no_grad():  # Reduce memory usage
            image = pipe(
                prompt,
                num_inference_steps=num_steps,
                guidance_scale=7.5,
                height=512,  # Smaller = faster (GitHub Actions has limited time)
                width=512
            ).images[0]

        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)

        print(f"[OK] Generated: {output_path.name}")

        # Save metadata
        metadata = _load_metadata()
        cache_key = _get_cache_key(prompt)
        metadata[cache_key] = {
            'source': 'local-stable-diffusion',
            'prompt': prompt,
            'path': str(output_path),
            'generated_at': datetime.now().isoformat(),
            'model': model_id,
            'steps': num_steps,
            'license': 'CreativeML Open RAIL-M - you own generated images',
            'cost': 'FREE (local generation)'
        }
        _save_metadata(metadata)

        # Clean up to free memory
        del pipe
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return output_path

    except ImportError as e:
        print(f"[ERROR] Required libraries not installed: {e}")
        print("[INFO] Install with: pip install diffusers transformers accelerate pillow torch")
        return None
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")
        return None


def create_prompt_from_briefing(briefing: Dict) -> str:
    """Create optimized prompt from briefing."""
    trending = briefing.get('trending_stories', [])
    if not trending:
        return "Russian government building, editorial photography style"

    top_keyword = trending[0]['keyword']

    # Optimized prompts for Stable Diffusion
    # More detailed = better results
    prompt_templates = {
        'ukraine': "Ukrainian flag waving in front of historic European architecture, golden hour lighting, professional editorial photograph, detailed, photorealistic",
        'kremlin': "Moscow Kremlin with red walls and golden domes at sunset, dramatic clouds, professional news photography, detailed architecture, photorealistic",
        'putin': "Russian government building with national flag, official architecture, editorial photography, dramatic lighting, professional quality",
        'military': "Modern military equipment in strategic location, editorial photography, dramatic composition, professional photojournalism style",
        'nato': "NATO headquarters building in Brussels, modern architecture, official diplomatic photography, clear sky, professional quality",
        'diplomacy': "International conference room with flags, diplomatic meeting setting, professional photography, detailed interior, photorealistic",
        'sanctions': "European Union building with flags, modern government architecture, editorial photography, professional quality",
        'energy': "Industrial oil pipeline infrastructure across landscape, dramatic sky, editorial photography, photojournalistic style, detailed",
    }

    keyword_lower = top_keyword.lower()
    for key, template in prompt_templates.items():
        if key in keyword_lower:
            return template

    # Generic fallback
    return f"Editorial photograph related to {top_keyword}, professional news photography, detailed, photorealistic, dramatic lighting"


def generate_for_briefing(briefing_path: Path, output_dir: Path,
                         num_steps: int = 20) -> Optional[Path]:
    """
    Auto-generate image from briefing.

    Args:
        briefing_path: Path to briefing JSON
        output_dir: Output directory
        num_steps: Inference steps (20-25 for GitHub Actions)

    Returns:
        Path to generated image
    """
    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    prompt = create_prompt_from_briefing(briefing)
    print(f"[INFO] Auto-generated prompt: {prompt}")

    # Check cache
    cache_key = _get_cache_key(prompt)
    metadata = _load_metadata()

    if cache_key in metadata:
        cached_path = Path(metadata[cache_key]['path'])
        if cached_path.exists():
            print(f"[OK] Using cached image: {cached_path.name}")
            return cached_path

    # Generate new image
    date = briefing.get('date', datetime.now().strftime('%Y-%m-%d'))
    output_path = output_dir / f"{date}-generated.png"

    return generate_image_cpu(prompt, output_path, num_steps=num_steps)


def main():
    parser = argparse.ArgumentParser(
        description='Local CPU image generation (free, no API keys)'
    )
    parser.add_argument('--prompt', help='Custom prompt')
    parser.add_argument('--briefing', help='Briefing JSON for auto-generation')
    parser.add_argument('--output', default='images/', help='Output directory')
    parser.add_argument('--steps', type=int, default=20,
                       help='Inference steps (20-25 for speed, 30-50 for quality)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-generate from briefing')
    parser.add_argument('--fast', action='store_true', default=True,
                       help='Use faster model (default)')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.auto and args.briefing:
        # Auto-generate
        print("[INFO] Auto-generating image from briefing...")
        img = generate_for_briefing(Path(args.briefing), output_dir, args.steps)

        if img:
            print(f"\n[SUCCESS] Image generated: {img}")
            print(f"[INFO] Cost: $0 (local generation)")
        else:
            print("\n[FAILED] Could not generate image")

    elif args.prompt:
        # Custom prompt
        print("[INFO] Generating from custom prompt...")
        output_path = output_dir / f"custom-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

        img = generate_image_cpu(args.prompt, output_path,
                                num_steps=args.steps,
                                use_fast_model=args.fast)

        if img:
            print(f"\n[SUCCESS] Image generated: {img}")
            print(f"[INFO] Cost: $0 (local generation)")
        else:
            print("\n[FAILED] Could not generate image")

    else:
        print("[ERROR] Provide either --prompt or --briefing with --auto")
        parser.print_help()


if __name__ == '__main__':
    main()
