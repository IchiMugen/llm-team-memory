# Roadmap — Known Limits and Future Directions

Current architecture is intentionally simple. These are the points where it
will break — and what to do when they do.

**These won't break when there are "too many files."  
They will break when agents act semi-autonomously, memory becomes
machine-generated at scale, and async parallel work between agents appears.**

---

## 1. `wiki/index.md` will become expensive

Single file read at every session start. As it grows it becomes noisy and
token-heavy — most of it irrelevant to the current session.

**Future:** split into `wiki/index/active.md`, `projects.md`, `concepts.md`, `team.md`.
Agents read only `active.md` by default, navigate deeper on demand.

---

## 2. No memory lifecycle

Memory is binary: it exists or it doesn't. Old context stays permanently
"equally important" as current context.

**Future:** lifecycle stages —
```
inbox/    ← newly written, pending review
active/   ← current, loaded by default
stable/   ← settled decisions, loaded on demand
archived/ ← historical, agents skip unless asked
```
Human reviews `inbox/` periodically, promotes or discards.

---

## 3. `wiki/tasks.md` will become a conflict zone

Single shared file means merge conflicts and duplicate tasks as soon as
more than one agent writes concurrently.

**Future:** per-project task files (`wiki/tasks/<slug>.md`) or split by
lifecycle (`backlog.md` / `active.md` / `done/YYYY-MM.md`).

---

## 4. No explicit ownership

No machine-readable owner or status on context and task files. Agents will
eventually overwrite each other's state and diverge on version of truth.

**Future:** frontmatter on context files:
```yaml
---
owner: claude-code
project: my-project
status: active
last_written: 2026-05-23
---
```
Agents check `owner` before writing. Only write if owner matches or is unset.

---

## When to act

Not now. Act when:

- Agents run semi-autonomously without per-session human review
- `wiki/logs/` is predominantly machine-generated
- Merge conflicts appear in `tasks.md` or `index.md`
- Session startup token cost becomes noticeably high

Until then, flat structure is the right default — simpler is more durable.
