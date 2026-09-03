"""
Git utilities for extracting staged diffs, checking repository status, and committing.
"""

from __future__ import annotations
import subprocess
from pathlib import Path
from typing import List, Optional


class GitError(Exception):
    """Custom exception for Git execution errors."""
    pass


def _run_git_command(args: List[str], cwd: Optional[Path] = None) -> str:
    """Run a git CLI command and return its stdout stripped."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or Path.cwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace"
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: git {' '.join(args)}\nError: {e.stderr.strip()}") from e
    except FileNotFoundError:
        raise GitError("Git executable not found on PATH. Please ensure git is installed.")


def is_git_repository(cwd: Optional[Path] = None) -> bool:
    """Check if the current or specified path is inside a git work tree."""
    try:
        out = _run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
        return out.lower() == "true"
    except GitError:
        return False


def get_git_root(cwd: Optional[Path] = None) -> Path:
    """Return the root path of the current git repository."""
    out = _run_git_command(["rev-parse", "--show-toplevel"], cwd=cwd)
    return Path(out)


def get_current_branch(cwd: Optional[Path] = None) -> str:
    """Get the current branch name."""
    try:
        return _run_git_command(["branch", "--show-current"], cwd=cwd)
    except GitError:
        return "HEAD (detached)"


def get_staged_files(cwd: Optional[Path] = None) -> List[str]:
    """Get list of files currently staged for commit."""
    out = _run_git_command(["diff", "--cached", "--name-only"], cwd=cwd)
    if not out:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def get_staged_diff(cwd: Optional[Path] = None) -> str:
    """Get unified diff of staged changes."""
    return _run_git_command(["diff", "--cached", "-U3"], cwd=cwd)


def get_branch_diff_against_base(base_branch: str = "main", cwd: Optional[Path] = None) -> str:
    """Get unified diff of current branch compared to a base branch for PR generation."""
    try:
        return _run_git_command(["diff", f"{base_branch}...HEAD"], cwd=cwd)
    except GitError:
        # Fallback to master if main doesn't exist
        if base_branch == "main":
            return _run_git_command(["diff", "master...HEAD"], cwd=cwd)
        raise


def execute_commit(message: str, cwd: Optional[Path] = None) -> str:
    """Execute git commit with the provided commit message."""
    return _run_git_command(["commit", "-m", message], cwd=cwd)
