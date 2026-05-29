import json
import re

from langchain_openai import ChatOpenAI

from backend.agents.prompts.angle import ANGLE_GENERATION_PROMPT, ANGLE_SCORING_PROMPT
from backend.agents.tracing import traced_node
from backend.config import settings
from backend.models.enums import ANGLE_COUNTS, ContentType


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, timeout=60)


def _get_scoring_llm() -> ChatOpenAI:
    # Scoring is a structured judgment, not a creative step. At default temperature
    # the model intermittently drops the thesis_fidelity field (reverting to the old
    # 4-axis schema) and picks off-thesis angles; temperature=0 makes it reliably
    # honor the schema + fidelity axis, which the fidelity gate depends on.
    return ChatOpenAI(
        model=settings.openai_model, api_key=settings.openai_api_key, timeout=60, temperature=0
    )


def _parse_json(text: str) -> list | dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(text)


def _usage(resp) -> dict:
    meta = getattr(resp, "usage_metadata", None) or {}
    return {
        "prompt_tokens": int(meta.get("input_tokens", 0) or 0),
        "completion_tokens": int(meta.get("output_tokens", 0) or 0),
    }


def _format_context(items: list[dict]) -> str:
    if not items:
        return "(no knowledge base context — rely on KEY FACTS only)"
    parts = []
    for i, item in enumerate(items, 1):
        parts.append(f"--- Document {i} ---\n{item.get('text', '')}")
    return "\n\n".join(parts)


def _bullets(items: list[str], placeholder: str = "(none)") -> str:
    return "\n".join(f"- {x}" for x in items) if items else placeholder


def _render_original_tweet_block(content_type: str, original_tweet_text: str) -> str:
    """Render the quoted tweet for QRT runs so angles respond to it; empty otherwise."""
    text = (original_tweet_text or "").strip()
    if content_type == ContentType.QUOTE_RETWEET and text:
        return (
            "\nQUOTED TWEET BEING RESPONDED TO (add genuine insight to / push back on "
            "this specific claim — do NOT summarize it):\n"
            f'"{text}"\n'
        )
    return "\n"


# Minimum thesis_fidelity an angle must clear to be preferred over off-thesis angles.
THESIS_FIDELITY_BAR = 7

_WORD_RE = re.compile(r"\w+")


def _num(a: dict, key: str) -> float:
    try:
        return float(a.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _fidelity_present(scored_angles: list[dict]) -> bool:
    """True only if every angle carries a numeric thesis_fidelity field.

    The scorer intermittently omits the field (reverting to the old 4-axis
    schema) even at temperature=0; when that happens the gate is blind, so we
    re-ask once before trusting it.
    """
    if not scored_angles:
        return False
    return all(
        isinstance(a, dict) and "thesis_fidelity" in a and a.get("thesis_fidelity") is not None
        for a in scored_angles
    )


def _headline_overlap(angle_text: str, topic_headline: str) -> float:
    """Jaccard word overlap — a deterministic, drift-resistant proxy for fidelity."""
    aw = set(_WORD_RE.findall((angle_text or "").lower()))
    hw = set(_WORD_RE.findall((topic_headline or "").lower()))
    if not aw or not hw:
        return 0.0
    return len(aw & hw) / len(aw | hw)


def _fidelity_gate(scored_angles: list[dict], llm_selected_idx: int, topic_headline: str) -> int:
    """Pick the highest-total_score angle whose thesis_fidelity >= bar.

    When no angle clears the bar (or the scorer dropped the fidelity field
    entirely), fall back to the angle most lexically faithful to the topic
    headline — NOT to the raw LLM pick, which is exactly what drifts. Missing
    thesis_fidelity is treated as 0 so the gate never crashes. Ties broken by
    hook_strength, matching the scoring prompt's tie-break rule.
    """
    eligible = [
        i for i, a in enumerate(scored_angles)
        if isinstance(a, dict) and _num(a, "thesis_fidelity") >= THESIS_FIDELITY_BAR
    ]
    if eligible:
        return max(
            eligible,
            key=lambda i: (_num(scored_angles[i], "total_score"), _num(scored_angles[i], "hook_strength")),
        )
    # Nothing cleared the bar — choose the most headline-faithful angle if that
    # signal is meaningful; otherwise defer to the LLM's bounds-checked pick.
    if topic_headline.strip():
        scored_overlap = [
            (i, _headline_overlap(a.get("angle_text", ""), topic_headline))
            for i, a in enumerate(scored_angles) if isinstance(a, dict)
        ]
        best_i, best_ov = max(scored_overlap, key=lambda t: t[1], default=(llm_selected_idx, 0.0))
        if best_ov > 0:
            return best_i
    return llm_selected_idx


def _angle_count_for(content_type: str) -> int:
    try:
        return ANGLE_COUNTS[ContentType(content_type)]
    except ValueError:
        return 5


def _fallback_angles(state: dict) -> list[dict]:
    seeds = state.get("angle_seeds") or []
    if seeds:
        return [{
            "angle_text": seeds[0],
            "angle_type": "synthesis",
            "why_it_works": "fallback from upstream angle_seeds",
        }]
    headline = state.get("topic_headline") or state.get("user_topic", "")
    return [{
        "angle_text": headline,
        "angle_type": "synthesis",
        "why_it_works": "fallback from topic_headline",
    }]


@traced_node("angle")
async def angle_node(state: dict, config: dict | None = None) -> dict:
    llm = _get_llm()
    scoring_llm = _get_scoring_llm()
    content_type = state.get("content_type", "tweet")
    rag_context = state.get("rag_context", []) or []

    topic_headline = state.get("topic_headline", "") or state.get("user_topic", "")
    key_facts = state.get("key_facts", []) or []
    tensions = state.get("tensions", []) or []
    angle_seeds = state.get("angle_seeds", []) or []
    audience_context = state.get("audience_context", "") or "(none)"
    original_tweet_block = _render_original_tweet_block(
        content_type, state.get("original_tweet_text", "")
    )

    angle_count = _angle_count_for(content_type)

    prompt_tokens = 0
    completion_tokens = 0

    resp = await llm.ainvoke(
        ANGLE_GENERATION_PROMPT.format(
            topic_headline=topic_headline or "(none)",
            original_tweet_block=original_tweet_block,
            key_facts=_bullets(key_facts),
            tensions=_bullets(tensions),
            angle_seeds=_bullets(angle_seeds),
            audience_context=audience_context,
            context_docs=_format_context(rag_context),
            content_type=content_type,
            angle_count=angle_count,
        )
    )
    u = _usage(resp)
    prompt_tokens += u["prompt_tokens"]
    completion_tokens += u["completion_tokens"]

    try:
        angles = _parse_json(resp.content)
        if not isinstance(angles, list) or not angles:
            angles = _fallback_angles(state)
    except Exception:
        angles = _fallback_angles(state)

    scoring_prompt = ANGLE_SCORING_PROMPT.format(
        content_type=content_type,
        topic_headline=topic_headline or "(none)",
        key_facts=_bullets(key_facts),
        angles_json=json.dumps(angles, indent=2),
    )
    resp2 = await scoring_llm.ainvoke(scoring_prompt)
    u = _usage(resp2)
    prompt_tokens += u["prompt_tokens"]
    completion_tokens += u["completion_tokens"]

    def _parse_scoring(content):
        try:
            sc = _parse_json(content)
            sa = sc.get("scored_angles", angles)
            idx = int(sc.get("selected_index", 0))
            if idx < 0 or idx >= len(sa):
                idx = 0
            return sa, idx, sc.get("selection_rationale", "")
        except Exception:
            return angles, 0, ""

    scored_angles, selected_idx, rationale = _parse_scoring(resp2.content)

    # The scorer occasionally drops thesis_fidelity entirely (reverting to the old
    # 4-axis schema), which blinds the gate. Re-ask once with an explicit reminder
    # before trusting the scores.
    if not _fidelity_present(scored_angles):
        resp2b = await scoring_llm.ainvoke(
            scoring_prompt
            + "\n\nCRITICAL: every angle MUST include an integer \"thesis_fidelity\" "
              "(1-10) field. Do not omit it. Re-score now."
        )
        u = _usage(resp2b)
        prompt_tokens += u["prompt_tokens"]
        completion_tokens += u["completion_tokens"]
        sa2, idx2, rat2 = _parse_scoring(resp2b.content)
        if _fidelity_present(sa2):
            scored_angles, selected_idx, rationale = sa2, idx2, rat2

    # Thesis-fidelity gate: prefer the highest-total on-thesis angle. When nothing
    # clears the bar (or fidelity is still missing), fall back to the most
    # headline-faithful angle — never the raw LLM pick, which is what drifts.
    if scored_angles:
        gated_idx = _fidelity_gate(scored_angles, selected_idx, topic_headline)
        if gated_idx != selected_idx:
            rationale = (
                f"[fidelity gate] overrode LLM pick (idx {selected_idx}) with "
                f"idx {gated_idx} for higher thesis fidelity. "
                + (rationale or "")
            ).strip()
            selected_idx = gated_idx

    for i, a in enumerate(scored_angles):
        a["selected"] = (i == selected_idx)

    selected = [scored_angles[selected_idx]] if scored_angles else angles[:1]

    strategy_note = ""
    if content_type == "thread" and len(scored_angles) > 1:
        supporting = [a for i, a in enumerate(scored_angles) if i != selected_idx][:2]
        strategy_note = f"PRIMARY ANGLE: {selected[0].get('angle_text', '')}\n"
        strategy_note += "SUPPORTING ANGLES FOR THREAD SEGMENTS:\n"
        for s in supporting:
            strategy_note += f"- {s.get('angle_text', '')}\n"

    return {
        "all_angles": scored_angles,
        "selected_angles": selected,
        "angle_strategy_note": strategy_note or rationale,
        "_trace_meta": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
    }
