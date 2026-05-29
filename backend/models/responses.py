from typing import Any, Optional

from pydantic import BaseModel, Field


class GenerateResponse(BaseModel):
    run_id: str
    status: str
    message: str


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    current_agent: str
    progress_pct: int = 0
    final_content: Optional[str] = None
    draft_iteration: int = 0
    error: Optional[str] = None


class RunResultResponse(BaseModel):
    run_id: str
    status: str
    final_content: str = ""
    content_type: str = ""
    all_angles: list[dict] = Field(default_factory=list)
    selected_angles: list[dict] = Field(default_factory=list)
    draft_history: list[str] = Field(default_factory=list)
    critic_feedback_history: list[dict] = Field(default_factory=list)
    fact_check_results: list[dict] = Field(default_factory=list)
    voice_review: Optional[dict] = None
    traces: list[dict] = Field(default_factory=list)
    trace_summary: dict = Field(default_factory=dict)
    error: Optional[str] = None


class RunSummary(BaseModel):
    run_id: str
    status: str
    topic: str
    content_type: str
    created_at: float
    current_agent: str = ""


class TraceResponse(BaseModel):
    run_id: str
    entries: list[dict] = Field(default_factory=list)
    total_duration_ms: float = 0
    total_tokens: int = 0
    total_llm_calls: int = 0


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    chunks_stored: int


class UploadListItem(BaseModel):
    file_id: str
    filename: str
    upload_type: str
    chunk_count: int
    uploaded_at: float


class HealthResponse(BaseModel):
    status: str
    chroma: bool
    openai: bool
