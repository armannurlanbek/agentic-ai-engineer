"""Test the Voice Reviewer with a fact-checked draft + kept/soften/remove claims.

Verifies:
  - real token capture
  - style profile extraction (or default-by-content-type fallback)
  - voice adjustment returns adjusted_draft + adjustments_made
  - preservation check catches dropped kept-claims and re-invokes
  - length ratio + voice_match_score reflect reality (no fabricated 0.8)

Usage:
    python test_voice_reviewer.py
    python test_voice_reviewer.py --content-type tweet
    python test_voice_reviewer.py --user-id default
"""
import argparse
import asyncio
import uuid

from backend.agents.voice_reviewer import voice_reviewer_node
from backend.models.state import create_initial_state


# Fact-checked draft (mirrors the kind of output the fact-checker would emit).
TEST_DRAFT = """The frontier AI race in 2026 is splitting along three axes. OpenAI shipped GPT-5 in late 2025, optimizing for extended reasoning over raw parameter count. Reports suggest DeepSeek R2 matches Claude 4.6 on most benchmarks at a meaningfully lower inference cost, though specific multipliers vary by workload.

The real story is more mundane: agent reliability remains an infrastructure problem, not a capability problem. Tool-spec ambiguity, not model intelligence, is what breaks most production deployments."""


# Simulated fact_check_results: 2 kept, 1 softened, 0 removed.
TEST_FC_RESULTS = [
    {
        "claim_text": "OpenAI shipped GPT-5 in late 2025",
        "claim_type": "event",
        "verified": True,
        "action": "keep",
        "rag_status": "supported",
        "rag_confidence": 0.85,
        "rag_evidence": "GPT-5 launched Q4 2025...",
        "web_status": "supported",
        "web_evidence": "",
    },
    {
        "claim_text": "optimizing for extended reasoning over raw parameter count",
        "claim_type": "comparison",
        "verified": True,
        "action": "keep",
        "rag_status": "supported",
        "rag_confidence": 0.72,
        "rag_evidence": "GPT-5 emphasized reasoning budget...",
        "web_status": "not_found",
        "web_evidence": "",
    },
    {
        "claim_text": "DeepSeek R2 matches Claude 4.6 on most benchmarks",
        "claim_type": "comparison",
        "verified": False,
        "action": "soften",
        "rag_status": "contradicted",
        "rag_confidence": 0.6,
        "rag_evidence": "Benchmarks varied 3x-19x across tasks...",
        "web_status": "unverifiable",
        "web_evidence": "",
    },
]


# Optional fake voice samples — terse, em-dashes, confident.
TEST_VOICE_SAMPLES = [
    {
        "text": "Every agent system fails the same way. Tools that look fine in isolation behave differently under load — and nobody notices until production. The fix isn't smarter models. It's tighter contracts."
    },
    {
        "text": "The benchmarks lie. Not because the numbers are wrong — because the questions they answer aren't the ones that matter at deploy time."
    },
]


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-type", default="essay", help="tweet|thread|essay|article|quote_retweet")
    parser.add_argument("--user-id", default="default")
    parser.add_argument("--skip-voice-samples", action="store_true", help="test default-profile path")
    parser.add_argument("--voice-description", default="", help="optional freeform tone note")
    args = parser.parse_args()

    print("=" * 70)
    print("VOICE REVIEWER TEST")
    print(f"  content_type:       {args.content_type}")
    print(f"  voice_samples:      {0 if args.skip_voice_samples else len(TEST_VOICE_SAMPLES)}")
    print(f"  voice_description:  {args.voice_description or '(none)'}")
    print(f"  kept claims:        {sum(1 for r in TEST_FC_RESULTS if r['action'] == 'keep')}")
    print(f"  soften claims:      {sum(1 for r in TEST_FC_RESULTS if r['action'] == 'soften')}")
    print("=" * 70)

    state = create_initial_state(
        run_id=f"test-voice-{uuid.uuid4().hex[:6]}",
        user_topic="Frontier AI labs 2026",
        content_type=args.content_type,
        user_id=args.user_id,
        voice_description=args.voice_description,
    )
    state["post_factcheck_draft"] = TEST_DRAFT
    state["fact_check_results"] = TEST_FC_RESULTS
    state["voice_samples"] = [] if args.skip_voice_samples else TEST_VOICE_SAMPLES

    print("\n--- INPUT DRAFT ---")
    print(TEST_DRAFT)

    print("\n--- Running Voice Reviewer ---")
    result = await voice_reviewer_node(state)

    vr = result.get("voice_review", {}) or {}

    print("\n--- STYLE PROFILE ---")
    sp = vr.get("style_profile", {}) or {}
    for k, v in sp.items():
        print(f"  {k:>26}: {v}")

    print("\n--- ADJUSTMENTS MADE ---")
    adj = vr.get("adjustments_made", []) or []
    if adj:
        for a in adj:
            print(f"  - {a}")
    else:
        print("  (none reported)")

    print("\n--- PRESERVATION CHECK ---")
    print(f"  kept_claims_total:      {vr.get('kept_claims_total')}")
    print(f"  kept_claims_preserved:  {vr.get('kept_claims_preserved')}")
    print(f"  restoration_attempted:  {vr.get('restoration_attempted')}")
    missing = vr.get("missing_kept_claims", []) or []
    if missing:
        print(f"  STILL MISSING ({len(missing)}):")
        for m in missing:
            print(f"    - {m}")
    else:
        print("  all kept claims preserved")

    print("\n--- LENGTH ---")
    print(f"  length_ratio:    {vr.get('length_ratio')}  (target 0.9-1.1)")
    print(f"  in_bounds:       {vr.get('length_in_bounds')}")
    print(f"  voice_match:     {vr.get('voice_match_score')}")

    print("\n--- FINAL CONTENT ---")
    print(result.get("final_content", ""))

    print("\n--- TRACE ---")
    for t in result.get("traces", []):
        print(f"  node={t.get('node_name')}  duration={t.get('duration_ms', 0):.0f}ms  "
              f"in={t.get('prompt_tokens', 0)}  out={t.get('completion_tokens', 0)}  "
              f"total={t.get('total_tokens', 0)}")

    print(f"\n  status: {result.get('status')}")


if __name__ == "__main__":
    asyncio.run(main())
