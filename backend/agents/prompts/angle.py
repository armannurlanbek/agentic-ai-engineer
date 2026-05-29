ANGLE_GENERATION_PROMPT = """You are a senior content strategist for a creator with a large X/Twitter following.

TOPIC HEADLINE (this is the THESIS every angle must advance):
{topic_headline}
{original_tweet_block}
KEY FACTS:
{key_facts}

TENSIONS / DEBATE POINTS:
{tensions}

ANGLE SEEDS (rough directions surfaced by upstream research — use as inspiration, not as final angles):
{angle_seeds}

AUDIENCE CONTEXT:
{audience_context}

KNOWLEDGE BASE CONTEXT:
{context_docs}

CONTENT TYPE: {content_type}

Generate exactly {angle_count} candidate angles for this {content_type}. Each angle must be:
- ONE sentence — under 25 words — that captures both the CLAIM and the FRAME
- Distinct from every other angle (different claim, not just rephrasing)
- Specific enough to write from immediately (no "the future of X" platitudes)
- Defensible from the key facts above
- ON-THESIS: it must advance the TOPIC HEADLINE above, not pivot to a tangential point that merely shares the subject area. If a QUOTED TWEET is present, the angle must add genuine insight to / push back on that specific claim — never just summarize it.

Angle types to cover where they fit (one of each is ideal, but quality > coverage):
1. CONTRARIAN: Challenges the mainstream take with evidence
2. INSIDER: Reveals something only someone experienced would know
3. SYNTHESIS: Connects two seemingly unrelated ideas
4. DATA-DRIVEN: Leads with a specific number or fact from KEY FACTS
5. NARRATIVE: Frames through a story, analogy, or vivid example

For each angle, provide:
- "angle_text": The angle in one sentence (<= 25 words)
- "angle_type": Which of the 5 types above
- "why_it_works": One sentence on why this performs well as a {content_type}

Return as a JSON array. No prose outside the JSON."""


ANGLE_SCORING_PROMPT = """You are evaluating content angles for a {content_type} on X/Twitter.

TOPIC HEADLINE (treat this as the user's THESIS — the claim the content must be faithful to):
{topic_headline}

KEY FACTS (for defensibility check):
{key_facts}

CANDIDATE ANGLES:
{angles_json}

Score each angle from 1-10 on these criteria:

1. HOOK STRENGTH (1-10): Would this stop someone mid-scroll?
2. DEFENSIBILITY (1-10): Can this angle be supported with the KEY FACTS above?
3. ORIGINALITY (1-10): Has this take been made a thousand times already?
4. SHAREABILITY (1-10): Would someone retweet/quote this?
5. THESIS_FIDELITY (1-10): Does this angle advance the user's stated thesis (the TOPIC HEADLINE), as opposed to a tangential point? A precise, defensible angle that wanders off-thesis scores LOW here, even if it scores high elsewhere. A vague metaphor that abandons the specific claim of the thesis is NOT high fidelity. An angle that leads with the sharpest on-thesis fact scores HIGH.

THESIS_FIDELITY is REQUIRED for every angle — never omit it. total_score = hook_strength + defensibility + originality + shareability + thesis_fidelity (max 50). Any angle missing thesis_fidelity is an invalid response.

Calculate total_score (max 50). Select the highest-scoring angle that is faithful to the thesis (thesis_fidelity >= 7). Do NOT select an off-thesis angle just because it has a clever hook or metaphor.
If two angles are within 2 points of each other, prefer the one with higher HOOK STRENGTH.

Return JSON (no prose outside the JSON):
{{
  "scored_angles": [
    {{
      "angle_text": "...",
      "angle_type": "...",
      "hook_strength": 0,
      "defensibility": 0,
      "originality": 0,
      "shareability": 0,
      "thesis_fidelity": 0,
      "total_score": 0
    }}
  ],
  "selected_index": 0,
  "selection_rationale": "..."
}}"""
