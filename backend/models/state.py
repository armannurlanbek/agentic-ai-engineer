from __future__ import annotations

import operator
import time
import uuid
from typing import Annotated, Any, Optional
from typing_extensions import TypedDict

from pydantic import BaseModel, Field

from backend.models.enums import ContentType


# ── Sub-models ──────────────────────────────────────────────────────────


class DiscoveredSource(BaseModel):
    url: str | None = None
    title: str
    snippet: str = ""
    full_text: str = ""
    source_type: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedContext(BaseModel):
    text: str
    source_file: str = ""
    collection: str = ""
    relevance_score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class Angle(BaseModel):
    angle_text: str
    angle_type: str = ""
    why_it_works: str = ""
    content_type_fit: float = Field(default=0, ge=0, le=5)
    score: float = Field(default=0, ge=0, le=40)
    selected: bool = False


class CriticVerdict(BaseModel):
    approved: bool
    score: float = Field(ge=0, le=10)
    rubric_scores: dict[str, float] = Field(default_factory=dict)
    line_edits: list[dict[str, str]] = Field(default_factory=list)
    summary: str = ""


class FactCheckResult(BaseModel):
    claim_text: str
    claim_type: str = ""
    verified: bool = False
    action: str = "keep"
    confidence: float = Field(default=0, ge=0, le=1)
    source: str = ""
    source_url: str | None = None
    evidence: str = ""


class VoiceReviewResult(BaseModel):
    style_profile: dict[str, Any] = Field(default_factory=dict)
    voice_match_score: float = Field(default=0, ge=0, le=1)
    adjustments_made: list[str] = Field(default_factory=list)
    final_content: str = ""


class AgentTraceEntry(BaseModel):
    node_name: str
    started_at: float
    finished_at: float
    duration_ms: float
    input_summary: str = ""
    output_summary: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── LangGraph State ────────────────────────────────────────────────────


class PipelineState(TypedDict, total=False):
    # User input (set once, never mutated)
    user_topic: str
    user_urls: list[str]
    content_type: str
    user_id: str
    voice_description: str
    target_length: str
    original_tweet_text: str

    # Discovery output
    discovered_sources: list[dict]
    selected_topic_summary: str
    discovery_search_queries: list[str]
    topic_headline: str
    key_facts: list[str]
    tensions: list[str]
    angle_seeds: list[str]
    audience_context: str

    # Retrieval output
    rag_context: list[dict]
    voice_samples: list[dict]

    # Angle output
    all_angles: list[dict]
    selected_angles: list[dict]
    angle_strategy_note: str

    # Draft/Critic loop
    current_draft: str
    draft_iteration: int
    max_draft_iterations: int
    critic_verdict: dict | None
    draft_passed: bool
    draft_history: Annotated[list[str], operator.add]
    critic_feedback_history: Annotated[list[dict], operator.add]

    # Fact Checker output
    fact_check_results: list[dict]
    post_factcheck_draft: str

    # Voice Reviewer output
    voice_review: dict | None
    final_content: str

    # Pipeline metadata
    run_id: str
    current_agent: str
    traces: Annotated[list[dict], operator.add]
    errors: Annotated[list[str], operator.add]
    status: str


def create_initial_state(
    *,
    run_id: str,
    user_topic: str,
    content_type: str,
    user_id: str = "default",
    user_urls: list[str] | None = None,
    voice_description: str = "",
    target_length: str = "medium",
    original_tweet_text: str = "",
    max_draft_iterations: int = 3,
) -> PipelineState:
    return PipelineState(
        user_topic=user_topic,
        user_urls=user_urls or [],
        content_type=content_type,
        user_id=user_id,
        voice_description=voice_description,
        target_length=target_length,
        original_tweet_text=original_tweet_text,
        discovered_sources=[],
        selected_topic_summary="",
        discovery_search_queries=[],
        topic_headline="",
        key_facts=[],
        tensions=[],
        angle_seeds=[],
        audience_context="",
        rag_context=[],
        voice_samples=[],
        all_angles=[],
        selected_angles=[],
        angle_strategy_note="",
        current_draft="",
        draft_iteration=0,
        max_draft_iterations=max_draft_iterations,
        critic_verdict=None,
        draft_passed=False,
        draft_history=[],
        critic_feedback_history=[],
        fact_check_results=[],
        post_factcheck_draft="",
        voice_review=None,
        final_content="",
        run_id=run_id,
        current_agent="pending",
        traces=[],
        errors=[],
        status="pending",
    )
