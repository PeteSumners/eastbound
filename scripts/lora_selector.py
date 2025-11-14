#!/usr/bin/env python3
"""
Intelligent LoRA Selection System for Eastbound

Automatically selects optimal LoRA combinations and prompts based on article content.
Uses semantic analysis of keywords and topics to choose the best photographic style.

Usage:
    from lora_selector import select_lora_strategy

    strategy = select_lora_strategy(
        article_title="Soviet-era corruption in modern Russia",
        trending_keywords=["kremlin", "corruption", "soviet", "moscow"]
    )
    # Returns: {
    #   'combo_name': 'soviet_nostalgia',
    #   'loras': [{'path': '...', 'strength': 0.5}, ...],
    #   'prompt_template': '...',
    #   'negative_prompt': '...'
    # }
"""

from pathlib import Path
from typing import Dict, List, Tuple
import json


# ============================================================================
# LORA CONFIGURATION
# ============================================================================

LORA_DIR = Path("models/loras")

# Available LoRA models with metadata
AVAILABLE_LORAS = {
    'steve_mccurry': {
        'path': LORA_DIR / 'steve_mccurry_v08.safetensors',
        'trigger_words': ['stvmccrr style', 'photography', 'stvmccrr'],
        'strengths': 'photojournalism, cultural portraits, documentary, emotive',
        'best_for': 'geopolitical events, cultural context, editorial photography',
        'recommended_weight': 0.7
    },
    'touch_realism': {
        'path': LORA_DIR / 'touch_of_realism_v2.safetensors',
        'trigger_words': [],  # No trigger words, enhances base SDXL
        'strengths': 'realistic depth of field, lens effects, professional lighting',
        'best_for': 'architecture, cityscapes, technical realism',
        'recommended_weight': 0.4
    },
    'film_photography': {
        'path': LORA_DIR / 'film_photography_v1.safetensors',
        'trigger_words': ['film photography', 'kodak', 'fuji'],
        'strengths': 'analog feel, film grain, vintage aesthetics',
        'best_for': 'historical themes, Soviet era, nostalgia',
        'recommended_weight': 0.5
    },
    'xportrait': {
        'path': LORA_DIR / 'xportrait_sdxl.safetensors',
        'trigger_words': ['humanistic documentary portrait'],
        'strengths': 'authentic portraits, emotional depth, documentary feel',
        'best_for': 'stakeholder personas, human interest, portraits',
        'recommended_weight': 0.7
    }
}


# ============================================================================
# LORA COMBINATION STRATEGIES
# ============================================================================

LORA_STRATEGIES = {
    'photojournalism_standard': {
        'description': 'Professional news photography for 90% of articles',
        'loras': [
            {'name': 'steve_mccurry', 'strength': 0.7},
            {'name': 'touch_realism', 'strength': 0.4}
        ],
        'prompt_template': (
            "Photography in stvmccrr style, {subject}, "
            "professional news photography, Sony A7III aesthetic, "
            "kodachrome, rich colors, emotive, cultural portrait, "
            "editorial quality, 8k, award winning photography"
        ),
        'negative_prompt': (
            "blurry, low quality, cartoon, oversaturated, text, watermark, "
            "artificial, perfect skin, plastic, oversharpened"
        ),
        'keywords': [
            'politics', 'government', 'diplomacy', 'international',
            'ukraine', 'russia', 'nato', 'summit', 'conference',
            'policy', 'sanctions', 'trade', 'economy'
        ]
    },

    'soviet_nostalgia': {
        'description': 'Historical/Cold War themes with vintage aesthetic',
        'loras': [
            {'name': 'film_photography', 'strength': 0.5},
            {'name': 'steve_mccurry', 'strength': 0.5}
        ],
        'prompt_template': (
            "Photography in stvmccrr style, {subject}, "
            "Soviet-era atmosphere, film photography, Kodak Portra 400, "
            "vintage documentary, film grain, analog warmth, "
            "1980s photojournalism, cultural context, historical authenticity"
        ),
        'negative_prompt': (
            "blurry, digital, modern, clean, oversaturated, text, watermark, "
            "contemporary, smartphone, artificial"
        ),
        'keywords': [
            'soviet', 'ussr', 'cold war', 'historical', 'archive',
            '1980s', '1990s', 'communist', 'kgb', 'stalin', 'lenin',
            'propaganda', 'vintage', 'nostalgia'
        ]
    },

    'kremlin_architecture': {
        'description': 'Russian government buildings and landmarks',
        'loras': [
            {'name': 'steve_mccurry', 'strength': 0.6},
            {'name': 'touch_realism', 'strength': 0.5}
        ],
        'prompt_template': (
            "Photography in stvmccrr style, {subject}, "
            "Moscow Kremlin with golden domes and red brick walls, "
            "dramatic sunset clouds, rich colors, kodachrome, "
            "Sony A7III aesthetic, telephoto lens compression, "
            "editorial photography, 8k, award winning, architectural detail"
        ),
        'negative_prompt': (
            "blurry, low quality, cartoon, text, watermark, oversaturated, "
            "modern architecture, glass buildings"
        ),
        'keywords': [
            'kremlin', 'moscow', 'russian government', 'red square',
            'st basil', 'putin', 'duma', 'ministry', 'government building'
        ]
    },

    'diplomatic_summit': {
        'description': 'Formal diplomatic events and conferences',
        'loras': [
            {'name': 'steve_mccurry', 'strength': 0.6},
            {'name': 'touch_realism', 'strength': 0.5}
        ],
        'prompt_template': (
            "Professional news photography, {subject}, "
            "international diplomatic summit, conference setting, "
            "telephoto lens compression, shallow depth of field, "
            "natural bokeh, Sony A7III aesthetic, editorial quality, "
            "formal composition, professional lighting, 8k"
        ),
        'negative_prompt': (
            "blurry, low quality, cartoon, text, watermark, casual, informal, "
            "party, celebration"
        ),
        'keywords': [
            'summit', 'conference', 'diplomatic', 'meeting', 'talks',
            'negotiations', 'un', 'nato', 'g7', 'g20', 'bilateral',
            'trilateral', 'peace talks'
        ]
    },

    'human_interest_portrait': {
        'description': 'Stakeholder personas and human-focused stories',
        'loras': [
            {'name': 'xportrait', 'strength': 0.7},
            {'name': 'touch_realism', 'strength': 0.3}
        ],
        'prompt_template': (
            "Humanistic documentary portrait, {subject}, "
            "natural lighting, authentic emotion, cultural context, "
            "editorial photography, environmental portrait, "
            "shallow depth of field, photojournalistic style, "
            "professional documentary photography"
        ),
        'negative_prompt': (
            "blurry, low quality, perfect skin, plastic, artificial, "
            "oversaturated, text, watermark, fashion photography, glamour, "
            "studio lighting, posed"
        ),
        'keywords': [
            'stakeholder', 'portrait', 'people', 'civilian', 'refugee',
            'persona', 'human interest', 'interview', 'profile',
            'everyday people', 'citizen'
        ]
    },

    'military_operations': {
        'description': 'Military and defense-related imagery',
        'loras': [
            {'name': 'steve_mccurry', 'strength': 0.7},
            {'name': 'touch_realism', 'strength': 0.4}
        ],
        'prompt_template': (
            "Photography in stvmccrr style, {subject}, "
            "military photojournalism, tactical photography, "
            "dramatic composition, editorial style, kodachrome, "
            "rich colors, documentary realism, professional news photography, "
            "8k, award winning photojournalism"
        ),
        'negative_prompt': (
            "blurry, low quality, glorified, propaganda, heroic, "
            "cartoon, text, watermark, video game, cgi"
        ),
        'keywords': [
            'military', 'army', 'defense', 'war', 'combat', 'troops',
            'soldiers', 'weapons', 'tanks', 'aircraft', 'navy',
            'operation', 'offensive', 'strike'
        ]
    },

    'energy_infrastructure': {
        'description': 'Oil, gas, and energy sector imagery',
        'loras': [
            {'name': 'steve_mccurry', 'strength': 0.6},
            {'name': 'touch_realism', 'strength': 0.5}
        ],
        'prompt_template': (
            "Professional news photography, {subject}, "
            "industrial photography, oil and gas infrastructure, "
            "dramatic lighting, Sony A7III aesthetic, "
            "editorial quality, architectural detail, "
            "industrial landscape, photojournalistic composition, 8k"
        ),
        'negative_prompt': (
            "blurry, low quality, cartoon, text, watermark, oversaturated, "
            "abstract, artistic, HDR, overedited"
        ),
        'keywords': [
            'energy', 'oil', 'gas', 'pipeline', 'refinery', 'gazprom',
            'lukoil', 'power plant', 'infrastructure', 'electricity',
            'fuel', 'petrol'
        ]
    },

    'east_asian_context': {
        'description': 'East Asian geopolitical themes',
        'loras': [
            {'name': 'steve_mccurry', 'strength': 0.7},
            {'name': 'touch_realism', 'strength': 0.4}
        ],
        'prompt_template': (
            "Photography in stvmccrr style, {subject}, "
            "East Asian geopolitics, cultural portrait, "
            "photojournalistic composition, editorial photography, "
            "kodachrome, rich colors, cultural context, "
            "professional news photography, 8k, award winning"
        ),
        'negative_prompt': (
            "blurry, low quality, cartoon, oversaturated, text, watermark, "
            "stereotypical, orientalist"
        ),
        'keywords': [
            'china', 'japan', 'korea', 'taiwan', 'beijing', 'tokyo',
            'seoul', 'pyongyang', 'xi jinping', 'asia', 'pacific',
            'east asian', 'sino-russian'
        ]
    }
}


# ============================================================================
# SELECTION LOGIC
# ============================================================================

def calculate_keyword_match_score(text: str, keywords: List[str]) -> float:
    """
    Calculate how well text matches a keyword list.

    Returns: Score from 0.0 (no match) to 1.0 (perfect match)
    """
    text_lower = text.lower()

    # Count exact matches
    matches = sum(1 for keyword in keywords if keyword in text_lower)

    if not keywords:
        return 0.0

    # Normalize by keyword list size
    score = matches / len(keywords)

    # Bonus for multiple matches (indicates strong theme)
    if matches > 2:
        score = min(1.0, score * 1.2)

    return score


def select_lora_strategy(article_title: str = "",
                         trending_keywords: List[str] = None,
                         article_excerpt: str = "",
                         verbose: bool = False) -> Dict:
    """
    Intelligently select the best LoRA combination for an article.

    Args:
        article_title: Article headline
        trending_keywords: Top trending topics from briefing
        article_excerpt: Article description/excerpt
        verbose: Print decision reasoning

    Returns:
        {
            'combo_name': str,
            'description': str,
            'loras': [{'path': Path, 'strength': float}, ...],
            'prompt_template': str,
            'negative_prompt': str,
            'available': bool  # Whether all LoRA files exist
        }
    """
    if trending_keywords is None:
        trending_keywords = []

    # Combine all text for analysis
    combined_text = f"{article_title} {' '.join(trending_keywords)} {article_excerpt}"

    # Score each strategy
    scores = {}
    for strategy_name, strategy in LORA_STRATEGIES.items():
        score = calculate_keyword_match_score(combined_text, strategy['keywords'])
        scores[strategy_name] = score

        if verbose:
            print(f"[SCORE] {strategy_name}: {score:.2f}")

    # Select best match (or default to photojournalism_standard)
    best_strategy_name = max(scores, key=scores.get)
    best_score = scores[best_strategy_name]

    # If no good match (score < 0.15), use default
    if best_score < 0.15:
        best_strategy_name = 'photojournalism_standard'
        if verbose:
            print(f"[INFO] No strong match (best score: {best_score:.2f}), using default")

    strategy = LORA_STRATEGIES[best_strategy_name]

    if verbose:
        print(f"\n[SELECTED] {best_strategy_name}")
        print(f"[REASON] {strategy['description']}")

    # Build LoRA config
    lora_configs = []
    all_available = True

    for lora_spec in strategy['loras']:
        lora_name = lora_spec['name']
        lora_info = AVAILABLE_LORAS.get(lora_name)

        if not lora_info:
            if verbose:
                print(f"[WARNING] LoRA '{lora_name}' not in AVAILABLE_LORAS")
            continue

        lora_path = lora_info['path']
        exists = lora_path.exists()

        if not exists:
            all_available = False
            if verbose:
                print(f"[WARNING] LoRA file not found: {lora_path}")

        lora_configs.append({
            'path': str(lora_path),
            'strength': lora_spec['strength'],
            'name': lora_name,
            'exists': exists
        })

    return {
        'combo_name': best_strategy_name,
        'description': strategy['description'],
        'loras': lora_configs,
        'prompt_template': strategy['prompt_template'],
        'negative_prompt': strategy['negative_prompt'],
        'available': all_available,
        'score': best_score
    }


def generate_prompt(strategy: Dict, subject: str) -> Tuple[str, str]:
    """
    Generate full prompt and negative prompt from strategy.

    Args:
        strategy: Output from select_lora_strategy()
        subject: Subject description to insert into template

    Returns:
        (full_prompt, negative_prompt)
    """
    prompt = strategy['prompt_template'].format(subject=subject)
    negative = strategy['negative_prompt']

    return prompt, negative


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface for testing LoRA selection."""
    import argparse

    parser = argparse.ArgumentParser(description='Test intelligent LoRA selection')
    parser.add_argument('--title', default='', help='Article title')
    parser.add_argument('--keywords', nargs='+', default=[], help='Trending keywords')
    parser.add_argument('--excerpt', default='', help='Article excerpt')
    parser.add_argument('--subject', default='breaking news event', help='Image subject')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show selection reasoning')

    args = parser.parse_args()

    print("="*60)
    print("INTELLIGENT LORA SELECTOR")
    print("="*60)

    print(f"\nInput:")
    print(f"  Title: {args.title}")
    print(f"  Keywords: {', '.join(args.keywords)}")
    print(f"  Excerpt: {args.excerpt}")

    # Select strategy
    strategy = select_lora_strategy(
        article_title=args.title,
        trending_keywords=args.keywords,
        article_excerpt=args.excerpt,
        verbose=args.verbose
    )

    print(f"\n{'='*60}")
    print(f"SELECTED STRATEGY: {strategy['combo_name']}")
    print(f"{'='*60}")
    print(f"Description: {strategy['description']}")
    print(f"Match Score: {strategy['score']:.2f}")
    avail_status = "YES" if strategy['available'] else "NO (download needed)"
    print(f"All LoRAs Available: {avail_status}")

    print(f"\nLoRA Configuration:")
    for lora in strategy['loras']:
        status = "[OK]" if lora['exists'] else "[MISSING]"
        print(f"  {status} {lora['name']} @ strength {lora['strength']}")
        print(f"        Path: {lora['path']}")

    # Generate sample prompt
    prompt, negative = generate_prompt(strategy, args.subject)

    print(f"\nGenerated Prompt:")
    print(f"  {prompt}")

    print(f"\nNegative Prompt:")
    print(f"  {negative}")

    print(f"\n{'='*60}")
    print("To use this strategy in image generation:")
    print(f"{'='*60}")
    print(f"""
python scripts/generate_images_local.py \\
  --prompt "{prompt}" \\
  --output images/test-{strategy['combo_name']}.png \\
  --steps 50 \\
  --loras {' '.join([f'"{l["path"]}"' for l in strategy['loras']])} \\
  --lora-weights {' '.join([str(l['strength']) for l in strategy['loras']])}
""")


if __name__ == '__main__':
    main()
