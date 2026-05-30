#!/usr/bin/env python3
"""
vault-sync.py
Background daemon - watches vault for changes and syncs automatically.

- Commits pending changes immediately on startup
- Commits and pushes local changes within 5 seconds of last edit
- Pulls from all remotes every 2 minutes
- Restarts itself when updated
- Runs silently in background, no window

Setup (run once per device):
    python /path/to/vault/scripts/setup-autosync.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PULL_INTERVAL = 120
DEBOUNCE = 5
CHECK_INTERVAL = 2

LOG = VAULT / "scripts" / "vault-sync.log"


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
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


def get_remotes() -> list[str]:
    _, out, _ = git("remote")
    return [r for r in out.splitlines() if r.strip()]


def ensure_git_identity():
    _, name, _ = git("config user.name")
    if not name:
        git("config user.name vault-sync")
        git("config user.email vault-sync@local")


def pull():
    for remote in get_remotes():
        code, out, err = git(f"pull {remote} main")
        if code != 0 and err:
            log(f"PULL {remote} ERROR: {err[:120]}")
        elif "Already up to date" not in out and out:
            log(f"Pulled from {remote}")


def push():
    ensure_git_identity()
    git("add -A")
    ts = datetime.now().strftime("%H:%M")
    code, out, err = git(f'commit -m "vault: auto-sync {ts}"')
    if "nothing to commit" in out:
        return
    if code != 0:
        log(f"Commit error: {err or out}")
        return
    log(f"Committed: {out[:80]}")
    for remote in get_remotes():
        code, _, err = git(f"push {remote} main")
        if code != 0 and err:
            log(f"Push {remote} error: {err[:120]}")
        elif code == 0:
            log(f"Pushed to {remote}")


def restart_if_updated(script_mtime: float) -> float:
    current = Path(__file__).stat().st_mtime
    if current != script_mtime:
        log("vault-sync.py updated - restarting...")
        subprocess.Popen(
            [sys.executable, str(Path(__file__))],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            close_fds=True,
        )
        sys.exit(0)
    return script_mtime


def main():
    log(f"vault-sync started - watching {VAULT}")
    _, status, _ = git("status --porcelain")
    log(f"Status: {status[:120] if status else 'clean'}")

    if status:
        push()

    last_pull = time.time()
    pending_since: float | None = None
    script_mtime = Path(__file__).stat().st_mtime

    while True:
        try:
            now = time.time()

            if now - last_pull >= PULL_INTERVAL:
                pull()
                last_pull = now
                script_mtime = restart_if_updated(script_mtime)

            if has_changes():
                if pending_since is None:
                    pending_since = now
            else:
                pending_since = None

            if pending_since is not None and now - pending_since >= DEBOUNCE:
                push()
                pending_since = None

        except Exception as e:
            log(f"ERROR: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
