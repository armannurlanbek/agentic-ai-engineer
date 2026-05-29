"""Bulk-fetch posts from curated AI/tech sources and ingest into ChromaDB.

Usage:
  python scripts/bulk_ingest_sources.py --list
  python scripts/bulk_ingest_sources.py --kind voice --max-per-source 8
  python scripts/bulk_ingest_sources.py --kind all --upload --user-id default
  python scripts/bulk_ingest_sources.py --source karpathy --upload
  python scripts/bulk_ingest_sources.py --download-only            # write .md files, skip Chroma

What it does:
  1. Pulls recent posts from each source's RSS feed (or sitemap fallback)
  2. Fetches each article HTML, strips chrome, extracts main text
  3. Writes a tagged .md file to data/corpus/{kind}/{source}/
  4. Optionally ingests into ChromaDB with metadata:
       {source, source_slug, kind, content_type, url, published_at, title}

Tagging:
  kind          = "voice" | "context"
  content_type  = "essay" | "blog_post" | "research" | "newsletter"
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import httpx
from bs4 import BeautifulSoup

# Make backend importable when running as a script
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.rag.chroma_client import get_context_collection, get_voice_collection  # noqa: E402
from backend.rag.ingest import ingest_document  # noqa: E402


CORPUS_DIR = ROOT / "data" / "corpus"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 30.0
INTER_REQUEST_DELAY = 0.4  # seconds, be polite


@dataclass
class Source:
    slug: str
    name: str
    feed_url: str
    kind: str           # "voice" | "context"
    content_type: str   # "essay" | "blog_post" | "research" | "newsletter"
    notes: str = ""
    # Fallback when feed_url 404s or returns no entries: scrape this HTML index page
    # and treat every <a href> matching link_pattern as a post.
    index_url: str | None = None
    link_pattern: str | None = None


# Curated source list. Keep this small and high-signal — quality beats volume.
SOURCES: list[Source] = [
    # ── Voice: prose to emulate ───────────────────────────────────────────────
    Source(
        slug="karpathy",
        name="Andrej Karpathy",
        feed_url="https://karpathy.github.io/feed.xml",
        kind="voice",
        content_type="essay",
        notes="Gold-standard explainer voice. Few posts but each is dense.",
    ),
    Source(
        slug="simonw",
        name="Simon Willison",
        feed_url="https://simonwillison.net/atom/everything/",
        kind="voice",
        content_type="blog_post",
        notes="Daily, terse, LLM-focused. Will be lots — cap with --max-per-source.",
    ),
    Source(
        slug="huyenchip",
        name="Chip Huyen",
        feed_url="https://huyenchip.com/feed.xml",
        kind="voice",
        content_type="essay",
        notes="Systems thinking, ML engineering, long-form.",
    ),
    Source(
        slug="eugene_yan",
        name="Eugene Yan",
        feed_url="https://eugeneyan.com/rss/",
        kind="voice",
        content_type="essay",
        notes="ML systems, eval, patterns. Production-AI focus.",
    ),
    Source(
        slug="lilian_weng",
        name="Lilian Weng",
        feed_url="https://lilianweng.github.io/index.xml",
        kind="voice",
        content_type="essay",
        notes="Researcher-as-writer. Deep dives.",
    ),
    Source(
        slug="raschka",
        name="Sebastian Raschka",
        feed_url="https://magazine.sebastianraschka.com/feed",
        kind="voice",
        content_type="newsletter",
        notes="Teaching-driven ML writing.",
    ),
    Source(
        slug="swyx",
        name="swyx",
        feed_url="https://www.swyx.io/rss.xml",
        kind="voice",
        content_type="essay",
        notes="AI Engineer operator voice.",
    ),
    Source(
        slug="paulg",
        name="Paul Graham",
        feed_url="http://www.aaronsw.com/2002/feeds/pgessays.rss",
        kind="voice",
        content_type="essay",
        notes="Classic essay structure. Many AI/tech writers are diluted PG.",
    ),

    # ── Context: factual grounding ────────────────────────────────────────────
    Source(
        slug="anthropic_news",
        name="Anthropic News",
        feed_url="",
        index_url="https://www.anthropic.com/news",
        link_pattern=r"^https?://www\.anthropic\.com/news/[^/?#]+$",
        kind="context",
        content_type="research",
        notes="No RSS; scrape news index page.",
    ),
    # OpenAI removed — Cloudflare blocks programmatic access (TLS fingerprint).
    # Workaround: manually save 5-10 key announcement pages as .md under
    # data/corpus/context/openai_blog/ then they'll be picked up by a future
    # "ingest local folder" mode (not implemented in this script).
    Source(
        slug="arxiv_cs_ai",
        name="arXiv cs.AI (latest)",
        feed_url="https://rss.arxiv.org/rss/cs.AI",
        kind="context",
        content_type="research",
        notes="Recent AI paper abstracts — high specificity, primary-source material.",
    ),
    Source(
        slug="arxiv_cs_cl",
        name="arXiv cs.CL (latest)",
        feed_url="https://rss.arxiv.org/rss/cs.CL",
        kind="context",
        content_type="research",
        notes="Recent NLP/LLM paper abstracts.",
    ),
    Source(
        slug="import_ai",
        name="Import AI",
        feed_url="https://jack-clark.net/feed/",
        kind="context",
        content_type="newsletter",
        notes="Weekly AI policy + research roundup, deep archive.",
    ),
    Source(
        slug="latent_space",
        name="Latent Space",
        feed_url="https://www.latent.space/feed",
        kind="context",
        content_type="newsletter",
        notes="Practitioner conversations / podcast transcripts.",
    ),
    Source(
        slug="stratechery_free",
        name="Stratechery (free posts)",
        feed_url="https://stratechery.com/feed/",
        kind="context",
        content_type="newsletter",
        notes="Strategy lens. Only Monday articles are public.",
    ),
]


def slugify(value: str, max_len: int = 80) -> str:
    value = re.sub(r"[^\w\s-]", "", value.lower()).strip()
    value = re.sub(r"[-\s]+", "-", value)
    return value[:max_len].strip("-") or "untitled"


def short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]


def extract_main_text(html: str) -> str:
    """Pull the article body out of a page. Best-effort — tuned for blog/news layouts."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # Prefer semantic containers
    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"role": "main"})
        or soup.find("div", class_=re.compile(r"(post|article|content|entry|markdown)", re.I))
        or soup.body
        or soup
    )

    text = container.get_text(separator="\n", strip=True)
    lines = [ln for ln in (l.strip() for l in text.splitlines()) if ln]

    # Collapse runs of short interleaved lines into paragraphs
    out: list[str] = []
    buf: list[str] = []
    for ln in lines:
        if len(ln) < 80 and (not buf or len(buf[-1]) < 80):
            buf.append(ln)
        else:
            if buf:
                out.append(" ".join(buf))
                buf = []
            out.append(ln)
    if buf:
        out.append(" ".join(buf))

    return "\n\n".join(out)


async def fetch_feed_entries(source: Source, client: httpx.AsyncClient, max_entries: int) -> list[dict]:
    entries: list[dict] = []

    if source.feed_url:
        try:
            resp = await client.get(source.feed_url, follow_redirects=True)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.content)
            for e in parsed.entries[:max_entries]:
                url = e.get("link") or ""
                title = (e.get("title") or "").strip()
                published = e.get("published") or e.get("updated") or ""
                if not url:
                    continue
                entries.append({"url": url, "title": title, "published": published})
        except Exception as e:
            print(f"    ! feed fetch failed for {source.slug}: {e}")

    if entries:
        return entries

    if source.index_url and source.link_pattern:
        print(f"    -> falling back to HTML index: {source.index_url}")
        try:
            entries = await scrape_index_for_links(
                source.index_url, source.link_pattern, client, max_entries
            )
        except Exception as e:
            print(f"    ! index scrape failed for {source.slug}: {e}")

    return entries


async def scrape_index_for_links(
    index_url: str,
    link_pattern: str,
    client: httpx.AsyncClient,
    max_entries: int,
) -> list[dict]:
    resp = await client.get(index_url, follow_redirects=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    base = f"{urlparse(index_url).scheme}://{urlparse(index_url).hostname}"
    pat = re.compile(link_pattern)

    seen: set[str] = set()
    entries: list[dict] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("/"):
            href = base + href
        if not pat.match(href):
            continue
        if href in seen:
            continue
        seen.add(href)
        title = a.get_text(strip=True) or href.rsplit("/", 1)[-1]
        entries.append({"url": href, "title": title, "published": ""})
        if len(entries) >= max_entries:
            break
    return entries


async def fetch_article(url: str, client: httpx.AsyncClient) -> str:
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        return extract_main_text(resp.text)
    except Exception as e:
        print(f"    ! article fetch failed {url}: {e}")
        return ""


def write_markdown(source: Source, entry: dict, body: str) -> Path:
    out_dir = CORPUS_DIR / source.kind / source.slug
    out_dir.mkdir(parents=True, exist_ok=True)

    title_slug = slugify(entry["title"] or short_hash(entry["url"]))
    path = out_dir / f"{title_slug}-{short_hash(entry['url'])}.md"

    frontmatter = (
        "---\n"
        f"source: {source.name}\n"
        f"source_slug: {source.slug}\n"
        f"kind: {source.kind}\n"
        f"content_type: {source.content_type}\n"
        f"url: {entry['url']}\n"
        f"title: {entry['title']}\n"
        f"published: {entry['published']}\n"
        "---\n\n"
    )

    path.write_text(frontmatter + body, encoding="utf-8")
    return path


def file_id_for(source_slug: str, url: str) -> str:
    return f"{source_slug}_{short_hash(url)}"


async def ingest_to_chroma(source: Source, entry: dict, body: str, user_id: str) -> int:
    collection = (
        get_voice_collection(user_id)
        if source.kind == "voice"
        else get_context_collection(user_id)
    )
    fid = file_id_for(source.slug, entry["url"])
    extra = {
        "source": source.name,
        "source_slug": source.slug,
        "kind": source.kind,
        "content_type": source.content_type,
        "url": entry["url"],
        "title": entry["title"],
        "published": entry["published"],
    }
    return await ingest_document(
        text=body,
        file_id=fid,
        filename=f"{source.slug}/{entry['url']}",
        collection=collection,
        extra_metadata=extra,
    )


async def process_source(
    source: Source,
    client: httpx.AsyncClient,
    *,
    max_entries: int,
    upload: bool,
    user_id: str,
    download_only: bool,
) -> dict:
    print(f"\n[{source.slug}] {source.name}  ({source.kind} / {source.content_type})")
    entries = await fetch_feed_entries(source, client, max_entries)
    print(f"  feed entries: {len(entries)}")

    saved = 0
    chunks_total = 0
    for i, entry in enumerate(entries, 1):
        body = await fetch_article(entry["url"], client)
        if not body or len(body) < 400:
            print(f"  [{i}/{len(entries)}] SKIP (too short): {entry['title'][:60]}")
            continue

        path = write_markdown(source, entry, body)
        saved += 1
        chunks = 0
        if upload and not download_only:
            try:
                chunks = await ingest_to_chroma(source, entry, body, user_id)
                chunks_total += chunks
            except Exception as e:
                print(f"  [{i}/{len(entries)}] ingest failed: {e}")

        suffix = f" -> {chunks} chunks" if upload else ""
        print(f"  [{i}/{len(entries)}] saved: {path.name}{suffix}")
        await asyncio.sleep(INTER_REQUEST_DELAY)

    return {"source": source.slug, "saved": saved, "chunks": chunks_total}


async def run(
    kinds: set[str],
    only_sources: set[str] | None,
    max_per_source: int,
    upload: bool,
    user_id: str,
    download_only: bool,
) -> None:
    selected = [s for s in SOURCES if s.kind in kinds]
    if only_sources:
        selected = [s for s in selected if s.slug in only_sources]

    if not selected:
        print("No sources selected.")
        return

    print(f"Processing {len(selected)} source(s)  upload={upload}  user_id={user_id}")
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers=headers) as client:
        results = []
        for source in selected:
            r = await process_source(
                source,
                client,
                max_entries=max_per_source,
                upload=upload,
                user_id=user_id,
                download_only=download_only,
            )
            results.append(r)

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    total_files = sum(r["saved"] for r in results)
    total_chunks = sum(r["chunks"] for r in results)
    for r in results:
        print(f"  {r['source']:18s}  files={r['saved']:3d}  chunks={r['chunks']:4d}")
    print(f"  {'TOTAL':18s}  files={total_files:3d}  chunks={total_chunks:4d}")
    print(f"\nCorpus directory: {CORPUS_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Bulk-ingest curated AI/tech sources into ChromaDB")
    parser.add_argument("--list", action="store_true", help="List sources and exit")
    parser.add_argument("--kind", choices=["voice", "context", "all"], default="all")
    parser.add_argument("--source", action="append", default=[], help="Slug filter (repeatable)")
    parser.add_argument("--max-per-source", type=int, default=10)
    parser.add_argument("--upload", action="store_true", help="Ingest into ChromaDB (default: just download)")
    parser.add_argument("--user-id", default="default")
    parser.add_argument("--download-only", action="store_true", help="Force skip Chroma even with --upload")
    args = parser.parse_args()

    if args.list:
        print(f"{'slug':18s}  {'kind':8s}  {'type':12s}  source")
        print("-" * 80)
        for s in SOURCES:
            print(f"{s.slug:18s}  {s.kind:8s}  {s.content_type:12s}  {s.name}")
        return

    kinds = {"voice", "context"} if args.kind == "all" else {args.kind}
    only_sources = set(args.source) if args.source else None

    asyncio.run(run(
        kinds=kinds,
        only_sources=only_sources,
        max_per_source=args.max_per_source,
        upload=args.upload,
        user_id=args.user_id,
        download_only=args.download_only,
    ))


if __name__ == "__main__":
    main()
