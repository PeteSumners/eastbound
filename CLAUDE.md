# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Eastbound is a Russian media analysis and translation service providing English-speaking audiences with accurate translations, context, and analysis of Russian media sources. This is a business/media project, NOT an intelligence operation.

## Core Principles (CRITICAL)

**Safety & Independence:**
- Everything published is public and transparent
- Completely independent from all governments
- Only analyze publicly available, open-source information
- Frame as journalism/research, NOT intelligence analysis
- Analyze perspectives from both Russian and American viewpoints

**Content Guidelines:**
- Translate accurately and provide cultural/political context
- Report objectively without taking partisan positions
- Acknowledge biases in sources
- Maintain professional, academic tone
- Never work with intelligence agencies or handle classified information

## Project Phases

**Phase 1 (MVP - Current):**
- GitHub Pages website (Jekyll)
- Twitter/X and LinkedIn for audience building
- Goal: 1,000+ website visitors per month

**Phase 2 (Growth - Future):**
- Enhanced website features (Next.js or similar)
- Stripe payment processing
- Premium tier: $20-50/month
- Corporate subscriptions: $500-2000/month

**Phase 3 (Scale - Years 1-3):**
- Team collaboration tools
- Custom CMS
- Analytics infrastructure

## Content Types

### Weekly Analysis Posts (1000-1500 words)
1. Hook: What happened and why it matters
2. Russian perspective from multiple sources
3. Context that Western audiences miss
4. Comparison with Western coverage
5. Implications for policy/business/culture
6. Source citations

### Translation Posts (500-1000 words + translation)
1. Introduction: Who, when, why it matters
2. Full accurate translation preserving tone
3. Context notes (cultural/political)
4. Analysis of what it reveals
5. Link to Russian original

## Russian Media Sources

**Major News:** TASS, RIA Novosti, Interfax, RT
**Business:** Kommersant, Vedomosti, RBC
**Analysis:** Carnegie Moscow, Telegram channels
**Government:** Kremlin.ru, MID Russia, Duma statements

## Development Notes

This repository contains a fully automated publishing system built on:

- Jekyll static site generator hosted on GitHub Pages
- Automated content generation using Claude AI (with anti-hallucination system)
- RSS feed monitoring of Russian media sources
- GitHub Actions for automated publishing workflows
- Twitter and LinkedIn API integration for social media posting
- Translation management tools
- Content scheduling/publishing workflow
- Analytics for tracking audience growth and engagement

When implementing features, prioritize:
1. Content creation and publishing workflow
2. Translation accuracy verification
3. Source citation management
4. AI safety and anti-hallucination measures
5. Analytics and metrics tracking
