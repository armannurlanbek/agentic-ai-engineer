# Agent Traces

End-to-end execution traces of the multi-agent content pipeline, one per content
type. Each run drives the full compiled LangGraph graph
(`Discovery → Retrieval → Angle → Draft Writer ⇄ Critic → Fact Checker → Voice Reviewer`)
and records every agent's work. Generated with `python test_e2e.py` against the
shipped corpus (`data/chroma_db/`).

## Runs

| Content type | File | Pipeline steps | Draft iters | Total tokens | Structural | Judge (overall) |
|---|---|---|---|---|---|---|
| Tweet | `e2e_tweet_e2e-tweet-939d19.json` | 9 | 2 | 25,639 | 10/10 | 5 |
| Quote Retweet | `e2e_qrt_e2e-qrt-c34250.json` | 9 | 2 | 21,296 | 11/11 | 6 |
| Thread | `e2e_thread_e2e-thread-72e644.json` | 9 | 2 | 42,322 | 11/11 | 6 |
| Essay | `e2e_essay_e2e-essay-acf503.json` | 9 | 2 | 69,702 | 8/8 | 6 |
| Article | `e2e_article_e2e-article-f42972.json` | 11 | 3 | 85,250 | 8/8 | 6 |

"Pipeline steps" counts every node invocation, so the Draft Writer ⇄ Critic loop
shows up as repeated `draft_writer`/`critic` entries (the article ran 3 draft
iterations → more steps).

## What each trace file contains

- **`case`** — the request (topic, content type, any quoted tweet).
- **`traces`** — the per-agent execution log: `node_name`, wall-clock `duration_ms`,
  and real `prompt_tokens` / `completion_tokens` / `total_tokens` for every step,
  in execution order (including each Draft↔Critic iteration).
- **`selected_topic_summary` / `selected_angles`** — the thesis-anchored brief and
  the angle the fidelity gate selected.
- **`fact_check_results`** — per claim: RAG/web verification status, evidence, and
  the keep / soften / remove action taken.
- **`voice_review`** — extracted style profile, length compliance, and which
  fact-checked claims were preserved.
- **`final_content`** — the finished output.
- **`assessment`** — a three-layer evaluation of the output:
  1. `structural` — deterministic contract checks (char caps, word floors, thread
     formatting, no hashtags/slop) sourced from the same constants the pipeline enforces.
  2. `slop` — AI-slop / hedge phrase linter.
  3. `judge` — an LLM-as-judge scoring insight density, originality, hook,
     authentic voice, and clarity against the assignment's criteria.

## Reproduce

```bash
python test_e2e.py             # all content types -> writes fresh traces here
python test_e2e.py --only essay
```
