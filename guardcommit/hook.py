"""
Git pre-commit hook manager for GuardCommit.
Installs offline secret and leak protection directly into .git/hooks/pre-commit.
"""

from __future__ import annotations
import os
import stat
from pathlib import Path
from guardcommit.git_utils import get_git_root, is_git_repository

HOOK_SCRIPT_CONTENT = """#!/bin/sh
# GuardCommit Pre-Commit Hook: Secret Leak & Safety Guard
# Generated automatically by `guardcommit hook install`

echo "🔍 [GuardCommit] Scanning staged changes for credentials & sensitive files..."

if command -v guardcommit >/dev/null 2>&1; then
    guardcommit scan --exit-on-error
    EXIT_CODE=$?
elif command -v python >/dev/null 2>&1; then
    python -m guardcommit.cli scan --exit-on-error
    EXIT_CODE=$?
else
    echo "⚠️ GuardCommit CLI not found in PATH. Skipping hook."
    exit 0
fi

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ [GuardCommit] Commit aborted due to security risk. Remove sensitive data or use --no-verify."
    exit 1
fi

echo "✅ [GuardCommit] Clean! Proceeding with commit."
exit 0
"""


def install_git_hook() -> Path:
    """Install pre-commit hook into the current git repository."""
    if not is_git_repository():
        raise RuntimeError("Current directory is not a Git repository.")

    root = get_git_root()
    hooks_dir = root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_file = hooks_dir / "pre-commit"
    with open(hook_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK_SCRIPT_CONTENT)

    try:
        st = os.stat(hook_file)
        os.chmod(hook_file, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass

    return hook_file


def uninstall_git_hook() -> bool:
    """Remove pre-commit hook from the current git repository."""
    if not is_git_repository():
        raise RuntimeError("Current directory is not a Git repository.")

    root = get_git_root()
    hook_file = root / ".git" / "hooks" / "pre-commit"
    if hook_file.exists():
        hook_file.unlink()
        return True
    return False
