import json

from langchain_openai import ChatOpenAI

from backend.agents.errors import LLMCallError
from backend.agents.prompts.discovery import (
    QUERY_CONSTRUCTION_PROMPT,
    TOPIC_INFERENCE_PROMPT,
    TOPIC_SUMMARY_PROMPT,
)
from backend.agents.tracing import traced_node
from backend.config import settings
from backend.models.enums import TAVILY_QUERY_COUNT, TOPIC_BRIEF_COUNTS, ContentType
from backend.tools.tavily_search import tavily_search
from backend.tools.url_scraper import fetch_url_content

MAX_SOURCES = 8
SNIPPET_OVERLAP_THRESHOLD = 0.8


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        timeout=60,
    )


def _parse_json(text: str) -> list | dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(text)


def _usage(resp) -> tuple[int, int]:
    meta = getattr(resp, "usage_metadata", None) or {}
    return int(meta.get("input_tokens", 0) or 0), int(meta.get("output_tokens", 0) or 0)


def _format_scraped_context(sources: list[dict]) -> str:
    working = [s for s in sources if s.get("source_type") != "user_url_failed" and s.get("snippet")]
    if not working:
        return "No URL context provided."
    parts = ["URL CONTEXT ALREADY GATHERED (do not duplicate these in your queries):"]
    for s in working[:5]:
        parts.append(f"- {s.get('title', '')}: {s.get('snippet', '')[:250]}")
    return "\n".join(parts)


def _snippet_overlap(a: str, b: str) -> float:
    """Jaccard over lowercased word sets — cheap near-duplicate check."""
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / max(len(wa | wb), 1)


def _dedupe_and_cap(sources: list[dict], cap: int = MAX_SOURCES) -> list[dict]:
    """Preserves input order. User URLs come first, then Tavily; we keep that priority."""
    kept: list[dict] = []
    seen_urls: set[str] = set()
    for s in sources:
        if s.get("source_type") == "user_url_failed":
            continue
        url = s.get("url") or ""
        if url and url in seen_urls:
            continue
        snippet = s.get("snippet", "") or ""
        if any(_snippet_overlap(snippet, k.get("snippet", "") or "") >= SNIPPET_OVERLAP_THRESHOLD for k in kept):
            continue
        kept.append(s)
        if url:
            seen_urls.add(url)
        if len(kept) >= cap:
            break
    return kept


def _render_original_tweet_block(content_type: str, original_tweet_text: str) -> str:
    """Render the quoted tweet for QRT runs; empty marker otherwise.

    Kept identical across the query + summary prompts so research engages the
    specific quoted claim instead of free-associating.
    """
    text = (original_tweet_text or "").strip()
    if content_type == ContentType.QUOTE_RETWEET and text:
        return (
            "\nQUOTED TWEET BEING RESPONDED TO (engage this specific claim directly):\n"
            f'"{text}"\n'
        )
    return "\n(not a quote retweet)\n"


def _render_summary_text(brief: dict, content_type: str) -> str:
    lines = [
        f"TOPIC: {brief.get('topic', '')}",
        f"CONTENT TYPE: {content_type}",
        "KEY FACTS:",
    ]
    for f in brief.get("key_facts", []):
        lines.append(f"- {f}")
    lines.append("TENSIONS:")
    for t in brief.get("tensions", []):
        lines.append(f"- {t}")
    lines.append("ANGLE SEEDS:")
    for s in brief.get("angle_seeds", []):
        lines.append(f"- {s}")
    lines.append(f"AUDIENCE CONTEXT: {brief.get('audience_context', '')}")
    return "\n".join(lines)


@traced_node("discovery")
async def discovery_node(state: dict, config: dict | None = None) -> dict:
    user_topic = state.get("user_topic", "")
    user_urls = state.get("user_urls", [])
    content_type = state.get("content_type", ContentType.TWEET)
    original_tweet_text = state.get("original_tweet_text", "")
    original_tweet_block = _render_original_tweet_block(content_type, original_tweet_text)
    llm = _get_llm()

    prompt_tokens = 0
    completion_tokens = 0

    raw_sources: list[dict] = []

    if user_urls:
        for url in user_urls:
            source = await fetch_url_content(url)
            raw_sources.append(source)

    has_topic = bool(user_topic.strip())

    if not has_topic and raw_sources:
        working_sources = [s for s in raw_sources if s["source_type"] != "user_url_failed"]
        if working_sources:
            sources_text = "\n\n".join(
                f"Title: {s['title']}\nContent: {s['snippet']}" for s in working_sources
            )
            resp = await llm.ainvoke(TOPIC_INFERENCE_PROMPT.format(sources_text=sources_text))
            user_topic = resp.content.strip()
            p, c = _usage(resp)
            prompt_tokens += p
            completion_tokens += c

    if not user_topic.strip():
        raise LLMCallError("discovery", "No topic provided and could not infer from URLs")

    query_count = TAVILY_QUERY_COUNT.get(content_type, 3)
    scraped_context = _format_scraped_context(raw_sources)

    try:
        resp = await llm.ainvoke(
            QUERY_CONSTRUCTION_PROMPT.format(
                user_topic=user_topic,
                content_type=content_type,
                query_count=query_count,
                scraped_context=scraped_context,
                original_tweet_block=original_tweet_block,
            )
        )
        queries = _parse_json(resp.content)
        p, c = _usage(resp)
        prompt_tokens += p
        completion_tokens += c
    except Exception:
        queries = [user_topic]

    search_queries: list[str] = []
    for q in queries[:query_count]:
        search_queries.append(q)
        try:
            results = await tavily_search(q, max_results=5)
            for r in results:
                if not any(s.get("url") == r["url"] for s in raw_sources if s.get("url")):
                    raw_sources.append(r)
        except Exception:
            pass

    if not raw_sources:
        raw_sources.append({
            "url": None,
            "title": "User Input",
            "snippet": user_topic,
            "full_text": user_topic,
            "source_type": "user_input",
        })

    sources = _dedupe_and_cap(raw_sources, cap=MAX_SOURCES)

    sources_for_summary = [
        {
            "url": s.get("url"),
            "title": s.get("title", ""),
            "snippet": (s.get("snippet", "") or "")[:400],
            "source_type": s.get("source_type", ""),
        }
        for s in sources
    ]

    fact_count, tension_count, seed_count = TOPIC_BRIEF_COUNTS.get(content_type, (3, 1, 2))

    resp = await llm.ainvoke(
        TOPIC_SUMMARY_PROMPT.format(
            content_type=content_type,
            user_topic=user_topic,
            sources_json=json.dumps(sources_for_summary, indent=2),
            fact_count=fact_count,
            tension_count=tension_count,
            seed_count=seed_count,
            original_tweet_block=original_tweet_block,
        )
    )
    p, c = _usage(resp)
    prompt_tokens += p
    completion_tokens += c

    try:
        brief = _parse_json(resp.content)
        if not isinstance(brief, dict):
            raise ValueError("brief is not a dict")
    except Exception:
        brief = {
            "topic": user_topic,
            "key_facts": [],
            "tensions": [],
            "angle_seeds": [],
            "audience_context": "",
        }

    topic_headline = str(brief.get("topic", user_topic)).strip()
    key_facts = [str(f).strip() for f in brief.get("key_facts", []) if str(f).strip()]
    tensions = [str(t).strip() for t in brief.get("tensions", []) if str(t).strip()]
    angle_seeds = [str(s).strip() for s in brief.get("angle_seeds", []) if str(s).strip()]
    audience_context = str(brief.get("audience_context", "")).strip()

    summary_text = _render_summary_text(
        {
            "topic": topic_headline,
            "key_facts": key_facts,
            "tensions": tensions,
            "angle_seeds": angle_seeds,
            "audience_context": audience_context,
        },
        content_type,
    )

    return {
        "discovered_sources": sources,
        "selected_topic_summary": summary_text,
        "discovery_search_queries": search_queries,
        "topic_headline": topic_headline,
        "key_facts": key_facts,
        "tensions": tensions,
        "angle_seeds": angle_seeds,
        "audience_context": audience_context,
        "_trace_meta": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        },
    }
