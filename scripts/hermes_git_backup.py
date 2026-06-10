#!/usr/bin/env python3
"""Backup valuable Hermes-produced artifacts to a GitHub repo.

Safety policy:
- Never copy secrets: .env, auth.json, credentials, tokens, raw logs, raw sessions DB/json.
- Prefer curated outputs/state/scripts/skills over runtime caches.
- Keep the repo deterministic: mirror selected files into a clean worktree, then commit if changed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(r"C:/Users/jax/AppData/Local/hermes")
REPO_DIR = HERMES_HOME / "backups" / "hermes-git"
REMOTE_URL = "https://github.com/hhive/hermes.git"

INCLUDE_FILES = [
    "a_stock_paper_portfolio.json",
    "a_stock_research_framework.md",
    "cron/jobs.json",
    "gateway_state.json",
]
INCLUDE_DIRS = [
    "scripts",
    "cron/output",
    "skills",
]
EXCLUDE_DIR_NAMES = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    "cache",
    "logs",
    "sessions",
    "weixin",
    "auth",
    "backups",
    "hermes-agent",
}
EXCLUDE_FILE_SUFFIXES = {".pyc", ".pyo", ".log", ".db", ".db-wal", ".db-shm", ".lock", ".pid"}
EXCLUDE_FILE_NAMES = {".env", "auth.json", "state.db", "state.db-wal", "state.db-shm", "sessions.json", "channel_directory.json", ".usage.json", ".curator_state", ".bundled_manifest", "lock.json", "taps.json"}


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=check)


def ensure_repo() -> None:
    REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
    if not (REPO_DIR / ".git").exists():
        try:
            run(["git", "clone", REMOTE_URL, str(REPO_DIR)], check=True)
        except subprocess.CalledProcessError:
            REPO_DIR.mkdir(parents=True, exist_ok=True)
            run(["git", "init"], cwd=REPO_DIR)
            run(["git", "remote", "add", "origin", REMOTE_URL], cwd=REPO_DIR)
    else:
        run(["git", "remote", "set-url", "origin", REMOTE_URL], cwd=REPO_DIR)
    run(["git", "config", "user.name", "Hermes Backup Bot"], cwd=REPO_DIR)
    run(["git", "config", "user.email", "hermes-backup@local"], cwd=REPO_DIR)


def safe_remove_tree(path: Path) -> None:
    for child in path.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def should_copy_file(path: Path) -> bool:
    name = path.name
    lower = name.lower()
    if name in EXCLUDE_FILE_NAMES or lower in EXCLUDE_FILE_NAMES:
        return False
    if any(part in EXCLUDE_DIR_NAMES for part in path.parts):
        return False
    if path.suffix.lower() in EXCLUDE_FILE_SUFFIXES:
        return False
    if "token" in lower or "secret" in lower or "credential" in lower:
        return False
    return path.is_file()


def copy_file(src: Path, dest: Path) -> None:
    if not src.exists() or not should_copy_file(src):
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_dir(src: Path, dest: Path) -> None:
    if not src.exists() or not src.is_dir():
        return
    for path in src.rglob("*"):
        rel = path.relative_to(src)
        if any(part in EXCLUDE_DIR_NAMES for part in rel.parts):
            continue
        if path.is_file() and should_copy_file(path):
            copy_file(path, dest / rel)


def write_manifest() -> None:
    manifest = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S %z"),
        "source_home": str(HERMES_HOME),
        "policy": {
            "included_files": INCLUDE_FILES,
            "included_dirs": INCLUDE_DIRS,
            "excluded": sorted(EXCLUDE_DIR_NAMES | EXCLUDE_FILE_NAMES),
            "note": "Secrets, auth, logs, raw sessions, runtime DBs, caches, and installed source/venv are intentionally excluded.",
        },
    }
    (REPO_DIR / "BACKUP_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    readme = """# Hermes Backup

This repository is populated automatically from the local Hermes home directory.

Backed up:
- Curated scripts under `scripts/`
- Cron job definitions and cron output under `cron/`
- Agent-created or customized skills under `skills/`
- A-share paper-trading portfolio/research state

Intentionally excluded:
- `.env`, tokens, credentials, `auth.json`
- Raw logs and raw sessions
- Runtime DB/lock/cache files
- Installed Hermes source checkout and virtualenv
"""
    (REPO_DIR / "README.md").write_text(readme, encoding="utf-8")


def stage_content() -> None:
    safe_remove_tree(REPO_DIR)
    for rel in INCLUDE_FILES:
        copy_file(HERMES_HOME / rel, REPO_DIR / rel)
    for rel in INCLUDE_DIRS:
        copy_dir(HERMES_HOME / rel, REPO_DIR / rel)
    write_manifest()
    gitignore = """.env
auth.json
*.log
*.db
*.db-wal
*.db-shm
*.lock
*.pid
__pycache__/
*.pyc
cache/
logs/
sessions/
weixin/
hermes-agent/
backups/
"""
    (REPO_DIR / ".gitignore").write_text(gitignore, encoding="utf-8")


def commit_and_push() -> int:
    run(["git", "add", "-A"], cwd=REPO_DIR)
    status = run(["git", "status", "--porcelain"], cwd=REPO_DIR).stdout.strip()
    if not status:
        print("Hermes backup: no changes to commit.")
        return 0
    message = "backup: Hermes artifacts " + datetime.now().strftime("%Y-%m-%d %H:%M")
    run(["git", "commit", "-m", message], cwd=REPO_DIR)
    branch = run(["git", "branch", "--show-current"], cwd=REPO_DIR).stdout.strip() or "main"
    if branch != "main":
        run(["git", "branch", "-M", "main"], cwd=REPO_DIR)
        branch = "main"
    push = run(["git", "push", "-u", "origin", branch], cwd=REPO_DIR, check=False)
    if push.returncode != 0:
        print("Hermes backup: commit created but push failed.")
        print((push.stderr or push.stdout).strip())
        return push.returncode
    print("Hermes backup: committed and pushed successfully.")
    print(message)
    return 0


def main() -> int:
    try:
        ensure_repo()
        stage_content()
        return commit_and_push()
    except subprocess.CalledProcessError as exc:
        print("Hermes backup failed:", " ".join(exc.cmd))
        print((exc.stderr or exc.stdout or "").strip())
        return exc.returncode or 1
    except Exception as exc:
        print(f"Hermes backup failed: {exc.__class__.__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
