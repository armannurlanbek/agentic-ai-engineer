import json

from langchain_openai import ChatOpenAI

from backend.agents.prompts.critic import CRITIC_PROMPT
from backend.agents.text_checks import structural_violations
from backend.agents.tracing import traced_node
from backend.config import settings


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, timeout=60)


def _parse_json(text: str) -> dict:
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


def _bullets(items: list[str], placeholder: str = "(none)") -> str:
    return "\n".join(f"- {x}" for x in items) if items else placeholder


@traced_node("critic")
async def critic_node(state: dict, config: dict | None = None) -> dict:
    llm = _get_llm()
    iteration = state.get("draft_iteration", 1)
    max_iterations = state.get("max_draft_iterations", 3)

    if iteration >= max_iterations:
        pass_threshold = 6.5
        min_criterion = 4
    else:
        pass_threshold = 7.0
        min_criterion = 5

    angle = ""
    if state.get("selected_angles"):
        angle = state["selected_angles"][0].get("angle_text", "")

    topic_headline = state.get("topic_headline") or state.get("user_topic", "") or "(none)"
    key_facts = _bullets(state.get("key_facts") or [])
    content_type = state.get("content_type", "tweet")
    current_draft = state.get("current_draft", "")

    resp = await llm.ainvoke(
        CRITIC_PROMPT.format(
            content_type=content_type,
            current_draft=current_draft,
            angle=angle,
            topic_headline=topic_headline,
            key_facts=key_facts,
            iteration=iteration,
            max_iterations=max_iterations,
            pass_threshold=pass_threshold,
            min_criterion=min_criterion,
        )
    )
    u = _usage(resp)

    try:
        verdict = _parse_json(resp.content)
    except Exception:
        verdict = {
            "approved": iteration >= max_iterations,
            "score": 0.0,
            "rubric_scores": {},
            "line_edits": [],
            "summary": "Critic JSON parse failed — pass-through with no signal.",
        }

    # Deterministic structural gate — code-authoritative, not trusting the LLM to
    # count characters/words. Objective violations (over char cap, under word floor,
    # hashtags, AI-slop) block approval and are injected as line edits so the
    # revision must fix them. We never force-approve a structurally-broken draft;
    # the loop instead exits on the iteration ceiling in should_continue_drafting.
    violations = structural_violations(content_type, current_draft)
    if violations:
        synthetic_edits = [
            {"location": "(whole draft)", "issue": v, "suggestion": "Fix this objective requirement before anything else."}
            for v in violations
        ]
        verdict["line_edits"] = synthetic_edits + (verdict.get("line_edits") or [])
        verdict["approved"] = False
        note = " STRUCTURAL ISSUES (block approval): " + " | ".join(violations)
        verdict["summary"] = (str(verdict.get("summary", "")) + note).strip()

    approved = bool(verdict.get("approved", False))

    return {
        "critic_verdict": verdict,
        "draft_passed": approved,
        "critic_feedback_history": [verdict],
        "_trace_meta": {
            "prompt_tokens": u["prompt_tokens"],
            "completion_tokens": u["completion_tokens"],
        },
    }
