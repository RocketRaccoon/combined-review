# tests/test_cleanup_worktree.py
"""Tests for cleanup-worktree.sh — triple-assertion gate before removal."""
import subprocess
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def cleanup(repo, worktree):
    return subprocess.run(
        [str(SCRIPTS_DIR / "cleanup-worktree.sh"), str(repo), str(worktree)],
        capture_output=True, text=True,
    )


def test_cleanup_removes_legitimate_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    wt = tmp_path / "combined-review-x-abcdef"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=tmp_repo, check=True)
    assert wt.exists()
    r = cleanup(tmp_repo, wt)
    assert r.returncode == 0, r.stderr
    assert not wt.exists()


def test_cleanup_refuses_repo_root(tmp_repo):
    r = cleanup(tmp_repo, tmp_repo)
    assert r.returncode != 0
    assert "refus" in r.stderr.lower() or "root" in r.stderr.lower()


def test_cleanup_refuses_arbitrary_directory(tmp_repo, tmp_path):
    arbitrary = tmp_path / "not-a-worktree"
    arbitrary.mkdir()
    r = cleanup(tmp_repo, arbitrary)
    assert r.returncode != 0
    assert arbitrary.exists()  # we DID NOT delete it


def test_cleanup_skips_when_marker_present(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    wt = tmp_path / "combined-review-x-keepme"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=tmp_repo, check=True)
    (wt / ".combined-review-keep").touch()
    r = cleanup(tmp_repo, wt)
    # We expect non-zero (refused) AND the worktree still exists.
    assert r.returncode != 0
    assert wt.exists()
