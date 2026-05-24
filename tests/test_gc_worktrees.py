# tests/test_gc_worktrees.py
"""Tests for gc-worktrees.sh — list-then-filter via git worktree list."""
import os
import subprocess
import time
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def gc(repo):
    return subprocess.run(
        [str(SCRIPTS_DIR / "gc-worktrees.sh"), str(repo)],
        capture_output=True, text=True,
    )


def make_aged_worktree(repo, tmp_path, name, age_hours):
    wt = tmp_path / name
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=repo, check=True)
    old = time.time() - (age_hours * 3600)
    os.utime(wt, (old, old))
    return wt


def test_gc_removes_old_combined_review(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    old_wt = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-aaa", 48)
    r = gc(tmp_repo)
    assert r.returncode == 0, r.stderr
    assert not old_wt.exists()


def test_gc_skips_marked_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    kept = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-keep", 48)
    (kept / ".combined-review-keep").touch()
    r = gc(tmp_repo)
    assert r.returncode == 0, r.stderr
    assert kept.exists()


def test_gc_skips_recent_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    recent = make_aged_worktree(tmp_repo, tmp_path, "combined-review-recent-bbb", 1)
    r = gc(tmp_repo)
    assert r.returncode == 0
    assert recent.exists()


def test_gc_skips_non_combined_review_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    other = make_aged_worktree(tmp_repo, tmp_path, "some-other-wt", 48)
    r = gc(tmp_repo)
    assert r.returncode == 0
    assert other.exists()
