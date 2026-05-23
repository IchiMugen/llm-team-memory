#!/usr/bin/env python3
"""
new-project.py
Creates a new project: vault entry + local CLAUDE.md + GitHub repo

Usage:
    python scripts/new-project.py <slug> ["description"] [--no-github]

Flags:
    --no-github   Skip GitHub repo creation even if gh CLI is available

Example:
    python scripts/new-project.py my-app "A description of my app"
    python scripts/new-project.py my-app "A description" --no-github
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPTS_DIR = Path(__file__).parent
VAULT_PATH = SCRIPTS_DIR.parent
TEMPLATES = SCRIPTS_DIR / "templates"
CONFIG_FILE = VAULT_PATH / ".vault-config.json"
DATE = datetime.now().strftime("%Y-%m-%d")
TIME = datetime.now().strftime("%H:%M")


def load_config():
    if not CONFIG_FILE.exists():
        print("✗ .vault-config.json not found. Run setup.py first.")
        sys.exit(1)
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def render(text, vars_):
    for k, v in vars_.items():
        text = text.replace(f"{{{{{k}}}}}", v)
    return text


def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ {cmd}")
        print(f"    {result.stderr.strip()}")
        return False
    return True


def slug_to_name(slug):
    return " ".join(w.capitalize() for w in slug.replace("-", " ").replace("_", " ").split())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_github = "--no-github" in sys.argv

    if not args:
        print("Usage: python new-project.py <slug> [\"description\"] [--no-github]")
        sys.exit(1)

    cfg = load_config()
    slug = args[0].lower().replace(" ", "-")
    desc = args[1] if len(args) > 1 else "No description yet"
    name = slug_to_name(slug)

    git_user = cfg.get("git_user", "")
    git_ssh = cfg.get("git_ssh_base", "")
    git_url = cfg.get("git_base_url", "")
    lead = cfg.get("lead_handle", "lead")
    vault = Path(cfg["vault_path"])

    vars_ = {
        "PROJECT_NAME":  name,
        "PROJECT_SLUG":  slug,
        "PROJECT_DESC":  desc,
        "GIT_USER":      git_user,
        "GIT_REPO_URL":  f"{git_url}/{slug}" if git_url else "",
        "GIT_SSH_URL":   f"{git_ssh}/{slug}.git" if git_ssh else "",
        "VAULT_PATH":    str(vault),
        "LEAD_HANDLE":   lead,
        "DATE":          DATE,
    }

    print(f"\n=== Creating project: {name} ({slug}) ===\n")

    # 1. Wiki entry
    wiki_dir = vault / "wiki" / "projects" / slug
    if wiki_dir.exists():
        print(f"  ⚠ Wiki entry already exists: wiki/projects/{slug}/")
    else:
        wiki_dir.mkdir(parents=True)
        src = TEMPLATES / "project-context.md"
        dst = wiki_dir / "context.md"
        dst.write_text(render(src.read_text(encoding="utf-8"), vars_), encoding="utf-8")
        print(f"  ✓ wiki/projects/{slug}/context.md")

    # 2. Register in index.md
    index = vault / "wiki" / "index.md"
    if index.exists():
        content = index.read_text(encoding="utf-8")
        if slug not in content:
            marker = "## Projects"
            insert = f"| {name} | [[projects/{slug}/context]] | planning | {DATE} |"
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if line.strip() == marker:
                    # find the table header row and insert after separator
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].startswith("|---"):
                            lines.insert(j+1, insert)
                            break
                    break
            index.write_text("\n".join(lines), encoding="utf-8")
            print(f"  ✓ wiki/index.md updated")

    # 3. tasks.md
    tasks = vault / "wiki" / "tasks.md"
    if tasks.exists():
        with open(tasks, "a", encoding="utf-8") as f:
            f.write(f"\n- [ ] {name}: initial setup and architecture @{lead} #{slug} priority:H\n")
        print(f"  ✓ wiki/tasks.md updated")

    # 4. Daily log — wiki/logs/YYYY-MM-DD.md (create if missing, append if exists)
    logs_dir = vault / "wiki" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log = logs_dir / f"{DATE}.md"
    entry = (
        f"## {TIME} | new-project.py | {slug}\n"
        f"**Done:** Project {name} created\n"
        f"**Changed:** wiki/index.md, wiki/tasks.md, wiki/projects/{slug}/context.md\n"
        f"**Decision:** none\n"
        f"**Next:** define architecture, fill context.md\n"
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
    print(f"  ✓ wiki/logs/{DATE}.md appended")

    # 5. Local project CLAUDE.md
    project_dir = vault.parent / slug
    project_dir.mkdir(exist_ok=True)
    claude_dst = project_dir / "CLAUDE.md"
    if claude_dst.exists():
        print(f"  ⚠ CLAUDE.md already exists in {project_dir}")
    else:
        src = TEMPLATES / "project-CLAUDE.md"
        claude_dst.write_text(render(src.read_text(encoding="utf-8"), vars_), encoding="utf-8")
        print(f"  ✓ {project_dir}/CLAUDE.md")

    # 6. GitHub repo
    if git_user and shutil.which("gh") and not no_github:
        check = subprocess.run(
            f"gh repo view {git_user}/{slug}",
            shell=True, capture_output=True
        )
        if check.returncode == 0:
            print(f"  ⚠ GitHub repo already exists: {git_user}/{slug}")
        else:
            ok = run(
                f'gh repo create {git_user}/{slug} --private --description "{desc}"'
            )
            if ok:
                print(f"  ✓ GitHub repo created: {git_url}/{slug}")
                # init and push
                readme = project_dir / "README.md"
                readme.write_text(
                    f"# {name}\n> {desc}\n\n"
                    f"## Vault\n"
                    f"Context: `vault/wiki/projects/{slug}/`  \n"
                    f"Contract: `CLAUDE.md` (read before starting any session)\n",
                    encoding="utf-8"
                )
                run("git init && git checkout -b main", cwd=project_dir)
                run("git add .", cwd=project_dir)
                run(f'git commit -m "init: {slug}"', cwd=project_dir)
                run(f"git remote add origin {git_ssh}/{slug}.git", cwd=project_dir)
                run("git push -u origin main", cwd=project_dir)
                print(f"  ✓ Initial commit pushed")
    elif git_user and not no_github:
        print(f"  ⚠ gh CLI not found — create repo manually:")
        print(f"    gh repo create {git_user}/{slug} --private")

    # Done
    print(f"\n=== Done: {name} ===\n")
    print(f"  Vault:   {vault}/wiki/projects/{slug}/")
    if git_url:
        print(f"  GitHub:  {git_url}/{slug}")
    print(f"  Local:   {project_dir}/")
    print(f"\n  Start a session:")
    print(f'  cd {project_dir} && claude  →  "Read CLAUDE.md then continue"\n')


if __name__ == "__main__":
    main()
