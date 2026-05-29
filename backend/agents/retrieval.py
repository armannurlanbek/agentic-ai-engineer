from backend.agents.tracing import traced_node
from backend.tools.chroma_tools import query_context_docs, query_voice_samples


VOICE_N_RESULTS = 12
VOICE_KEEP_AFTER_DEDUPE = 5
VOICE_MAX_PER_SOURCE = 2
CONTEXT_N_RESULTS = 20
CONTEXT_KEEP_AFTER_DEDUPE = 8
CONTEXT_MAX_PER_SOURCE = 3
VOICE_MIN_RELEVANCE = 0.45
CONTEXT_MIN_RELEVANCE = 0.50


def _dedupe_and_diversify(chunks: list[dict], keep: int, max_per_source: int) -> list[dict]:
    """Dedupe by (source_slug, filename) then cap by source_slug for diversity.

    Why: ingestion splits each post into many overlapping chunks, AND a single
    publication (e.g. latent_space) can dominate top-K with many different
    issues. Want neither artifact in the downstream prompt.
    """
    seen: dict[tuple, dict] = {}
    for c in chunks:
        meta = c.get("metadata", {}) or {}
        key = (meta.get("source_slug", ""), meta.get("filename") or c.get("source_file", ""))
        if key not in seen or c.get("relevance_score", 0) > seen[key].get("relevance_score", 0):
            seen[key] = c
    deduped = sorted(seen.values(), key=lambda x: x.get("relevance_score", 0), reverse=True)

    per_source: dict[str, int] = {}
    diversified: list[dict] = []
    for c in deduped:
        slug = (c.get("metadata", {}) or {}).get("source_slug", "")
        if per_source.get(slug, 0) >= max_per_source:
            continue
        diversified.append(c)
        per_source[slug] = per_source.get(slug, 0) + 1
        if len(diversified) >= keep:
            break
    return diversified


@traced_node("retrieval")
async def retrieval_node(state: dict, config: dict | None = None) -> dict:
    user_id = state.get("user_id", "default")

    topic_headline = state.get("topic_headline", "") or state.get("user_topic", "")
    key_facts = state.get("key_facts", []) or []
    angle_seeds = state.get("angle_seeds", []) or []

    if not topic_headline:
        topic_summary = state.get("selected_topic_summary", "")
        topic_headline = topic_summary.split("\n")[0] if topic_summary else ""

    voice_parts = [topic_headline] + angle_seeds[:2]
    voice_query = " ".join(p for p in voice_parts if p).strip()[:400] or topic_headline
    raw_voice = await query_voice_samples(voice_query, user_id, n_results=VOICE_N_RESULTS)
    voice_results = [v for v in raw_voice if v.get("relevance_score", 0) >= VOICE_MIN_RELEVANCE]
    voice_results = _dedupe_and_diversify(voice_results, VOICE_KEEP_AFTER_DEDUPE, VOICE_MAX_PER_SOURCE)

    context_parts = [topic_headline] + key_facts[:5]
    context_query = " ".join(p for p in context_parts if p).strip()[:500] or topic_headline
    raw_context = await query_context_docs(context_query, user_id, n_results=CONTEXT_N_RESULTS)
    context_results = [c for c in raw_context if c.get("relevance_score", 0) >= CONTEXT_MIN_RELEVANCE]
    context_results = _dedupe_and_diversify(context_results, CONTEXT_KEEP_AFTER_DEDUPE, CONTEXT_MAX_PER_SOURCE)

    return {
        "voice_samples": voice_results,
        "rag_context": context_results,
        "_trace_meta": {"prompt_tokens": 0, "completion_tokens": 0},
    }
