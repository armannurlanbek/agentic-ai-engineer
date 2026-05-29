"""Test the Angle Agent in isolation with hand-built post-Discovery + post-Retrieval state.

Usage:
    python test_angle.py
    python test_angle.py --content-type tweet
    python test_angle.py --content-type essay --skip-retrieval

The script:
  1. Hand-builds the structured Discovery output (topic_headline, key_facts, etc.)
  2. (Optional) Calls real Retrieval against ./data/chroma_db/ to populate rag_context
  3. Runs angle_node and prints all 5 candidates + the selected one + scores + tokens
"""
import argparse
import asyncio
import json
import uuid

from backend.agents.angle import angle_node
from backend.agents.retrieval import retrieval_node
from backend.models.state import create_initial_state


DEFAULT_HEADLINE = "Frontier AI labs in 2026 are diverging on what they optimize for, not converging on capability."
DEFAULT_FACTS = [
    "OpenAI shipped GPT-5 in late 2025 emphasizing extended reasoning over parameter scale",
    "Anthropic's Constitutional AI 2.0 reduces sycophancy at the cost of more user pushback",
    "DeepSeek R2 matches Claude 4.6 on most benchmarks at 1/15th inference cost",
    "Most production AI agent failures trace to tool-spec ambiguity, not raw model capability",
]
DEFAULT_TENSIONS = [
    "Capability per dollar (OpenAI) vs alignment per capability (Anthropic) vs distribution (Google) — no single winner",
    "Open weights (DeepSeek) closing on closed frontier faster than most Western labs predicted",
]
DEFAULT_SEEDS = [
    "The frontier race in 2026 isn't about who's smartest — it's about who's optimizing for what",
    "Export controls accidentally made Chinese labs more architecturally creative than Western ones",
    "Agent reliability is now an infrastructure problem, not a model problem",
]
DEFAULT_AUDIENCE = "AI builders, ML researchers, and tech-savvy product people watching the lab race week-to-week."


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-type", default="thread", help="tweet|quote_retweet|thread|essay|article")
    parser.add_argument("--skip-retrieval", action="store_true", help="Skip the RAG call (use empty rag_context)")
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    print("=" * 70)
    print("ANGLE AGENT TEST")
    print(f"  content_type: {args.content_type}")
    print(f"  user_id:      {args.user_id}")
    print(f"  retrieval:    {'skipped' if args.skip_retrieval else 'real corpus'}")
    print("=" * 70)

    state = create_initial_state(
        run_id=f"test-angle-{uuid.uuid4().hex[:6]}",
        user_topic=DEFAULT_HEADLINE,
        content_type=args.content_type,
        user_id=args.user_id,
    )
    state["topic_headline"] = DEFAULT_HEADLINE
    state["key_facts"] = DEFAULT_FACTS
    state["tensions"] = DEFAULT_TENSIONS
    state["angle_seeds"] = DEFAULT_SEEDS
    state["audience_context"] = DEFAULT_AUDIENCE

    if not args.skip_retrieval:
        print("\n--- Running Retrieval first to populate rag_context ---")
        ret = await retrieval_node(state)
        state["rag_context"] = ret.get("rag_context", [])
        state["voice_samples"] = ret.get("voice_samples", [])
        state["traces"] = ret.get("traces", [])
        print(f"  voice samples: {len(state['voice_samples'])}  rag context: {len(state['rag_context'])}")

    print("\n--- INPUT STATE ---")
    print(f"  topic_headline:   {state['topic_headline']}")
    print(f"  key_facts:        {len(state['key_facts'])}")
    print(f"  tensions:         {len(state['tensions'])}")
    print(f"  angle_seeds:      {len(state['angle_seeds'])}")
    print(f"  rag_context:      {len(state.get('rag_context', []))}")

    print("\n--- Running Angle ---")
    result = await angle_node(state)

    all_angles = result.get("all_angles", [])
    selected = result.get("selected_angles", [])
    strategy = result.get("angle_strategy_note", "")

    print(f"\n--- ALL ANGLES ({len(all_angles)}) ---")
    for i, a in enumerate(all_angles):
        marker = "[SELECTED]" if a.get("selected") else "         "
        total = a.get("total_score", "?")
        atype = a.get("angle_type", "?")
        text = a.get("angle_text", "")
        print(f"\n  {marker} #{i}  total={total}  type={atype}")
        print(f"           text:    {text}")
        if "hook_strength" in a:
            print(f"           scores:  hook={a.get('hook_strength')}  "
                  f"def={a.get('defensibility')}  orig={a.get('originality')}  "
                  f"share={a.get('shareability')}")
        if a.get("why_it_works"):
            print(f"           why:     {a.get('why_it_works')}")

    print("\n--- SELECTED ANGLE(S) ---")
    for s in selected:
        print(f"  -> {s.get('angle_text', '')}")

    print("\n--- STRATEGY NOTE ---")
    print(f"  {strategy or '(none)'}")

    print("\n--- TRACES ---")
    for t in result.get("traces", []):
        print(f"  node={t.get('node_name')}  duration={t.get('duration_ms', 0):.0f}ms  "
              f"in={t.get('prompt_tokens', 0)}  out={t.get('completion_tokens', 0)}  "
              f"total={t.get('total_tokens', 0)}  error={t.get('error') or 'None'}")


if __name__ == "__main__":
    asyncio.run(main())
