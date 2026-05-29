QUERY_CONSTRUCTION_PROMPT = """You are a research strategist for a content creator.

THESIS / STANCE (the queries must serve this, not wander from it):
{user_topic}

Content type: {content_type}
{original_tweet_block}

{scraped_context}

Generate exactly {query_count} search queries that will surface information NOT already present in the context above (if any).

Each query should hunt for one of:
1. The most recent developments (include "2025" or "2026" in at least one query)
2. Contrarian or underreported perspectives that complicate the thesis
3. Concrete data points, statistics, or named examples that directly test the thesis
4. Adjacent angles — second-order effects, who-loses analysis, historical parallels — but only where they bear on the thesis above

Every query must serve the thesis. Do not broaden into adjacent subjects that merely share keywords; a query about a neighboring topic (even one likely to have hard numbers) is drift.

Avoid queries that would surface the same articles already in the context. If the context already covers a fact, search for the next layer of the thesis.

Return as a JSON array of strings. No commentary."""


TOPIC_SUMMARY_PROMPT = """Create a structured topic brief from these scored sources for a content creator writing a {content_type}.

Scored sources (ranked by insight potential):
{sources_json}

THE THESIS / STANCE (this is the spine of the brief — everything must serve it):
{user_topic}
{original_tweet_block}

Return STRICT JSON (no markdown, no commentary) with this exact shape:

{{
  "topic": "1 sentence core topic",
  "key_facts": [
    "Fact with specific number/name/date — (source: domain or title)",
    "..."
  ],
  "tensions": [
    "Genuine debate point grounded in the sources",
    "..."
  ],
  "angle_seeds": [
    "Provocative but defensible take that could anchor a {content_type}",
    "..."
  ],
  "audience_context": "Who cares about this right now and why"
}}

Counts required for content type "{content_type}":
- key_facts: {fact_count}
- tensions: {tension_count}
- angle_seeds: {seed_count}

Rules:
- THE TOPIC HEADLINE must restate the thesis above. Do NOT replace the thesis with whatever the sources happen to emphasize — if the sources drift, the headline stays anchored to the thesis.
- RELEVANCE IS PRIMARY: every key fact must directly support, complicate, or refute the thesis. Drop tangential facts even when they are well-sourced and carry great numbers. A specific number about an adjacent subject is still drift — leave it out.
- KEY FACTS must also include specific numbers, names, dates, or quoted phrases — but specificity is secondary to relevance. A vague-but-on-thesis fact beats a precise-but-off-thesis one; prefer facts that are both.
- TENSIONS must be real disagreements between credible parties that bear on the thesis, not strawmen.
- ANGLE SEEDS should be takes a thoughtful operator would *want* to read, and each must advance the thesis — not generic punditry, not a pivot to an adjacent story.
- Every fact and tension must be traceable to one of the scored sources."""


TOPIC_INFERENCE_PROMPT = """Given these articles/pages, identify the single unifying topic or theme.
If no clear theme exists, identify the most substantive topic from the highest-quality source.

Sources:
{sources_text}

Return: A 1-2 sentence topic description."""
