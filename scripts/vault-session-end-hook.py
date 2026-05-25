#!/usr/bin/env python3
"""
vault-session-end-hook.py
Claude Code Stop hook — enforces vault write before every session ends.

Exit 0 → allow stop
Exit 2 → block stop, inject message to agent

Registered automatically by: scripts/link-claude-memory.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATE = datetime.now().strftime("%Y-%m-%d")
TIME = datetime.now().strftime("%H:%M")
SESSION_DIR = Path.home() / ".claude" / "session_starts"


def find_vault() -> Path | None:
    here = Path(__file__).resolve().parent.parent
    if (here / ".vault-config.json").exists():
        return here
    fallback = Path.home() / "vault"
    if (fallback / ".vault-config.json").exists():
        return fallback
    return None


def load_lead(vault: Path) -> str:
    try:
        cfg = json.loads((vault / ".vault-config.json").read_text(encoding="utf-8"))
        return cfg.get("lead_handle", "lead")
    except Exception:
        return "lead"


def get_session_start(session_id: str) -> datetime:
    """Return session start time, recording it on first call."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    session_file = SESSION_DIR / f"{session_id}.txt"
    if session_file.exists():
        return datetime.fromisoformat(session_file.read_text().strip())
    now = datetime.now()
    session_file.write_text(now.isoformat())
    return now


def cleanup_old_sessions():
    """Remove session start files older than 24 hours."""
    if not SESSION_DIR.exists():
        return
    cutoff = datetime.now().timestamp() - 86400
    for f in SESSION_DIR.glob("*.txt"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except Exception:
            pass


def log_written_this_session(vault: Path, session_start: datetime) -> bool:
    """Check if today's log was modified after this session started."""
    log = vault / "wiki" / "logs" / f"{DATE}.md"
    if not log.exists():
        return False
    mtime = datetime.fromtimestamp(log.stat().st_mtime)
    return mtime > session_start


def detect_project(cwd: str, vault: Path) -> str:
    cwd_name = Path(cwd).name.lower()
    projects_dir = vault / "wiki" / "projects"
    if projects_dir.exists():
        for p in projects_dir.iterdir():
            if p.name.lower() in cwd_name or cwd_name in p.name.lower():
                return p.name
    return cwd_name


def main() -> None:
    try:
        event = json.loads(sys.stdin.read())
    except Exception:
        event = {}

    if event.get("stop_hook_active"):
        sys.exit(0)

    vault = find_vault()
    if not vault:
        sys.exit(0)

    session_id = event.get("session_id", "unknown")
    session_start = get_session_start(session_id)
    cleanup_old_sessions()

    lead = load_lead(vault)
    cwd = event.get("cwd", "")
    project = detect_project(cwd, vault)
    log_ok = log_written_this_session(vault, session_start)

    if not log_ok:
        issues = [
            f"No session log written since this session started. Append to `wiki/logs/{DATE}.md`:\n"
            f"```\n"
            f"## {TIME} | {lead} | {project}\n"
            f"**Done:** <one-line summary>\n"
            f"**Changed:** <files or none>\n"
            f"**Decision:** <ADR or none>\n"
            f"**Next:** <what follows>\n"
            f"---\n"
            f"```\n"
            f"If nothing meaningful happened, write: `**Done:** Q&A only, no changes`"
        ]
    else:
        issues = []

    if not issues:
        sys.exit(0)

    msg = "**Vault checklist — complete before ending session:**\n\n"
    for i, issue in enumerate(issues, 1):
        msg += f"{i}. {issue}\n\n"
    msg += "Complete the checklist and the session will end automatically."

    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    sys.exit(2)


if __name__ == "__main__":
    main()
