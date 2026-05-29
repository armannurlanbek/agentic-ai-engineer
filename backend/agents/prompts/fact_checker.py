CLAIM_EXTRACTION_PROMPT = """You are a fact-checking editor. Extract every factual claim from this draft.

DRAFT:
{draft}

A "claim" is any statement that:
- Asserts a specific fact (number, date, name, event, statistic)
- Attributes a position or quote to a person or organization
- States a causal relationship ("X led to Y")
- Makes a comparison ("X is larger/faster/better than Y")

A claim is NOT:
- An opinion clearly framed as opinion
- A rhetorical question
- A commonly accepted truism
- A hypothetical
- A subjective assessment

For each claim, extract:
{{
  "claim_text": "<exact text containing the claim>",
  "claim_type": "statistic" | "attribution" | "causal" | "comparison" | "event" | "other",
  "verification_query": "<a SHORT, specific web search query — under 12 words — that would surface evidence>"
}}

Return as a JSON array. If no factual claims, return []. No prose outside the JSON."""


CLAIM_VERIFICATION_PROMPT = """Does the following context support, contradict, or not address this claim?

CLAIM: {claim_text}

CONTEXT:
{context}

Return JSON (no prose outside the JSON):
{{
  "status": "supported" | "contradicted" | "not_found",
  "evidence": "<exact quote from context if supported/contradicted, else empty string>",
  "confidence": <float 0-1>
}}"""


WEB_VERIFICATION_PROMPT = """Do these search results support or contradict this claim?

CLAIM: {claim_text}

SEARCH RESULTS:
{search_results}

Return JSON (no prose outside the JSON):
{{
  "status": "supported" | "contradicted" | "unverifiable",
  "evidence": "<relevant excerpt>",
  "confidence": <float 0-1>
}}"""


DRAFT_CORRECTION_PROMPT = """You are a fact-checking editor making targeted corrections to a draft.

ORIGINAL DRAFT:
{draft}

CORRECTIONS TO APPLY (each item includes evidence for context):
{corrections_json}

Rules:
1. For "soften" claims: add appropriate hedging language ("reports suggest", "an estimated", "according to X") without changing the core meaning. Use the evidence to write a SPECIFIC hedge, not generic.
2. For "remove" claims: excise the claim and smoothly connect the surrounding text. If the claim IS the central argument, replace it with the closest weaker but defensible version drawn from the evidence.
3. Preserve the draft's voice, structure, and argument flow
4. Do NOT rewrite sections that aren't flagged
5. Do NOT add new claims or information beyond what's in the evidence

Output ONLY the corrected draft."""
