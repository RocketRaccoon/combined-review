# tests/test_orchestrate_phase_c_post.py
"""Tests for orchestrate.py phase-c-post + cleanup.

Covers the three exit branches (valid → 0; first-fail → 2 NO cleanup;
second-fail → 1 WITH cleanup) and the cleanup-correctness contracts
(directory vs file, save_path preservation, idempotency)."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from tests.conftest import SCRIPTS_DIR

ORCH = SCRIPTS_DIR / "orchestrate.py"

VALID_CLUSTERS = {
    "scope_summary": "uncommitted (1 file)",
    "mode": "code",
    "focus": None,
    "reviewer_summary": {
        "codex": {"status": "ok", "raw_findings": 1, "parse_warnings": 0},
        "claude": [{"agent": "code-reviewer", "status": "ok",
                    "raw_findings": 1, "parse_warnings": 0}],
    },
    "clusters": [{
        "tag": "agreement", "severity": "high",
        "file": "app/main.py", "line": "42",
        "category": "bug", "title": "null pointer",
        "synthesized_detail": "Both reviewers flagged the same nullcheck.",
        "sources": [
            {"source": "codex", "severity": "high"},
            {"source": "claude:code-reviewer", "severity": "high"},
        ],
    }],
    "unparsed_chunks": [],
}


def _make_state(tmp_path, *, save_path=None, validation_attempts=0,
                with_worktree=False, keep_worktree=False):
    """Build a state file ready for phase-c-post."""
    transcripts_dir = tmp_path / "transcripts"
    transcripts_dir.mkdir()
    (transcripts_dir / "code-reviewer.txt").write_text("---FINDING---\nseverity: high\nfile: a\nline: 1\ncategory: bug\ntitle: x\ndetail: |\n  y\n---END-FINDING---\n")
    (transcripts_dir / "all.txt").write_text("")
    paths = {
        "prompt": str(tmp_path / "prompt.md"),
        "codex_stdout": str(tmp_path / "codex-stdout"),
        "codex_stderr": str(tmp_path / "codex-stderr"),
        "codex_status": str(tmp_path / "codex-status.json"),
        "claude_transcripts_dir": str(transcripts_dir),
        "clusters_file": str(tmp_path / "clusters.json"),
    }
    for k in ("prompt", "codex_stdout", "codex_stderr"):
        Path(paths[k]).write_text("")
    Path(paths["codex_status"]).write_text(json.dumps({"status": "ok"}))
    worktree_path = None
    if with_worktree:
        worktree_path = tmp_path / "fake-worktree"
        worktree_path.mkdir()
    state = {
        "version": 1,
        "config": {
            "no_codex": False, "mode": "code", "save_path": save_path,
            "keep_worktree": keep_worktree,
        },
        "scope": {
            "kind": "uncommitted",
            "repo_root": str(tmp_path),
            "worktree_path": str(worktree_path) if worktree_path else None,
        },
        "paths": paths,
        "validation_attempts": validation_attempts,
    }
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state))
    return state_path


def _write_clusters(state_path, data):
    state = json.loads(state_path.read_text())
    Path(state["paths"]["clusters_file"]).write_text(
        data if isinstance(data, str) else json.dumps(data)
    )


def _run(state_path):
    state = json.loads(state_path.read_text())
    return subprocess.run(
        ["python3", str(ORCH), "phase-c-post",
         "--state", str(state_path),
         "--clusters-file", state["paths"]["clusters_file"]],
        capture_output=True, text=True,
    )


def test_phase_c_post_valid_renders_and_exits_0(tmp_path):
    state_path = _make_state(tmp_path)
    _write_clusters(state_path, VALID_CLUSTERS)
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    assert "# Combined Review" in r.stdout
    assert "null pointer" in r.stdout


def test_phase_c_post_first_validation_fail_exits_2_no_cleanup(tmp_path):
    """PR #178 review: spec preserves the one-shot LLM repair flow.
    First validation fail → exit 2 with validator error on stderr.
    Cleanup must NOT run — Claude needs the state file intact to retry."""
    state_path = _make_state(tmp_path)
    _write_clusters(state_path, {"clusters": [], "scope_summary": "x"})  # missing required fields
    r = _run(state_path)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "required" in r.stderr.lower() or "schema" in r.stderr.lower()
    # State file MUST still exist with validation_attempts=1
    assert state_path.exists()
    st = json.loads(state_path.read_text())
    assert st["validation_attempts"] == 1
    # Temp files NOT cleaned up
    assert Path(st["paths"]["prompt"]).exists()
    assert Path(st["paths"]["claude_transcripts_dir"]).exists()


def test_phase_c_post_second_validation_fail_exits_1_with_cleanup(tmp_path):
    state_path = _make_state(tmp_path, validation_attempts=1, with_worktree=True)
    _write_clusters(state_path, "not even json")
    worktree = json.loads(state_path.read_text())["scope"]["worktree_path"]
    transcripts = json.loads(state_path.read_text())["paths"]["claude_transcripts_dir"]
    r = _run(state_path)
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert "synthesis failed" in r.stdout.lower() or "raw outputs" in r.stdout.lower()
    # Cleanup ran — state file, transcripts dir gone
    assert not state_path.exists()
    assert not Path(transcripts).exists()


def test_phase_c_post_preserves_save_path(tmp_path):
    """PR #178 review: --save target lives in state.config.save_path, NOT
    state.paths. Cleanup iterates state.paths only; save file must persist."""
    save_path = tmp_path / "saved-report.md"
    state_path = _make_state(tmp_path, save_path=str(save_path))
    _write_clusters(state_path, VALID_CLUSTERS)
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    assert save_path.exists()
    assert "# Combined Review" in save_path.read_text()


def test_phase_c_post_cleanup_handles_transcripts_as_directory(tmp_path):
    """PR #178 review: paths.claude_transcripts_dir is a DIR not a file.
    Cleanup must use shutil.rmtree, not Path.unlink (which raises on dirs)."""
    state_path = _make_state(tmp_path)
    transcripts = json.loads(state_path.read_text())["paths"]["claude_transcripts_dir"]
    # Add an extra file inside — verify non-empty dir is still rmtree'd
    (Path(transcripts) / "extra.txt").write_text("audit")
    _write_clusters(state_path, VALID_CLUSTERS)
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    assert not Path(transcripts).exists()


# ---- cleanup subcommand ----

def _run_cleanup(state_path):
    return subprocess.run(
        ["python3", str(ORCH), "cleanup", "--state", str(state_path)],
        capture_output=True, text=True,
    )


def test_cleanup_removes_temp_files_and_state(tmp_path):
    state_path = _make_state(tmp_path)
    st = json.loads(state_path.read_text())
    transcripts = st["paths"]["claude_transcripts_dir"]
    r = _run_cleanup(state_path)
    assert r.returncode == 0, r.stderr
    assert not state_path.exists()
    assert not Path(transcripts).exists()
    assert not Path(st["paths"]["prompt"]).exists()


def test_cleanup_missing_state_exits_non_zero(tmp_path):
    r = _run_cleanup(tmp_path / "nonexistent.json")
    assert r.returncode != 0
    assert "state" in r.stderr.lower() or "not found" in r.stderr.lower()


def test_cleanup_preserves_save_path_file(tmp_path):
    save = tmp_path / "report.md"
    save.write_text("# already saved")
    state_path = _make_state(tmp_path, save_path=str(save))
    r = _run_cleanup(state_path)
    assert r.returncode == 0, r.stderr
    # User-saved file must NOT be removed
    assert save.exists()
    assert save.read_text() == "# already saved"
