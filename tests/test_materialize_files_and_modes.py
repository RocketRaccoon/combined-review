# tests/test_materialize_files_and_modes.py
"""Tests for materialize-scope.py — files scope and doc_files for non-code modes."""
import json
import subprocess
from tests.conftest import run_script


def files_scope(repo, files, mode="code"):
    return {
        "kind": "files", "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": files, "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": False, "mode": mode, "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def test_files_scope_reads_current_content(tmp_repo):
    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
    (tmp_repo / "plan.md").write_text("# plan\nbar\n")
    scope = files_scope(tmp_repo, ["spec.md", "plan.md"])
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "files"
    assert out["unified_diff"] is None
    assert out["changed_files"] == []
    docs = {d["path"]: d for d in out["doc_files"]}
    assert "spec.md" in docs
    assert docs["spec.md"]["content"] == "# spec\nfoo\n"
    assert out["has_reviewable_changes"] is True


def test_files_scope_with_spec_mode_preserves_doc_files(tmp_repo):
    """Regression: maybe_populate_doc_files() must not overwrite materialize_files()'s
    output. Was: --mode spec + files-scope wiped doc_files because the helper iterated
    over an empty changed_files. Now: helper short-circuits for files scope."""
    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
    scope = files_scope(tmp_repo, ["spec.md"], mode="spec")
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert len(out["doc_files"]) == 1
    assert out["doc_files"][0]["path"] == "spec.md"
    assert out["doc_files"][0]["content"] == "# spec\nfoo\n"


def test_non_code_mode_with_diff_scope_populates_doc_files(tmp_repo):
    # Set up a base-scope review on a .md change with --mode spec
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feat"], cwd=tmp_repo, check=True)
    (tmp_repo / "design.md").write_text("# design\n")
    subprocess.run(["git", "add", "design.md"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "design"], cwd=tmp_repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    scope = files_scope(tmp_repo, [], mode="spec")
    scope["kind"] = "base"
    scope["base_sha"] = base_sha
    scope["head_sha"] = head_sha
    scope["base_ref_name"] = "main"
    scope["needs_clean_worktree"] = True
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    paths = {d["path"]: d for d in out["doc_files"]}
    assert "design.md" in paths
    assert "design" in paths["design.md"]["content"]
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)
