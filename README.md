# Content Engine — Multi-Agent X/Twitter Content Generator

A taste-driven content generation tool for X/Twitter built on a **7-agent LangGraph
pipeline**. It turns a topic (or a tweet to quote, or URLs) into tweets, quote retweets,
threads, essays, or research articles — optimizing for insight density, original angles,
authentic voice, and grounded facts rather than generic AI slop.

## Pipeline

```
Discovery → Retrieval (RAG) → Angle → Draft Writer ⇄ Critic → Fact Checker → Voice Reviewer
```

| Agent | Role |
|---|---|
| **Discovery** | Tavily research + URL scraping → a thesis-anchored brief (topic, key facts, tensions, angle seeds) |
| **Retrieval** | ChromaDB RAG: separate voice-sample and context queries, deduped + source-diversified |
| **Angle** | Generates candidate angles, then scores them on hook/defensibility/originality/shareability + a **thesis-fidelity gate** that kills topic drift |
| **Draft Writer ⇄ Critic** | Content-type-specific drafting with an 8-axis critic loop (max 3 iterations, plateau + structural gates); long-form uses an additive expansion loop to hit word floors |
| **Fact Checker** | Per-claim two-tier verification (RAG → Tavily web), parallelized; keeps / softens / removes claims with evidence |
| **Voice Reviewer** | Applies a learned style profile, enforces length contracts, strips slop/hashtags, and preserves verified claims |

Structural contracts (character caps, word floors, banned-slop list, thread formatting)
live in `backend/models/enums.py` and `backend/agents/text_checks.py` — enforced by the
agents **and** verified by the test harness from the same source of truth.

## Tech Stack

- **Orchestration:** LangGraph `StateGraph` + `MemorySaver`
- **LLM:** OpenAI (gpt-4o) via `langchain-openai`
- **RAG:** ChromaDB (persistent) + `text-embedding-3-small`
- **Search:** Tavily (`search_depth=advanced`)
- **Backend:** FastAPI + uvicorn (async); background-task run manager with polling
- **Frontend:** Next.js + Tailwind

## Repository Layout

```
backend/        FastAPI app, agents, prompts, tools, RAG, routers
frontend/       Next.js app (generate UI, traces, uploads)
data/corpus/    Source knowledge corpus (168 docs: arXiv, Anthropic, Import AI, etc.)
data/chroma_db/ Prebuilt embeddings — the app ships with corpus knowledge ready to use
scripts/        Corpus bulk-ingestion
test_*.py       Per-agent + end-to-end evaluation harness (test_e2e.py)
traces/         Exported agent traces from evaluation runs
```

## Local Development

```bash
# Backend
python -m venv venv && source venv/Scripts/activate   # Windows; use bin/activate on *nix
pip install -r requirements.txt
cp .env.example .env                                   # add OPENAI_API_KEY + TAVILY_API_KEY
uvicorn backend.main:app --reload                      # http://localhost:8000

# Frontend
cd frontend && npm install
cp .env.example .env.local                             # NEXT_PUBLIC_API_URL=http://localhost:8000/api
npm run dev                                            # http://localhost:3000
```

## Evaluation Harness

`python test_e2e.py` runs the full pipeline across all 5 content types and scores each on
three layers: **structural assertions** (length caps, word floors, formatting),
an **AI-slop linter**, and an **LLM-as-judge** on the assignment's grading axes. Per-run
traces and finals are written to `traces/`.

```bash
python test_e2e.py                 # all content types
python test_e2e.py --only essay    # single type
```

## Deployment

**Backend → Railway**
1. New project from this GitHub repo (root directory = repo root).
2. Start command comes from the `Procfile`: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
3. Set environment variables: `OPENAI_API_KEY`, `TAVILY_API_KEY`, and `ALLOWED_ORIGINS`
   (your Vercel URL, e.g. `https://your-app.vercel.app`).
4. The prebuilt `data/chroma_db/` ships with the image, so the corpus is queryable on first
   boot with no re-ingestion. (Note: user-uploaded docs write to the container filesystem,
   which is ephemeral on Railway — attach a volume at `data/chroma_db` to persist them.)

**Frontend → Vercel**
1. Import the repo, set **root directory = `frontend`**.
2. Set `NEXT_PUBLIC_API_URL` to your Railway backend URL + `/api`.
3. Deploy (Next.js is auto-detected).

## Environment Variables

| Variable | Where | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | backend | LLM + embeddings |
| `TAVILY_API_KEY` | backend | web search / discovery |
| `ALLOWED_ORIGINS` | backend | comma-separated CORS origins (Vercel URL in prod) |
| `NEXT_PUBLIC_API_URL` | frontend | backend API base URL incl. `/api` |
