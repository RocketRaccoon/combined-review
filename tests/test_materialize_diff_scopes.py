# tests/test_materialize_diff_scopes.py
"""Tests for materialize-scope.py — base and commit scopes (worktree-based)."""
import json
import subprocess
from pathlib import Path

from tests.conftest import run_script


def base_scope(repo, **overrides):
    s = {
        "kind": None, "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    s.update(overrides)
    return s


def add_commit(repo, path, content, msg):
    (repo / path).write_text(content)
    subprocess.run(["git", "add", path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=repo, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()


def test_base_scope_three_dot_diff(tmp_repo):
    # main has initial commit; feature branches off, gets one commit
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    head_sha = add_commit(tmp_repo, "feature.py", "x = 1\n", "feat: add feature.py")
    scope = base_scope(tmp_repo, kind="base", base_sha=base_sha, head_sha=head_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "base"
    assert out["has_reviewable_changes"] is True
    assert any(f["path"] == "feature.py" for f in out["changed_files"])
    # worktree was created and recorded
    assert out["worktree_path"]  # truthy
    assert Path(out["worktree_path"]).exists()
    # cleanup
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)


def test_commit_scope(tmp_repo):
    sha = add_commit(tmp_repo, "added.py", "y = 2\n", "feat: added.py")
    scope = base_scope(tmp_repo, kind="commit", commit_sha=sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "commit"
    assert any(f["path"] == "added.py" for f in out["changed_files"])
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)


def test_commit_scope_root_commit_errors(tmp_repo):
    # The very first commit in tmp_repo has no parent — it's a root commit.
    root_sha = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        cwd=tmp_repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    scope = base_scope(tmp_repo, kind="commit", commit_sha=root_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "root commit" in r.stderr.lower()
    # Critical: no worktree leak even though make_worktree() succeeded
    leftover = [
        line for line in subprocess.run(
            ["git", "worktree", "list", "--porcelain"], cwd=tmp_repo,
            capture_output=True, text=True,
        ).stdout.splitlines() if "combined-review-" in line
    ]
    assert leftover == []


def test_commit_scope_merge_commit_errors(tmp_repo):
    # Build a merge commit on tmp_repo
    subprocess.run(["git", "checkout", "-q", "-b", "side"], cwd=tmp_repo, check=True)
    (tmp_repo / "side.py").write_text("s = 1\n")
    subprocess.run(["git", "add", "side.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "side commit"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "checkout", "-q", "-"], cwd=tmp_repo, check=True)  # back to default
    (tmp_repo / "main.py").write_text("m = 1\n")
    subprocess.run(["git", "add", "main.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "main commit"], cwd=tmp_repo, check=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "-m", "merge", "side"],
        cwd=tmp_repo, capture_output=True, text=True, check=True,
    )
    merge_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True,
    ).stdout.strip()
    scope = base_scope(tmp_repo, kind="commit", commit_sha=merge_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "merge commit" in r.stderr.lower()
