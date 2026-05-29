from tavily import TavilyClient

from backend.config import settings

_tavily_client: TavilyClient | None = None


def get_tavily_client() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=settings.tavily_api_key)
    return _tavily_client


async def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    client = get_tavily_client()
    response = client.search(
        query=query,
        search_depth=settings.tavily_search_depth,
        max_results=max_results,
    )
    results = []
    for r in response.get("results", []):
        results.append({
            "url": r.get("url", ""),
            "title": r.get("title", ""),
            "snippet": r.get("content", "")[:500],
            "full_text": r.get("content", ""),
            "source_type": "tavily_search",
        })
    return results
