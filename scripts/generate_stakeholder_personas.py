#!/usr/bin/env python3
"""
Random Stakeholder Persona Generator

Generates diverse, random personas from around the world who have stakes
in Russian media narratives. Shows how propaganda affects real people.

Usage:
    python generate_stakeholder_personas.py --count 3
    python generate_stakeholder_personas.py --briefing research/briefing.json
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List


# World regions with associated countries
REGIONS = {
    'Eastern Europe': ['Ukraine', 'Poland', 'Lithuania', 'Latvia', 'Estonia', 'Belarus', 'Moldova', 'Romania', 'Bulgaria'],
    'Western Europe': ['Germany', 'France', 'UK', 'Spain', 'Italy', 'Netherlands', 'Belgium', 'Sweden', 'Norway'],
    'North America': ['USA', 'Canada', 'Mexico'],
    'Latin America': ['Brazil', 'Argentina', 'Colombia', 'Ecuador', 'Peru', 'Chile', 'Venezuela'],
    'Middle East': ['Turkey', 'Israel', 'UAE', 'Saudi Arabia', 'Iran', 'Syria', 'Iraq', 'Egypt'],
    'East Asia': ['China', 'Japan', 'South Korea', 'Taiwan', 'Vietnam', 'Philippines'],
    'South Asia': ['India', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Nepal'],
    'Africa': ['South Africa', 'Nigeria', 'Kenya', 'Ethiopia', 'Egypt', 'Ghana', 'Tanzania'],
    'Russia/CIS': ['Russia', 'Kazakhstan', 'Georgia', 'Armenia', 'Azerbaijan'],
    'Oceania': ['Australia', 'New Zealand'],
}

# Cities by country (for specificity)
CITIES = {
    'Ukraine': ['Kyiv', 'Lviv', 'Odesa', 'Kharkiv', 'Dnipro'],
    'Poland': ['Warsaw', 'Krakow', 'Gdansk', 'Wroclaw'],
    'USA': ['New York', 'Washington DC', 'Los Angeles', 'Chicago', 'Houston', 'Miami'],
    'Russia': ['Moscow', 'St. Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Kazan'],
    'China': ['Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou', 'Chengdu'],
    'Germany': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'],
    'UK': ['London', 'Manchester', 'Birmingham', 'Edinburgh'],
    'Brazil': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador'],
    'India': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'],
    'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse'],
    'Ecuador': ['Quito', 'Guayaquil', 'Cuenca'],
    'Turkey': ['Istanbul', 'Ankara', 'Izmir'],
    'South Africa': ['Johannesburg', 'Cape Town', 'Durban'],
    'Nigeria': ['Lagos', 'Abuja', 'Kano', 'Port Harcourt'],
}

# Demographics
AGES = list(range(22, 75))

OCCUPATIONS = [
    # Business/Finance
    'investment banker', 'venture capitalist', 'startup founder', 'cryptocurrency trader',
    'corporate lawyer', 'management consultant', 'real estate developer', 'hedge fund manager',

    # Tech
    'software engineer', 'data scientist', 'cybersecurity analyst', 'product manager',
    'UX designer', 'DevOps engineer', 'AI researcher', 'blockchain developer',

    # Government/Military
    'diplomat', 'military officer', 'intelligence analyst', 'policy advisor',
    'government official', 'UN worker', 'embassy staffer', 'defense contractor',

    # Media/Communications
    'journalist', 'social media influencer', 'PR consultant', 'podcaster',
    'YouTube content creator', 'TikTok creator', 'news editor', 'foreign correspondent',

    # Academia/Research
    'university professor', 'graduate student', 'think tank researcher', 'historian',
    'political scientist', 'economist', 'sociologist', 'international relations scholar',

    # Healthcare
    'doctor', 'nurse', 'medical researcher', 'public health official',
    'pharmacist', 'hospital administrator', 'mental health counselor',

    # Energy/Industry
    'oil company executive', 'renewable energy engineer', 'factory manager',
    'supply chain manager', 'logistics coordinator', 'mining engineer',

    # Creative/Arts
    'musician', 'filmmaker', 'photographer', 'artist', 'writer', 'dancer',
    'theater director', 'fashion designer', 'graphic designer',

    # Service/Trades
    'restaurant owner', 'hotel manager', 'tour guide', 'taxi driver',
    'construction worker', 'electrician', 'mechanic', 'farmer',

    # NGO/Activism
    'human rights activist', 'NGO director', 'community organizer',
    'environmental activist', 'refugee advocate', 'humanitarian worker',

    # Education
    'high school teacher', 'university lecturer', 'language tutor',
    'education administrator', 'school principal',

    # Misc
    'small business owner', 'freelance consultant', 'stay-at-home parent',
    'retiree', 'student', 'military veteran', 'refugee',
]

# Lifestyle descriptors (for flavor)
LIFESTYLE_DESCRIPTORS = [
    'affluent', 'middle-class', 'working-class', 'struggling',
    'aspiring', 'successful', 'ambitious', 'disillusioned',
    'optimistic', 'cynical', 'politically active', 'apolitical',
    'religious', 'secular', 'traditional', 'progressive',
    'urban', 'suburban', 'rural', 'cosmopolitan',
    'tech-savvy', 'social media addicted', 'offline-first',
    'multilingual', 'expat', 'immigrant', 'first-generation',
]

# Personal stakes/concerns based on topics
TOPIC_STAKES = {
    'ukraine': [
        'has family in {country}',
        'works with Ukrainian refugees',
        'imports grain from Ukraine region',
        'invests in Eastern European markets',
        'worried about World War III',
        'concerned about nuclear escalation',
        'supports Ukraine with donations',
        'follows conflict on social media obsessively',
    ],
    'energy': [
        'pays high heating bills',
        'works in renewable energy sector',
        'employed by oil company',
        'invested in Russian gas futures',
        'concerned about energy independence',
        'owns gas station',
    ],
    'nato': [
        'lives near NATO base',
        'has family in military',
        'works for defense contractor',
        'opposes military expansion',
        'supports NATO membership for {country}',
    ],
    'sanctions': [
        'business affected by sanctions',
        'can\'t access Russian market anymore',
        'sells to European customers',
        'imports Chinese goods',
    ],
    'nuclear': [
        'lives near potential target',
        'works in nuclear industry',
        'anti-nuclear activist',
        'Cold War survivor, fears repeat',
    ],
    'economy': [
        'struggling with inflation',
        'invested in stocks',
        'small business facing recession',
        'recently laid off',
    ],
}


def generate_persona(topic: str = None) -> Dict:
    """
    Generate a random stakeholder persona.

    Args:
        topic: Optional topic to tailor stakes to

    Returns:
        Dict with persona details
    """
    # Select random region and country
    region = random.choice(list(REGIONS.keys()))
    country = random.choice(REGIONS[region])

    # Get city if available
    city = random.choice(CITIES.get(country, [country]))

    # Demographics
    age = random.choice(AGES)
    occupation = random.choice(OCCUPATIONS)

    # Lifestyle
    descriptors = random.sample(LIFESTYLE_DESCRIPTORS, k=random.randint(1, 3))

    # Personal stake
    stakes = []

    # Topic-specific stakes
    if topic:
        topic_lower = topic.lower()
        for key, stake_list in TOPIC_STAKES.items():
            if key in topic_lower:
                stake = random.choice(stake_list)
                # Fill in country if placeholder
                stake = stake.replace('{country}', country)
                stakes.append(stake)

    # Generic stakes
    generic_stakes = [
        'follows international news daily',
        'concerned about global stability',
        'worries about economic impact',
        'has friends in multiple countries',
        'travels internationally for work',
        'uses social media to stay informed',
        'distrusts mainstream media',
        'seeks alternative perspectives',
        'affected by global supply chains',
    ]

    if not stakes:  # Add generic if no topic-specific
        stakes.append(random.choice(generic_stakes))
    else:  # Add one generic to topic-specific
        stakes.append(random.choice(generic_stakes))

    # Generate perspective
    perspectives = [
        'skeptical of Western narratives',
        'skeptical of Russian narratives',
        'trying to understand both sides',
        'strongly pro-Ukraine',
        'sympathetic to Russian position',
        'neutral, just wants peace',
        'worried about escalation',
        'frustrated with media bias',
        'seeking objective information',
        'influenced by social media',
    ]
    perspective = random.choice(perspectives)

    return {
        'name': _generate_name(country),
        'age': age,
        'occupation': occupation,
        'location': f"{city}, {country}",
        'region': region,
        'descriptors': descriptors,
        'stakes': stakes,
        'perspective': perspective,
    }


def _generate_name(country: str) -> str:
    """Generate culturally appropriate name."""

    # Simple approach: use country-appropriate first names
    names_by_region = {
        'Ukraine': ['Oleksandr', 'Natalia', 'Dmytro', 'Kateryna', 'Yuriy', 'Olena'],
        'Poland': ['Piotr', 'Anna', 'Jakub', 'Zofia', 'Wojciech', 'Maria'],
        'USA': ['Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica'],
        'Russia': ['Dmitry', 'Elena', 'Sergei', 'Olga', 'Vladimir', 'Natasha'],
        'China': ['Wei', 'Li', 'Zhang', 'Wang', 'Chen', 'Liu'],
        'Germany': ['Hans', 'Greta', 'Klaus', 'Heidi', 'Jurgen', 'Petra'],
        'France': ['Pierre', 'Marie', 'Jean', 'Sophie', 'Antoine', 'Camille'],
        'Brazil': ['João', 'Ana', 'Carlos', 'Juliana', 'Pedro', 'Beatriz'],
        'India': ['Raj', 'Priya', 'Amit', 'Anjali', 'Vikram', 'Neha'],
        'Ecuador': ['Carlos', 'María', 'Diego', 'Sofía', 'Miguel', 'Valentina'],
        'UK': ['William', 'Emma', 'George', 'Olivia', 'Harry', 'Charlotte'],
        'Turkey': ['Mehmet', 'Ayşe', 'Ali', 'Fatma', 'Mustafa', 'Zeynep'],
        'Nigeria': ['Chioma', 'Oluwaseun', 'Adebayo', 'Ngozi', 'Emeka', 'Amara'],
    }

    if country in names_by_region:
        return random.choice(names_by_region[country])
    else:
        # Generic names
        generic = ['Alex', 'Sam', 'Jordan', 'Taylor', 'Morgan', 'Casey']
        return random.choice(generic)


def format_persona(persona: Dict, index: int = None) -> str:
    """Format persona for display in post."""

    descriptors = ', '.join(persona['descriptors'])
    stakes = '\n     - '.join(persona['stakes'])

    title = f"Stakeholder {index}" if index else "Random Stakeholder"

    return f"""### {title}: {persona['name']}

**Profile:**
- **Age:** {persona['age']}
- **Location:** {persona['location']}
- **Occupation:** {persona['occupation']}
- **Background:** {descriptors}

**Personal Stakes:**
     - {stakes}

**Perspective:** {persona['perspective']}

---
"""


def generate_personas_for_briefing(briefing_path: Path, count: int = 3) -> List[Dict]:
    """Generate personas tailored to briefing topic."""

    with open(briefing_path, 'r', encoding='utf-8') as f:
        briefing = json.load(f)

    # Get top keyword for context
    topic = None
    if briefing.get('trending_stories'):
        topic = briefing['trending_stories'][0]['keyword']

    # Generate diverse personas
    personas = []
    for _ in range(count):
        persona = generate_persona(topic)
        personas.append(persona)

    return personas


def main():
    parser = argparse.ArgumentParser(description='Generate random stakeholder personas')
    parser.add_argument('--count', type=int, default=3,
                       help='Number of personas to generate')
    parser.add_argument('--briefing', help='Briefing JSON to tailor personas to')
    parser.add_argument('--output', help='Output file (JSON)')

    args = parser.parse_args()

    if args.briefing:
        personas = generate_personas_for_briefing(Path(args.briefing), args.count)
        print(f"[INFO] Generated {len(personas)} personas for topic")
    else:
        personas = [generate_persona() for _ in range(args.count)]
        print(f"[INFO] Generated {len(personas)} random personas")

    # Display
    print("\n" + "=" * 70)
    print("STAKEHOLDER PERSONAS")
    print("=" * 70 + "\n")

    for i, persona in enumerate(personas, 1):
        print(format_persona(persona, i))

    # Save if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(personas, f, indent=2)
        print(f"\n[OK] Saved to {args.output}")


if __name__ == '__main__':
    main()
