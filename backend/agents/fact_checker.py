import asyncio
import json

from langchain_openai import ChatOpenAI

from backend.agents.prompts.fact_checker import (
    CLAIM_EXTRACTION_PROMPT,
    CLAIM_VERIFICATION_PROMPT,
    DRAFT_CORRECTION_PROMPT,
    WEB_VERIFICATION_PROMPT,
)
from backend.agents.tracing import traced_node
from backend.config import settings
from backend.tools.chroma_tools import query_context_docs
from backend.tools.tavily_search import tavily_search


PER_CLAIM_RAG_CHUNKS = 3
PER_CLAIM_WEB_RESULTS = 3
RAG_CONFIDENCE_FLOOR = 0.7  # below this, fall through to web verification


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, timeout=60)


def _parse_json(text: str) -> list | dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(text)


def _usage(resp) -> tuple[int, int]:
    meta = getattr(resp, "usage_metadata", None) or {}
    return (
        int(meta.get("input_tokens", 0) or 0),
        int(meta.get("output_tokens", 0) or 0),
    )


# (rag_status, web_status) -> action
# - keep:   no change
# - soften: add hedging language
# - remove: excise the claim
# All combinations are explicit so behavior is auditable, including
# the previously-missing (not_found, not_found) case.
ACTION_RULES = {
    ("supported", "supported"):    "keep",
    ("supported", "not_found"):    "keep",
    ("supported", "unverifiable"): "keep",
    ("supported", "contradicted"): "soften",
    ("not_found", "supported"):    "keep",
    ("not_found", "unverifiable"): "soften",
    ("not_found", "contradicted"): "remove",
    ("not_found", "not_found"):    "soften",   # neither found it — hedge or drop
    ("contradicted", "supported"): "soften",   # genuine tension; hedge it
    ("contradicted", "unverifiable"): "remove",
    ("contradicted", "contradicted"): "remove",
    ("contradicted", "not_found"): "remove",
}


async def _verify_one_claim(
    claim: dict,
    user_id: str,
    discovered_snippets: str,
    llm: ChatOpenAI,
) -> tuple[dict, int, int]:
    """Verify a single claim. Returns (result_dict, prompt_tokens, completion_tokens)."""
    claim_text = claim.get("claim_text", "")
    verification_query = claim.get("verification_query", "") or claim_text
    p_tokens = 0
    c_tokens = 0

    # --- Tier 1: RAG (per-claim, not a giant shared blob) ---
    rag_chunks = await query_context_docs(verification_query, user_id, n_results=PER_CLAIM_RAG_CHUNKS)
    rag_context_parts = [c.get("text", "") for c in rag_chunks if c.get("text")]
    if discovered_snippets:
        rag_context_parts.append(discovered_snippets)
    rag_context = "\n\n".join(rag_context_parts)[:6000]

    rag_status, rag_confidence, rag_evidence = "not_found", 0.0, ""
    if rag_context.strip():
        try:
            resp = await llm.ainvoke(
                CLAIM_VERIFICATION_PROMPT.format(
                    claim_text=claim_text,
                    context=rag_context,
                )
            )
            i, o = _usage(resp)
            p_tokens += i
            c_tokens += o
            rag_result = _parse_json(resp.content)
            rag_status = rag_result.get("status", "not_found")
            rag_confidence = float(rag_result.get("confidence", 0) or 0)
            rag_evidence = rag_result.get("evidence", "") or ""
        except Exception:
            pass

    # --- Tier 2: Web (only if RAG didn't find OR found weakly) ---
    web_status, web_evidence = "unverifiable", ""
    needs_web = (
        rag_status == "not_found"
        or (rag_status == "supported" and rag_confidence < RAG_CONFIDENCE_FLOOR)
    )
    if needs_web:
        try:
            search_results = await tavily_search(verification_query, max_results=PER_CLAIM_WEB_RESULTS)
            if search_results:
                formatted = "\n\n".join(
                    f"Source: {r.get('title', '')}\n{r.get('snippet', '')}"
                    for r in search_results
                )
                resp = await llm.ainvoke(
                    WEB_VERIFICATION_PROMPT.format(
                        claim_text=claim_text,
                        search_results=formatted,
                    )
                )
                i, o = _usage(resp)
                p_tokens += i
                c_tokens += o
                web_result = _parse_json(resp.content)
                web_status = web_result.get("status", "unverifiable")
                web_evidence = web_result.get("evidence", "") or ""
        except Exception:
            web_status = "unverifiable"

    action = ACTION_RULES.get((rag_status, web_status), "soften")
    # `verified` reports "the claim has affirmative support somewhere" rather
    # than "the action is keep" — these can diverge (e.g., supported+contradicted
    # becomes soften but the claim WAS verified by RAG).
    verified = rag_status == "supported" or web_status == "supported"

    return (
        {
            "claim_text": claim_text,
            "claim_type": claim.get("claim_type", "other"),
            "verified": verified,
            "action": action,
            "rag_status": rag_status,
            "rag_confidence": rag_confidence,
            "rag_evidence": rag_evidence[:500],
            "web_status": web_status,
            "web_evidence": web_evidence[:500],
        },
        p_tokens,
        c_tokens,
    )


@traced_node("fact_checker")
async def fact_checker_node(state: dict, config: dict | None = None) -> dict:
    llm = _get_llm()
    draft = state.get("current_draft", "")
    user_id = state.get("user_id", "default")
    discovered_sources = state.get("discovered_sources", []) or []

    prompt_tokens = 0
    completion_tokens = 0

    # Step 1: extract claims
    resp = await llm.ainvoke(CLAIM_EXTRACTION_PROMPT.format(draft=draft))
    i, o = _usage(resp)
    prompt_tokens += i
    completion_tokens += o
    try:
        claims = _parse_json(resp.content)
        if not isinstance(claims, list):
            claims = []
    except Exception:
        claims = []

    if not claims:
        return {
            "fact_check_results": [],
            "post_factcheck_draft": draft,
            "_trace_meta": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        }

    # Pre-format discovered_sources once — every claim sees the same backdrop
    discovered_snippets = "\n\n".join(
        f"[{s.get('title', '')}] {s.get('full_text') or s.get('snippet', '')}"
        for s in discovered_sources if isinstance(s, dict)
    )[:4000]

    # Step 2: verify all claims in parallel
    tasks = [
        _verify_one_claim(claim, user_id, discovered_snippets, llm)
        for claim in claims
    ]
    verification_outputs = await asyncio.gather(*tasks)

    results: list[dict] = []
    corrections: list[dict] = []
    for result, p_tok, c_tok in verification_outputs:
        prompt_tokens += p_tok
        completion_tokens += c_tok
        results.append(result)
        if result["action"] != "keep":
            corrections.append({
                "claim_text": result["claim_text"],
                "action": result["action"],
                "reason": f"RAG: {result['rag_status']} / Web: {result['web_status']}",
                "evidence": (result["rag_evidence"] or result["web_evidence"])[:300],
            })

    # Step 3: apply corrections if any
    if corrections:
        resp = await llm.ainvoke(
            DRAFT_CORRECTION_PROMPT.format(
                draft=draft,
                corrections_json=json.dumps(corrections, indent=2),
            )
        )
        i, o = _usage(resp)
        prompt_tokens += i
        completion_tokens += o
        corrected_draft = resp.content.strip()
    else:
        corrected_draft = draft

    return {
        "fact_check_results": results,
        "post_factcheck_draft": corrected_draft,
        "_trace_meta": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
    }
