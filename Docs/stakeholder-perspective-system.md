# Stakeholder Perspective System

## Purpose & Philosophy

The Stakeholder Perspective System adds **human grounding** to geopolitical analysis by showing how Russian media narratives affect real people around the world.

**Key Principle:** Russian state media isn't just abstract propaganda—it influences real stakeholders with real interests: investors making decisions, refugees making plans, business owners navigating sanctions, activists organizing campaigns, and ordinary people trying to understand global events.

## What This System Does

**Generates 3-5 random personas per article who have material stakes in the day's Russian media narratives.**

Each persona represents:
- A specific person from a specific location
- With a specific occupation and socioeconomic background
- Who has direct material interests affected by Russian media narratives
- With a perspective shaped by their circumstances

**This is NOT:**
- ❌ A representative sample (these are random individuals)
- ❌ Opinion polling data
- ❌ Demographic analysis
- ❌ Predictive modeling of public opinion

**This IS:**
- ✅ Concrete examples of how abstract geopolitics affects real people
- ✅ Diverse perspectives from different countries and backgrounds
- ✅ A reminder that media narratives have real-world consequences
- ✅ Context for understanding multi-sided stakes in conflicts

## How It Works

### Technical Implementation

**Script:** `scripts/generate_stakeholder_personas.py`

**Generation Algorithm:**
1. Receives briefing with trending keywords (e.g., "ukraine", "sanctions", "energy")
2. Randomly selects 3-5 countries from 10 global regions (40+ countries)
3. Randomly selects occupations from 100+ profession pool
4. Assigns topic-specific stakes based on trending keywords
5. Generates culturally appropriate names for each country
6. Assigns perspective/stance (pro-Russian, pro-Ukrainian, neutral, skeptical, etc.)

**Persona Data Structure:**
```python
{
  'name': 'Oleksandr',
  'age': 42,
  'occupation': 'small business owner',
  'location': 'Lviv, Ukraine',
  'region': 'Eastern Europe',
  'descriptors': ['middle-class', 'politically active', 'urban'],
  'stakes': [
    'business affected by sanctions',
    'follows international news daily'
  ],
  'perspective': 'trying to understand both sides'
}
```

### Topic-Specific Stakes

The system maps trending topics to relevant personal stakes:

**Ukraine conflict:**
- Has family in [country]
- Works with Ukrainian refugees
- Imports grain from Ukraine region
- Worried about World War III
- Concerned about nuclear escalation

**Energy/Sanctions:**
- Pays high heating bills
- Works in renewable energy sector
- Employed by oil company
- Business affected by sanctions

**NATO/Military:**
- Lives near NATO base
- Has family in military
- Works for defense contractor
- Opposes military expansion

### Geographic Diversity

**10 Global Regions Represented:**
1. Eastern Europe (Ukraine, Poland, Baltics, etc.)
2. Western Europe (Germany, France, UK, etc.)
3. North America (USA, Canada, Mexico)
4. Latin America (Brazil, Argentina, Colombia, etc.)
5. Middle East (Turkey, Israel, UAE, Iran, Syria, etc.)
6. East Asia (China, Japan, South Korea, Taiwan, etc.)
7. South Asia (India, Pakistan, Bangladesh, etc.)
8. Africa (South Africa, Nigeria, Kenya, Ethiopia, etc.)
9. Russia/CIS (Russia, Kazakhstan, Georgia, etc.)
10. Oceania (Australia, New Zealand)

**100+ Occupations Including:**
- Business/Finance: investment banker, startup founder, hedge fund manager
- Tech: software engineer, AI researcher, cybersecurity analyst
- Government: diplomat, military officer, policy advisor
- Media: journalist, social media influencer, foreign correspondent
- Academia: professor, think tank researcher, political scientist
- Healthcare: doctor, public health official
- Energy/Industry: oil executive, renewable energy engineer, factory manager
- Activism: human rights activist, NGO director, environmental advocate
- Service/Trades: restaurant owner, construction worker, farmer
- And many more...

## Integration with Articles

### Article Section Format

The stakeholder section appears near the end of each analysis article (after main content, before sources).

**Section Structure:**
```markdown
## Stakeholder Perspectives: Real-World Impact

*The following section presents randomly generated personas from around the world who have material stakes in today's Russian media narratives. These are not representative samples or opinion polls—they're concrete examples of how abstract geopolitics affects real people with real interests. Each persona is randomly selected from a global pool representing diverse countries, occupations, and socioeconomic backgrounds.*

### Stakeholder 1: [Name]

**Profile:**
- **Age:** 42
- **Location:** Lviv, Ukraine
- **Occupation:** Small business owner
- **Background:** Middle-class, politically active, urban

**Personal Stakes:**
- Business affected by sanctions
- Follows international news daily
- Worried about economic impact

**Perspective:** Trying to understand both sides

**What Today's Russian Media Means for [Name]:**
[AI-generated analysis of how today's specific narratives affect this persona]

---

[Repeat for 3-5 personas]
```

### AI-Generated Individual Analysis

For each persona, the AI considers:
- How today's specific trending topics affect this person's material interests
- Whether Russian media narratives align with or contradict their lived experience
- What questions or concerns they might have based on the coverage
- How their background shapes their interpretation of the narratives

**Example:**
> "For Elena, a German renewable energy engineer, today's Russian coverage of sanctions 'running out' creates professional uncertainty. Her company has pivoted away from Russian natural gas projects, and narrative suggesting Western economic pressure is failing may affect investor confidence in European energy transition funding. She's skeptical of Russian framing but concerned about the political implications if sanctions fatigue becomes real."

## Why This Approach Matters

### 1. Humanizes Abstract Geopolitics
- "Sanctions on Russia" → "Ahmed's import business can't get parts"
- "Peace negotiations" → "Natalia wonders if it's safe to return home"
- "Energy crisis" → "Hans pays 3x heating bills this winter"

### 2. Shows Multi-Sided Complexity
Random selection ensures diverse perspectives:
- Ukrainian refugee advocate AND Russian expatriate businessman
- American diplomat AND Indian energy trader
- Polish NATO supporter AND Turkish neutral observer

### 3. Grounds Propaganda Analysis in Reality
Russian media narratives don't exist in a vacuum—they interact with real people making real decisions. This system shows **who is affected and how**.

### 4. Avoids Western Centrism
By including voices from Latin America, Africa, Asia, Middle East—not just US/Europe—we show that Russian media narratives have global impact.

### 5. Demonstrates Complexity Without False Balance
Including diverse perspectives ≠ "both sides are equally valid"
- We can show a Russian pensioner's view AND acknowledge Ukrainian trauma
- We can include a Syrian perspective on Western intervention without endorsing Russian imperialism
- Complexity is the point—real stakeholders have real interests that don't align with neat narratives

## Randomization Philosophy

**Why random selection instead of targeted analysis?**

1. **Avoiding bias:** Pre-selecting personas risks editorial bias toward "convenient" perspectives
2. **Showing breadth:** Random selection over time demonstrates global diversity of stakes
3. **Intellectual honesty:** We don't claim to know which perspectives "matter most"
4. **Narrative surprise:** Random personas sometimes reveal unexpected angles we wouldn't have considered

## Usage Example

When the daily automation runs:
```bash
python scripts/generate_stakeholder_personas.py --briefing research/2025-11-13-briefing.json --count 4
```

This generates 4 random personas tailored to today's trending topics (e.g., ukraine, corruption, sanctions), which the AI then integrates into the article with individualized analysis.

## Future Enhancements

**Potential additions:**
- Historical tracking: "What did Elena think last week vs. today?"
- Persistent persona pool: 200 pre-generated personas, select subset each day
- Demographic analytics: Over time, ensure good geographic/occupation distribution
- Reader feedback: Which personas resonate most with audiences?

## Related Documentation

- [Content Generation Pipeline](content-generation-pipeline.md)
- [Anti-Hallucination System](anti-hallucination.md)
- [Briefing Database Structure](briefing-database-structure.md)
