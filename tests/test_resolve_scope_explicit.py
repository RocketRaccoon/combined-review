# tests/test_resolve_scope_explicit.py
"""Tests for resolve-scope.py — explicit scope flags only."""
import json
import subprocess
from tests.conftest import run_script


def resolve(cfg, cwd=None):
    r = run_script("resolve-scope.py", input=json.dumps(cfg), cwd=cwd)
    return r


def make_cfg(**kw):
    base = {
        "scope_flag": None, "pr_number": None, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    base.update(kw)
    return base


def test_uncommitted_scope(tmp_repo):
    (tmp_repo / "new.txt").write_text("x")
    r = resolve(make_cfg(scope_flag="uncommitted"), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "uncommitted"
    assert scope["repo_root"] == str(tmp_repo)
    assert scope["worktree_path"] is None
    assert scope["needs_clean_worktree"] is False


def test_base_scope_resolves_sha(tmp_repo):
    # Create a feature branch with one commit
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    (tmp_repo / "x.txt").write_text("y")
    subprocess.run(["git", "add", "x.txt"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
    r = resolve(make_cfg(scope_flag="base", base_branch="main"), cwd=tmp_repo)
    # git init default branch may be 'main' or 'master' depending on config
    if r.returncode != 0:
        # retry with detected default branch
        head = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
            cwd=tmp_repo, capture_output=True, text=True
        ).stdout.split()
        default = "master" if "master" in head else "main"
        r = resolve(make_cfg(scope_flag="base", base_branch=default), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "base"
    assert len(scope["base_sha"]) == 40
    assert len(scope["head_sha"]) == 40
    assert scope["base_sha"] != scope["head_sha"]
    assert scope["needs_clean_worktree"] is True


def test_commit_scope_resolves_sha(tmp_repo):
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    r = resolve(make_cfg(scope_flag="commit", commit_sha=sha), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "commit"
    assert scope["commit_sha"] == sha
    assert scope["needs_clean_worktree"] is True


def test_files_scope_passes_paths(tmp_repo):
    (tmp_repo / "spec.md").write_text("# spec")
    r = resolve(make_cfg(scope_flag="files", files=["spec.md"]), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "files"
    assert scope["files"] == ["spec.md"]
    assert scope["needs_clean_worktree"] is False


def test_files_scope_rejects_nonexistent(tmp_repo):
    r = resolve(make_cfg(scope_flag="files", files=["nope.md"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "nope.md" in r.stderr


def test_files_scope_rejects_absolute_paths(tmp_repo, tmp_path):
    """Regression for path-traversal / data-exfiltration. Absolute paths must
    be refused outright — inlining /Users/.../.ssh/id_rsa or /etc/passwd into
    the review prompt would send it to Codex (remote) + Claude sub-agents.
    `Path(repo_root) / absolute_path` evaluates to the absolute path in
    pathlib, so the previous `.exists()` check accepted any local file."""
    leaked = tmp_path / "leaked.txt"
    leaked.write_text("would-be-exfiltrated")
    r = resolve(make_cfg(scope_flag="files", files=[str(leaked)]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "absolute" in r.stderr.lower()


def test_files_scope_rejects_dotdot_escape(tmp_repo, tmp_path):
    """`../other-dir/secret.txt` must be rejected even though it's a relative
    path — after resolve() it lands outside repo_root."""
    outside = tmp_path / "outside.txt"
    outside.write_text("not in repo")
    # tmp_repo lives at tmp_path/"repo"; ../outside.txt escapes
    r = resolve(make_cfg(scope_flag="files", files=["../outside.txt"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()


def test_files_scope_rejects_symlink_pointing_outside(tmp_repo, tmp_path):
    """A symlink inside the repo whose target is outside the repo must also be
    rejected — resolve() follows symlinks, so the canonical path escapes."""
    outside = tmp_path / "secret.txt"
    outside.write_text("secret")
    (tmp_repo / "innocent.txt").symlink_to(outside)
    r = resolve(make_cfg(scope_flag="files", files=["innocent.txt"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()


def test_files_scope_preserves_symlink_path_when_target_is_in_repo(tmp_repo):
    """Regression: an in-repo symlink pointing at another in-repo file must keep
    its user-supplied name in the resolved scope, NOT be replaced with the
    target path. Otherwise materialize_files() sees a regular file and the
    symlink metadata (target path) never makes it into the prompt."""
    (tmp_repo / "real.md").write_text("# real file\n")
    (tmp_repo / "alias.md").symlink_to("real.md")
    r = resolve(make_cfg(scope_flag="files", files=["alias.md"]), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    # The returned path must be the user's input, not the target
    assert scope["files"] == ["alias.md"]


def test_files_scope_rejects_directory(tmp_repo):
    """A directory passed in files-scope must be rejected. Earlier behavior
    would let exists() pass and produce a doc_files entry with kind=text and
    content=None — confusing prompt with no value to the reviewer."""
    (tmp_repo / "subdir").mkdir()
    r = resolve(make_cfg(scope_flag="files", files=["subdir"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "regular file" in r.stderr.lower() or "directory" in r.stderr.lower()
