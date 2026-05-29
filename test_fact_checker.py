"""Test the Fact Checker against the real corpus.

Feeds it a hand-built draft mixing real + fabricated claims so we can see
which get flagged for soften/remove vs kept.

Usage:
    python test_fact_checker.py
    python test_fact_checker.py --user-id default
"""
import argparse
import asyncio
import uuid

from backend.agents.fact_checker import fact_checker_node
from backend.models.state import create_initial_state


# Mixed draft: some claims are real and findable, others are fabricated
# or distorted to see if RAG + web verification flag them correctly.
TEST_DRAFT = """The frontier AI race in 2026 is splitting along three axes. OpenAI shipped GPT-5 in late 2025, optimizing for extended reasoning over raw parameter count. Anthropic's Claude 4.7 reportedly beats GPT-5 by 87% on the SuperGLUE benchmark, a number no one outside the labs has confirmed. DeepSeek R2 matches Claude 4.6 on most benchmarks at roughly 1/15th the inference cost.

Meanwhile, Sam Altman announced last week that OpenAI will pivot entirely to humanoid robotics by Q3, a claim that has not appeared in any public statement. The real story is more mundane: agent reliability remains an infrastructure problem, not a capability problem. Tool-spec ambiguity, not model intelligence, is what breaks most production deployments."""


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    print("=" * 70)
    print("FACT CHECKER TEST")
    print(f"  user_id: {args.user_id}")
    print("=" * 70)

    state = create_initial_state(
        run_id=f"test-fc-{uuid.uuid4().hex[:6]}",
        user_topic="Frontier AI labs 2026",
        content_type="essay",
        user_id=args.user_id,
    )
    state["current_draft"] = TEST_DRAFT
    state["discovered_sources"] = []  # leave empty; rely on RAG + web

    print("\n--- INPUT DRAFT ---")
    print(TEST_DRAFT)

    print("\n--- Running Fact Checker (parallel per-claim verification) ---")
    result = await fact_checker_node(state)

    fc_results = result.get("fact_check_results", [])
    print(f"\n--- CLAIMS EXTRACTED: {len(fc_results)} ---")

    keep, soften, remove = 0, 0, 0
    for i, r in enumerate(fc_results, 1):
        action = r.get("action", "?")
        if action == "keep":
            keep += 1
        elif action == "soften":
            soften += 1
        elif action == "remove":
            remove += 1
        print(f"\n  [{i}] action={action.upper()}  verified={r.get('verified')}  type={r.get('claim_type')}")
        print(f"      claim:    {r.get('claim_text', '')[:160]}")
        print(f"      rag:      status={r.get('rag_status')}  conf={r.get('rag_confidence', 0):.2f}")
        if r.get("rag_evidence"):
            print(f"      rag_ev:   {r['rag_evidence'][:160]}")
        print(f"      web:      status={r.get('web_status')}")
        if r.get("web_evidence"):
            print(f"      web_ev:   {r['web_evidence'][:160]}")

    print(f"\n--- ACTION BREAKDOWN ---")
    print(f"  keep:   {keep}")
    print(f"  soften: {soften}")
    print(f"  remove: {remove}")

    print(f"\n--- POST-FACTCHECK DRAFT ---")
    print(result.get("post_factcheck_draft", ""))

    print("\n--- TRACE ---")
    for t in result.get("traces", []):
        print(f"  node={t.get('node_name')}  duration={t.get('duration_ms', 0):.0f}ms  "
              f"in={t.get('prompt_tokens', 0)}  out={t.get('completion_tokens', 0)}  "
              f"total={t.get('total_tokens', 0)}")


if __name__ == "__main__":
    asyncio.run(main())
