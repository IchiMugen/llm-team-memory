# llm-team-memory

> Shared memory for AI-assisted teams.  
> One setup wizard. Works with Claude Code, Codex, Cursor, or any agent with file access.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-blueviolet)
![Works with Codex](https://img.shields.io/badge/works%20with-Codex-black)

---

## Non-goals

This tool is intentionally simple. It will never be:

- An autonomous agent orchestration framework
- A vector search or semantic retrieval platform
- A cloud memory backend or SaaS service
- A replacement for project management tools (Jira, Linear, Notion)
- A plugin ecosystem

---

## Background

Based on Andrej Karpathy's [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): instead of RAG over raw documents, maintain a persistent wiki that LLMs incrementally build and query. This repo adapts that idea for teams — multiple agents, multiple machines, one shared knowledge base.

---

## What is this?

One Obsidian vault, shared across your whole team. Every AI agent on every machine reads the same rules file and writes to the same log.

- One shared Obsidian vault as the memory layer for all projects
- Every AI agent reads the same contract (`CLAUDE.md`)
- Agents log what they did; team members see it in Obsidian in real time
- Auto-sync daemon keeps all machines in sync — no manual git, no Obsidian Git required
- New projects created with one command — vault entry + GitHub repo + local CLAUDE.md

```
vault/
├── CLAUDE.md                  <- master contract for all agents
├── claude-memory/             <- agent cross-device memory (auto-loaded by Claude Code)
├── raw/                       <- source material (immutable, humans add)
└── wiki/
    ├── index.md               <- agents read this first
    ├── logs/
    │   └── YYYY-MM-DD.md      <- one file per day (no merge conflicts)
    ├── tasks.md               <- shared task board
    ├── projects/<slug>/       <- per-project context + state (auto-created)
    │   ├── context.md         <- architecture, stack, decisions (stable)
    │   └── state.md           <- current sprint, last session, what's next
    ├── team/                  <- one file per person
    ├── decisions/             <- ADRs
    ├── concepts/              <- shared patterns
    └── sources/               <- ingest summaries
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
- Git hosting (GitHub / skip)
- VPS sync (optional)

When done:
1. Open the vault folder in Obsidian
2. Run `python vault/scripts/setup-autosync.py` to start auto-sync
3. In Claude Code / Codex: `"Read CLAUDE.md then continue"`

---

## Auto-sync (OS-level daemon)

The vault syncs automatically via a background daemon — no Obsidian Git plugin needed, no manual git commands, survives machine restarts and crashes.

**One-time setup per machine:**

```bash
# With Python (recommended):
python /path/to/vault/scripts/setup-autosync.py

# Without Python (Windows only):
vault\scripts\setup-autosync.bat
```

What it does:
- Registers `VaultAutoSync.vbs` in the Windows Startup folder (auto-starts on login)
- The VBS runs a watchdog loop — restarts the daemon if it crashes
- Starts the daemon immediately

**How the daemon works:**
- Checks for changes every 2 seconds
- Commits + pushes to all remotes within 5 seconds of last edit
- Commits immediately on startup (prevents merge conflicts)
- Pulls from all remotes every 2 minutes
- Auto-configures git user identity if not set
- Logs to `vault/scripts/vault-sync.log`

**First-time setup on a new machine (if vault has uncommitted state):**

```bash
vault\scripts\first-setup.bat
```

This stashes local changes, pulls, restores, and starts the daemon.

---

## Create a new project

```bash
python $VAULT_PATH/scripts/new-project.py my-project "Short description"

# Skip GitHub repo creation:
python $VAULT_PATH/scripts/new-project.py my-project "Short description" --no-github
```

Creates:
- `vault/wiki/projects/my-project/context.md` — architecture and decisions
- `vault/wiki/projects/my-project/state.md` — current sprint state
- Entry in `wiki/index.md` and `wiki/tasks.md`
- `my-project/CLAUDE.md` (inherits from vault contract)
- Private GitHub repo + initial commit (requires `gh` CLI)

---

## Add a team member

```bash
python $VAULT_PATH/scripts/add-member.py <github-username>

# Optional flags:
python $VAULT_PATH/scripts/add-member.py <github-username> --handle alice --agent "Cursor" --role Designer
```

New member setup:
```bash
git clone https://github.com/<your-username>/vault vault
python vault/scripts/setup-autosync.py
```

---

## Session enforcement (Stop hook)

`scripts/link-claude-memory.py` registers a Claude Code **Stop hook**:

- Tracks session start time per session ID
- If no log entry written since session started → shows log template, blocks exit
- Agent cannot exit until vault is updated

The hook fires at the end of every session automatically.

---

## Cross-device agent memory

`claude-memory/MEMORY.md` is auto-loaded by Claude Code at every session start (including after context summarization). It contains the agent's persistent knowledge: user profile, collaboration rules, project state, team info.

To set up on a new device:
```bash
python vault/scripts/link-claude-memory.py
```

This creates a junction/symlink so Claude Code reads from the vault automatically.

---

## How agents use the vault

Session start trigger:
```
Read CLAUDE.md then continue
```

The agent:
1. Reads `CLAUDE.md` (rules, write boundaries, memory policy)
2. Reads `wiki/index.md` and `wiki/tasks.md`
3. Reads `wiki/projects/<this-project>/context.md` + `state.md`
4. Works
5. Appends to `wiki/logs/YYYY-MM-DD.md`, updates `state.md`, updates `tasks.md`

---

## Sync options

**GitHub** (simplest): vault is a private GitHub repo, `setup-autosync.py` handles everything.

**Self-hosted VPS** (more private): bare git repo on your server.
```bash
# On VPS (run once):
bash vault/scripts/vault-sync-setup.sh

# On each machine — add VPS as second remote:
git remote add origin ssh://user@your-vps/~/repos/vault.git
git push -u origin main
```

The daemon pushes to all configured remotes automatically.

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
- Obsidian (free) — for reading the vault
- `gh` CLI (optional, for GitHub repo creation)

---

## License

MIT
