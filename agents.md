┌─────────────────┐
   X / arXiv / HN ──▶│ Discovery Agent │  ranks candidates by
                     └────────┬────────┘  "insight potential"
                              ▼
                     ┌─────────────────┐
                     │ Retrieval Agent │  pulls grounding context
                     │   (RAG corpus)  │  + author's voice samples
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │  Angle Agent    │  generates 4-6 distinct
                     │                 │  theses, picks 2 strongest
                     └────────┬────────┘
                              ▼
              ┌──────────────────────────────┐
              │      DRAFT ⇄ CRITIC LOOP      │
              │  Draft Writer → Critic →      │ ◀── the core.
              │  (revise) → Critic → ...      │     loops until
              │  max 3 iterations             │     critic passes
              └──────────────┬───────────────┘
                              ▼
                     ┌─────────────────┐
                     │  Fact Checker   │  extracts claims,
                     │                 │  verifies vs sources
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │  Voice Reviewer │  final pass: matches
                     │                 │  archive style
                     └────────┬────────┘
                              ▼
                   structured trace + output