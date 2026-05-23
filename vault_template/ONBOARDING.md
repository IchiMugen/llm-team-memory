# Onboarding

## What is this vault?

Shared memory for the team and all AI agents (Claude Code, Codex, Cursor, etc.).
You read it through Obsidian. Agents write to it after every session.
Git keeps everything in sync.

**The vault is not the code.** Code lives in GitHub repos.
The vault is the knowledge layer on top of all projects.

---

## Setup

### 1. Clone the vault
```bash
git clone <vault-repo-url> vault
```
Ask your team lead for the URL.

### 2. Open in Obsidian
- Download at obsidian.md
- "Open folder as vault" → select the `vault` folder

### 3. Install Obsidian Git plugin
Settings → Community plugins → Browse → "Obsidian Git" → Install → Enable

Plugin settings:
- Commit message: `{{hostname}}: {{date}}`
- Auto pull interval: `5` minutes
- Pull before push: ✓
- Sync method: merge

### 4. You're already added
Your team lead ran `scripts/add-member.py` to invite you and create your team page.
Open `wiki/team/<your-handle>.md` and fill in your timezone and stack.

### 5. Read the contract
Open `CLAUDE.md`. Pay attention to:
- **Write boundaries** — what you (and your agent) may touch
- **Memory policy** — what belongs in the vault and what doesn't

---

## Daily workflow

**Morning:** Obsidian auto-pulls → check `wiki/logs/` (what agents did)
→ check `wiki/tasks.md` (what needs doing)

**Start any agent session:**
```
Read CLAUDE.md then continue
```
Agent reads vault context, picks up tasks, starts working.
At session end it writes to `wiki/logs/YYYY-MM-DD.md` (today's file).

**Create a new project:**
```bash
python $VAULT_PATH/scripts/new-project.py my-project "Short description"
```

**Add a team member (team lead only):**
```bash
python $VAULT_PATH/scripts/add-member.py <github-username>
# Optional: --handle <nick> --agent "Cursor" --role Developer
```
Sends a GitHub collaborator invite, creates their team page, updates CLAUDE.md, and commits everything.

**Drop a source into the vault:**
```bash
cp article.pdf $VAULT_PATH/raw/
# Then in your agent: "I added a file to raw/. Please ingest it."
```

---

## Rules

- `raw/` is immutable — only add, never edit
- `wiki/logs/` is append-only — never edit past entries
- Merge conflicts in a log file → keep both entries, append below
- Architecture changes → write ADR first, then implement
- Agents work on feature branches, PRs to merge to main
