import chromadb
from chromadb.config import Settings

from backend.config import settings

_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def get_voice_collection(user_id: str) -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=f"voice_samples_{user_id}",
        metadata={"hnsw:space": "cosine"},
    )


def get_context_collection(user_id: str) -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=f"context_docs_{user_id}",
        metadata={"hnsw:space": "cosine"},
    )
