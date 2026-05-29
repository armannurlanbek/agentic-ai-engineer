"""Test the Retrieval Agent against the real ChromaDB at ./data/chroma_db/.

Usage:
    python test_retrieval.py
    python test_retrieval.py --topic "mechanistic interpretability"
    python test_retrieval.py --topic "AI agents" --content-type essay
    python test_retrieval.py --user-id default --topic "startup advice"

The script hand-builds a post-Discovery state with topic_headline + key_facts
(skipping the actual Discovery LLM calls), then runs retrieval_node and prints
what voice + context chunks come back.
"""
import argparse
import asyncio
import uuid

from backend.agents.retrieval import retrieval_node
from backend.models.state import create_initial_state
from backend.rag.chroma_client import get_context_collection, get_voice_collection


DEFAULT_TOPIC = "How to build a reliable AI agent in 2026"
DEFAULT_FACTS = [
    "Anthropic released Claude 4.7 with tool-use improvements that reduce error-recovery loops",
    "Most production agent failures trace to tool-spec ambiguity, not model capability limits",
    "Eval-driven development beats prompt-tuning once an agent has more than three tools",
]
DEFAULT_ANGLE_SEEDS = [
    "Agents fail at the seams, not the models",
    "The boring infrastructure work is what separates demos from deployments",
]


def _print_chunk(i: int, chunk: dict, max_chars: int = 240) -> None:
    meta = chunk.get("metadata", {}) or {}
    src = meta.get("source_slug") or meta.get("source") or "?"
    title = meta.get("title") or chunk.get("source_file", "")
    rel = chunk.get("relevance_score", 0)
    text = chunk.get("text", "").replace("\n", " ").strip()
    print(f"\n  [{i}] rel={rel:.3f}  source={src}")
    print(f"      title:  {title[:80]}")
    print(f"      text:   {text[:max_chars]}{'...' if len(text) > max_chars else ''}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="Topic headline (what Discovery would emit)")
    parser.add_argument("--content-type", default="thread", help="tweet|quote_retweet|thread|essay|article")
    parser.add_argument("--user-id", default="default", help="Chroma user_id (collection scope)")
    args = parser.parse_args()

    voice_count = get_voice_collection(args.user_id).count()
    context_count = get_context_collection(args.user_id).count()

    print("=" * 70)
    print("RETRIEVAL AGENT TEST (real corpus)")
    print(f"  user_id:      {args.user_id}")
    print(f"  voice chunks: {voice_count}")
    print(f"  ctx chunks:   {context_count}")
    print("=" * 70)

    if voice_count == 0 and context_count == 0:
        print("\nERROR: collections are empty. Run bulk_ingest_sources.py first.")
        return

    state = create_initial_state(
        run_id=f"test-retrieval-{uuid.uuid4().hex[:6]}",
        user_topic=args.topic,
        content_type=args.content_type,
        user_id=args.user_id,
    )
    state["topic_headline"] = args.topic
    state["key_facts"] = DEFAULT_FACTS
    state["angle_seeds"] = DEFAULT_ANGLE_SEEDS

    print(f"\n  topic_headline: {state['topic_headline']}")
    print(f"  content_type:   {state['content_type']}")
    print(f"  key_facts:      {len(state['key_facts'])}  angle_seeds: {len(state['angle_seeds'])}")

    result = await retrieval_node(state)

    print("\n--- VOICE SAMPLES (style exemplars, deduped by source+file) ---")
    voice = result.get("voice_samples", [])
    if not voice:
        print("  (none returned — try lowering VOICE_MIN_RELEVANCE or use a more on-topic query)")
    for i, v in enumerate(voice, 1):
        _print_chunk(i, v)

    print("\n--- RAG CONTEXT (factual grounding, deduped by source+file) ---")
    ctx = result.get("rag_context", [])
    if not ctx:
        print("  (none returned)")
    for i, c in enumerate(ctx, 1):
        _print_chunk(i, c)

    print("\n--- TRACE ---")
    for t in result.get("traces", []):
        print(f"  node={t.get('node_name')}  duration={t.get('duration_ms', 0):.0f}ms  "
              f"tokens={t.get('total_tokens', 0)}  error={t.get('error') or 'None'}")

    print("\n--- SUMMARY ---")
    print(f"  voice returned: {len(voice)} (unique authors: "
          f"{len({(v.get('metadata',{}) or {}).get('source_slug') for v in voice})})")
    print(f"  ctx   returned: {len(ctx)} (unique sources: "
          f"{len({(c.get('metadata',{}) or {}).get('source_slug') for c in ctx})})")


if __name__ == "__main__":
    asyncio.run(main())
