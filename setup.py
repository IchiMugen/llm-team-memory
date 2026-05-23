#!/usr/bin/env python3
"""
llm-team-memory setup wizard
Karpathy-style shared memory for teams using Claude Code / Codex

Usage:
    python setup.py

Requirements:
    Python 3.8+  (no external dependencies for setup)
    git
    gh CLI (optional, for GitHub repo creation)
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Windows terminals often default to cp1251 — force UTF-8 so box-drawing
# characters and checkmarks don't crash the script.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

# ── Config ───────────────────────────────────────────────────────────────────

VERSION = "1.0.0"
TEMPLATE_DIR = Path(__file__).parent / "vault_template"
SCRIPTS_DIR = Path(__file__).parent / "scripts"

AGENTS = ["Claude Code", "Codex", "Cursor", "Windsurf", "Other"]
GIT_HOSTS = ["GitHub", "Skip (local only)"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def banner():
    print("\n" + "═" * 60)
    print("  llm-team-memory  v" + VERSION)
    print("  Karpathy-style shared memory for AI-assisted teams")
    print("═" * 60 + "\n")

def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    while True:
        val = input(f"  {prompt}{suffix}: ").strip()
        if val:
            return val
        if default is not None:
            return default
        print("  ↳ Required.")

def ask_choice(prompt, options, default=0):
    print(f"\n  {prompt}")
    for i, opt in enumerate(options):
        marker = "●" if i == default else "○"
        print(f"    {marker} [{i+1}] {opt}")
    while True:
        raw = input(f"  Choice [1-{len(options)}] (default {default+1}): ").strip()
        if not raw:
            return options[default]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  ↳ Enter a number between 1 and {len(options)}")

def ask_list(prompt, hint="comma-separated"):
    print(f"\n  {prompt} ({hint})")
    raw = input("  → ").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]

def ask_yn(prompt, default=True):
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"  {prompt} {suffix}: ").strip().lower()
    if not raw:
        return default
    return raw.startswith("y")

def run(cmd, cwd=None, check=True):
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    if check and result.returncode != 0:
        print(f"  ✗ Command failed: {cmd}")
        print(f"    {result.stderr.strip()}")
        return False
    return result.returncode == 0

def check_dependency(name):
    return shutil.which(name) is not None

# ── Template rendering ────────────────────────────────────────────────────────

def render(text, vars_):
    for k, v in vars_.items():
        text = text.replace(f"{{{{{k}}}}}", v)
    return text

def copy_template(src, dst, vars_):
    dst.parent.mkdir(parents=True, exist_ok=True)
    content = src.read_text(encoding="utf-8")
    dst.write_text(render(content, vars_), encoding="utf-8")

# ── Steps ─────────────────────────────────────────────────────────────────────

def collect_config():
    print("  Let's configure your team vault.\n")

    config = {}

    # Vault location
    default_vault = str(Path.home() / "vault")
    config["vault_path"] = Path(ask("Vault location", default_vault)).expanduser().resolve()

    # Projects base
    default_projects = str(config["vault_path"].parent)
    config["projects_base"] = Path(ask("Where to create new projects", default_projects)).expanduser().resolve()

    # Team lead
    config["lead_handle"] = ask("Your handle / username", "lead")
    config["lead_agent"] = ask_choice("Your AI agent", AGENTS)
    config["lead_tz"] = ask("Your timezone", "UTC+0")

    # Team members
    print("\n  Team members (besides you):")
    members = []
    while True:
        handle = input("  + Member handle (or Enter to skip): ").strip()
        if not handle:
            break
        agent = ask_choice(f"  {handle}'s agent", AGENTS)
        members.append({"handle": handle, "agent": agent})
    config["members"] = members

    # Git hosting
    config["git_host"] = ask_choice("Git hosting", GIT_HOSTS)

    if config["git_host"] == "GitHub":
        config["git_user"] = ask("GitHub username")
        config["git_base_url"] = f"https://github.com/{config['git_user']}"
        config["git_ssh_base"] = f"git@github.com:{config['git_user']}"
    else:
        config["git_user"] = ""
        config["git_base_url"] = ""
        config["git_ssh_base"] = ""

    # Vault sync
    config["use_vps_sync"] = ask_yn("Sync vault via self-hosted VPS (SSH)?", default=False)
    if config["use_vps_sync"]:
        config["vps_host"] = ask("VPS host (IP or domain)")
        config["vps_user"] = ask("VPS SSH user", "ubuntu")
        config["vps_repo_path"] = ask("Path on VPS for bare repo", "~/repos/vault.git")
    else:
        config["vps_host"] = ""
        config["vps_user"] = ""
        config["vps_repo_path"] = ""

    # Languages
    config["default_lang"] = ask("Primary language(s)", "Python")

    config["date"] = datetime.now().strftime("%Y-%m-%d")

    return config


def build_vars(config):
    """Flatten config into template variables."""
    lead = config["lead_handle"]
    git_user = config.get("git_user", "")
    git_base = config.get("git_base_url", "")
    git_ssh = config.get("git_ssh_base", "")
    vps = ""
    if config.get("use_vps_sync"):
        path = config["vps_repo_path"]
        # Ensure there's a / separator between host and path (~/... needs /~/)
        if not path.startswith("/"):
            path = "/" + path
        vps = f"ssh://{config['vps_user']}@{config['vps_host']}{path}"

    # Team table rows — always 4 columns to match the header
    github_col = f"@{git_user}" if git_user else "—"
    team_rows = f"| {lead} | Lead | {config['lead_agent']} | {github_col} |"
    for m in config.get("members", []):
        team_rows += f"\n| {m['handle']} | Developer | {m['agent']} | — |"

    # Team file list for index
    team_files = f"| [[team/{lead}]] | {lead} | Lead |"
    for m in config.get("members", []):
        team_files += f"\n| [[team/{m['handle']}]] | {m['handle']} | Developer |"

    return {
        "LEAD_HANDLE":   lead,
        "LEAD_AGENT":    config["lead_agent"],
        "LEAD_TZ":       config["lead_tz"],
        "GIT_USER":      git_user,
        "GIT_BASE_URL":  git_base,
        "GIT_SSH_BASE":  git_ssh,
        "VPS_REMOTE":    vps,
        "DEFAULT_LANG":  config["default_lang"],
        "DATE":          config["date"],
        "TEAM_ROWS":     team_rows,
        "TEAM_FILES":    team_files,
        "VAULT_PATH":    str(config["vault_path"]),
        "GIT_HOST":      config["git_host"],
    }


def create_vault(config, vars_):
    vault = config["vault_path"]
    print(f"\n  Creating vault at {vault} ...")

    if vault.exists() and any(vault.iterdir()):
        if not ask_yn(f"{vault} is not empty. Continue?", default=False):
            print("  ↳ Aborted.")
            sys.exit(0)

    # Copy all template files
    for src in TEMPLATE_DIR.rglob("*"):
        if src.is_file():
            rel = src.relative_to(TEMPLATE_DIR)
            dst = vault / rel
            copy_template(src, dst, vars_)

    # Create team pages
    team_template = vault / "wiki" / "team" / "_template.md"
    lead_page = vault / "wiki" / "team" / f"{config['lead_handle']}.md"
    if team_template.exists():
        content = team_template.read_text(encoding="utf-8")
        content = render(content, {
            "HANDLE":  config["lead_handle"],
            "ROLE":    "Lead",
            "AGENT":   config["lead_agent"],
            "TZ":      config["lead_tz"],
            "GIT_HANDLE": config.get("git_user", "—"),
        })
        lead_page.write_text(content, encoding="utf-8")

    for m in config.get("members", []):
        page = vault / "wiki" / "team" / f"{m['handle']}.md"
        content = team_template.read_text(encoding="utf-8")
        content = render(content, {
            "HANDLE":     m["handle"],
            "ROLE":       "Developer",
            "AGENT":      m["agent"],
            "TZ":         "—",
            "GIT_HANDLE": "—",
        })
        page.write_text(content, encoding="utf-8")

    # Create initial daily log entry (logs/<date>.md, not a template — filename must be real)
    logs_dir = vault / "wiki" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"{config['date']}.md"
    log_file.write_text(
        f"# Log — {config['date']}\n\n"
        f"> Append-only. Never edit past entries.\n"
        f"> Format: HH:MM | handle | project-slug\n\n"
        f"---\n\n"
        f"## setup | vault\n"
        f"**Done:** Vault initialized\n"
        f"**Changed:** all files\n"
        f"**Decision:** none\n"
        f"**Next:** open in Obsidian, install Obsidian Git plugin, create first project\n"
        f"---\n",
        encoding="utf-8",
    )

    # Create raw/ directory (immutable source layer)
    raw_dir = vault / "raw"
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / ".gitkeep").touch()

    # Copy scripts
    scripts_dst = vault / "scripts"
    scripts_dst.mkdir(exist_ok=True)
    for src in SCRIPTS_DIR.rglob("*"):
        if src.is_file():
            rel = src.relative_to(SCRIPTS_DIR)
            dst = scripts_dst / rel
            copy_template(src, dst, vars_)
            if dst.suffix == ".sh" or dst.stem in ("new-project", "vault-sync-setup"):
                dst.chmod(0o755)

    # Make new-project.py executable
    np = scripts_dst / "new-project.py"
    if np.exists():
        np.chmod(0o755)

    print(f"  ✓ Vault structure created ({sum(1 for _ in vault.rglob('*') if _.is_file())} files)")


def init_git(config):
    vault = config["vault_path"]

    if not check_dependency("git"):
        print("  ✗ git not found — skipping git init")
        return

    print("\n  Initialising git ...")
    run("git init", cwd=vault)
    # Set default branch to main without relying on git version or global config
    run("git symbolic-ref HEAD refs/heads/main", cwd=vault)
    run("git add .", cwd=vault)
    run('git commit -m "vault: initial setup (llm-team-memory)"', cwd=vault)
    print("  ✓ Initial commit done")

    if config.get("use_vps_sync") and config.get("vps_host"):
        path = config["vps_repo_path"]
        if not path.startswith("/"):
            path = "/" + path
        remote = f"ssh://{config['vps_user']}@{config['vps_host']}{path}"
        run(f"git remote add origin {remote}", cwd=vault)
        print(f"  ✓ Remote set to {remote}")
        print("  → Run on VPS first: bash scripts/vault-sync-setup.sh")
        print("  → Then: git push -u origin main")
    elif config.get("git_host") == "GitHub" and check_dependency("gh"):
        if ask_yn("  Create GitHub repo for vault?", default=False):
            run(f'gh repo create {config["git_user"]}/vault --private --description "Karpathy-style shared memory for AI-assisted teams"', cwd=vault)
            run(f'git remote add origin {config["git_ssh_base"]}/vault.git', cwd=vault)
            run("git push -u origin main", cwd=vault)
            print(f"  ✓ Pushed to {config['git_base_url']}/vault")


def write_config(config, vars_):
    """Save non-sensitive config for new-project.py to read."""
    cfg = {
        "vault_path":    str(config["vault_path"]),
        "projects_base": str(config.get("projects_base", config["vault_path"].parent)),
        "git_user":      config.get("git_user", ""),
        "git_host":      config["git_host"],
        "git_ssh_base":  config.get("git_ssh_base", ""),
        "git_base_url":  config.get("git_base_url", ""),
        "lead_handle":   config["lead_handle"],
        "default_lang":  config["default_lang"],
    }
    cfg_path = config["vault_path"] / ".vault-config.json"
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(f"  ✓ Config saved to .vault-config.json")


def print_summary(config):
    vault = config["vault_path"]
    print("\n" + "═" * 60)
    print("  ✓ Setup complete!")
    print("═" * 60)
    print(f"\n  Vault:   {vault}")
    if config.get("git_base_url"):
        print(f"  GitHub:  {config['git_base_url']}/vault")
    print(f"\n  Next steps:")
    print(f"  1. Open {vault} in Obsidian as a vault")
    print(f"  2. Install Obsidian Git plugin")
    print(f"     Settings: pull on startup ✓, auto-pull: 5min")
    print(f"  3. In Claude Code / Codex:")
    print(f'     "Read CLAUDE.md then continue"')
    print(f"  4. Create your first project:")
    print(f"     python {vault}/scripts/new-project.py my-project")
    print(f"\n  Read ONBOARDING.md to share with team members.")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    banner()

    try:
        config = collect_config()
        vars_ = build_vars(config)

        print("\n" + "─" * 60)
        print("  Ready to create vault. Summary:")
        print(f"    Path:    {config['vault_path']}")
        print(f"    Lead:    {config['lead_handle']} ({config['lead_agent']})")
        print(f"    Members: {len(config.get('members', []))}")
        print(f"    Git:     {config['git_host']}")
        if config.get("git_user"):
            print(f"    User:    {config['git_user']}")
        print("─" * 60)

        if not ask_yn("\n  Proceed?"):
            print("  Aborted.")
            sys.exit(0)

        create_vault(config, vars_)
        init_git(config)
        write_config(config, vars_)
        print_summary(config)

    except (KeyboardInterrupt, EOFError):
        print("\n\n  Interrupted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
