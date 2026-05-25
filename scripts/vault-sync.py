#!/usr/bin/env python3
"""
vault-sync.py
Background daemon — watches vault for changes and syncs automatically.

- Commits and pushes local changes within 5 seconds of last edit
- Pulls remote changes every 30 seconds
- Runs silently in background, no window

Setup (run once per device):
    python D:/vault/scripts/setup-autosync.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PULL_INTERVAL = 120  # seconds between pulls
DEBOUNCE = 5         # seconds to wait after last change before committing
CHECK_INTERVAL = 2   # seconds between status checks

LOG = VAULT / "scripts" / "vault-sync.log"


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line)
        # Keep log under 500 lines
        lines = LOG.read_text(encoding="utf-8").splitlines()
        if len(lines) > 500:
            LOG.write_text("\n".join(lines[-400:]) + "\n", encoding="utf-8")
    except Exception:
        pass


def git(cmd: str) -> tuple[int, str, str]:
    result = subprocess.run(
        f'git -C "{VAULT}" {cmd}',
        shell=True, capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def has_changes() -> bool:
    _, out, _ = git("status --porcelain")
    return bool(out)


def pull():
    code, out, err = git("pull --rebase --autostash")
    if code != 0 and err:
        log(f"PULL ERROR: {err}")
    elif "Already up to date" not in out and out:
        log(f"Pulled: {out[:120]}")


def push():
    git("add -A")
    ts = datetime.now().strftime("%H:%M")
    code, out, err = git(f'commit -m "vault: auto-sync {ts}"')
    if "nothing to commit" in out or code != 0:
        return
    log(f"Committed: {out[:80]}")

    for remote in ["github", "origin"]:
        code, _, err = git(f"push {remote} main")
        if code != 0 and err and "does not appear to be a git repository" not in err:
            log(f"Push {remote} error: {err[:100]}")
        elif code == 0:
            log(f"Pushed to {remote}")


def main():
    log(f"vault-sync started — watching {VAULT}")

    # Commit any pending changes immediately on startup (no debounce)
    if has_changes():
        push()

    last_pull = time.time()
    pending_since: float | None = None

    while True:
        try:
            now = time.time()

            # Pull
            if now - last_pull >= PULL_INTERVAL:
                pull()
                last_pull = now

            # Detect local changes
            if has_changes():
                if pending_since is None:
                    pending_since = now
            else:
                pending_since = None

            # Push after debounce
            if pending_since is not None and now - pending_since >= DEBOUNCE:
                push()
                pending_since = None

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
