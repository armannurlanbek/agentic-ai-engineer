"""Structural checks shared by Draft Writer, Critic, Voice Reviewer, and the
e2e harness. Centralizing them guarantees that what the pipeline *enforces* is
exactly what the tests *verify* — the two can never drift apart.

All thresholds live in backend.models.enums (CHAR_LIMITS, WORD_BANDS,
SLOP_PHRASES, THREAD_*). This module only implements the logic.
"""
from __future__ import annotations

import re

from backend.models.enums import (
    CHAR_LIMITS,
    SLOP_PHRASES,
    THREAD_MIN_SEGMENTS,
    THREAD_SEGMENT_CHAR_LIMIT,
    WORD_BANDS,
    ContentType,
)

_HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
# A numbered segment marker: start-of-line (or start-of-string) "1/", "1.", "1)".
_SEGMENT_RE = re.compile(r"(?m)^\s*\(?(\d{1,2})\s*[/.)]")
_WORD_RE = re.compile(r"\S+")


def _as_ct(content_type) -> ContentType | None:
    if isinstance(content_type, ContentType):
        return content_type
    try:
        return ContentType(content_type)
    except (ValueError, TypeError):
        return None


def word_count(text: str) -> int:
    return len(_WORD_RE.findall(text or ""))


def thread_segments(text: str) -> list[str]:
    """Split a thread into its numbered segments. Returns segment bodies in order.

    Robust to segments separated by blank lines OR run together inline.
    """
    text = text or ""
    # Find all marker positions at line starts first.
    marks = list(_SEGMENT_RE.finditer(text))
    if len(marks) >= 2:
        segs = []
        for i, m in enumerate(marks):
            start = m.start()
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            segs.append(text[start:end].strip())
        return [s for s in segs if s]
    # Fallback: markers may be inline (e.g. "... 2/ ..."). Split on " N/" tokens.
    inline = re.split(r"(?:(?<=\s)|^)(\d{1,2})/\s", text)
    if len(inline) >= 3:
        # inline = [pre, num, body, num, body, ...]
        segs = []
        it = iter(inline[1:])
        for num, body in zip(it, it):
            segs.append(f"{num}/ {body.strip()}")
        return [s for s in segs if s]
    return [text.strip()] if text.strip() else []


def find_hashtags(text: str) -> list[str]:
    return [h.strip() for h in _HASHTAG_RE.findall(text or "")]


def find_slop(text: str) -> list[str]:
    low = (text or "").lower()
    return [p for p in SLOP_PHRASES if p in low]


def char_limit_for(content_type) -> int | None:
    ct = _as_ct(content_type)
    return CHAR_LIMITS.get(ct) if ct else None


def word_band_for(content_type):
    ct = _as_ct(content_type)
    return WORD_BANDS.get(ct) if ct else None


def structural_violations(content_type, text: str) -> list[str]:
    """Return a list of human-readable structural problems for this content type.

    Empty list == structurally clean. Used by the critic to force revision and by
    the voice reviewer to decide whether a length-fix pass is needed.
    """
    ct = _as_ct(content_type)
    text = text or ""
    problems: list[str] = []

    cap = CHAR_LIMITS.get(ct) if ct else None
    if cap is not None and len(text) > cap:
        problems.append(
            f"Exceeds the {cap}-character limit for {ct.value}: it is {len(text)} characters. "
            f"Cut at least {len(text) - cap} characters."
        )

    if ct == ContentType.THREAD:
        segs = thread_segments(text)
        if len(segs) < THREAD_MIN_SEGMENTS:
            problems.append(
                f"Thread has only {len(segs)} numbered segment(s); needs at least "
                f"{THREAD_MIN_SEGMENTS}. Number each tweet (1/, 2/, ...) on its own line, "
                f"separated by a blank line."
            )
        over = [(i + 1, len(s)) for i, s in enumerate(segs) if len(s) > THREAD_SEGMENT_CHAR_LIMIT]
        for idx, n in over:
            problems.append(f"Thread segment {idx} is {n} chars (> {THREAD_SEGMENT_CHAR_LIMIT}). Tighten it.")

    band = WORD_BANDS.get(ct) if ct else None
    if band:
        floor, _target, ceiling = band
        wc = word_count(text)
        if wc < floor:
            problems.append(
                f"Under length for {ct.value}: {wc} words, floor is {floor}. "
                f"Expand with concrete detail from KEY FACTS / KNOWLEDGE CONTEXT — "
                f"do not pad with filler."
            )
        elif wc > ceiling:
            problems.append(f"Over length for {ct.value}: {wc} words, ceiling is {ceiling}. Tighten.")

    if ct in (ContentType.TWEET, ContentType.QUOTE_RETWEET, ContentType.THREAD):
        tags = find_hashtags(text)
        if tags:
            problems.append(f"Remove hashtags ({', '.join(tags)}); they are not allowed in {ct.value}.")

    slop = find_slop(text)
    if slop:
        problems.append(f"Remove AI-slop phrasing: {', '.join(slop)}.")

    return problems


def truncate_to_char_limit(text: str, cap: int) -> str:
    """Last-resort hard truncation to <= cap chars, at a sentence then word boundary.

    Only used by the voice reviewer as a safety net after the LLM length-fix pass
    fails to comply — shipping a valid tweet beats shipping an over-limit one.
    """
    text = (text or "").strip()
    if len(text) <= cap:
        return text
    window = text[:cap]
    # Prefer ending at the last sentence boundary within the window.
    m = list(re.finditer(r"[.!?](?:\s|$)", window))
    if m and m[-1].end() >= cap * 0.6:
        return window[: m[-1].end()].strip()
    # Otherwise cut at the last word boundary.
    cut = window.rsplit(" ", 1)[0].strip()
    return (cut or window).strip()
