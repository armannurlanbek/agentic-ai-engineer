from fastapi import APIRouter, HTTPException

from backend.models.responses import TraceResponse
from backend.routers.pipeline import run_manager

router = APIRouter()


@router.get("/traces/{run_id}", response_model=TraceResponse)
async def get_trace(run_id: str):
    record = await run_manager.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Run not found")

    traces = record.traces
    total_duration = 0.0
    total_tokens = 0

    if traces:
        first = traces[0]
        last = traces[-1]
        total_duration = (last.get("finished_at", 0) - first.get("started_at", 0)) * 1000
        total_tokens = sum(t.get("total_tokens", 0) for t in traces)

    return TraceResponse(
        run_id=run_id,
        entries=traces,
        total_duration_ms=round(total_duration, 2),
        total_tokens=total_tokens,
        total_llm_calls=len([t for t in traces if t.get("total_tokens", 0) > 0]),
    )
