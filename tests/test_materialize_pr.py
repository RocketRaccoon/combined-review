# tests/test_materialize_pr.py
"""Tests for materialize-scope.py PR scope.

Simulates `gh pr checkout` by hand-applying the head SHA inside the worktree,
since we don't have GitHub in the test loop.
"""
import json
import subprocess
from pathlib import Path

from tests.conftest import run_script


def test_pr_stale_snapshot_failure(tmp_repo, fake_bin):
    # gh pr checkout: do nothing (worktree stays at the initial commit).
    # The PR scope wants head_sha=<nonexistent SHA>, which should fail loudly.
    gh = fake_bin / "gh"
    gh.write_text('#!/bin/sh\nexit 0\n')
    gh.chmod(0o755)
    scope = {
        "kind": "pr", "pr_number": 99,
        "base_ref_name": "main", "head_ref_name": "feature",
        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
        "base_sha": "0" * 40, "head_sha": "f" * 40, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "force-pushed" in r.stderr.lower() or "stale" in r.stderr.lower() or "unreachable" in r.stderr.lower()


def test_pr_happy_path(tmp_repo, fake_bin):
    # Set up: initial commit on main; create feature branch with a commit;
    # capture both SHAs. Make gh pr checkout a no-op (worktree is already
    # at the head via our test setup) — and skip the base-repo fetch by
    # using the local repo's URL.
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    (tmp_repo / "f.py").write_text("z = 3\n")
    subprocess.run(["git", "add", "f.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    # Fake `gh pr checkout` resets the worktree to head_sha
    gh = fake_bin / "gh"
    gh.write_text(
        '#!/bin/sh\n'
        '# only handle `gh pr checkout`; defer to git for the rest\n'
        f'if [ "$1" = "pr" ] && [ "$2" = "checkout" ]; then\n'
        f'  git -C "$PWD" reset --hard {head_sha} >/dev/null\n'
        '  exit 0\n'
        'fi\n'
        'exit 1\n'
    )
    gh.chmod(0o755)
    scope = {
        "kind": "pr", "pr_number": 1,
        "base_ref_name": "main", "head_ref_name": "feature",
        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
        "base_sha": base_sha, "head_sha": head_sha, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "pr"
    assert any(f["path"] == "f.py" for f in out["changed_files"])
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)
