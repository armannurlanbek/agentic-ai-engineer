from pathlib import Path

from pydantic_settings import BaseSettings

# Anchor the vector store to the repo root, not the process CWD — Railway and other
# hosts may launch uvicorn from a different working directory, and a relative path
# would then silently create an empty DB instead of finding the shipped corpus.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CHROMA_DIR = str(_REPO_ROOT / "data" / "chroma_db")


class Settings(BaseSettings):
    openai_api_key: str = ""
    tavily_api_key: str = ""
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    chroma_persist_dir: str = _DEFAULT_CHROMA_DIR
    max_draft_iterations: int = 3
    tavily_search_depth: str = "advanced"
    # Comma-separated allowed CORS origins. Default "*" so the deployed frontend
    # works out of the box; set to the Vercel URL(s) in production to lock down.
    allowed_origins: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
