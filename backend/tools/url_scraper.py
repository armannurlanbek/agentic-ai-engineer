import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from backend.config import settings


def _is_twitter_url(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host in ("x.com", "twitter.com", "www.x.com", "www.twitter.com")


def _parse_tweet_url(url: str) -> tuple[str, str]:
    """Extract (username, tweet_id) from an X/Twitter URL."""
    match = re.search(r"(?:x\.com|twitter\.com)/(\w+)/status/(\d+)", url)
    if match:
        return match.group(1), match.group(2)
    return "", ""


async def _fetch_tweet_via_search(url: str) -> dict:
    """Search Tavily for the tweet content since X blocks direct scraping."""
    from tavily import TavilyClient

    username, tweet_id = _parse_tweet_url(url)
    if not username:
        return {
            "url": url,
            "title": url,
            "snippet": "[Could not parse X/Twitter URL]",
            "full_text": "",
            "source_type": "x_tweet_failed",
        }

    client = TavilyClient(api_key=settings.tavily_api_key)

    queries = [
        f"@{username} tweet {tweet_id}",
        f"site:x.com {username} {tweet_id}",
        f"{username} twitter status {tweet_id}",
    ]

    best_content = ""
    best_title = ""

    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
            )
            for r in response.get("results", []):
                content = r.get("content", "")
                result_url = r.get("url", "")
                if content and len(content) > len(best_content):
                    best_content = content
                    best_title = r.get("title", "")
        except Exception:
            continue

    if best_content:
        title = f"@{username}: {best_title}" if best_title else f"@{username} tweet"
        return {
            "url": url,
            "title": title,
            "snippet": best_content[:500],
            "full_text": best_content[:10000],
            "source_type": "x_tweet",
        }

    return {
        "url": url,
        "title": f"@{username} (tweet not found via search)",
        "snippet": f"[Could not retrieve tweet from @{username}. Paste the tweet text manually for best results.]",
        "full_text": "",
        "source_type": "x_tweet_failed",
    }


async def _fetch_generic_url(url: str, timeout: float = 15.0) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "ContentEngine/1.0"})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else url
        text = soup.get_text(separator="\n", strip=True)
        text = "\n".join(line for line in text.split("\n") if line.strip())

        return {
            "url": url,
            "title": title,
            "snippet": text[:500],
            "full_text": text[:10000],
            "source_type": "user_url",
        }
    except Exception as e:
        return {
            "url": url,
            "title": url,
            "snippet": f"[UNREACHABLE: {str(e)[:100]}]",
            "full_text": "",
            "source_type": "user_url_failed",
        }


async def fetch_url_content(url: str, timeout: float = 15.0) -> dict:
    if _is_twitter_url(url):
        return await _fetch_tweet_via_search(url)

    return await _fetch_generic_url(url, timeout)
