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


# Note: Image caching removed - generates fresh images every time
# HuggingFace model caching is still enabled (automatic via ~/.cache/huggingface)


def generate_image_cpu(prompt: str, output_path: Path,
                       num_steps: int = 50,
                       use_fast_model: bool = False,
                       negative_prompt: str = None) -> Optional[Path]:
    """
    Generate image using SDXL on CPU.

    Optimized for GitHub Actions:
    - Uses full SDXL base (best quality at 25-50 steps)
    - CPU-only (no GPU required)
    - ~8-10 minutes per image on GitHub runners

    Args:
        prompt: Description of image
        output_path: Where to save
        num_steps: Inference steps (25-50 optimal for SDXL)
        use_fast_model: Use SDXL Turbo (faster but lower quality)
        negative_prompt: What to avoid in generation

    Returns:
        Path to generated image or None if failed
    """
    try:
        print(f"[LOCAL-GEN] Generating image on CPU...")
        print(f"[LOCAL-GEN] Prompt: {prompt}")
        print(f"[LOCAL-GEN] Steps: {num_steps}")
        if negative_prompt:
            print(f"[LOCAL-GEN] Negative: {negative_prompt}")

        # Import here to avoid slow startup if not needed
        from diffusers import AutoPipelineForText2Image
        import torch

        # Force CPU mode
        device = "cpu"
        torch_dtype = torch.float32  # CPU needs float32

        # Choose model
        if use_fast_model:
            # SDXL Turbo: SDXL quality at 1-4 steps (much faster!)
            # ~6.5GB download, ~2-3 min generation on GitHub Actions
            model_id = "stabilityai/sdxl-turbo"
            print(f"[LOCAL-GEN] Using SDXL Turbo: {model_id}")
            print(f"[LOCAL-GEN] (SDXL quality optimized for 1-4 steps)")
        else:
            # Full SDXL: Best quality at 25-50 steps
            # ~6.9GB download, ~8-10 min at 50 steps on GitHub Actions
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
            print(f"[LOCAL-GEN] Using full SDXL: {model_id}")
            print(f"[LOCAL-GEN] (Best quality at 25-50 steps)")

        print(f"[LOCAL-GEN] Loading model... (first run downloads ~6.9GB)")

        # Load pipeline with CPU optimizations
        pipe = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            variant="fp16" if model_id == "stabilityai/sdxl-turbo" else None,
        )

        pipe = pipe.to(device)

        # Enable CPU optimizations
        pipe.enable_attention_slicing()

        print(f"[LOCAL-GEN] Model loaded, starting generation...")
        if model_id == "stabilityai/sdxl-turbo":
            print(f"[LOCAL-GEN] This will take 2-3 minutes on CPU...")
        else:
            print(f"[LOCAL-GEN] This will take 8-10 minutes on CPU...")

        # Default negative prompt if none provided
        if negative_prompt is None:
            negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, text, logo"

        # Generate image
        with torch.no_grad():
            if model_id == "stabilityai/sdxl-turbo":
                # SDXL Turbo optimal settings: guidance_scale=0.0, 1-4 steps
                image = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_steps,
                    guidance_scale=0.0,  # SDXL Turbo requires guidance_scale=0.0
                    height=512,
                    width=512
                ).images[0]
            else:
                # Full SDXL settings: guidance_scale=7.5, 25-50 steps
                image = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_steps,
                    guidance_scale=7.5,
                    height=512,
                    width=512
                ).images[0]

        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)

        print(f"[OK] Generated: {output_path.name}")
        print(f"[INFO] Model: {model_id}")
        print(f"[INFO] Steps: {num_steps}")
        print(f"[INFO] Cost: FREE (local generation)")

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
    """Create optimized prompt from briefing with better edge case handling."""
    trending = briefing.get('trending_stories', [])
    if not trending:
        return "Russian government building with national symbols, professional news photography, golden hour lighting, detailed architecture"

    top_keyword = trending[0]['keyword']
    keyword_lower = top_keyword.lower()

    # Expanded prompts optimized for SDXL
    # More detailed and specific for better results
    prompt_templates = {
        # Geopolitical
        'ukraine': "Ukrainian flag waving in front of historic Kiev architecture, golden hour lighting, professional editorial photograph, detailed stonework, photorealistic, 8k quality",
        'russia': "Moscow skyline with Kremlin towers and Saint Basil's Cathedral, dramatic sunset clouds, professional news photography, architectural details, photorealistic",
        'kremlin': "Moscow Kremlin with red brick walls and golden domes at sunset, dramatic clouds reflecting off Moscow River, professional news photography, detailed architecture, photorealistic",
        'putin': "Russian government building with large Russian flag, imposing neoclassical architecture, editorial photography, dramatic lighting, professional quality, detailed facade",

        # Military & Security
        'military': "Modern military convoy on strategic highway, editorial photography, dramatic composition, professional photojournalism style, high detail",
        'nato': "NATO headquarters building in Brussels with member flags, modern architecture, official diplomatic photography, clear sky, professional quality, detailed",
        'defense': "Military command center exterior, modern architecture, professional news photography, dramatic lighting, detailed",

        # Diplomacy & International
        'diplomacy': "International conference room with world flags arranged in rows, diplomatic meeting setting, professional photography, detailed interior, warm lighting, photorealistic",
        'summit': "Large diplomatic summit venue with flags of nations, grand architecture, professional event photography, detailed, photorealistic",
        'un': "United Nations headquarters building in New York, modern international architecture, editorial photography, blue sky, professional quality",

        # Economics
        'sanctions': "European Union building with member state flags, modern government architecture in Brussels, editorial photography, professional quality, detailed facade",
        'energy': "Industrial oil and gas pipeline infrastructure across rolling landscape, dramatic stormy sky, editorial photography, photojournalistic style, high detail, 8k",
        'economy': "Stock exchange trading floor with digital screens showing data, professional business photography, dynamic composition, detailed",
        'oil': "Oil refinery industrial complex at golden hour, pipes and towers silhouetted against orange sky, editorial photography, detailed, cinematic",
        'gas': "Natural gas processing facility with industrial infrastructure, professional industrial photography, dramatic lighting, detailed machinery",

        # Media & Information
        'propaganda': "Television broadcast studio with news desk and screens, professional broadcast photography, detailed equipment, dramatic lighting",
        'media': "News broadcasting tower with satellite dishes against dramatic sky, professional photography, architectural detail, photorealistic",
        'information': "Modern data center with server racks and blue lighting, professional technology photography, detailed, high quality",

        # Technology
        'cyber': "Futuristic cybersecurity operations center with multiple screens, professional technology photography, blue and green lighting, detailed",
        'technology': "Modern tech campus with glass architecture, professional architectural photography, clear sky, detailed reflections",

        # Geographies
        'europe': "Historic European city square with classical architecture, golden hour lighting, professional photography, detailed stonework, photorealistic",
        'asia': "Modern Asian cityscape with mix of traditional and contemporary architecture, professional photography, dramatic sky, detailed",
        'china': "Beijing architecture with traditional Chinese elements and modern buildings, professional photography, detailed, photorealistic",

        # Fallback categories for weird keywords
        'http': "Modern newsroom with journalists at computers and screens, professional news photography, dynamic composition, detailed",
        'www': "Global communications network visualization, professional abstract photography, detailed, high quality",
    }

    # Try to match keyword to template
    for key, template in prompt_templates.items():
        if key in keyword_lower:
            return template

    # Better generic fallback with filtering
    # Remove technical keywords that don't make visual sense
    skip_keywords = ['http', 'https', 'www', 'com', 'org', 'net', 'html', 'php']
    if any(skip in keyword_lower for skip in skip_keywords):
        # Use second trending topic if available
        if len(trending) > 1:
            secondary_keyword = trending[1]['keyword']
            for key, template in prompt_templates.items():
                if key in secondary_keyword.lower():
                    return template
        # Ultimate fallback for technical keywords
        return "Russian government building with national flag, imposing neoclassical architecture, professional news photography, golden hour lighting, detailed facade, photorealistic"

    # Generic fallback for normal keywords
    return f"Professional editorial photograph depicting {top_keyword}, dramatic lighting, photojournalistic style, detailed composition, high quality, photorealistic"


def generate_for_briefing(briefing_path: Path, output_dir: Path,
                         num_steps: int = 50) -> Optional[Path]:
    """
    Auto-generate image from briefing.

    Args:
        briefing_path: Path to briefing JSON
        output_dir: Output directory
        num_steps: Inference steps (25-50 optimal for SDXL)

    Returns:
        Path to generated image
    """
    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    prompt = create_prompt_from_briefing(briefing)
    print(f"[INFO] Auto-generated prompt: {prompt}")

    # Generate new image (no caching - always fresh)
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
    parser.add_argument('--steps', type=int, default=50,
                       help='Inference steps (25-50 optimal for SDXL)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-generate from briefing')
    parser.add_argument('--fast', action='store_true', default=False,
                       help='Use SDXL Turbo (faster, lower quality)')

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
