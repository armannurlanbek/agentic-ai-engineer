import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend.agents.graph import content_pipeline
from backend.models.requests import GenerateRequest
from backend.models.responses import (
    GenerateResponse,
    RunResultResponse,
    RunStatusResponse,
    RunSummary,
)
from backend.services.run_manager import RunManager, compute_progress

logger = logging.getLogger(__name__)

router = APIRouter()
run_manager = RunManager()


async def _execute_pipeline(run_id: str, initial_state: dict):
    await run_manager.mark_running(run_id)
    try:
        final_state = await content_pipeline.ainvoke(
            initial_state,
            config={
                "configurable": {"thread_id": run_id},
                "run_name": f"content-pipeline-{run_id[:8]}",
            },
        )
        await run_manager.mark_completed(run_id, final_state)
    except Exception as exc:
        logger.exception(f"Pipeline failed for run {run_id}")
        await run_manager.mark_failed(run_id, str(exc))


@router.post("/generate", response_model=GenerateResponse)
async def start_generation(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
):
    run_id, initial_state = await run_manager.create_run(
        topic=request.topic,
        content_type=request.content_type.value,
        user_id=request.user_id,
        user_urls=request.urls,
        voice_description=request.voice_description,
        target_length=request.target_length,
        original_tweet_text=request.original_tweet_text,
        max_draft_iterations=request.max_draft_iterations,
    )

    background_tasks.add_task(_execute_pipeline, run_id, initial_state)

    return GenerateResponse(
        run_id=run_id,
        status="pending",
        message="Pipeline started. Poll GET /api/runs/{run_id} for status.",
    )


@router.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run_status(run_id: str):
    record = await run_manager.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return RunStatusResponse(
        run_id=record.run_id,
        status=record.status.value,
        current_agent=record.current_agent,
        progress_pct=compute_progress(record.current_agent),
        final_content=record.final_content,
        draft_iteration=record.draft_iteration,
        error=record.error,
    )


@router.get("/runs/{run_id}/result", response_model=RunResultResponse)
async def get_run_result(run_id: str):
    record = await run_manager.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Run not found")

    fs = record.final_state or {}

    return RunResultResponse(
        run_id=record.run_id,
        status=record.status.value,
        final_content=record.final_content or "",
        content_type=record.content_type,
        all_angles=fs.get("all_angles", []),
        selected_angles=fs.get("selected_angles", []),
        draft_history=fs.get("draft_history", []),
        critic_feedback_history=fs.get("critic_feedback_history", []),
        fact_check_results=fs.get("fact_check_results", []),
        voice_review=fs.get("voice_review"),
        traces=record.traces,
        trace_summary=record.trace_summary,
        error=record.error,
    )


@router.get("/runs", response_model=list[RunSummary])
async def list_runs(limit: int = 20):
    records = await run_manager.list_runs(limit)
    return [
        RunSummary(
            run_id=r.run_id,
            status=r.status.value,
            topic=r.topic,
            content_type=r.content_type,
            created_at=r.created_at,
            current_agent=r.current_agent,
        )
        for r in records
    ]
