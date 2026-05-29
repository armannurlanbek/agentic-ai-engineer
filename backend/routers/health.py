from fastapi import APIRouter

from backend.config import settings
from backend.models.responses import HealthResponse
from backend.rag.chroma_client import get_chroma_client

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    openai_ok = bool(settings.openai_api_key)
    chroma_ok = True
    chroma_error = None
    collections = None

    # Use the same client the pipeline uses, and report collection counts so a
    # "healthy" response also confirms the shipped corpus actually loaded.
    try:
        client = get_chroma_client()
        client.heartbeat()
        collections = {c.name: c.count() for c in client.list_collections()}
    except Exception as e:
        chroma_ok = False
        chroma_error = f"{type(e).__name__}: {e}"

    return HealthResponse(
        status="ok" if (chroma_ok and openai_ok) else "degraded",
        chroma=chroma_ok,
        openai=openai_ok,
        chroma_path=settings.chroma_persist_dir,
        chroma_error=chroma_error,
        collections=collections,
    )
