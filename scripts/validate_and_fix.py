#!/usr/bin/env python3
"""Validate and fix common AI hallucinations in generated content."""

import re
from datetime import datetime

def validate_and_fix_content(content, actual_date, sources):
    """
    Validate AI-generated content and fix common hallucinations.

    Args:
        content: The AI-generated markdown content
        actual_date: The actual date (datetime object)
        sources: List of actual sources used

    Returns:
        Fixed content with hallucinations corrected
    """
    fixed_content = content

    # 1. Fix date hallucinations
    # Replace any incorrect month references with the correct month
    correct_month_year = actual_date.strftime("%B %Y")

    # Pattern: "Month YYYY" where Month is wrong
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    for month in months:
        if month != actual_date.strftime("%B"):
            # Replace wrong month with correct month in phrases like "May 2025 News Digest"
            wrong_pattern = f"{month} {actual_date.year}"
            fixed_content = fixed_content.replace(wrong_pattern, correct_month_year)

    # 2. Fix year hallucinations (e.g., 2024 when it should be 2025)
    current_year = actual_date.year
    for wrong_year in range(2020, 2030):
        if wrong_year != current_year:
            # Only replace if it appears in date contexts
            pattern = rf'\b{wrong_year}\b(?=\s*(News|Digest|Coverage|Analysis|Report))'
            fixed_content = re.sub(pattern, str(current_year), fixed_content)

    # 3. Ensure sources are real
    # Check that cited sources are in our actual source list
    valid_sources = {'TASS', 'RIA Novosti', 'Interfax', 'RT', 'Kommersant'}

    # Find all "According to X" patterns
    source_pattern = r'According to ([A-Za-z\s]+),'
    for match in re.finditer(source_pattern, fixed_content):
        cited_source = match.group(1).strip()
        # Warn if source isn't in our list (but don't auto-fix as it might be legitimate)
        if cited_source not in valid_sources and cited_source not in sources:
            print(f"WARNING: Potentially hallucinated source: {cited_source}")

    # 4. Fix common date format issues
    # Ensure dates are in consistent format
    fixed_content = re.sub(
        r'(\d{1,2})(st|nd|rd|th)\s+of\s+([A-Z][a-z]+)\s+(\d{4})',
        r'\3 \1, \4',
        fixed_content
    )

    return fixed_content

def validate_structure(content):
    """Check that required sections are present."""
    required_sections = [
        "## HOOK",
        "## RUSSIAN PERSPECTIVE",
        "## CONTEXT",
        "## COMPARISON"
    ]

    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"WARNING: Missing sections: {', '.join(missing)}")
        return False

    return True

def inject_facts(content, facts):
    """
    Inject programmatically-verified facts into placeholders.

    Args:
        content: Content with {fact_name} placeholders
        facts: Dict of fact_name -> fact_value
    """
    for key, value in facts.items():
        placeholder = f"{{{key}}}"
        content = content.replace(placeholder, str(value))

    return content

if __name__ == '__main__':
    # Test example
    test_content = """## Russian Media Coverage: May 2025 News Digest

According to TASS, Russia announced new policies in April 2024.
According to FakeSource, something happened.
"""

    test_date = datetime(2025, 11, 5)
    test_sources = ['TASS']

    fixed = validate_and_fix_content(test_content, test_date, test_sources)
    print("FIXED CONTENT:")
    print(fixed)
