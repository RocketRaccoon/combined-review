# tests/test_orchestrate_run_codex.py
"""Tests for orchestrate.py run-codex — thin wrapper around run-codex.py.

Uses fake_bin to stub out `codex` so the test doesn't depend on a real
authenticated codex CLI. Verifies the wrapper sources every path from
state.paths and writes a status JSON that phase-c-pre can consume.
"""
import json
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

from tests.conftest import SCRIPTS_DIR

ORCH = SCRIPTS_DIR / "orchestrate.py"


def _make_state(tmp_path, repo_root, worktree_path=None):
    """Build a minimal state file the way phase-a would."""
    prompt = tmp_path / "prompt.md"
    prompt.write_text("# Review prompt\n\nDo a code review.\n")
    state_path = tmp_path / "state.json"
    state = {
        "version": 1,
        "config": {"no_codex": False, "mode": "code"},
        "scope": {
            "kind": "uncommitted",
            "repo_root": str(repo_root),
            "worktree_path": str(worktree_path) if worktree_path else None,
        },
        "paths": {
            "prompt": str(prompt),
            "codex_stdout": str(tmp_path / "codex-stdout"),
            "codex_stderr": str(tmp_path / "codex-stderr"),
            "codex_status": str(tmp_path / "codex-status.json"),
            "claude_transcripts_dir": str(tmp_path / "transcripts"),
            "clusters_file": None,
        },
        "validation_attempts": 0,
    }
    state_path.write_text(json.dumps(state))
    return state_path, state


def test_run_codex_invokes_run_codex_py_and_writes_status(tmp_repo, tmp_path, fake_bin):
    """Stub codex with a tiny script that emits a known string + sandbox flag.
    Verify orchestrate.py run-codex writes a status JSON with status=ok."""
    # Fake codex needs to handle three calls:
    #   `codex exec --help`               — preflight in run-codex.py; must mention --sandbox
    #   `codex exec --sandbox read-only -` — actual review run
    #   (anything else — exit 0)
    (fake_bin / "codex").write_text(textwrap.dedent("""\
        #!/bin/sh
        # `codex exec --help` — preflight grep target
        for arg in "$@"; do
          if [ "$arg" = "--help" ]; then
            echo '  -s, --sandbox <SANDBOX_MODE>  Configure the process restrictions'
            exit 0
          fi
        done
        # `codex exec --sandbox read-only -` — review run
        if [ "$1" = "exec" ]; then
          cat >/dev/null   # consume stdin prompt
          printf '%s\\n' '---FINDING---' 'severity: low' 'file: x.py' 'line: 1' 'category: style' 'title: stub' 'detail: |' '  ok' '---END-FINDING---'
          exit 0
        fi
        exit 0
    """))
    (fake_bin / "codex").chmod(0o755)

    state_path, state = _make_state(tmp_path, tmp_repo)

    r = subprocess.run(
        ["python3", str(ORCH), "run-codex", "--state", str(state_path)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    # Status file should now exist with status=ok
    assert Path(state["paths"]["codex_status"]).exists()
    status = json.loads(Path(state["paths"]["codex_status"]).read_text())
    assert status["status"] == "ok"
    # Stdout file should contain the stub finding
    stdout_text = Path(state["paths"]["codex_stdout"]).read_text()
    assert "---FINDING---" in stdout_text
    assert "stub" in stdout_text


def test_run_codex_missing_state_file(tmp_path):
    """Bad state path should exit non-zero with a clean message."""
    r = subprocess.run(
        ["python3", str(ORCH), "run-codex", "--state", str(tmp_path / "nonexistent.json")],
        capture_output=True, text=True,
    )
    assert r.returncode != 0
    assert "state" in r.stderr.lower() or "not found" in r.stderr.lower()
