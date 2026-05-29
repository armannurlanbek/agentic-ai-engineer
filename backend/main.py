from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import health, pipeline, traces, upload

app = FastAPI(
    title="Content Engine",
    description="High-quality X/Twitter content generation via multi-agent LangGraph pipeline",
    version="1.0.0",
)

# CORS origins are env-configurable (ALLOWED_ORIGINS, comma-separated). Default "*"
# so the deployed frontend works immediately; credentials are only enabled when
# explicit origins are set (browsers reject credentials with a wildcard origin).
_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials="*" not in _origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(traces.router, prefix="/api", tags=["traces"])
