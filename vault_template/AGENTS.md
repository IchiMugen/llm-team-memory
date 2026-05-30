# Agent Instructions

This vault is a shared team memory. Read this file if you are an AI agent
(Claude Code, Codex, Cursor, Windsurf, or any other).

## Step 1 — Read the team contract
Read `CLAUDE.md` in this directory. It defines write boundaries, session
protocol, and memory policy for all agents.

## Step 2 — Read agent memory
Read `claude-memory/MEMORY.md`. It contains your persistent context:
who the team is, active projects, collaboration rules.

## Step 3 — Read project context
Read `wiki/projects/<active-project>/context.md` and
`wiki/projects/<active-project>/state.md` for the project you are working on.

## Step 4 — Work

## Step 5 — Before ending the session
Append a log entry to `wiki/logs/YYYY-MM-DD.md` (create if missing).
Format is in `CLAUDE.md`.
Update `wiki/projects/<active-project>/state.md`.
