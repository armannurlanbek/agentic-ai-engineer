from langchain_openai import ChatOpenAI

from backend.agents.prompts.draft_writer import (
    EXPANSION_PROMPT,
    FIRST_DRAFT_ARTICLE,
    FIRST_DRAFT_ESSAY,
    FIRST_DRAFT_QRT,
    FIRST_DRAFT_THREAD,
    FIRST_DRAFT_TWEET,
    NO_SLOP_RULE,
    REVISION_PROMPT,
)
from backend.agents.text_checks import structural_violations, word_count
from backend.agents.tracing import traced_node
from backend.config import settings
from backend.models.enums import WORD_BANDS, ContentType

# Long-form drafts that come back under the word floor get up to this many
# dedicated expansion passes — gpt-4o reliably under-produces on a single shot
# and "expand" beats "rewrite" for actually growing length.
MAX_EXPANSION_PASSES = 2


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, timeout=90)


def _usage(resp) -> dict:
    meta = getattr(resp, "usage_metadata", None) or {}
    return {
        "prompt_tokens": int(meta.get("input_tokens", 0) or 0),
        "completion_tokens": int(meta.get("output_tokens", 0) or 0),
    }


def _format_context(items: list[dict]) -> str:
    if not items:
        return "(no knowledge base context available)"
    return "\n\n".join(f"--- Document {i} ---\n{item.get('text', '')}" for i, item in enumerate(items[:5], 1))


def _format_voice(items: list[dict]) -> str:
    if not items:
        return "(no voice samples — use natural, confident writing)"
    return "\n\n".join(f"--- Sample {i} ---\n{item.get('text', '')}" for i, item in enumerate(items[:3], 1))


def _bullets(items: list[str], placeholder: str = "(none)") -> str:
    return "\n".join(f"- {x}" for x in items) if items else placeholder


def _get_thread_length(target_length: str) -> int:
    return {"short": 5, "medium": 8, "long": 12}.get(target_length, 8)


def _word_floor_target(content_type: str, target_length: str) -> tuple[int, int]:
    """Return (floor, target_words) for long-form. Floor comes from the shared
    WORD_BANDS contract the critic enforces; target scales with target_length."""
    try:
        floor, target, ceiling = WORD_BANDS[ContentType(content_type)]
    except (ValueError, KeyError):
        floor, target, ceiling = (700, 1100, 1900)
    scaled = {"short": floor + (target - floor) // 2, "medium": target, "long": ceiling}
    return floor, scaled.get(target_length, target)


def _common_fields(state: dict) -> dict:
    return {
        "topic_headline": state.get("topic_headline") or state.get("user_topic", "") or "(none)",
        "key_facts": _bullets(state.get("key_facts") or []),
        "tensions": _bullets(state.get("tensions") or []),
        "audience_context": state.get("audience_context") or "(none)",
        "voice_samples": _format_voice(state.get("voice_samples") or []),
        "context_docs": _format_context(state.get("rag_context") or []),
        "no_slop": NO_SLOP_RULE,
    }


def _build_first_draft_prompt(state: dict) -> str:
    content_type = state.get("content_type", ContentType.TWEET)
    angle = state["selected_angles"][0].get("angle_text", "") if state.get("selected_angles") else ""
    target_length = state.get("target_length", "medium")
    common = _common_fields(state)

    if content_type == ContentType.TWEET:
        return FIRST_DRAFT_TWEET.format(angle=angle, **common)

    if content_type == ContentType.QUOTE_RETWEET:
        # QRT only uses a subset of common fields
        return FIRST_DRAFT_QRT.format(
            original_tweet=state.get("original_tweet_text", ""),
            angle=angle,
            topic_headline=common["topic_headline"],
            key_facts=common["key_facts"],
            voice_samples=common["voice_samples"],
            no_slop=common["no_slop"],
        )

    if content_type == ContentType.THREAD:
        length = _get_thread_length(target_length)
        return FIRST_DRAFT_THREAD.format(
            angle=angle,
            strategy_note=state.get("angle_strategy_note", "") or "(none)",
            thread_length=length,
            body_end=length - 2,
            climax=length - 1,
            close=length,
            **common,
        )

    if content_type == ContentType.ESSAY:
        floor, wc = _word_floor_target(content_type, target_length)
        return FIRST_DRAFT_ESSAY.format(angle=angle, word_count=wc, word_floor=floor, **common)

    # Article fallback
    floor, wc = _word_floor_target(content_type, target_length)
    return FIRST_DRAFT_ARTICLE.format(angle=angle, word_count=wc, word_floor=floor, **common)


def _build_revision_prompt(state: dict) -> str:
    feedback = state.get("critic_verdict") or {}
    iteration = state.get("draft_iteration", 1)

    line_edits = feedback.get("line_edits", []) or []
    edits_text = "\n".join(
        f"- Location: \"{e.get('location', '')}\"\n  Issue: {e.get('issue', '')}\n  Suggestion: {e.get('suggestion', '')}"
        for e in line_edits
    ) or "(no specific line edits)"

    urgency = "Focus on the highest-impact changes first."
    if iteration >= 2:
        urgency = "This is your FINAL revision. Make it count. Address remaining weaknesses aggressively."

    angle = ""
    if state.get("selected_angles"):
        angle = state["selected_angles"][0].get("angle_text", "")

    common = _common_fields(state)

    content_type = state.get("content_type", "tweet")
    current_draft = state.get("current_draft", "")
    # Objective, code-computed problems with the current draft (length, char cap,
    # hashtags, slop). These are non-negotiable and lead the revision.
    violations = structural_violations(content_type, current_draft)
    hard_requirements = "\n".join(f"- {v}" for v in violations) or "(none — draft is structurally valid)"

    return REVISION_PROMPT.format(
        content_type=content_type,
        current_draft=current_draft,
        score=feedback.get("score", 0),
        feedback_summary=feedback.get("summary", ""),
        line_edits=edits_text,
        hard_requirements=hard_requirements,
        angle=angle,
        topic_headline=common["topic_headline"],
        key_facts=common["key_facts"],
        voice_samples=common["voice_samples"],
        context_docs=common["context_docs"],
        no_slop=common["no_slop"],
        urgency_note=urgency,
    )


def _word_floor(content_type: str) -> int | None:
    try:
        return WORD_BANDS[ContentType(content_type)][0]
    except (ValueError, KeyError):
        return None


async def _expand_to_floor(llm, draft: str, content_type: str, state: dict) -> tuple[str, int, int]:
    """If a long-form draft is under its word floor, add new substantive sections
    until it clears the floor (bounded). Returns (draft, prompt_tokens, completion_tokens)."""
    floor = _word_floor(content_type)
    if floor is None:
        return draft, 0, 0
    common = _common_fields(state)
    p_tot = c_tot = 0
    passes = 0
    while word_count(draft) < floor and passes < MAX_EXPANSION_PASSES:
        resp = await llm.ainvoke(
            EXPANSION_PROMPT.format(
                content_type=content_type,
                current_words=word_count(draft),
                word_floor=floor,
                draft=draft,
                key_facts=common["key_facts"],
                context_docs=common["context_docs"],
                no_slop=common["no_slop"],
            )
        )
        u = _usage(resp)
        p_tot += u["prompt_tokens"]
        c_tot += u["completion_tokens"]
        expanded = resp.content.strip()
        # only accept if it actually grew — otherwise stop trying
        if word_count(expanded) > word_count(draft):
            draft = expanded
        else:
            break
        passes += 1
    return draft, p_tot, c_tot


@traced_node("draft_writer")
async def draft_writer_node(state: dict, config: dict | None = None) -> dict:
    llm = _get_llm()
    iteration = state.get("draft_iteration", 0)
    is_first_draft = iteration == 0
    content_type = state.get("content_type", ContentType.TWEET)

    prompt = _build_first_draft_prompt(state) if is_first_draft else _build_revision_prompt(state)
    resp = await llm.ainvoke(prompt)
    new_draft = resp.content.strip()
    u = _usage(resp)
    prompt_tokens = u["prompt_tokens"]
    completion_tokens = u["completion_tokens"]

    # Long-form: guarantee the draft clears its word floor before handoff, so the
    # critic/fact-checker/voice stages never have to manufacture length.
    new_draft, p_exp, c_exp = await _expand_to_floor(llm, new_draft, content_type, state)
    prompt_tokens += p_exp
    completion_tokens += c_exp

    return {
        "current_draft": new_draft,
        "draft_iteration": iteration + 1,
        "draft_history": [new_draft],
        "_trace_meta": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
    }
