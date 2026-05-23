# llm-team-memory

> Karpathy-style shared memory for AI-assisted teams.  
> One setup wizard. Works with Claude Code, Codex, Cursor, or any agent with file access.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-blueviolet)
![Works with Codex](https://img.shields.io/badge/works%20with-Codex-black)

---

## What is this?

In April 2026, Andrej Karpathy published a pattern for building a knowledge base
that an LLM maintains — not you. Drop sources in, ask questions, let the agent
keep everything organised. The wiki compounds with every session.

**This repo extends that pattern to teams:**

- One shared Obsidian vault as the memory layer for all projects
- Every AI agent on every machine reads the same contract (`CLAUDE.md`)
- Agents log what they did; team members see it in Obsidian in real time
- New projects created with one command — vault entry + GitHub repo + local CLAUDE.md

```
vault/                         ← shared memory (one git repo, Obsidian frontend)
├── CLAUDE.md                  ← master contract for all agents
├── raw/                       ← source material (immutable, humans add)
└── wiki/
    ├── index.md               ← agents read this first
    ├── log.md                 ← append-only: what agents did
    ├── tasks.md               ← shared task board
    ├── projects/<slug>/       ← per-project context (auto-created)
    ├── team/                  ← one file per person
    ├── decisions/             ← ADRs
    ├── concepts/              ← shared patterns
    └── sources/               ← ingest summaries

project-a/                     ← code repo (separate git)
└── CLAUDE.md                  ← inherits from vault CLAUDE.md

project-b/
└── CLAUDE.md
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
> Python 3.7+ supports this env var. Or upgrade to Python 3.8+ and
> use `python -X utf8 setup.py`.

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
- Record in `wiki/log.md`
- `my-project/CLAUDE.md` (inherits from vault contract)
- Private GitHub repo + initial commit (requires `gh` CLI, skipped with `--no-github`)

---

## How agents use the vault

Every agent session starts with:
```
Read CLAUDE.md then continue
```

The agent:
1. Reads `CLAUDE.md` (team rules, GitHub workflow, code standards)
2. Reads `wiki/index.md` (what exists)
3. Reads `wiki/tasks.md` (what needs doing)
4. Reads `wiki/projects/<this-project>/context.md` (project state)
5. Works
6. Appends to `wiki/log.md`, updates `wiki/tasks.md`, updates context if needed

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

Works with any agent that can read and write files:

| Agent | How to start |
|---|---|
| Claude Code | `"Read CLAUDE.md then continue"` |
| Codex | Same |
| Cursor | Same, or set CLAUDE.md as rules file |
| Windsurf | Same |
| Custom | Point agent at CLAUDE.md as system context |

---

## Bugs fixed vs. original

This repo includes fixes over the initial release:

| Bug | Fix |
|-----|-----|
| Unicode crash on Windows (cp1251) | Auto-reconfigure stdout/stdin to UTF-8 |
| SSH URL missing `/` before `~` | Path normalised in `build_vars` and `init_git` |
| Team table 3-col vs 4-col header mismatch | Always emit 4 columns, `—` when no GitHub handle |
| `raw/` directory missing after setup | Created with `.gitkeep` in `create_vault` |
| GitHub repo auto-created without opt-out | `--no-github` flag added to `new-project.py` |
| `git checkout -b main` fails on git ≥2.28 default | Use `git symbolic-ref HEAD` instead |
| `EOFError` on piped/scripted input | Caught alongside `KeyboardInterrupt` |

---

## Requirements

- Python 3.8+
- git
- Obsidian (free) + Obsidian Git plugin
- `gh` CLI (optional, for GitHub repo creation)

---

## License

MIT
