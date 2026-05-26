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


def test_render_skips_unified_diff_when_doc_files_present():
    """Regression for prompt-size blowup observed on PR #152 smoke run.

    When both unified_diff and doc_files are present (non-code modes on diff
    scopes, where materialize mirrors changed text files into doc_files), the
    diff is just `+`-prefixed duplication of the same content. Keeping both
    made the rendered prompt ~720KB and Claude's Agent tool timed out reading
    it. Now: skip the diff section when doc_files is populated; the per-file
    content covers everything.
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
