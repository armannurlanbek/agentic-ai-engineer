"""End-to-end pipeline test harness.

Runs the full compiled graph (Discovery -> Retrieval -> Angle -> Draft<->Critic
-> Fact Checker -> Voice Reviewer) across a small high-signal matrix of requests,
then assesses each output on three layers:

  1. Structural assertions  - deterministic contract checks (per content type)
  2. AI-slop linter          - banned-phrase / hedge scan
  3. LLM-as-judge            - scores output on the assignment's grading axes

Full traces + finals are written to traces/ (a required deliverable).

Usage:
    python test_e2e.py                 # all 5 runs
    python test_e2e.py --only tweet    # single case
    python test_e2e.py --only essay --max-iter 2
"""
import argparse
import asyncio
import json
import re
import sys
import time
import uuid
from pathlib import Path

# When stdout is piped to a file on Windows, Python defaults to cp1252 and
# print() of UTF-8 content (em-dashes, curly quotes) raises UnicodeEncodeError,
# killing the run mid-output. Force UTF-8 so console output never crashes.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from langchain_openai import ChatOpenAI

from backend.agents.graph import content_pipeline
from backend.agents.text_checks import (
    find_hashtags,
    find_slop,
    structural_violations,
    thread_segments,
    word_count,
)
from backend.agents.tracing import compute_trace_summary
from backend.config import settings
from backend.models.enums import CHAR_LIMITS, THREAD_MIN_SEGMENTS, WORD_BANDS, ContentType
from backend.models.state import create_initial_state


TRACES_DIR = Path("traces")
EXPECTED_NODES = {
    "discovery", "retrieval", "angle",
    "draft_writer", "critic", "fact_checker", "voice_reviewer",
}
# Retrieval is embeddings-only — no chat-completion tokens expected.
ZERO_LLM_NODES = {"retrieval"}


# ── Test matrix ──────────────────────────────────────────────────────────
# Each case is chosen to light up a distinct path through the pipeline.
TEST_CASES = [
    {
        "name": "tweet",
        "content_type": "tweet",
        "user_topic": "Why most production AI agents fail on reliability, not capability",
        "note": "RAG-hit (corpus deep on agents) + voice samples from corpus",
    },
    {
        "name": "qrt",
        "content_type": "quote_retweet",
        "user_topic": "Open-weight models are closing on closed frontier faster than Western labs predicted",
        "original_tweet_text": "DeepSeek just dropped another open model that matches frontier closed models on most benchmarks. The moat was never the weights.",
        "note": "QRT path — must add insight, not summarize the original",
    },
    {
        "name": "thread",
        "content_type": "thread",
        "user_topic": "What eval-driven development actually looks like for LLM agents in 2026",
        "note": "RAG-hit, multi-segment numbered output",
    },
    {
        "name": "essay",
        "content_type": "essay",
        "user_topic": "Frontier AI labs in 2026 are diverging on what they optimize for, not converging on capability",
        "note": "RAG-hit, long-form argument structure",
    },
    {
        "name": "article",
        "content_type": "article",
        "user_topic": "The economics of specialty coffee sourcing and why direct-trade margins are misunderstood",
        "note": "RAG-MISS (non-AI topic) — tests graceful degradation + fact-checker web fallback",
    },
]


# ── Layer 2: AI-slop linter (uses the exact SLOP list the pipeline forbids) ──
HEDGE_PHRASES = [
    "i think", "in my opinion", "arguably", "it could be argued",
    "some might say", "it seems that", "perhaps", "kind of", "sort of",
]
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF\U00002190-\U000021FF\U00002B00-\U00002BFF]"
)


def slop_scan(text: str) -> dict:
    low = text.lower()
    slop_hits = find_slop(text)  # same SLOP_PHRASES the agents enforce against
    hedge_hits = [p for p in HEDGE_PHRASES if p in low]
    return {
        "slop_phrases": slop_hits,
        "hedge_phrases": hedge_hits,
        "slop_count": len(slop_hits),
        "hedge_count": len(hedge_hits),
        "clean": len(slop_hits) == 0,
    }


# ── Layer 1: structural assertions (thresholds sourced from shared constants) ──
def _ct(content_type: str):
    try:
        return ContentType(content_type)
    except ValueError:
        return None


def structural_checks(case: dict, final: str, state: dict) -> list[tuple[str, bool, str]]:
    """Return list of (check_name, passed, detail). Thresholds come from the same
    enums (CHAR_LIMITS, WORD_BANDS, THREAD_MIN_SEGMENTS) the pipeline enforces, so
    a pass here means the pipeline's own contract was met."""
    ct = case["content_type"]
    ct_enum = _ct(ct)
    checks: list[tuple[str, bool, str]] = []

    # --- universal ---
    traces = state.get("traces", [])
    fired = {t.get("node_name") for t in traces}
    checks.append(("all_nodes_fired", EXPECTED_NODES.issubset(fired),
                   f"missing: {EXPECTED_NODES - fired or 'none'}"))

    llm_traces = [t for t in traces if t.get("node_name") not in ZERO_LLM_NODES]
    zero_tok = [t.get("node_name") for t in llm_traces if t.get("total_tokens", 0) == 0]
    checks.append(("all_llm_nodes_have_tokens", not zero_tok,
                   f"zero-token nodes: {zero_tok or 'none'}"))

    checks.append(("final_non_empty", bool(final.strip()), f"{len(final)} chars"))

    has_repl = "�" in final
    checks.append(("no_encoding_noise", not has_repl,
                   "replacement char present" if has_repl else "clean"))

    no_emoji = not EMOJI_RE.search(final)
    if ct in ("tweet", "quote_retweet", "thread"):
        checks.append(("no_emoji", no_emoji, "emoji found" if not no_emoji else "none"))
        tags = find_hashtags(final)
        checks.append(("no_hashtags", not tags, ", ".join(tags) if tags else "none"))

    # --- per content type (constants-sourced) ---
    cap = CHAR_LIMITS.get(ct_enum) if ct_enum else None
    if cap is not None:
        n = len(final)
        checks.append((f"within_{cap}_chars", n <= cap, f"{n} chars (cap {cap})"))
    if ct == "quote_retweet":
        orig = case.get("original_tweet_text", "")
        ow = set(re.findall(r"\w+", orig.lower()))
        fw = set(re.findall(r"\w+", final.lower()))
        overlap = len(ow & fw) / max(len(ow), 1)
        checks.append(("qrt_not_echo", overlap < 0.6, f"word overlap {overlap:.2f}"))
    if ct == "thread":
        segs = thread_segments(final)
        checks.append(("thread_min_segments", len(segs) >= THREAD_MIN_SEGMENTS,
                       f"{len(segs)} segments (min {THREAD_MIN_SEGMENTS})"))
        over = [i + 1 for i, s in enumerate(segs) if len(s) > 280]
        checks.append(("thread_segments_within_280", not over,
                       f"over-limit segments: {over or 'none'}"))
    band = WORD_BANDS.get(ct_enum) if ct_enum else None
    if band:
        floor, _target, ceiling = band
        wc = word_count(final)
        checks.append((f"{ct}_word_band", floor <= wc <= ceiling,
                       f"{wc} words (band {floor}-{ceiling})"))

    # --- authoritative: the pipeline's own structural contract must be clean ---
    viol = structural_violations(ct, final)
    checks.append(("no_structural_violations", not viol,
                   f"{len(viol)} violation(s)" + (f": {viol[0]}" if viol else "")))

    # --- voice reviewer signals ---
    vr = state.get("voice_review") or {}
    if vr:
        checks.append(("voice_length_in_bounds", bool(vr.get("length_in_bounds")),
                       f"ratio {vr.get('length_ratio')}, {vr.get('char_count')} chars"))
        missing = vr.get("missing_kept_claims") or []
        checks.append(("kept_claims_preserved", len(missing) == 0, f"{len(missing)} missing"))

    return checks


# ── Layer 3: LLM-as-judge ────────────────────────────────────────────────
JUDGE_PROMPT = """You are a demanding editor judging AI-generated content for X/Twitter.
The bar: smart, high-insight, original, authentic voice — NOT generic AI slop.

CONTENT TYPE: {content_type}
TOPIC: {topic}

CONTENT:
{content}

Score each axis 1-10 (10 = exceptional, 5 = mediocre, 1 = slop). Be harsh and specific.

Return JSON (no prose outside the JSON):
{{
  "insight_density": <1-10>,
  "originality": <1-10>,
  "hook_strength": <1-10>,
  "authentic_voice": <1-10>,
  "clarity": <1-10>,
  "overall": <1-10>,
  "one_line_verdict": "<single sentence — what's strongest and what's weakest>"
}}"""


def _judge_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, timeout=60)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(text)


async def judge(case: dict, final: str) -> dict:
    llm = _judge_llm()
    try:
        resp = await llm.ainvoke(JUDGE_PROMPT.format(
            content_type=case["content_type"],
            topic=case["user_topic"],
            content=final,
        ))
        return _parse_json(resp.content)
    except Exception as e:
        return {"error": str(e)}


# ── Runner ───────────────────────────────────────────────────────────────
async def run_one(case: dict, max_iter: int) -> dict:
    run_id = f"e2e-{case['name']}-{uuid.uuid4().hex[:6]}"
    print(f"\n{'=' * 74}\n  RUN: {case['name'].upper()}  ({case['content_type']})\n"
          f"  topic: {case['user_topic']}\n  note:  {case['note']}\n{'=' * 74}")

    state = create_initial_state(
        run_id=run_id,
        user_topic=case["user_topic"],
        content_type=case["content_type"],
        user_id="default",
        original_tweet_text=case.get("original_tweet_text", ""),
        max_draft_iterations=max_iter,
    )

    t0 = time.time()
    try:
        final_state = await content_pipeline.ainvoke(
            state, config={"configurable": {"thread_id": run_id}}
        )
    except Exception as e:
        print(f"  !! PIPELINE RAISED: {type(e).__name__}: {e}")
        return {"name": case["name"], "error": f"{type(e).__name__}: {e}", "run_id": run_id}
    wall = time.time() - t0

    final = final_state.get("final_content", "") or ""
    traces = final_state.get("traces", [])
    summary = compute_trace_summary(traces)

    # assessment
    structural = structural_checks(case, final, final_state)
    slop = slop_scan(final)
    verdict = await judge(case, final)

    # node-by-node trace line
    print("\n  --- TRACE (node: ms / tokens) ---")
    for t in traces:
        print(f"    {t.get('node_name', '?'):>14}: {t.get('duration_ms', 0):>7.0f}ms  "
              f"tok={t.get('total_tokens', 0)}"
              + (f"  ERROR: {t['error']}" if t.get("error") else ""))
    print(f"    {'WALL':>14}: {wall * 1000:>7.0f}ms   total_tokens={summary['total_tokens']}  "
          f"llm_calls~{summary['total_llm_calls']}  draft_iters={final_state.get('draft_iteration')}")

    print("\n  --- STRUCTURAL ---")
    s_pass = 0
    for name, ok, detail in structural:
        print(f"    [{'PASS' if ok else 'FAIL'}] {name:<26} {detail}")
        s_pass += int(ok)
    print(f"    => {s_pass}/{len(structural)} passed")

    print("\n  --- SLOP LINTER ---")
    print(f"    slop phrases: {slop['slop_phrases'] or 'none'}")
    print(f"    hedges:       {slop['hedge_phrases'] or 'none'}")

    print("\n  --- LLM JUDGE ---")
    if "error" in verdict:
        print(f"    judge error: {verdict['error']}")
    else:
        for k in ("insight_density", "originality", "hook_strength", "authentic_voice", "clarity", "overall"):
            print(f"    {k:>16}: {verdict.get(k)}")
        print(f"    verdict: {verdict.get('one_line_verdict', '')}")

    print("\n  --- FINAL CONTENT ---")
    print("    " + final.replace("\n", "\n    "))

    # persist
    TRACES_DIR.mkdir(exist_ok=True)
    out_path = TRACES_DIR / f"e2e_{case['name']}_{run_id}.json"
    out_path.write_text(json.dumps({
        "case": case,
        "run_id": run_id,
        "wall_ms": round(wall * 1000),
        "trace_summary": summary,
        "traces": traces,
        "draft_iteration": final_state.get("draft_iteration"),
        "draft_passed": final_state.get("draft_passed"),
        "selected_topic_summary": final_state.get("selected_topic_summary"),
        "selected_angles": final_state.get("selected_angles"),
        "fact_check_results": final_state.get("fact_check_results"),
        "voice_review": final_state.get("voice_review"),
        "final_content": final,
        "assessment": {
            "structural": [{"check": n, "pass": ok, "detail": d} for n, ok, d in structural],
            "slop": slop,
            "judge": verdict,
        },
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  trace written: {out_path}")

    return {
        "name": case["name"],
        "run_id": run_id,
        "wall_ms": round(wall * 1000),
        "total_tokens": summary["total_tokens"],
        "draft_iters": final_state.get("draft_iteration"),
        "structural_pass": s_pass,
        "structural_total": len(structural),
        "slop_count": slop["slop_count"],
        "judge_overall": verdict.get("overall") if "error" not in verdict else None,
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default=None, help="run a single case by name")
    parser.add_argument("--max-iter", type=int, default=3)
    args = parser.parse_args()

    cases = TEST_CASES
    if args.only:
        cases = [c for c in TEST_CASES if c["name"] == args.only]
        if not cases:
            print(f"no case named '{args.only}'. options: {[c['name'] for c in TEST_CASES]}")
            return

    print("#" * 74)
    print(f"# END-TO-END PIPELINE TEST  ({len(cases)} run(s), model={settings.openai_model})")
    print("#" * 74)

    results = []
    for case in cases:
        results.append(await run_one(case, args.max_iter))

    # ── summary table ──
    print(f"\n{'#' * 74}\n# SUMMARY\n{'#' * 74}")
    print(f"  {'run':<9} {'struct':<8} {'slop':<5} {'judge':<6} {'iters':<6} {'tokens':<8} {'wall':<7}")
    for r in results:
        if r.get("error"):
            print(f"  {r['name']:<9} ERROR: {r['error']}")
            continue
        struct = f"{r['structural_pass']}/{r['structural_total']}"
        print(f"  {r['name']:<9} {struct:<8} {r['slop_count']:<5} "
              f"{str(r['judge_overall']):<6} {str(r['draft_iters']):<6} "
              f"{r['total_tokens']:<8} {r['wall_ms']/1000:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
