from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    tavily_api_key: str = ""
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    chroma_persist_dir: str = "./data/chroma_db"
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
