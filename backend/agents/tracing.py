import asyncio
import functools
import time
from typing import Any, Callable

from langchain_core.runnables import RunnableConfig

from backend.agents.errors import PipelineError
from backend.models.state import AgentTraceEntry

MAX_RETRIES = 2
RETRY_DELAY = 1.0


def _summarize(text: Any, max_len: int = 200) -> str:
    s = str(text)
    return s[:max_len] + "..." if len(s) > max_len else s


def traced_node(node_name: str):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(state: dict, config: RunnableConfig | None = None) -> dict:
            started_at = time.time()
            error_msg = None
            output_summary = ""
            prompt_tokens = 0
            completion_tokens = 0
            result: dict = {}

            last_error = None
            for attempt in range(MAX_RETRIES + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(state, config)
                    else:
                        result = func(state, config)

                    meta = result.pop("_trace_meta", {})
                    prompt_tokens = meta.get("prompt_tokens", 0)
                    completion_tokens = meta.get("completion_tokens", 0)

                    output_summary = _summarize(
                        result.get("final_content")
                        or result.get("current_draft")
                        or result.get("selected_topic_summary")
                        or result.get("chosen_angle")
                        or str(list(result.keys()))
                    )
                    last_error = None
                    break

                except PipelineError as exc:
                    last_error = exc
                    if exc.retryable and attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    error_msg = f"{type(exc).__name__}: {exc} (after {attempt + 1} attempts)"
                    result = {"errors": [f"[{node_name}] {error_msg}"]}
                    break

                except Exception as exc:
                    last_error = exc
                    error_msg = f"{type(exc).__name__}: {exc}"
                    result = {"errors": [f"[{node_name}] {error_msg}"]}
                    break

            finished_at = time.time()
            duration_ms = round((finished_at - started_at) * 1000, 2)

            trace_entry = AgentTraceEntry(
                node_name=node_name,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                input_summary=_summarize(state.get("user_topic", "")),
                output_summary=output_summary,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                error=error_msg,
            )

            result["traces"] = [trace_entry.model_dump()]
            result["current_agent"] = node_name

            if error_msg and last_error:
                raise last_error

            return result

        return wrapper
    return decorator


def compute_trace_summary(traces: list[dict]) -> dict:
    if not traces:
        return {"total_duration_ms": 0, "total_tokens": 0, "total_llm_calls": 0}

    return {
        "total_duration_ms": round(
            (traces[-1].get("finished_at", 0) - traces[0].get("started_at", 0)) * 1000, 2
        ),
        "total_tokens": sum(t.get("total_tokens", 0) for t in traces),
        "total_llm_calls": len([t for t in traces if t.get("total_tokens", 0) > 0]),
    }
