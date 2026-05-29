from backend.rag.chroma_client import get_context_collection, get_voice_collection
from backend.rag.query import query_collection


async def query_voice_samples(
    query_text: str,
    user_id: str,
    n_results: int = 5,
) -> list[dict]:
    collection = get_voice_collection(user_id)
    return await query_collection(query_text, collection, n_results=n_results)


async def query_context_docs(
    query_text: str,
    user_id: str,
    n_results: int = 10,
    max_distance: float = 1.5,
) -> list[dict]:
    collection = get_context_collection(user_id)
    return await query_collection(
        query_text, collection, n_results=n_results, max_distance=max_distance
    )
