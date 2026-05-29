STYLE_PROFILE_PROMPT = """Analyze these writing samples to extract a precise style profile.

WRITING SAMPLES:
{voice_samples}

{voice_description_block}

Return JSON (no prose outside the JSON):
{{
  "avg_sentence_length": <int words>,
  "sentence_length_variance": "low" | "medium" | "high",
  "vocabulary_level": "simple" | "moderate" | "advanced" | "mixed",
  "favorite_constructions": ["<pattern>"],
  "tone_markers": ["<marker>"],
  "paragraph_length": "short (1-2 sentences)" | "medium (3-4)" | "long (5+)",
  "opening_style": "<how they typically start>",
  "closing_style": "<how they typically end>",
  "punctuation_habits": ["<habit>"],
  "formality_level": <1-10>,
  "humor_frequency": "none" | "rare" | "occasional" | "frequent"
}}"""


VOICE_DESCRIPTION_BLOCK_TEMPLATE = """AUTHOR-PROVIDED TONE NOTE (supplemental signal — reconcile with samples):
{voice_description}"""


VOICE_ADJUSTMENT_PROMPT = """You are a ghostwriter making final voice adjustments to a fact-checked draft.

FACT-CHECKED DRAFT:
{draft}

AUTHOR'S STYLE PROFILE:
{style_profile_json}

REFERENCE SAMPLES:
{voice_samples}

CLAIMS THAT MUST BE PRESERVED VERBATIM (the fact checker verified these — do NOT rewrite their substance, only their phrasing/voice):
{must_preserve_block}

ADJUSTMENT RULES:
1. PRESERVE: Every must-preserve claim's specifics (numbers, names, dates, entities). You may reword AROUND them, but the factual content stays.
2. ADJUST: Sentence structure, word choice, punctuation, rhythm.
3. MATCH: Opening and closing style to the author's patterns. Calibrate formality to the profile.
4. NO NEW CLAIMS: Do not invent new facts, numbers, or attributions.
5. LENGTH: {length_directive}
6. NO SLOP: Do not introduce AI-slop phrasing ("delve", "revolutionize", "seamless", "navigate the landscape", "ever-evolving", "a testament to", "in conclusion", etc.). No hashtags. No emojis. If the draft already contains any, remove them.
7. PRESERVE STRUCTURE: If the draft is a numbered thread, keep each "N/" tweet on its own line separated by a blank line. Do not merge segments.

Return JSON (no prose outside the JSON):
{{
  "adjusted_draft": "<the final, voice-adjusted draft as one string>",
  "adjustments_made": ["<specific change 1>", "<specific change 2>", "..."]
}}

Each item in adjustments_made should be a concrete change you made (e.g., "broke 3 long sentences into staccato pairs", "swapped 'utilize' for 'use' throughout", "added em-dash asides in opener"). No generic items like "improved voice"."""


LENGTH_FIX_PROMPT = """The following {content_type} is the wrong length and MUST be fixed.

CURRENT DRAFT ({current_len} characters / {current_words} words):
{draft}

PROBLEM: {length_problem}

CLAIMS THAT MUST STILL APPEAR (with their specifics intact):
{must_preserve_block}

Rewrite to satisfy the length requirement while keeping the voice and every must-preserve claim.
Cut filler and redundancy first; never drop a verified specific. Do not add hashtags, emojis, or AI-slop.

Return JSON (no prose outside the JSON):
{{
  "adjusted_draft": "<the corrected draft as one string>",
  "adjustments_made": ["<what you cut or tightened>"]
}}"""


RESTORATION_PROMPT = """Your previous voice adjustment dropped or distorted these verified claims. Restore them.

CURRENT ADJUSTED DRAFT:
{draft}

CLAIMS YOU MUST RESTORE (each was verified and must appear with its specifics intact):
{missing_claims_block}

Rules:
1. Restore each missing claim by integrating it naturally into the existing voice — do not just paste it back.
2. Keep every other adjustment from the current draft.
3. Length stays within 90-110% of current.

Return JSON (no prose outside the JSON):
{{
  "adjusted_draft": "<the restored draft as one string>",
  "adjustments_made": ["<what you restored and where>"]
}}"""


# Defaults vary by content type. Tweets are not paragraphs; threads are
# short-paragraph-equivalent; essays/articles have longer paragraph beats.
DEFAULT_STYLE_PROFILES: dict[str, dict] = {
    "tweet": {
        "avg_sentence_length": 11,
        "sentence_length_variance": "high",
        "vocabulary_level": "moderate",
        "favorite_constructions": ["direct claims", "no hedging"],
        "tone_markers": ["confident", "conversational"],
        "paragraph_length": "n/a (single beat)",
        "opening_style": "specific claim or surprising fact",
        "closing_style": "memorable reframe",
        "punctuation_habits": ["periods over commas", "no emojis"],
        "formality_level": 4,
        "humor_frequency": "rare",
    },
    "quote_retweet": {
        "avg_sentence_length": 12,
        "sentence_length_variance": "high",
        "vocabulary_level": "moderate",
        "favorite_constructions": ["one fresh insight added to the original"],
        "tone_markers": ["confident", "additive (not summarizing)"],
        "paragraph_length": "n/a (single beat)",
        "opening_style": "fresh angle, not restatement",
        "closing_style": "implication or counter-claim",
        "punctuation_habits": ["periods over commas"],
        "formality_level": 4,
        "humor_frequency": "rare",
    },
    "thread": {
        "avg_sentence_length": 13,
        "sentence_length_variance": "high",
        "vocabulary_level": "moderate",
        "favorite_constructions": ["hook line standalone", "one new idea per tweet"],
        "tone_markers": ["confident", "conversational"],
        "paragraph_length": "short (1-2 sentences per tweet)",
        "opening_style": "hook that works standalone",
        "closing_style": "memorable reframe or call to thought",
        "punctuation_habits": ["periods over commas"],
        "formality_level": 4,
        "humor_frequency": "occasional",
    },
    "essay": {
        "avg_sentence_length": 16,
        "sentence_length_variance": "high",
        "vocabulary_level": "moderate",
        "favorite_constructions": ["em-dashes for asides", "concrete-then-abstract"],
        "tone_markers": ["confident", "argued"],
        "paragraph_length": "short (2-4 sentences)",
        "opening_style": "bold claim grounded in a specific",
        "closing_style": "implication that reframes the opening",
        "punctuation_habits": ["em-dashes", "colons for emphasis"],
        "formality_level": 5,
        "humor_frequency": "rare",
    },
    "article": {
        "avg_sentence_length": 18,
        "sentence_length_variance": "high",
        "vocabulary_level": "advanced",
        "favorite_constructions": ["topic sentence then evidence", "named-entity attribution"],
        "tone_markers": ["measured", "evidence-led"],
        "paragraph_length": "medium (3-4 sentences)",
        "opening_style": "scene or specific datum",
        "closing_style": "synthesis that names the stakes",
        "punctuation_habits": ["standard", "occasional em-dash"],
        "formality_level": 6,
        "humor_frequency": "none",
    },
}


def default_profile_for(content_type: str) -> dict:
    """Return a copy of the default style profile appropriate for the content type."""
    profile = DEFAULT_STYLE_PROFILES.get(content_type) or DEFAULT_STYLE_PROFILES["essay"]
    return dict(profile)
