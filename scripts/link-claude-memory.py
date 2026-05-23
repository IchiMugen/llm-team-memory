#!/usr/bin/env python3
"""
link-claude-memory.py
Links vault/claude-memory/ into Claude Code's local memory directory.
Run once on each device after cloning the vault.

Usage:
    python scripts/link-claude-memory.py

What it does:
    Finds ~/.claude/projects/ directories, lets you pick the right one,
    then replaces its memory/ folder with a symlink/junction to vault/claude-memory/.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VAULT = Path(__file__).parent.parent
MEMORY_SRC = VAULT / "claude-memory"


def find_claude_projects():
    claude_dir = Path.home() / ".claude" / "projects"
    if not claude_dir.exists():
        return []
    return [p for p in claude_dir.iterdir() if p.is_dir()]


def main():
    if not MEMORY_SRC.exists():
        print(f"ERROR: {MEMORY_SRC} not found. Is this run from inside the vault?")
        sys.exit(1)

    projects = find_claude_projects()
    if not projects:
        print("No ~/.claude/projects/ directories found.")
        print("Open Claude Code in your project directory first, then re-run.")
        sys.exit(1)

    print("\n=== link-claude-memory.py ===\n")
    print(f"Memory source: {MEMORY_SRC}\n")
    print("Found Claude Code project directories:")
    for i, p in enumerate(projects):
        memory = p / "memory"
        status = "junction/symlink" if (memory.exists() and not memory.is_dir()) else \
                 "exists" if memory.exists() else "missing"
        print(f"  [{i+1}] {p.name}  (memory: {status})")

    print()
    raw = input("  Link which project? (number, or Enter to cancel): ").strip()
    if not raw or not raw.isdigit():
        print("  Cancelled.")
        sys.exit(0)

    idx = int(raw) - 1
    if idx < 0 or idx >= len(projects):
        print("  Invalid choice.")
        sys.exit(1)

    target = projects[idx] / "memory"

    if target.exists():
        confirm = input(f"  {target} exists. Remove and replace with link? [y/N]: ").strip().lower()
        if confirm != "y":
            print("  Cancelled.")
            sys.exit(0)
        if target.is_symlink() or (sys.platform == "win32" and not target.is_dir()):
            target.unlink()
        else:
            shutil.rmtree(target)

    if sys.platform == "win32":
        result = subprocess.run(
            f'mklink /J "{target}" "{MEMORY_SRC}"',
            shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}")
            print(f"  Try running as Administrator or create manually:")
            print(f'  mklink /J "{target}" "{MEMORY_SRC}"')
            sys.exit(1)
    else:
        target.symlink_to(MEMORY_SRC)

    print(f"\n  Linked: {target}")
    print(f"       -> {MEMORY_SRC}")
    print(f"\n  Claude Code will now read/write memory from vault/claude-memory/")
    print(f"  Sync it with: git -C \"{VAULT}\" push\n")


if __name__ == "__main__":
    main()
