from fastapi import APIRouter

from backend.config import settings
from backend.models.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    chroma_ok = True
    openai_ok = bool(settings.openai_api_key)

    try:
        import chromadb
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        client.heartbeat()
    except Exception:
        chroma_ok = False

    return HealthResponse(
        status="ok" if (chroma_ok and openai_ok) else "degraded",
        chroma=chroma_ok,
        openai=openai_ok,
    )
