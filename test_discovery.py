"""Test the Discovery Agent in isolation."""
import asyncio
import json
from backend.models.state import create_initial_state
from backend.agents.discovery import discovery_node

async def main():
    state = create_initial_state(
        run_id="test-discovery-002",
        user_topic="",
        content_type="quote_retweet",
        user_urls=["https://nationalbusiness.kz/news/kazahstan-stal-aktsionerom-konkurenta-chatgpt-5c639f/"],
    )

    print("=" * 60)
    print("DISCOVERY AGENT TEST — URL mode (Karpathy tweet)")
    print(f"URLs: {state['user_urls']}")
    print(f"Content type: {state['content_type']}")
    print("=" * 60)

    result = await discovery_node(state)

    print("\n--- DISCOVERED SOURCES ---")
    sources = result.get("discovered_sources", [])
    for i, s in enumerate(sources, 1):
        print(f"\n  [{i}] {s.get('source_type', 'unknown')}")
        print(f"      Title: {s.get('title', 'N/A')}")
        print(f"      URL:   {s.get('url', 'N/A')}")
        print(f"      Snip:  {(s.get('snippet', '') or '')[:160]}...")

    print("\n--- SEARCH QUERIES GENERATED ---")
    for i, q in enumerate(result.get("discovery_search_queries", []), 1):
        print(f"  {i}. {q}")

    print("\n--- STRUCTURED BRIEF ---")
    print(f"  Headline:  {result.get('topic_headline', '')}")
    print(f"  Audience:  {result.get('audience_context', '')}")
    print("  Key facts:")
    for f in result.get("key_facts", []):
        print(f"    - {f}")
    print("  Tensions:")
    for t in result.get("tensions", []):
        print(f"    - {t}")
    print("  Angle seeds:")
    for s in result.get("angle_seeds", []):
        print(f"    - {s}")

    print("\n--- TOPIC SUMMARY (rendered) ---")
    print(result.get("selected_topic_summary", "EMPTY"))

    print("\n--- TRACE ---")
    for t in result.get("traces", []):
        print(f"  Node: {t.get('node_name')}")
        print(f"  Duration: {t.get('duration_ms', 0):.0f}ms")
        print(f"  Tokens: in={t.get('prompt_tokens', 0)}  out={t.get('completion_tokens', 0)}  total={t.get('total_tokens', 0)}")
        print(f"  Error: {t.get('error', 'None')}")

if __name__ == "__main__":
    asyncio.run(main())
