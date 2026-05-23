# LLM Wiki Pattern (Karpathy)

**Source:** Andrej Karpathy, GitHub Gist, April 2026
**Applied in:** this vault

## Core idea

The LLM builds and maintains the knowledge base. Humans curate what goes in.
No vector DB, no RAG pipeline — just structured markdown and an agent with file access.

> "The LLM writes and maintains all of the data of the wiki.
> I rarely touch it directly." — Karpathy

## Three layers

- `raw/` — immutable source documents. Humans add, agents read only.
- `wiki/` — LLM-generated and maintained pages. Agents write, humans read.
- `CLAUDE.md` — schema: rules, templates, naming conventions for agents.

## Three operations

**Ingest** — drop source in `raw/` → agent creates summary, updates index,
cascades updates to related pages, appends to log.

**Query** — ask a question → agent reads `index.md` first (not all files),
navigates to relevant pages, answers with `[[wiki-links]]`. Valuable answers
saved as permanent wiki pages.

**Lint** — health check → agent finds broken links, contradictions, stale pages.

## Scale

Works best for 10 to a few hundred documents per topic.
Beyond that, token cost of interlinks grows — consider vector search.

## Key difference from RAG

Wiki is a compiled artifact that compounds with each ingest.
RAG re-derives from scratch on every query.

## Team adaptation

In team use: agents write to `log.md` and `tasks.md` after every session.
All participants see agent activity in real time via Obsidian + git sync.
Each participant's AI agent reads the same `CLAUDE.md` — consistent behaviour
across Claude Code, Codex, Cursor, or any other tool with file access.
