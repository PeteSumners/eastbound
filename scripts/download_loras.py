#!/usr/bin/env python3
"""
Download SDXL LoRA Models for Eastbound

Downloads recommended LoRAs from HuggingFace and provides instructions
for manual Civitai downloads (which require browser authentication).

Usage:
    python scripts/download_loras.py
"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download

# Create loras directory
LORA_DIR = Path("models/loras")
LORA_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("EASTBOUND LORA DOWNLOADER")
print("="*60)

# Download from HuggingFace (works programmatically)
print("\n[1/3] Downloading Steve McCurry Photography LoRA from HuggingFace...")
try:
    file_path = hf_hub_download(
        repo_id="imagepipeline/Steve-McCurry-Photography-SDXL-LoRa",
        filename="stvmccrr.safetensors",
        local_dir=str(LORA_DIR),
        local_dir_use_symlinks=False
    )
    print(f"[OK] Downloaded to: {file_path}")

    # Rename to standard name
    target = LORA_DIR / "steve_mccurry_v08.safetensors"
    if Path(file_path).exists() and not target.exists():
        Path(file_path).rename(target)
        print(f"[OK] Renamed to: {target}")
except Exception as e:
    print(f"[ERROR] Failed to download Steve McCurry LoRA: {e}")

# Civitai models require manual download (browser authentication)
print("\n" + "="*60)
print("MANUAL DOWNLOADS REQUIRED (Civitai models)")
print("="*60)

print("""
[2/3] Touch of Realism V2 (435 MB)
-------------------------------
1. Open in browser: https://civitai.com/models/1705430/touch-of-realism-sdxl
2. Click "Download" button for V2 version
3. Save file as: models/loras/touch_of_realism_v2.safetensors

Direct link (may require login):
https://civitai.com/api/download/models/6396587


[3/3] SDXL Film Photography Style (870 MB)
-------------------------------
1. Open in browser: https://civitai.com/models/158945/sdxl-film-photography-style
2. Click "Download" button for v1.0 version
3. Save file as: models/loras/film_photography_v1.safetensors

Direct link (may require login):
https://civitai.com/api/download/models/530559


ALTERNATIVE: Use browser to download both files, then move them to:
C:\\Users\\PeteS\\Desktop\\Eastbound\\models\\loras\\
""")

print("\n" + "="*60)
print("DOWNLOAD STATUS")
print("="*60)

# Check what we have
loras = list(LORA_DIR.glob("*.safetensors"))
if loras:
    print(f"\n[OK] Found {len(loras)} LoRA file(s):")
    for lora in loras:
        size_mb = lora.stat().st_size / (1024 * 1024)
        status = "✓ Valid" if size_mb > 50 else "✗ Too small (download failed)"
        print(f"  {status}: {lora.name} ({size_mb:.1f} MB)")
else:
    print("\n[WARNING] No LoRA files found yet")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("""
Once you have at least one LoRA downloaded:

1. Test single LoRA:
   python scripts/generate_images_local.py \\
     --prompt "Photography in stvmccrr style, Moscow Kremlin, kodachrome" \\
     --output images/test-lora.png \\
     --lora models/loras/steve_mccurry_v08.safetensors \\
     --lora-strength 0.7 \\
     --steps 50

2. Update automation to use LoRAs (see Docs/sdxl-lora-advanced-strategy.md)

3. Experiment with LoRA combinations!
""")
