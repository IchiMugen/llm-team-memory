# Team Vault — Master Agent Contract

> This is the **top-level contract** for all agents on this team.
> Every agent (Claude Code, Codex, Cursor, etc.) reads this file
> before any project-level CLAUDE.md.
> Humans use Obsidian to read the vault. Git keeps it in sync.

---

## Team

| Handle | Role | Agent | GitHub |
|--------|------|-------|--------|
{{TEAM_ROWS}}

> To add a member: copy `wiki/team/_template.md` → rename → fill in → add row above.

---

## Active Projects

> Auto-populated by `scripts/new-project.py`.
> See `wiki/index.md` for full list with status.

---

## Session Protocol (mandatory for all agents)

### On session START — read in this order:
1. This file (`CLAUDE.md`) ✓
2. `wiki/index.md` — what exists in the vault
3. `wiki/tasks.md` — current tasks and owners
4. `wiki/projects/<this-project>/context.md` — project context

### On session END — write in this order:
1. Append to `wiki/log.md` (append-only, never edit past entries)
2. Update `wiki/tasks.md` — mark done, add newly found tasks
3. Update `wiki/projects/<this-project>/context.md` if architecture changed
4. If architectural decision was made → create ADR in `wiki/decisions/`

### Log entry format (strict):
```
## YYYY-MM-DD HH:MM | <handle> | <project-slug>
**Done:** one-line summary
**Changed:** file1, file2 (or "none")
**Decision:** ADR-XXX title (or "none")
**Next:** what logically follows
---
```

---

## GitHub Workflow

### Repository naming
```
<project-slug>        # main code repo
```

### Branch strategy
- `main` — always deployable, protected
- `<handle>/<feature>` — personal feature branches
- Agents work on feature branches, never push directly to main
- PR required to merge — at minimum one human review

### Commit message format
```
<project-slug>: <what> [<why> if non-obvious]
```

### PR description (agents must fill this)
```markdown
## What
[one line]

## Why
[one line]

## Changes
- file: what changed

## Tested
- [ ] tests pass
- [ ] manual test: [what you did]

## Vault
- [ ] wiki/log.md appended
- [ ] wiki/tasks.md updated
- [ ] context.md updated if architecture changed
```

---

## Documentation Standards

| Content type | Location |
|---|---|
| Architecture decisions | `vault/wiki/decisions/ADR-XXX.md` |
| Project context | `vault/wiki/projects/<slug>/context.md` |
| Session log | `vault/wiki/log.md` |
| Task board | `vault/wiki/tasks.md` |
| Source material | `vault/raw/` |
| Code docs / README | In the code repo |

### README standard (every repo):
```markdown
# Project Name
> One sentence description.

## What it does
[2-3 sentences]

## Stack
[list]

## Setup
[minimal steps to run]

## Vault
Context: vault/wiki/projects/<slug>/
Contract: CLAUDE.md
```

---

## Code Standards

- **Primary language:** {{DEFAULT_LANG}}
- **Minimal footprint:** do the minimum needed, nothing more
- **Checkpoint rule:** before any destructive action (delete, overwrite,
  major refactor) → announce what you're about to do → wait for confirmation
  if change affects more than 50 lines
- **Tests:** write before marking a task done
- **Never touch `raw/`** — immutable source layer
- **Never edit past entries in `log.md`** — append only

---

## Ingest Protocol (Karpathy pattern)

When a new source is dropped into `raw/`:
1. Read document, extract key takeaways
2. Create `wiki/sources/<slug>.md` with summary
3. Update related pages in `wiki/concepts/` or `wiki/projects/`
4. Add entry to `wiki/index.md` sources table
5. Append ingest record to `wiki/log.md`

When a valuable query answer emerges → save as a permanent wiki page.

---

## New Project

```bash
python {{VAULT_PATH}}/scripts/new-project.py <slug> "description"
```

Creates: vault wiki entry + local CLAUDE.md + GitHub repo + initial commit.

---

## Resume Trigger

Any agent receiving `"Read CLAUDE.md then continue"`:
1. Read this file
2. Read `wiki/index.md`
3. Read `wiki/tasks.md`
4. Read `wiki/projects/<active-project>/context.md`
5. Continue work
