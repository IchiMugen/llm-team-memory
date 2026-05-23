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
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATE = datetime.now().strftime("%Y-%m-%d")
TIME = datetime.now().strftime("%H:%M")


def find_vault() -> Path | None:
    # Prefer location relative to this script (vault/scripts/this.py → vault/)
    here = Path(__file__).resolve().parent.parent
    if (here / ".vault-config.json").exists():
        return here
    # Fallback: well-known location
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


def git_status(vault: Path) -> str:
    result = subprocess.run(
        "git status --porcelain",
        shell=True, cwd=vault, capture_output=True, text=True
    )
    return result.stdout.strip()


def log_written_today(vault: Path) -> bool:
    log = vault / "wiki" / "logs" / f"{DATE}.md"
    if not log.exists():
        return False
    mtime = datetime.fromtimestamp(log.stat().st_mtime)
    return mtime.date() == datetime.now().date()


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

    # Prevent infinite loop — Claude Code sets this on retry
    if event.get("stop_hook_active"):
        sys.exit(0)

    vault = find_vault()
    if not vault:
        sys.exit(0)

    lead = load_lead(vault)
    cwd = event.get("cwd", "")
    project = detect_project(cwd, vault)
    changes = git_status(vault)
    log_ok = log_written_today(vault)

    issues = []

    if not log_ok:
        issues.append(
            f"No session log for today. Append to `wiki/logs/{DATE}.md`:\n"
            f"```\n"
            f"## {TIME} | {lead} | {project}\n"
            f"**Done:** <one-line summary>\n"
            f"**Changed:** <files or none>\n"
            f"**Decision:** <ADR or none>\n"
            f"**Next:** <what follows>\n"
            f"---\n"
            f"```\n"
            f"If nothing meaningful happened, write: `**Done:** Q&A only, no changes`"
        )

    if changes:
        issues.append(
            f"Vault has uncommitted changes:\n```\n{changes}\n```\n"
            f"Run:\n"
            f'```\n'
            f'git -C "{vault}" add -A && '
            f'git -C "{vault}" commit -m "vault: {project} session {DATE}" && '
            f'git -C "{vault}" push\n'
            f'```'
        )

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
