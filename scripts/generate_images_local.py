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
from typing import Optional, Dict, List
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


# Note: Image caching removed - generates fresh images every time
# HuggingFace model caching is still enabled (automatic via ~/.cache/huggingface)


def generate_image_cpu(prompt: str, output_path: Path,
                       num_steps: int = 50,
                       negative_prompt: str = None,
                       lora_path: str = None,
                       lora_strength: float = 0.5,
                       lora_configs: List[Dict] = None) -> Optional[Path]:
    """
    Generate image using SDXL on CPU.

    Optimized for quality:
    - Uses full SDXL base (best quality at 50 steps)
    - CPU-only (no GPU required)
    - ~40-50 minutes per image on CPU

    Args:
        prompt: Description of image
        output_path: Where to save
        num_steps: Inference steps (default: 50, optimal for SDXL)
        negative_prompt: What to avoid in generation
        lora_configs: List of LoRA configs for multi-LoRA loading

    Returns:
        Path to generated image or None if failed
    """
    try:
        print(f"[LOCAL-GEN] Generating image on CPU...", flush=True)
        print(f"[LOCAL-GEN] Prompt: {prompt}", flush=True)
        print(f"[LOCAL-GEN] Steps: {num_steps}", flush=True)
        if negative_prompt:
            print(f"[LOCAL-GEN] Negative: {negative_prompt}", flush=True)

        # Import here to avoid slow startup if not needed
        from diffusers import AutoPipelineForText2Image
        import torch

        # Force CPU mode
        device = "cpu"
        torch_dtype = torch.float32  # CPU needs float32

        # Use full SDXL base model
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        print(f"[LOCAL-GEN] Using full SDXL: {model_id}", flush=True)
        print(f"[LOCAL-GEN] Best quality at 50 steps", flush=True)
        print(f"[LOCAL-GEN] Loading model... (first run downloads ~6.9GB)", flush=True)

        # Load pipeline with CPU optimizations
        pipe = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
        )

        pipe = pipe.to(device)

        # Enable CPU optimizations
        pipe.enable_attention_slicing()

        # Load LoRA weights if provided (multi-LoRA support)
        if lora_configs:
            print(f"[LORA] Loading {len(lora_configs)} LoRA model(s)...", flush=True)
            for i, lora_config in enumerate(lora_configs, 1):
                lora_path = lora_config['path']
                strength = lora_config['strength']
                lora_name = Path(lora_path).stem

                print(f"[LORA] {i}. {lora_name} @ strength {strength}", flush=True)

                try:
                    pipe.load_lora_weights(lora_path)
                    pipe.fuse_lora(lora_scale=strength)
                    print(f"[OK] LoRA {i} fused successfully", flush=True)
                except Exception as e:
                    print(f"[WARNING] Failed to load LoRA {i}: {e}", flush=True)
                    print(f"[INFO] Continuing with previous LoRAs", flush=True)
        elif lora_path:
            # Legacy single LoRA support (backward compatible)
            print(f"[LOCAL-GEN] Loading LoRA weights from: {lora_path}", flush=True)
            print(f"[LOCAL-GEN] LoRA strength: {lora_strength}", flush=True)
            try:
                pipe.load_lora_weights(lora_path)
                pipe.fuse_lora(lora_scale=lora_strength)
                print(f"[LOCAL-GEN] LoRA loaded successfully", flush=True)
            except Exception as e:
                print(f"[WARNING] Failed to load LoRA: {e}", flush=True)
                print(f"[INFO] Continuing with base SDXL model", flush=True)

        print(f"[LOCAL-GEN] Model loaded, starting generation...", flush=True)
        print(f"[LOCAL-GEN] Estimated time: {int(num_steps * 0.8)}-{int(num_steps * 1.0)} minutes on CPU...", flush=True)

        # Default negative prompt if none provided
        if negative_prompt is None:
            negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, text, logo"

        # Progress callback to show live updates
        import time
        start_time = time.time()
        last_print_time = start_time

        def progress_callback(pipe, step, timestep, callback_kwargs):
            nonlocal last_print_time
            current_time = time.time()
            elapsed = current_time - start_time

            # Print every step for visibility
            percent = (step / num_steps) * 100
            elapsed_str = f"{int(elapsed)}s"
            print(f"[PROGRESS] Step {step}/{num_steps} ({percent:.0f}%) - Elapsed: {elapsed_str}", flush=True)

            return callback_kwargs

        # Generate image
        with torch.no_grad():
            print(f"[GENERATE] Starting inference at {time.strftime('%H:%M:%S')}", flush=True)

            # Full SDXL settings: guidance_scale=7.5, 50 steps optimal
            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_steps,
                guidance_scale=7.5,
                height=512,
                width=512,
                callback_on_step_end=progress_callback
            ).images[0]

            total_time = time.time() - start_time
            print(f"[COMPLETE] Generation finished in {int(total_time)}s ({total_time/60:.1f} minutes)", flush=True)

        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)

        print(f"[OK] Generated: {output_path.name}", flush=True)
        print(f"[INFO] Model: {model_id}", flush=True)
        print(f"[INFO] Steps: {num_steps}", flush=True)
        print(f"[INFO] Cost: FREE (local generation)", flush=True)

        # Clean up to free memory
        del pipe
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return output_path

    except ImportError as e:
        print(f"[ERROR] Required libraries not installed: {e}", flush=True)
        print("[INFO] Install with: pip install diffusers transformers accelerate pillow torch", flush=True)
        return None
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}", flush=True)
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
                         num_steps: int = 50,
                         lora_path: str = None,
                         lora_strength: float = 0.5) -> Optional[Path]:
    """
    Auto-generate image from briefing.

    Args:
        briefing_path: Path to briefing JSON
        output_dir: Output directory
        num_steps: Inference steps (25-50 optimal for SDXL)
        lora_path: Optional path to LoRA weights
        lora_strength: LoRA strength (0.0-1.0)

    Returns:
        Path to generated image
    """
    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    prompt = create_prompt_from_briefing(briefing)
    print(f"[INFO] Auto-generated prompt: {prompt}", flush=True)

    # Generate new image (no caching - always fresh)
    date = briefing.get('date', datetime.now().strftime('%Y-%m-%d'))
    output_path = output_dir / f"{date}-generated.png"

    return generate_image_cpu(prompt, output_path, num_steps=num_steps,
                             lora_path=lora_path, lora_strength=lora_strength)


def main():
    parser = argparse.ArgumentParser(
        description='Local CPU image generation (free, no API keys)'
    )
    parser.add_argument('--prompt', help='Custom prompt')
    parser.add_argument('--briefing', help='Briefing JSON for auto-generation')
    parser.add_argument('--output', default='images/', help='Output directory')
    parser.add_argument('--steps', type=int, default=50,
                       help='Inference steps (default: 50, optimal for SDXL)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-generate from briefing')
    parser.add_argument('--lora', help='Path to single LoRA weights file (.safetensors)')
    parser.add_argument('--lora-strength', type=float, default=0.5,
                       help='LoRA strength/scale (0.0-1.0, default: 0.5)')
    parser.add_argument('--loras', nargs='+', help='Multiple LoRA paths (e.g., --loras lora1.safetensors lora2.safetensors)')
    parser.add_argument('--lora-weights', nargs='+', type=float, help='Weights for multiple LoRAs (e.g., --lora-weights 0.7 0.4)')
    parser.add_argument('--lora-combo', help='Preset LoRA combination (photojournalism, soviet, kremlin, diplomatic, portrait, military, energy, east_asian)')
    parser.add_argument('--negative', help='Negative prompt')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build LoRA configuration
    lora_configs = None

    if args.lora_combo:
        # Use preset combination
        LORA_DIR = Path("models/loras")
        PRESETS = {
            'photojournalism_standard': [
                {'path': str(LORA_DIR / 'steve_mccurry_v08.safetensors'), 'strength': 0.7},
                {'path': str(LORA_DIR / 'touch_of_realism_v2.safetensors'), 'strength': 0.4}
            ],
            'soviet_nostalgia': [
                {'path': str(LORA_DIR / 'film_photography_v1.safetensors'), 'strength': 0.5},
                {'path': str(LORA_DIR / 'steve_mccurry_v08.safetensors'), 'strength': 0.5}
            ],
            'kremlin_architecture': [
                {'path': str(LORA_DIR / 'steve_mccurry_v08.safetensors'), 'strength': 0.6},
                {'path': str(LORA_DIR / 'touch_of_realism_v2.safetensors'), 'strength': 0.5}
            ],
            'diplomatic_summit': [
                {'path': str(LORA_DIR / 'steve_mccurry_v08.safetensors'), 'strength': 0.6},
                {'path': str(LORA_DIR / 'touch_of_realism_v2.safetensors'), 'strength': 0.5}
            ],
            'military_operations': [
                {'path': str(LORA_DIR / 'steve_mccurry_v08.safetensors'), 'strength': 0.7},
                {'path': str(LORA_DIR / 'touch_of_realism_v2.safetensors'), 'strength': 0.4}
            ],
            'energy_infrastructure': [
                {'path': str(LORA_DIR / 'steve_mccurry_v08.safetensors'), 'strength': 0.6},
                {'path': str(LORA_DIR / 'touch_of_realism_v2.safetensors'), 'strength': 0.5}
            ],
            'east_asian_context': [
                {'path': str(LORA_DIR / 'steve_mccurry_v08.safetensors'), 'strength': 0.7},
                {'path': str(LORA_DIR / 'touch_of_realism_v2.safetensors'), 'strength': 0.4}
            ]
        }

        if args.lora_combo in PRESETS:
            lora_configs = PRESETS[args.lora_combo]
            print(f"[INFO] Using preset combo: {args.lora_combo}", flush=True)
        else:
            print(f"[WARNING] Unknown preset '{args.lora_combo}', using base SDXL", flush=True)

    elif args.loras:
        # Multiple LoRAs specified manually
        if args.lora_weights and len(args.lora_weights) == len(args.loras):
            lora_configs = [
                {'path': path, 'strength': weight}
                for path, weight in zip(args.loras, args.lora_weights)
            ]
        else:
            # Use default strength if weights not specified
            default_weight = args.lora_strength
            lora_configs = [
                {'path': path, 'strength': default_weight}
                for path in args.loras
            ]
            print(f"[INFO] No weights specified, using {default_weight} for all LoRAs", flush=True)

    if args.auto and args.briefing:
        # Auto-generate
        print("[INFO] Auto-generating image from briefing...", flush=True)
        img = generate_for_briefing(Path(args.briefing), output_dir, args.steps,
                                   lora_path=args.lora, lora_strength=args.lora_strength)

        if img:
            print(f"\n[SUCCESS] Image generated: {img}", flush=True)
            print(f"[INFO] Cost: $0 (local generation)", flush=True)
            if args.lora:
                print(f"[INFO] LoRA used: {args.lora} (strength: {args.lora_strength})", flush=True)
        else:
            print("\n[FAILED] Could not generate image", flush=True)

    elif args.prompt:
        # Custom prompt
        print("[INFO] Generating from custom prompt...", flush=True)
        output_path = output_dir / f"custom-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

        img = generate_image_cpu(args.prompt, output_path,
                                num_steps=args.steps,
                                negative_prompt=args.negative,
                                lora_path=args.lora,
                                lora_strength=args.lora_strength,
                                lora_configs=lora_configs)

        if img:
            print(f"\n[SUCCESS] Image generated: {img}", flush=True)
            print(f"[INFO] Cost: $0 (local generation)", flush=True)
        else:
            print("\n[FAILED] Could not generate image", flush=True)

    else:
        print("[ERROR] Provide either --prompt or --briefing with --auto", flush=True)
        parser.print_help()


if __name__ == '__main__':
    main()
