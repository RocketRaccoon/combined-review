# tests/test_resolve_scope_autodetect.py
"""Tests for resolve-scope.py auto-detect when scope_flag is None."""
import json
import subprocess
from tests.conftest import run_script
from tests.test_resolve_scope_pr import FAKE_GH_JSON, write_fake_gh


def make_cfg_auto():
    return {
        "scope_flag": None, "pr_number": None, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def make_dirty(repo):
    (repo / "dirty.txt").write_text("uncommitted\n")


def fake_gh_no_pr(fake_bin):
    """`gh pr view` exits 1 (no PR for this branch)."""
    gh = fake_bin / "gh"
    gh.write_text('#!/bin/sh\necho "no pull requests found" >&2\nexit 1\n')
    gh.chmod(0o755)


def test_autodetect_dirty_no_pr_implies_uncommitted(tmp_repo, fake_bin):
    fake_gh_no_pr(fake_bin)
    make_dirty(tmp_repo)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["kind"] == "uncommitted"


def test_autodetect_dirty_plus_pr_errors(tmp_repo, fake_bin):
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    make_dirty(tmp_repo)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "ambig" in r.stderr.lower() or "uncommitted" in r.stderr.lower()


def test_autodetect_clean_with_pr_implies_pr(tmp_repo, fake_bin):
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["kind"] == "pr"


def test_autodetect_default_branch_clean_errors(tmp_repo, fake_bin):
    fake_gh_no_pr(fake_bin)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "nothing" in r.stderr.lower() or "default" in r.stderr.lower()


def fake_gh_auth_required(fake_bin):
    """`gh pr view` exits non-zero with an auth message — distinct from 'no PR'."""
    gh = fake_bin / "gh"
    gh.write_text(
        '#!/bin/sh\necho "error: not authenticated. Run gh auth login" >&2\nexit 4\n'
    )
    gh.chmod(0o755)


def test_autodetect_gh_auth_failure_halts_not_silently_uncommitted(tmp_repo, fake_bin):
    """Regression for PR #3 follow-up review (smoke run).

    Previously `pr_for_current_branch()` returned None on every non-zero
    `gh pr view`. With expired auth + a dirty tree, auto-detect silently
    fell through to `uncommitted` instead of `pr` — the user reviewed the
    wrong scope and the report was misleading. Now: non-zero `gh pr view`
    that is NOT 'no pull requests found' halts auto-detect with a clean
    error message telling the user to fix auth OR pass an explicit scope."""
    fake_gh_auth_required(fake_bin)
    make_dirty(tmp_repo)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    # Must mention gh and the actionable fix
    assert "gh" in r.stderr.lower()
    assert "auth" in r.stderr.lower() or "explicit scope" in r.stderr.lower()
    # And must NOT have fallen through to uncommitted
    assert "uncommitted" not in r.stderr.lower() or "explicit scope" in r.stderr.lower()


def test_autodetect_gh_auth_failure_halts_on_clean_branch_too(tmp_repo, fake_bin):
    """Same regression but on a clean feature branch — pr_for_current_branch
    still must not silently say 'no PR' here either, or auto-detect would
    fall through to `base` against the default branch."""
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    fake_gh_auth_required(fake_bin)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "gh" in r.stderr.lower()


def test_autodetect_explicit_scope_unaffected_by_gh_auth(tmp_repo, fake_bin):
    """When the user passes an explicit scope flag, auto-detect (and the gh
    probe inside it) MUST be skipped — explicit scopes should work even
    with broken gh."""
    fake_gh_auth_required(fake_bin)
    make_dirty(tmp_repo)
    cfg = make_cfg_auto()
    cfg["scope_flag"] = "uncommitted"  # explicit
    r = run_script("resolve-scope.py", input=json.dumps(cfg), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["kind"] == "uncommitted"
