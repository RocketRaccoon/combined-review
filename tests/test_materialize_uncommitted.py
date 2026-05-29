# tests/test_materialize_uncommitted.py
"""Tests for materialize-scope.py — uncommitted scope only."""
import json
import subprocess
from tests.conftest import run_script


def base_scope(repo):
    return {
        "kind": "uncommitted", "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": False, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def materialize(scope):
    return run_script("materialize-scope.py", input=json.dumps(scope))


def test_uncommitted_modified_file(tmp_repo):
    (tmp_repo / "README.md").write_text("# changed\n")
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "uncommitted"
    assert out["has_reviewable_changes"] is True
    assert out["changed_file_count"] == 1
    assert "README.md" in out["unified_diff"]
    files = out["changed_files"]
    assert len(files) == 1
    assert files[0]["path"] == "README.md"
    assert files[0]["status"] == "modified"
    assert files[0]["kind"] == "text"
    assert files[0]["post_content"] == "# changed\n"


def test_uncommitted_untracked_file_included(tmp_repo):
    (tmp_repo / "brand_new.py").write_text("print('hi')\n")
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    files = {f["path"]: f for f in out["changed_files"]}
    assert "brand_new.py" in files
    assert files["brand_new.py"]["status"] == "added"
    assert files["brand_new.py"]["post_content"] == "print('hi')\n"
    assert out["total_lines_changed"] >= 1


def test_uncommitted_clean_tree_empty(tmp_repo):
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["has_reviewable_changes"] is False
    assert out["changed_file_count"] == 0
    assert out["total_lines_changed"] == 0
    assert out["unified_diff"] in ("", None)


def test_uncommitted_deleted_file(tmp_repo):
    (tmp_repo / "README.md").unlink()
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
    assert "README.md" in files
    assert files["README.md"]["status"] == "deleted"
    assert files["README.md"]["post_content"] is None
    assert files["README.md"]["pre_content"] is not None


def test_uncommitted_handles_symlink(tmp_repo):
    """Regression guard for the PR #152 review finding: symlink_target() calls
    os.readlink(), and earlier drafts of the plan added `import os` only in a
    later task. On-disk code already has the import — this test makes sure a
    future commit can't quietly drop it without failing CI.

    A symlink in the working tree must appear in changed_files with kind=symlink
    and its symlink_target populated."""
    # Create the link target first (a normal text file) so the symlink isn't dangling.
    (tmp_repo / "target.md").write_text("link target\n")
    subprocess.run(["git", "add", "target.md"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add target"], cwd=tmp_repo, check=True)
    # Now add an untracked symlink to it in the working tree.
    (tmp_repo / "link.md").symlink_to("target.md")
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
    assert "link.md" in files, f"symlink missing from changed_files: {list(files)}"
    entry = files["link.md"]
    assert entry["kind"] == "symlink"
    assert entry["symlink_target"] == "target.md"
    assert entry["status"] == "added"  # untracked


def test_uncommitted_deleted_binary_file(tmp_repo):
    """Regression: deleting a tracked binary file used to crash materialization
    because the deleted-path branch forced kind='text' and then called git show
    with text=True, raising UnicodeDecodeError. Now: detect kind from HEAD and
    skip text decoding for binary."""
    # Commit a real binary (PNG header) so it's tracked at HEAD
    bin_path = tmp_repo / "logo.png"
    # 8-byte PNG signature + a NUL byte so any text detection trips on it
    bin_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff\xfe\xfd binary garbage")
    subprocess.run(["git", "add", "logo.png"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add binary"], cwd=tmp_repo, check=True)
    # Now delete it in the working tree
    bin_path.unlink()
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
    assert "logo.png" in files
    entry = files["logo.png"]
    assert entry["status"] == "deleted"
    assert entry["kind"] == "binary"
    # Critical: must NOT have tried to decode the binary as text
    assert entry["pre_content"] is None
    assert "binary" in (entry.get("note") or "").lower()
