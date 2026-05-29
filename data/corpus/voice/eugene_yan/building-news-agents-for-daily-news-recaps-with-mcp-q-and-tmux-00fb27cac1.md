---
source: Eugene Yan
source_slug: eugene_yan
kind: voice
content_type: essay
url: https://eugeneyan.com//writing/news-agents/
title: Building News Agents for Daily News Recaps with MCP, Q, and tmux
published: Sun, 04 May 2025 00:00:00 +0000
---

Main Agent (in the main tmux pane) ├── Read feeds.txt ├── Split feeds into 3 chunks ├── Spawns 3 Sub-Agents (in separate tmux panes) │   ├── Sub-Agent #1 │   │   ├── Process feeds in chunk 1 │   │   └── Report back when done │   ├── Sub-Agent #2 │   │   ├── Process feeds in chunk 2 │   │   └── Report back when done │   └── Sub-Agent #3 │       ├── Process feeds in chunk 3 │       └── Report back when done └── Combine everything into main-summary.md