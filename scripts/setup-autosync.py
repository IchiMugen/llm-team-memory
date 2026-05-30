#!/usr/bin/env python3
"""
setup-autosync.py
Registers vault-sync.py to autostart on Windows login (no admin required).
Run once per device after cloning the vault.

Usage:
    python D:/vault/scripts/setup-autosync.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VAULT = Path(__file__).resolve().parent.parent
SYNC_SCRIPT = VAULT / "scripts" / "vault-sync.py"
STARTUP_DIR = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
VBS_NAME = "VaultAutoSync.vbs"


def find_pythonw() -> str:
    import shutil
    for candidate in ["pythonw", "pythonw3"]:
        path = shutil.which(candidate)
        if path:
            return path
    return shutil.which("python") or "python"


def create_vbs(pythonw: str, vbs_path: Path) -> None:
    # Watchdog loop: restarts vault-sync.py if it crashes
    content = (
        f'Set WshShell = CreateObject("WScript.Shell")\n'
        f'Do\n'
        f'    WshShell.Run Chr(34) & "{pythonw}" & Chr(34) & " " & Chr(34) & "{SYNC_SCRIPT}" & Chr(34), 0, True\n'
        f'    WScript.Sleep 5000\n'
        f'Loop\n'
    )
    vbs_path.write_text(content, encoding="utf-8")


def main():
    if sys.platform != "win32":
        print("This script is for Windows only.")
        print(f"On Linux/Mac, add to cron:")
        print(f"  */2 * * * * python3 {SYNC_SCRIPT} &")
        sys.exit(0)

    pythonw = find_pythonw()
    vbs_path = STARTUP_DIR / VBS_NAME

    print(f"\n=== setup-autosync.py ===\n")
    print(f"Vault:   {VAULT}")
    print(f"Script:  {SYNC_SCRIPT}")
    print(f"Python:  {pythonw}")
    print(f"Startup: {vbs_path}\n")

    if not SYNC_SCRIPT.exists():
        print(f"ERROR: {SYNC_SCRIPT} not found.")
        sys.exit(1)

    STARTUP_DIR.mkdir(parents=True, exist_ok=True)

    create_vbs(pythonw, vbs_path)
    print(f"Registered: {vbs_path}")
    print(f"vault-sync will start automatically on next login.\n")

    print(f"Starting now...")
    subprocess.Popen(
        [pythonw, str(SYNC_SCRIPT)],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
        close_fds=True,
    )
    print(f"vault-sync is running in background.")
    print(f"Log: {VAULT}/scripts/vault-sync.log\n")


if __name__ == "__main__":
    main()
