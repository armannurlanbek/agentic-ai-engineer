"""Test the Draft Writer <-> Critic loop in isolation.

Manually drives the loop (write -> critique -> revise -> ...) so each iteration
prints its draft, score, line edits, and tokens. Uses the conditional-edge
logic from graph.py to decide when to stop.

Usage:
    python test_draft_critic.py
    python test_draft_critic.py --content-type tweet
    python test_draft_critic.py --content-type thread --max-iter 3
    python test_draft_critic.py --skip-retrieval
"""
import argparse
import asyncio
import uuid

from backend.agents.angle import angle_node
from backend.agents.critic import critic_node
from backend.agents.draft_writer import draft_writer_node
from backend.agents.graph import should_continue_drafting, DRAFT_WRITER, FACT_CHECKER
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
    "Capability per dollar vs alignment per capability vs distribution — no single optimization target wins",
    "Open weights closing on closed frontier faster than most Western labs predicted",
]
DEFAULT_SEEDS = [
    "The frontier race in 2026 isn't about who's smartest — it's about who's optimizing for what",
    "Export controls accidentally made Chinese labs more architecturally creative",
    "Agent reliability is an infrastructure problem, not a model problem",
]
DEFAULT_AUDIENCE = "AI builders, ML researchers, and tech-savvy product people."


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content-type", default="tweet", help="tweet|thread|essay")
    parser.add_argument("--max-iter", type=int, default=3)
    parser.add_argument("--skip-retrieval", action="store_true")
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    print("=" * 70)
    print(f"DRAFT WRITER <-> CRITIC TEST")
    print(f"  content_type: {args.content_type}")
    print(f"  max_iter:     {args.max_iter}")
    print("=" * 70)

    state = create_initial_state(
        run_id=f"test-draft-{uuid.uuid4().hex[:6]}",
        user_topic=DEFAULT_HEADLINE,
        content_type=args.content_type,
        user_id=args.user_id,
        max_draft_iterations=args.max_iter,
    )
    state["topic_headline"] = DEFAULT_HEADLINE
    state["key_facts"] = DEFAULT_FACTS
    state["tensions"] = DEFAULT_TENSIONS
    state["angle_seeds"] = DEFAULT_SEEDS
    state["audience_context"] = DEFAULT_AUDIENCE

    if not args.skip_retrieval:
        print("\n--- Retrieval ---")
        ret = await retrieval_node(state)
        state["rag_context"] = ret.get("rag_context", [])
        state["voice_samples"] = ret.get("voice_samples", [])
        state["traces"] = list(ret.get("traces", []))
        print(f"  voice={len(state['voice_samples'])}  ctx={len(state['rag_context'])}")

    print("\n--- Angle ---")
    ang = await angle_node(state)
    state["all_angles"] = ang.get("all_angles", [])
    state["selected_angles"] = ang.get("selected_angles", [])
    state["angle_strategy_note"] = ang.get("angle_strategy_note", "")
    state["traces"] = (state.get("traces") or []) + list(ang.get("traces", []))
    if state["selected_angles"]:
        print(f"  selected: {state['selected_angles'][0].get('angle_text', '')}")

    # Drive the loop
    iter_n = 0
    while True:
        iter_n += 1
        print(f"\n{'=' * 70}\n  ITERATION {iter_n}  (state.draft_iteration={state.get('draft_iteration', 0)})\n{'=' * 70}")

        # Draft Writer
        dw = await draft_writer_node(state)
        state["current_draft"] = dw["current_draft"]
        state["draft_iteration"] = dw["draft_iteration"]
        state["draft_history"] = (state.get("draft_history") or []) + dw.get("draft_history", [])
        state["traces"] = (state.get("traces") or []) + list(dw.get("traces", []))

        dw_trace = dw.get("traces", [{}])[-1] if dw.get("traces") else {}
        print(f"\n--- DRAFT (iter {state['draft_iteration']}) ---")
        print(state["current_draft"])
        print(f"\n  [draft_writer tokens: in={dw_trace.get('prompt_tokens', 0)}  "
              f"out={dw_trace.get('completion_tokens', 0)}  duration={dw_trace.get('duration_ms', 0):.0f}ms]")

        # Critic
        cr = await critic_node(state)
        state["critic_verdict"] = cr["critic_verdict"]
        state["draft_passed"] = cr["draft_passed"]
        state["critic_feedback_history"] = (state.get("critic_feedback_history") or []) + cr.get("critic_feedback_history", [])
        state["traces"] = (state.get("traces") or []) + list(cr.get("traces", []))

        verdict = state["critic_verdict"]
        cr_trace = cr.get("traces", [{}])[-1] if cr.get("traces") else {}
        print(f"\n--- CRITIC VERDICT ---")
        print(f"  approved:  {verdict.get('approved')}  score: {verdict.get('score')}")
        rubric = verdict.get("rubric_scores", {})
        if rubric:
            print("  rubric:    " + "  ".join(f"{k}={v}" for k, v in rubric.items()))
        print(f"  summary:   {verdict.get('summary', '')}")
        edits = verdict.get("line_edits", []) or []
        if edits:
            print(f"  line_edits ({len(edits)}):")
            for e in edits[:3]:
                print(f"    - issue: {e.get('issue', '')[:100]}")
                print(f"      suggest: {e.get('suggestion', '')[:100]}")
        print(f"\n  [critic tokens: in={cr_trace.get('prompt_tokens', 0)}  "
              f"out={cr_trace.get('completion_tokens', 0)}  duration={cr_trace.get('duration_ms', 0):.0f}ms]")

        # Conditional edge
        next_node = should_continue_drafting(state)
        print(f"\n  -> next: {next_node}")
        if next_node == FACT_CHECKER:
            break
        if iter_n > args.max_iter + 1:  # safety cap
            print("\n  SAFETY BREAK")
            break

    # Final summary
    print(f"\n{'=' * 70}\n  FINAL\n{'=' * 70}")
    print(f"  iterations:    {state['draft_iteration']}")
    print(f"  draft_passed:  {state.get('draft_passed')}")
    print(f"  exit reason:   ", end="")
    if state.get("draft_passed"):
        print("critic approved")
    elif state["draft_iteration"] >= args.max_iter:
        print("max iterations reached")
    else:
        print("plateau (score didn't improve >= 0.3)")

    print("\n  score history:")
    for i, v in enumerate(state.get("critic_feedback_history", []), 1):
        print(f"    iter {i}: {v.get('score'):.2f}  approved={v.get('approved')}")

    total_in = sum(t.get("prompt_tokens", 0) for t in state.get("traces", []))
    total_out = sum(t.get("completion_tokens", 0) for t in state.get("traces", []))
    print(f"\n  total tokens:  in={total_in}  out={total_out}  combined={total_in + total_out}")


if __name__ == "__main__":
    asyncio.run(main())
