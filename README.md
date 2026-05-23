# llm-team-memory

> Shared memory for AI-assisted teams.  
> One setup wizard. Works with Claude Code, Codex, Cursor, or any agent with file access.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-blueviolet)
![Works with Codex](https://img.shields.io/badge/works%20with-Codex-black)

---

## Background

The pattern is based on Andrej Karpathy's [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): instead of RAG over raw documents, you maintain a persistent wiki that LLMs incrementally build and query. This repo adapts that idea for teams — multiple agents, multiple projects, one shared knowledge base.

---

## What is this?

One Obsidian vault, shared across your whole team. Every AI agent on every machine
reads the same rules file and writes to the same log. The knowledge base grows
with every session — without you maintaining it manually.

- One shared Obsidian vault as the memory layer for all projects
- Every AI agent on every machine reads the same contract (`CLAUDE.md`)
- Agents log what they did; team members see it in Obsidian in real time
- New projects created with one command — vault entry + GitHub repo + local CLAUDE.md

```
vault/
├── CLAUDE.md                  ← master contract for all agents
├── raw/                       ← source material (immutable, humans add)
└── wiki/
    ├── index.md               ← agents read this first
    ├── logs/
    │   └── YYYY-MM-DD.md      ← one file per day (no merge conflicts)
    ├── tasks.md               ← shared task board
    ├── projects/<slug>/       ← per-project context (auto-created)
    ├── team/                  ← one file per person
    ├── decisions/             ← ADRs
    ├── concepts/              ← shared patterns
    └── sources/               ← ingest summaries

project-a/                     ← code repo (separate git)
└── CLAUDE.md                  ← inherits from vault CLAUDE.md
```

---

## Quick start

```bash
git clone https://github.com/IchiMugen/llm-team-memory
cd llm-team-memory
python setup.py
```

> **Windows users:** if you see a `UnicodeEncodeError`, run with:
> ```
> set PYTHONUTF8=1 && python setup.py
> ```

The wizard asks:
- Where to create your vault
- Your handle and AI agent
- Team members and their agents
- Git hosting (GitHub / GitLab / Gitea / skip)
- VPS sync (optional — sets up a bare git repo for Obsidian Git)

When it's done:
1. Open the vault folder in Obsidian
2. Install the **Obsidian Git** plugin (pull on startup, auto-pull every 5 min)
3. In Claude Code / Codex: `"Read CLAUDE.md then continue"`

---

## Create a new project

```bash
python $VAULT_PATH/scripts/new-project.py my-project "Short description"

# Skip GitHub repo creation:
python $VAULT_PATH/scripts/new-project.py my-project "Short description" --no-github
```

This creates:
- `vault/wiki/projects/my-project/context.md`
- Entry in `wiki/index.md` and `wiki/tasks.md`
- Entry in today's `wiki/logs/YYYY-MM-DD.md`
- `my-project/CLAUDE.md` (inherits from vault contract)
- Private GitHub repo + initial commit (requires `gh` CLI, skipped with `--no-github`)

---

## Add a team member

```bash
python $VAULT_PATH/scripts/add-member.py <github-username>

# Optional flags:
python $VAULT_PATH/scripts/add-member.py <github-username> --handle alice --agent "Cursor" --role Designer
```

This:
- Sends a GitHub collaborator invite to the vault repo
- Creates `wiki/team/<handle>.md` from the team template
- Adds a row to `CLAUDE.md` team table
- Commits and pushes everything

The new member clones the vault once they accept the GitHub invite:
```bash
git clone https://github.com/<your-username>/vault vault
```

Requires `gh` CLI and a GitHub-hosted vault. For VPS-only setups, grant SSH access manually.

---

## Automatic session enforcement

`scripts/link-claude-memory.py` registers a Claude Code **Stop hook** that fires at the end of every session:

- If today's log is missing → agent gets the log template and must fill it before stopping
- If vault has uncommitted changes → agent gets the commit command and must run it

The agent cannot exit until the vault is updated. No reminders needed.

---

## How agents use the vault

Every agent session starts with:
```
Read CLAUDE.md then continue
```

The agent:
1. Reads `CLAUDE.md` (team rules, write boundaries, memory policy)
2. Reads `wiki/index.md` (what exists)
3. Reads `wiki/tasks.md` (what needs doing)
4. Reads `wiki/projects/<this-project>/context.md` (project state)
5. Works
6. Appends to `wiki/logs/YYYY-MM-DD.md`, updates `wiki/tasks.md`, updates context if needed

---

## Write boundaries and memory policy

`CLAUDE.md` ships with explicit rules about what agents may and may not touch:

**Agents may write to:** daily logs, tasks, active project context, new ADRs, new source summaries.

**Agents must not touch:** `raw/`, `wiki/index.md`, `CLAUDE.md`, other projects' context, past log entries.

**Memory policy — write only when durable and confirmed:**
- Decisions made, reproducible discoveries, meaningful state changes
- Not: assumptions, speculative architecture, step-by-step narration, duplicates

This keeps the vault from rotting. A six-month-old vault should be as useful as a fresh one.

---

## Sync options

**GitHub** (simplest for small teams): vault is a private GitHub repo,
everyone clones it, Obsidian Git handles push/pull automatically.

**Self-hosted VPS** (more private): bare git repo on your server.
```bash
# On VPS (run once):
bash $VAULT_PATH/scripts/vault-sync-setup.sh

# On each machine:
git remote add origin ssh://user@your-vps/~/repos/vault.git
git push -u origin main

# Team member clone:
git clone ssh://user@your-vps/~/repos/vault.git vault
```

---

## Agent compatibility

| Agent | How to start |
|---|---|
| Claude Code | `"Read CLAUDE.md then continue"` |
| Codex | Same |
| Cursor | Same, or set CLAUDE.md as rules file |
| Windsurf | Same |
| Custom | Point agent at CLAUDE.md as system context |

---

## Requirements

- Python 3.8+
- git
- Obsidian (free) + Obsidian Git plugin
- `gh` CLI (optional, for GitHub repo creation)

---

## License

MIT
