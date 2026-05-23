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

### 4. Set VAULT_PATH
```bash
# Add to ~/.bashrc or ~/.zshrc or ~/.profile
export VAULT_PATH="$HOME/vault"
```

### 5. Add yourself to the team
- Copy `wiki/team/_template.md` → save as `wiki/team/<your-handle>.md`
- Fill in your role, agent, stack, timezone
- Add your row to `wiki/index.md` → Team table

### 6. Read the contract
Open `CLAUDE.md`. This governs how all agents behave.

---

## Daily workflow

**Morning:** Obsidian auto-pulls → check `wiki/log.md` (what agents did overnight)
→ check `wiki/tasks.md` (what needs doing)

**Start any agent session:**
```
Read CLAUDE.md then continue
```
Agent reads vault context, picks up tasks, starts working.

**Create a new project:**
```bash
python $VAULT_PATH/scripts/new-project.py my-project "Short description"
```

**Drop a source into the vault:**
```bash
cp article.pdf $VAULT_PATH/raw/articles/
# Then in your agent:
# "I added a new file to raw/articles/. Please ingest it."
```

**Write an ADR:**
```bash
cp $VAULT_PATH/scripts/templates/adr.md \
   $VAULT_PATH/wiki/decisions/adr-00X-short-title.md
# Fill it in, add to wiki/index.md decisions table
```

---

## Rules

- `raw/` is immutable — only add, never edit
- `wiki/log.md` is append-only — never edit past entries
- Merge conflicts in `log.md` → keep both, append below
- Architecture changes → write ADR first, then implement
- Agents work on feature branches, PRs to merge to main
