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

> To add a member: `python scripts/add-member.py <github-username> [--handle <nick>] [--agent "Cursor"] [--role Developer]`

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
1. Append to `wiki/logs/YYYY-MM-DD.md` — today's date, create if missing
2. Update `wiki/tasks.md` — mark done, add newly found tasks
3. Update `wiki/projects/<this-project>/context.md` if architecture changed
4. If architectural decision was made → create ADR in `wiki/decisions/`

### Log entry format (strict):
```
## HH:MM | <handle> | <project-slug>
**Done:** one-line summary of what actually happened
**Changed:** file1, file2 (or "none")
**Decision:** ADR-XXX title (or "none")
**Next:** what logically follows
---
```

> One entry per session. Date is the filename, not repeated in the entry.

---

## Write Boundaries

Agents **MAY** write to:

| Path | Rule |
|------|------|
| `wiki/logs/YYYY-MM-DD.md` | Append only. One entry per session. |
| `wiki/tasks.md` | Mark tasks done, append new ones under "Discovered by Agent". |
| `wiki/projects/<active-project>/context.md` | Update only if architecture or state changed. |
| `wiki/decisions/ADR-XXX.md` | New file only — never edit an existing ADR. |
| `wiki/sources/<slug>.md` | New file only (ingest protocol). |
| `wiki/concepts/<slug>.md` | Create or update. |

Agents **MUST NOT** touch:

| Path | Reason |
|------|--------|
| `raw/` | Immutable source layer — humans add, agents read. |
| `wiki/index.md` | Human-maintained index. `new-project.py` adds rows; agents don't. |
| `CLAUDE.md` | Contract is human-owned. |
| Past log entries | Append-only. Never edit what another session wrote. |
| Other projects' `context.md` | Only write to the active project. |

---

## Memory Policy

Write to the vault only when the information is **durable and confirmed**.

**WRITE:**
- Decisions that were made (architecture, tooling, process)
- Discoveries that are reproducible and non-obvious
- State changes that matter (migration applied, feature shipped, API changed)
- Newly found tasks worth tracking

**DO NOT WRITE:**
- Transient thoughts or "I think maybe…"
- Unverified assumptions
- Speculative architecture ("we could do X someday")
- Information already present in `context.md`
- Step-by-step work narration ("now I'm editing file X…")
- Anything you wouldn't want a new team member to read six months from now

> If you're unsure whether something belongs in the vault — it doesn't.

---

## GitHub Workflow

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
- [ ] wiki/logs/YYYY-MM-DD.md appended
- [ ] wiki/tasks.md updated
- [ ] context.md updated if architecture changed
```

---

## Documentation Standards

| Content type | Location |
|---|---|
| Architecture decisions | `wiki/decisions/ADR-XXX.md` |
| Project context | `wiki/projects/<slug>/context.md` |
| Session logs | `wiki/logs/YYYY-MM-DD.md` |
| Task board | `wiki/tasks.md` |
| Source material | `raw/` |
| Code docs / README | In the code repo |

---

## Code Standards

- **Primary language:** {{DEFAULT_LANG}}
- **Minimal footprint:** do the minimum needed, nothing more
- **Checkpoint rule:** before any destructive action (delete, overwrite,
  major refactor) → announce what you're about to do → wait for confirmation
  if change affects more than 50 lines
- **Tests:** write before marking a task done

---

## Ingest Protocol

When a new source is dropped into `raw/`:
1. Read document, extract key takeaways
2. Create `wiki/sources/<slug>.md` with summary
3. Update related pages in `wiki/concepts/` or `wiki/projects/`
4. Add entry to `wiki/index.md` sources table
5. Append ingest record to today's log

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
