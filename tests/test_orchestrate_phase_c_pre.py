# tests/test_orchestrate_phase_c_pre.py
"""Tests for orchestrate.py phase-c-pre.

Covers the four reviewer-outcome cases (ok, failed, timeout, skipped) plus
the PR #152 HIGH regression: empty codex status file (codex SIGKILLed
before writing must not crash phase-c-pre on json.loads(''))."""
import json
import subprocess
from pathlib import Path

ORCH = Path(__file__).parent.parent / "scripts" / "orchestrate.py"

CLAUDE_TRANSCRIPT = """\
---FINDING---
severity: high
file: app/main.py
line: 42
category: bug
title: null pointer
detail: |
  Accessing user.id before nullcheck.
---END-FINDING---
"""

CODEX_STDOUT = """\
---FINDING---
severity: medium
file: app/main.py
line: 88
category: perf
title: O(n^2) loop
detail: |
  Could be O(n).
---END-FINDING---
"""


def _make_state(tmp_path, *, codex_status=None, no_codex=False,
                claude_agent="code-reviewer", codex_stdout_text=CODEX_STDOUT):
    """Build a state file with reviewer outputs already written. codex_status
    can be: None (empty file), 'ok'/'failed'/'timeout' (write that status),
    or a dict (write it verbatim)."""
    transcripts_dir = tmp_path / "transcripts"
    transcripts_dir.mkdir()
    if claude_agent:
        (transcripts_dir / f"{claude_agent}.txt").write_text(CLAUDE_TRANSCRIPT)
    codex_stdout = tmp_path / "codex-stdout"
    codex_stderr = tmp_path / "codex-stderr"
    codex_status_path = tmp_path / "codex-status.json"
    codex_stdout.write_text(codex_stdout_text or "")
    codex_stderr.write_text("")
    if codex_status is None:
        codex_status_path.write_text("")  # empty — the SIGKILL case
    elif isinstance(codex_status, str):
        codex_status_path.write_text(json.dumps({
            "status": codex_status, "exit_code": 0 if codex_status == "ok" else 1,
            "duration_ms": 1000, "timeout_seconds": 300,
        }))
    else:
        codex_status_path.write_text(json.dumps(codex_status))
    state = {
        "version": 1,
        "config": {"no_codex": no_codex, "mode": "code"},
        "scope": {"kind": "uncommitted", "repo_root": str(tmp_path)},
        "paths": {
            "prompt": str(tmp_path / "prompt.md"),
            "codex_stdout": str(codex_stdout),
            "codex_stderr": str(codex_stderr),
            "codex_status": str(codex_status_path),
            "claude_transcripts_dir": str(transcripts_dir),
            "clusters_file": None,
        },
        "validation_attempts": 0,
    }
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state))
    return state_path


def _run(state_path):
    return subprocess.run(
        ["python3", str(ORCH), "phase-c-pre", "--state", str(state_path)],
        capture_output=True, text=True,
    )


def test_phase_c_pre_normalizes_codex_and_claude(tmp_path):
    state_path = _make_state(tmp_path, codex_status="ok")
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    # Clusters file allocated, empty, ready for Claude to Write
    assert Path(out["clusters_file"]).exists()
    assert Path(out["clusters_file"]).read_text() == ""
    # Findings normalized from both sides
    nf = out["normalized_findings"]
    assert isinstance(nf["codex"], list)
    assert len(nf["codex"]) == 1
    assert nf["codex"][0]["title"] == "O(n^2) loop"
    assert isinstance(nf["claude"], dict)
    assert "code-reviewer" in nf["claude"]
    assert len(nf["claude"]["code-reviewer"]["findings"]) == 1
    # Reviewer summary
    rs = out["reviewer_summary"]
    assert rs["codex"]["status"] == "ok"
    assert rs["codex"]["raw_findings"] == 1
    assert len(rs["claude"]) == 1
    assert rs["claude"][0]["agent"] == "code-reviewer"
    assert rs["claude"][0]["status"] == "ok"
    assert rs["claude"][0]["raw_findings"] == 1
    # State now records the clusters_file path
    st = json.loads(state_path.read_text())
    assert st["paths"]["clusters_file"] == out["clusters_file"]


def test_phase_c_pre_handles_codex_failed(tmp_path):
    state_path = _make_state(tmp_path, codex_status={
        "status": "failed", "exit_code": 2, "duration_ms": 500,
        "timeout_seconds": 300, "error": "codex unreachable",
    })
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["reviewer_summary"]["codex"]["status"] == "failed"
    assert "unreachable" in out["reviewer_summary"]["codex"].get("error", "").lower()
    # Codex findings empty; claude side still parses
    assert out["normalized_findings"]["codex"] == []
    assert len(out["normalized_findings"]["claude"]["code-reviewer"]["findings"]) == 1


def test_phase_c_pre_handles_codex_timeout(tmp_path):
    state_path = _make_state(tmp_path, codex_status="timeout")
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["reviewer_summary"]["codex"]["status"] == "timeout"


def test_phase_c_pre_handles_no_codex(tmp_path):
    """--no-codex set in config; status file empty (run-codex never invoked).
    Must NOT try to parse it."""
    state_path = _make_state(tmp_path, no_codex=True, codex_status=None,
                              codex_stdout_text="")
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    summary = json.loads(r.stdout)["reviewer_summary"]
    assert summary["codex"]["status"] == "skipped"


def test_phase_c_pre_handles_empty_status_file(tmp_path):
    """PR #152 HIGH: codex SIGKILLed mid-run leaves a 0-byte status file.
    Must NOT crash on json.loads(''); treat as failure with explanatory error."""
    state_path = _make_state(tmp_path, codex_status=None, no_codex=False,
                              codex_stdout_text="")
    r = _run(state_path)
    assert r.returncode == 0, r.stderr  # MUST NOT crash
    summary = json.loads(r.stdout)["reviewer_summary"]
    assert summary["codex"]["status"] == "failed"
    err = summary["codex"].get("error", "").lower()
    assert "did not write" in err or "empty" in err or "killed" in err


def test_phase_c_pre_skips_all_txt_audit_file(tmp_path):
    """Tests should not treat $TRANSCRIPTS_DIR/all.txt as a per-agent
    transcript — it's the concatenated audit file Claude writes for
    debugging. Normalizing it would double-count findings."""
    state_path = _make_state(tmp_path, codex_status="ok")
    # Add an all.txt that contains a DIFFERENT finding — would be double-counted
    # if the orchestrator treated it as an agent transcript.
    transcripts_dir = json.loads(state_path.read_text())["paths"]["claude_transcripts_dir"]
    (Path(transcripts_dir) / "all.txt").write_text(CLAUDE_TRANSCRIPT)
    r = _run(state_path)
    assert r.returncode == 0, r.stderr
    nf = json.loads(r.stdout)["normalized_findings"]
    # Still exactly one agent and one finding — all.txt did NOT register as an agent
    assert list(nf["claude"].keys()) == ["code-reviewer"]
