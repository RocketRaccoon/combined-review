# tests/test_render_prompt.py
"""Tests for render-prompt.py — assembles mode template + materialized blob + schema."""
import json
from tests.conftest import run_script


def make_materialized(**overrides):
    base = {
        "scope_kind": "uncommitted",
        "scope_summary": "uncommitted changes",
        "unified_diff": "diff --git a/x b/x\n+y\n",
        "changed_files": [
            {"path": "x", "status": "modified", "kind": "text",
             "post_content": "y\n", "pre_content": None, "old_path": None,
             "lines_changed": "(modified)", "note": None},
        ],
        "doc_files": [], "total_lines_changed": 1,
        "changed_file_count": 1, "has_reviewable_changes": True,
        "warnings": [],
    }
    base.update(overrides)
    return base


def test_render_includes_mode_template():
    r = run_script(
        "render-prompt.py", "--mode", "code",
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0, r.stderr
    assert "Code Review Mode" in r.stdout
    assert "FINDING" in r.stdout  # schema appendix
    assert "no-edit" not in r.stdout.lower()  # we use the "read only" wording
    assert "diff --git" in r.stdout
    assert "y\n" in r.stdout


def test_render_includes_focus():
    r = run_script(
        "render-prompt.py", "--mode", "code", "--focus", "API contract changes",
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0
    assert "API contract changes" in r.stdout


def test_focus_file_mode_handles_shell_metacharacters(tmp_path):
    """Focus text containing $(...), backticks, etc. must round-trip safely."""
    f = tmp_path / "focus.txt"
    f.write_text("review $(rm -rf /) carefully and `dangerous` patterns")
    r = run_script(
        "render-prompt.py", "--mode", "code", "--focus-file", str(f),
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0, r.stderr
    # The literal text must appear verbatim — no shell expansion happens
    # because the orchestrator passes a file path, not the text itself.
    assert "review $(rm -rf /) carefully" in r.stdout
    assert "`dangerous` patterns" in r.stdout


def test_focus_and_focus_file_mutually_exclusive(tmp_path):
    f = tmp_path / "focus.txt"; f.write_text("x")
    r = run_script(
        "render-prompt.py", "--mode", "code",
        "--focus", "y", "--focus-file", str(f),
        input=json.dumps(make_materialized()),
    )
    assert r.returncode != 0


def test_render_doc_mode_uses_doc_files():
    mat = make_materialized(
        scope_kind="files", unified_diff=None, changed_files=[],
        doc_files=[{"path": "spec.md", "status": "current", "content": "# spec\n"}],
    )
    r = run_script(
        "render-prompt.py", "--mode", "spec",
        input=json.dumps(mat),
    )
    assert r.returncode == 0
    assert "Spec Review Mode" in r.stdout
    assert "spec.md" in r.stdout
    assert "# spec" in r.stdout


def test_render_handles_nested_fences_in_doc(tmp_path):
    """Specs/plans commonly contain ``` blocks. A naive triple-backtick wrapper
    would let the inner ``` close the outer fence prematurely, swallowing the
    schema appendix. Verify the schema appendix is still present and intact."""
    doc_with_fences = (
        "# Spec\n\n"
        "Example code:\n\n"
        "```python\n"
        "def f(): return 1\n"
        "```\n\n"
        "Another block:\n\n"
        "````diff\n"  # nested fence with FOUR backticks
        "+ added line\n"
        "````\n"
    )
    mat = make_materialized(
        scope_kind="files", unified_diff=None, changed_files=[],
        doc_files=[{"path": "spec.md", "status": "current",
                    "content": doc_with_fences}],
    )
    r = run_script("render-prompt.py", "--mode", "spec",
                   input=json.dumps(mat))
    assert r.returncode == 0, r.stderr
    out = r.stdout
    # Doc content must appear
    assert "def f(): return 1" in out
    assert "+ added line" in out
    # Schema appendix must NOT have been swallowed by an unbalanced fence
    assert "---FINDING---" in out
    assert "End of prompt" not in out or "FINDING" in out  # schema present


def test_render_skips_unified_diff_when_all_files_added():
    """Regression for prompt-size blowup observed on PR #152 smoke run.

    When every changed file is newly added AND doc_files is populated (non-code
    modes on diff scopes mirror text files into doc_files), the diff is just
    `+`-prefixed duplication of the same content. Keeping both made the
    rendered prompt ~720KB and Claude's Agent tool timed out. For all-added
    scopes the diff carries no unique info, so skip it.
    """
    big_text = "line\n" * 1000  # 5000 chars
    mat = make_materialized(
        scope_kind="pr",
        unified_diff="+" + "\n+".join(["line"] * 1000),  # mirrors big_text
        changed_files=[{
            "path": "spec.md", "status": "added", "kind": "text",
            "post_content": big_text, "pre_content": None, "old_path": None,
            "lines_changed": "(modified)", "note": None,
        }],
        doc_files=[{"path": "spec.md", "status": "added", "content": big_text}],
    )
    r = run_script("render-prompt.py", "--mode", "spec",
                   input=json.dumps(mat))
    assert r.returncode == 0, r.stderr
    out = r.stdout
    # The diff section header must NOT appear
    assert "### Unified diff" not in out
    # The diff content (lines prefixed with `+`) must NOT appear
    assert "+line" not in out
    # The doc content MUST still appear (twice, once in changed_files render
    # once in doc_files render — but that's not blowup, that's the design)
    assert big_text.strip() in out
    # And the omission note must be present so the reviewer knows
    assert "unified diff omitted" in out


def test_render_keeps_unified_diff_when_any_file_modified():
    """The slim rule must NOT apply when a changed file is `modified` — its
    `-`-line context (deleted/rewritten content) lives ONLY in the diff. If
    we dropped the diff, a docs/spec PR that removed a requirement would
    render only the final text, hiding the deletion from the reviewer."""
    mat = make_materialized(
        scope_kind="pr",
        unified_diff=(
            "diff --git a/spec.md b/spec.md\n"
            "@@ -1,3 +1,3 @@\n"
            " keep this\n"
            "-DELETED REQUIREMENT\n"
            "+NEW REQUIREMENT\n"
        ),
        changed_files=[{
            "path": "spec.md", "status": "modified", "kind": "text",
            "post_content": "keep this\nNEW REQUIREMENT\n",
            "pre_content": None, "old_path": None,
            "lines_changed": "(modified)", "note": None,
        }],
        doc_files=[{"path": "spec.md", "status": "modified",
                    "content": "keep this\nNEW REQUIREMENT\n"}],
    )
    r = run_script("render-prompt.py", "--mode", "spec",
                   input=json.dumps(mat))
    assert r.returncode == 0, r.stderr
    out = r.stdout
    # Diff section MUST be present
    assert "### Unified diff" in out
    # The `-` line MUST be visible — that's the whole point
    assert "-DELETED REQUIREMENT" in out
    assert "+NEW REQUIREMENT" in out
    # Omission note must NOT appear
    assert "unified diff omitted" not in out


def test_render_keeps_unified_diff_when_any_file_deleted():
    """Same principle as modified: a `deleted` file's `-`-prefixed content
    lives in the diff. We do render `pre_content` for deletions separately
    in render_changed_files, but the diff is still the authoritative source
    and we should not silently drop it on mixed-status scopes."""
    mat = make_materialized(
        scope_kind="pr",
        unified_diff=(
            "diff --git a/old.md b/old.md\n"
            "deleted file mode 100644\n"
            "@@ -1 +0,0 @@\n"
            "-removed file content\n"
        ),
        changed_files=[{
            "path": "old.md", "status": "deleted", "kind": "text",
            "post_content": None, "pre_content": "removed file content\n",
            "old_path": None, "lines_changed": "(modified)", "note": None,
        }],
        doc_files=[{"path": "old.md", "status": "deleted",
                    "content": "removed file content\n"}],
    )
    r = run_script("render-prompt.py", "--mode", "spec",
                   input=json.dumps(mat))
    assert r.returncode == 0, r.stderr
    assert "### Unified diff" in r.stdout
    assert "-removed file content" in r.stdout
    assert "unified diff omitted" not in r.stdout


def test_render_keeps_unified_diff_when_doc_files_empty():
    """Code-mode + diff scopes have empty doc_files. The unified diff is the
    review subject; keep it."""
    mat = make_materialized(
        scope_kind="base",
        unified_diff="diff --git a/x b/x\n@@ -1 +1 @@\n-old\n+new\n",
        doc_files=[],
    )
    r = run_script("render-prompt.py", "--mode", "code",
                   input=json.dumps(mat))
    assert r.returncode == 0, r.stderr
    assert "### Unified diff" in r.stdout
    assert "+new" in r.stdout
    assert "unified diff omitted" not in r.stdout
