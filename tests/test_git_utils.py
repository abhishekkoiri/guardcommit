import subprocess
from pathlib import Path
import pytest
from guardcommit.git_utils import is_git_repository, get_staged_files, get_staged_diff


def test_is_git_repo_current(tmp_path):
    assert not is_git_repository(cwd=tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert is_git_repository(cwd=tmp_path)


def test_staged_files_and_diff(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)

    assert get_staged_files(cwd=tmp_path) == []

    test_file = tmp_path / "hello.py"
    test_file.write_text("print('hello world')\n", encoding="utf-8")
    subprocess.run(["git", "add", "hello.py"], cwd=tmp_path, check=True)

    staged = get_staged_files(cwd=tmp_path)
    assert staged == ["hello.py"]

    diff = get_staged_diff(cwd=tmp_path)
    assert "+print('hello world')" in diff
