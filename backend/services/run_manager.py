import asyncio
import time
import uuid
from typing import Optional

from pydantic import BaseModel, Field

from backend.agents.graph import NODE_ORDER
from backend.agents.tracing import compute_trace_summary
from backend.models.enums import RunStatus
from backend.models.state import PipelineState, create_initial_state


class RunRecord(BaseModel):
    run_id: str
    status: RunStatus = RunStatus.PENDING
    current_agent: str = "pending"
    created_at: float = Field(default_factory=time.time)
    finished_at: Optional[float] = None
    topic: str = ""
    content_type: str = ""
    final_content: Optional[str] = None
    final_state: Optional[dict] = None
    traces: list[dict] = Field(default_factory=list)
    trace_summary: dict = Field(default_factory=dict)
    draft_iteration: int = 0
    error: Optional[str] = None


def compute_progress(current_agent: str) -> int:
    if current_agent in ("pending", ""):
        return 0
    if current_agent == "done":
        return 100
    if current_agent == "failed":
        return -1
    try:
        idx = NODE_ORDER.index(current_agent)
        return int((idx / (len(NODE_ORDER) - 1)) * 100)
    except ValueError:
        return 0


class RunManager:
    def __init__(self):
        self._runs: dict[str, RunRecord] = {}
        self._lock = asyncio.Lock()

    async def create_run(
        self,
        topic: str,
        content_type: str,
        **kwargs,
    ) -> tuple[str, PipelineState]:
        run_id = str(uuid.uuid4())
        initial_state = create_initial_state(
            run_id=run_id,
            user_topic=topic,
            content_type=content_type,
            **kwargs,
        )

        record = RunRecord(
            run_id=run_id,
            topic=topic,
            content_type=content_type,
        )

        async with self._lock:
            self._runs[run_id] = record

        return run_id, initial_state

    async def mark_running(self, run_id: str):
        async with self._lock:
            record = self._runs.get(run_id)
            if record:
                record.status = RunStatus.RUNNING

    async def update_from_state(self, run_id: str, state: dict):
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                return
            record.current_agent = state.get("current_agent", record.current_agent)
            record.traces = state.get("traces", record.traces)
            record.draft_iteration = state.get("draft_iteration", record.draft_iteration)

    async def mark_completed(self, run_id: str, final_state: dict):
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                return
            record.status = RunStatus.COMPLETED
            record.finished_at = time.time()
            record.current_agent = "done"
            record.final_content = final_state.get("final_content", "")
            record.traces = final_state.get("traces", [])
            record.trace_summary = compute_trace_summary(record.traces)
            record.draft_iteration = final_state.get("draft_iteration", 0)
            record.final_state = {
                k: v for k, v in final_state.items()
                if k not in ("_trace_meta",)
            }

    async def mark_failed(self, run_id: str, error: str, partial_state: dict | None = None):
        async with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                return
            record.status = RunStatus.FAILED
            record.finished_at = time.time()
            record.error = error
            record.current_agent = "failed"
            if partial_state:
                record.traces = partial_state.get("traces", [])
                record.trace_summary = compute_trace_summary(record.traces)

    async def get_run(self, run_id: str) -> Optional[RunRecord]:
        async with self._lock:
            return self._runs.get(run_id)

    async def list_runs(self, limit: int = 20) -> list[RunRecord]:
        async with self._lock:
            runs = sorted(
                self._runs.values(),
                key=lambda r: r.created_at,
                reverse=True,
            )
            return runs[:limit]
