#!/usr/bin/env python3
"""
add-member.py
Adds a team member to the vault: GitHub invite + team page + CLAUDE.md entry.

Usage:
    python scripts/add-member.py <github-username>
    python scripts/add-member.py <github-username> --handle <nick> --agent "Cursor" --role Developer

Defaults:
    --handle   same as github-username
    --agent    Claude Code
    --role     Developer
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPTS_DIR = Path(__file__).parent
VAULT = SCRIPTS_DIR.parent
CONFIG_FILE = VAULT / ".vault-config.json"
DATE = datetime.now().strftime("%Y-%m-%d")
TIME = datetime.now().strftime("%H:%M")

AGENTS = ["Claude Code", "Codex", "Cursor", "Windsurf", "Other"]


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ERROR: {cmd}")
        print(f"  {result.stderr.strip()}")
        return None
    return result.stdout.strip()


def load_config():
    if not CONFIG_FILE.exists():
        print("ERROR: .vault-config.json not found.")
        sys.exit(1)
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def parse_args():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print(__doc__)
        sys.exit(1)

    github_user = args[0]
    handle = github_user
    agent = "Claude Code"
    role = "Developer"

    i = 1
    while i < len(args):
        if args[i] == "--handle" and i + 1 < len(args):
            handle = args[i + 1]; i += 2
        elif args[i] == "--agent" and i + 1 < len(args):
            agent = args[i + 1]; i += 2
        elif args[i] == "--role" and i + 1 < len(args):
            role = args[i + 1]; i += 2
        else:
            i += 1

    return github_user, handle, agent, role


def invite_collaborator(github_user, cfg):
    git_user = cfg.get("git_user", "")
    if not git_user:
        print("  SKIP: no GitHub user in config, skipping invite")
        return False

    repo = f"{git_user}/vault"
    print(f"  Inviting @{github_user} to {repo} ...")
    result = run(
        f'gh api repos/{repo}/collaborators/{github_user} -X PUT -f permission=push',
        check=False
    )
    if result is None:
        # gh api returns non-zero on 201 (invite sent) sometimes — check separately
        check = run(
            f'gh api repos/{repo}/collaborators/{github_user}',
            check=False
        )
        if check is None:
            print(f"  WARNING: Could not verify invite — check GitHub manually:")
            print(f"    https://github.com/{repo}/settings/access")
            return False

    print(f"  Invited. They will receive a GitHub email invitation.")
    return True


def create_team_page(handle, github_user, agent, role):
    template = VAULT / "wiki" / "team" / "_template.md"
    page = VAULT / "wiki" / "team" / f"{handle}.md"

    if page.exists():
        print(f"  SKIP: wiki/team/{handle}.md already exists")
        return

    if template.exists():
        content = template.read_text(encoding="utf-8")
        content = (content
            .replace("{{HANDLE}}", handle)
            .replace("{{ROLE}}", role)
            .replace("{{AGENT}}", agent)
            .replace("{{TZ}}", "—")
            .replace("{{GIT_HANDLE}}", github_user))
        page.write_text(content, encoding="utf-8")
    else:
        page.write_text(
            f"# {handle} — {role}\n\n"
            f"## Agent\n{agent}\n\n"
            f"## GitHub\n@{github_user}\n\n"
            f"## Timezone\n—\n",
            encoding="utf-8",
        )
    print(f"  Created wiki/team/{handle}.md")


def add_to_claude_md(handle, agent, role, github_user):
    claude = VAULT / "CLAUDE.md"
    content = claude.read_text(encoding="utf-8")

    row = f"| {handle} | {role} | {agent} | @{github_user} |"
    if handle in content:
        print(f"  SKIP: {handle} already in CLAUDE.md")
        return

    # Insert before the closing ">" of the team table
    marker = "> To add a member:"
    content = content.replace(marker, f"{row}\n{marker}")
    claude.write_text(content, encoding="utf-8")
    print(f"  Added {handle} to CLAUDE.md team table")


def append_log(handle, github_user):
    logs_dir = VAULT / "wiki" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log = logs_dir / f"{DATE}.md"
    entry = (
        f"## {TIME} | add-member.py | vault\n"
        f"**Done:** Added team member {handle} (@{github_user})\n"
        f"**Changed:** wiki/team/{handle}.md, CLAUDE.md\n"
        f"**Decision:** none\n"
        f"**Next:** member accepts GitHub invite and clones vault\n"
        f"---\n"
    )
    if not log.exists():
        log.write_text(
            f"# Log — {DATE}\n\n"
            f"> Append-only. Never edit past entries.\n"
            f"> Format: HH:MM | handle | project-slug\n\n"
            f"---\n\n" + entry,
            encoding="utf-8",
        )
    else:
        with open(log, "a", encoding="utf-8") as f:
            f.write("\n" + entry)


def push(handle):
    run(f'git -C "{VAULT}" add .', check=False)
    run(f'git -C "{VAULT}" commit -m "vault: add team member {handle}"', check=False)
    # push to all remotes that are reachable
    for remote in ["github", "origin"]:
        result = run(f'git -C "{VAULT}" push {remote} main', check=False)
        if result is not None:
            print(f"  Pushed to {remote}")


def main():
    github_user, handle, agent, role = parse_args()
    cfg = load_config()

    print(f"\n=== Adding member: {handle} (@{github_user}) ===\n")

    invite_collaborator(github_user, cfg)
    create_team_page(handle, github_user, agent, role)
    add_to_claude_md(handle, agent, role, github_user)
    append_log(handle, github_user)
    push(handle)

    print(f"\n=== Done ===\n")
    print(f"  {handle} will receive a GitHub invite at @{github_user}")
    print(f"  Once accepted, they clone:")
    print(f"    git clone https://github.com/{cfg.get('git_user','')}/vault vault")
    print(f"  Then open vault/ in Obsidian + install Obsidian Git plugin.")
    print()


if __name__ == "__main__":
    main()
