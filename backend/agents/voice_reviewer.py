import json
import re

from langchain_openai import ChatOpenAI

from backend.agents.prompts.voice_reviewer import (
    LENGTH_FIX_PROMPT,
    RESTORATION_PROMPT,
    STYLE_PROFILE_PROMPT,
    VOICE_ADJUSTMENT_PROMPT,
    VOICE_DESCRIPTION_BLOCK_TEMPLATE,
    default_profile_for,
)
from backend.agents.text_checks import (
    char_limit_for,
    find_hashtags,
    structural_violations,
    truncate_to_char_limit,
    word_count,
)
from backend.agents.tracing import traced_node
from backend.config import settings
from backend.models.enums import WORD_BANDS, ContentType


def _floor_for(content_type: str) -> int | None:
    try:
        return WORD_BANDS[ContentType(content_type)][0]
    except (ValueError, KeyError):
        return None


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, timeout=60)


def _parse_json(text: str) -> dict:
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


def _format_voice(items: list[dict]) -> str:
    if not items:
        return ""
    return "\n\n".join(f"--- Sample {i+1} ---\n{item.get('text', '')}" for i, item in enumerate(items))


# Anchors are the tokens that, if dropped, mean the claim's substance is gone:
# numbers (including %, $, decimals), and multi-letter capitalized words (proper
# nouns, acronyms). Paraphrasing is fine; losing these is not.
_NUMBER_RE = re.compile(r"\d[\d,.\-%]*")
_PROPER_RE = re.compile(r"\b[A-Z][A-Za-z0-9]{1,}\b")
_STOP_PROPER = {"The", "A", "An", "And", "Or", "But", "If", "When", "While", "This", "That", "These", "Those", "It", "Its", "I", "You", "We", "They"}


def _anchors_for(claim_text: str) -> list[str]:
    nums = _NUMBER_RE.findall(claim_text)
    propers = [w for w in _PROPER_RE.findall(claim_text) if w not in _STOP_PROPER]
    # de-dup, preserve order
    seen: set[str] = set()
    out: list[str] = []
    for tok in nums + propers:
        if tok not in seen:
            seen.add(tok)
            out.append(tok)
    return out


def _kept_claims(fact_check_results: list[dict]) -> list[dict]:
    return [r for r in (fact_check_results or []) if r.get("action") == "keep"]


def _missing_kept_claims(kept: list[dict], output_text: str) -> list[dict]:
    """A kept claim is 'missing' if ALL of its anchor tokens are absent from output.

    Matching is case-insensitive: the claim extractor often grabs a sentence
    fragment that starts with a capitalized word which appears lowercase in
    context (e.g. 'Economy,' vs 'the economy'), and we only care that the
    substance survived, not its casing."""
    low = output_text.lower()
    missing: list[dict] = []
    for claim in kept:
        anchors = _anchors_for(claim.get("claim_text", ""))
        if not anchors:
            continue  # no measurable anchors → can't tell, skip
        if not any(a.lower() in low for a in anchors):
            missing.append({**claim, "anchors": anchors})
    return missing


def _length_ratio(original: str, adjusted: str) -> float:
    o = max(len(original), 1)
    return len(adjusted) / o


_HASHTAG_STRIP_RE = re.compile(r"\s*#\w+")


def _strip_hashtags(text: str) -> str:
    """Deterministically remove hashtags (banned in tweet/qrt/thread). Safety net
    in case the LLM length-fix pass leaves one in."""
    cleaned = _HASHTAG_STRIP_RE.sub("", text)
    # collapse any double spaces the removal created, preserve newlines
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return cleaned.strip()


def _length_directive(content_type: str) -> str:
    cap = char_limit_for(content_type)
    if cap:
        return (
            f"The output MUST be {cap} characters or fewer — this is a {content_type}. "
            f"Never exceed {cap} characters."
        )
    floor = _floor_for(content_type)
    if floor:
        return (
            f"Stay within 92-112% of the input length and NEVER drop below {floor} words — "
            f"this is long-form {content_type}. Tighten wordiness, but do not cut substance."
        )
    return "Output must stay within 90-110% of the input length."


@traced_node("voice_reviewer")
async def voice_reviewer_node(state: dict, config: dict | None = None) -> dict:
    llm = _get_llm()
    draft = state.get("post_factcheck_draft", "") or state.get("current_draft", "")
    voice_samples = state.get("voice_samples", []) or []
    voice_description = (state.get("voice_description") or "").strip()
    content_type = state.get("content_type", "essay")
    fact_check_results = state.get("fact_check_results", []) or []

    prompt_tokens = 0
    completion_tokens = 0

    # ── Step 1: style profile ─────────────────────────────────────────
    if voice_samples:
        description_block = (
            VOICE_DESCRIPTION_BLOCK_TEMPLATE.format(voice_description=voice_description)
            if voice_description else ""
        )
        resp = await llm.ainvoke(
            STYLE_PROFILE_PROMPT.format(
                voice_samples=_format_voice(voice_samples),
                voice_description_block=description_block,
            )
        )
        i, o = _usage(resp)
        prompt_tokens += i
        completion_tokens += o
        try:
            style_profile = _parse_json(resp.content)
            if not isinstance(style_profile, dict):
                style_profile = default_profile_for(content_type)
        except Exception:
            style_profile = default_profile_for(content_type)
    elif voice_description:
        style_profile = default_profile_for(content_type)
        # blend the description as an explicit tone marker
        markers = list(style_profile.get("tone_markers", []))
        if voice_description not in markers:
            markers.append(voice_description)
        style_profile["tone_markers"] = markers
    else:
        style_profile = default_profile_for(content_type)

    # ── Step 2: voice adjustment ─────────────────────────────────────
    kept = _kept_claims(fact_check_results)
    if kept:
        must_preserve_block = "\n".join(
            f"- {c.get('claim_text', '').strip()}" for c in kept if c.get("claim_text")
        )
    else:
        must_preserve_block = "(none flagged — apply voice adjustments freely while preserving the draft's substantive content)"

    voice_text = _format_voice(voice_samples) if voice_samples else "No samples available."

    resp = await llm.ainvoke(
        VOICE_ADJUSTMENT_PROMPT.format(
            draft=draft,
            style_profile_json=json.dumps(style_profile, indent=2),
            voice_samples=voice_text,
            must_preserve_block=must_preserve_block,
            length_directive=_length_directive(content_type),
        )
    )
    i, o = _usage(resp)
    prompt_tokens += i
    completion_tokens += o

    adjustments_made: list[str] = []
    try:
        parsed = _parse_json(resp.content)
        final_content = (parsed.get("adjusted_draft") or "").strip()
        adj = parsed.get("adjustments_made") or []
        if isinstance(adj, list):
            adjustments_made = [str(x) for x in adj if x]
        if not final_content:
            raise ValueError("empty adjusted_draft")
    except Exception:
        # if JSON parse fails entirely, fall back to raw content (better than nothing)
        final_content = resp.content.strip()
        adjustments_made = []

    # ── Step 3: preservation check + targeted restoration ────────────
    missing = _missing_kept_claims(kept, final_content)
    restoration_attempted = False
    if missing:
        restoration_attempted = True
        missing_block = "\n".join(
            f"- {m.get('claim_text', '').strip()}  [anchors: {', '.join(m.get('anchors', []))}]"
            for m in missing
        )
        resp = await llm.ainvoke(
            RESTORATION_PROMPT.format(
                draft=final_content,
                missing_claims_block=missing_block,
            )
        )
        i, o = _usage(resp)
        prompt_tokens += i
        completion_tokens += o
        try:
            parsed = _parse_json(resp.content)
            restored = (parsed.get("adjusted_draft") or "").strip()
            adj = parsed.get("adjustments_made") or []
            if restored:
                final_content = restored
            if isinstance(adj, list):
                adjustments_made.extend(str(x) for x in adj if x)
        except Exception:
            pass  # keep current final_content
        # re-check; whatever's still missing gets reported but we don't loop
        missing = _missing_kept_claims(kept, final_content)

    # ── Step 3.5: structural enforcement (length cap/floor, hashtags, slop) ──
    # The voice pass can inflate short content (a tweet ballooning past 280) or
    # leave slop/hashtags. Drive a single corrective pass off the shared structural
    # checks, then fall back to deterministic safety nets the LLM can't bypass.
    structural_problems = structural_violations(content_type, final_content)
    length_fix_attempted = False
    if structural_problems:
        length_fix_attempted = True
        resp = await llm.ainvoke(
            LENGTH_FIX_PROMPT.format(
                content_type=content_type,
                current_len=len(final_content),
                current_words=word_count(final_content),
                draft=final_content,
                length_problem="; ".join(structural_problems),
                must_preserve_block=must_preserve_block,
            )
        )
        i, o = _usage(resp)
        prompt_tokens += i
        completion_tokens += o
        try:
            parsed = _parse_json(resp.content)
            fixed = (parsed.get("adjusted_draft") or "").strip()
            adj = parsed.get("adjustments_made") or []
            if fixed:
                final_content = fixed
            if isinstance(adj, list):
                adjustments_made.extend(str(x) for x in adj if x)
        except Exception:
            pass  # keep current final_content

    # Deterministic safety nets — hard guarantees, not LLM goodwill:
    if content_type in ("tweet", "quote_retweet", "thread") and find_hashtags(final_content):
        final_content = _strip_hashtags(final_content)
        adjustments_made.append("Removed hashtags (not allowed in this format).")
    cap = char_limit_for(content_type)
    if cap and len(final_content) > cap:
        final_content = truncate_to_char_limit(final_content, cap)
        adjustments_made.append(f"Hard-truncated to <= {cap} characters (length-fix pass did not comply).")

    # Long-form guard: a single-call voice rewrite tends to COMPRESS long content
    # (gpt-4o's output-length ceiling), so it can silently drop an article below its
    # floor. The pre-voice fact-checked draft was already expanded past the floor and
    # already written with voice-sample guidance — a floor-meeting draft beats an
    # over-compressed one, so revert when voice shrank it below the floor.
    floor = _floor_for(content_type)
    if floor and word_count(final_content) < floor and word_count(draft) > word_count(final_content):
        final_content = draft
        adjustments_made.append(
            f"Reverted to pre-voice draft to preserve >= {floor}-word length "
            f"(voice pass compressed it below the floor)."
        )

    # ── Step 4: real signals (computed AFTER all length edits) ────────
    missing = _missing_kept_claims(kept, final_content)
    residual_violations = structural_violations(content_type, final_content)
    length_ratio = _length_ratio(draft, final_content)
    floor = _floor_for(content_type)
    if cap:
        length_in_bounds = len(final_content) <= cap
    elif floor:
        # long-form: the real contract is the absolute word floor, not ratio-vs-draft
        length_in_bounds = word_count(final_content) >= floor
    else:
        # thread: the real contract is per-segment caps + min segment count (both in
        # structural_violations); total length-vs-draft is soft, and polishing a thread
        # legitimately tightens it, so allow a wide band.
        length_in_bounds = 0.75 <= length_ratio <= 1.25
    structurally_clean = not residual_violations
    kept_total = len([k for k in kept if _anchors_for(k.get("claim_text", ""))])
    kept_preserved = kept_total - len(missing)
    preservation_ratio = (kept_preserved / kept_total) if kept_total else 1.0
    # blended signal: claim preservation dominates; length + structural cleanliness fill the rest
    voice_match_score = round(
        0.6 * preservation_ratio
        + 0.2 * (1.0 if length_in_bounds else 0.0)
        + 0.2 * (1.0 if structurally_clean else 0.0),
        3,
    )

    return {
        "voice_review": {
            "style_profile": style_profile,
            "voice_match_score": voice_match_score,
            "adjustments_made": adjustments_made,
            "char_count": len(final_content),
            "word_count": word_count(final_content),
            "length_ratio": round(length_ratio, 3),
            "length_in_bounds": length_in_bounds,
            "structurally_clean": structurally_clean,
            "residual_violations": residual_violations,
            "length_fix_attempted": length_fix_attempted,
            "kept_claims_total": kept_total,
            "kept_claims_preserved": kept_preserved,
            "missing_kept_claims": [m.get("claim_text", "") for m in missing],
            "restoration_attempted": restoration_attempted,
        },
        "final_content": final_content,
        "status": "completed",
        "_trace_meta": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
    }
