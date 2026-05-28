# tests/test_orchestrate_phase_a.py
"""End-to-end tests for orchestrate.py phase-a.

Covers scope-kind happy paths (uncommitted, base, pr), early-exit paths
(nothing to review, not a git repo), and the two PR #178 review fixes
(shlex.split preserving quoted focus; claude_transcripts_dir allocated
and present in state.paths)."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from tests.conftest import run_script


def _phase_a(args_string: str, cwd):
    return subprocess.run(
        ["python3", str(Path(__file__).parent.parent / "scripts" / "orchestrate.py"),
         "phase-a"],
        input=args_string,
        cwd=cwd, capture_output=True, text=True,
    )


def test_phase_a_uncommitted_returns_prompt_path_and_state(tmp_repo):
    (tmp_repo / "README.md").write_text("# changed\n")
    r = _phase_a("--uncommitted --mode code", tmp_repo)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert Path(out["prompt_path"]).exists()
    assert Path(out["state_file"]).exists()
    state = json.loads(Path(out["state_file"]).read_text())
    assert state["scope"]["kind"] == "uncommitted"
    assert state["config"]["mode"] == "code"
    assert state["validation_attempts"] == 0


def test_phase_a_empty_uncommitted_exits_2(tmp_repo):
    r = _phase_a("--uncommitted", tmp_repo)
    assert r.returncode == 2, r.stderr
    assert "nothing to review" in r.stderr.lower()


def test_phase_a_outside_git_repo_exits_3(tmp_path):
    r = _phase_a("--uncommitted", tmp_path)  # tmp_path is not a git repo
    assert r.returncode == 3, (r.returncode, r.stderr)
    assert "git" in r.stderr.lower()


def test_phase_a_preserves_quoted_focus(tmp_repo):
    """PR #178 review fix: args_string.split() would mangle this. shlex.split keeps it."""
    (tmp_repo / "README.md").write_text("# changed\n")
    r = _phase_a('--uncommitted --mode code --focus "API surface"', tmp_repo)
    assert r.returncode == 0, r.stderr
    state = json.loads(Path(json.loads(r.stdout)["state_file"]).read_text())
    assert state["config"]["focus"] == "API surface"


def test_phase_a_allocates_claude_transcripts_dir(tmp_repo):
    """phase-c-pre reads transcripts from this dir; Claude writes into it
    between phase-a and phase-c-pre. Must exist before Claude needs it."""
    (tmp_repo / "README.md").write_text("# changed\n")
    r = _phase_a("--uncommitted --mode code", tmp_repo)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert "claude_transcripts_dir" in out
    td = Path(out["claude_transcripts_dir"])
    assert td.exists() and td.is_dir()
    # Same path is recorded in state.paths
    state = json.loads(Path(out["state_file"]).read_text())
    assert state["paths"]["claude_transcripts_dir"] == str(td)


def test_phase_a_uses_python_tempfile_not_mktemp(tmp_repo):
    """PR #152 HIGH: mktemp -t is non-portable. Python tempfile produces
    sane filenames; verify no literal 'XXXXXX' appears in the state path."""
    (tmp_repo / "README.md").write_text("# changed\n")
    r = _phase_a("--uncommitted --mode code", tmp_repo)
    out = json.loads(r.stdout)
    assert "XXXXXX" not in Path(out["state_file"]).name
    assert "XXXXXX" not in Path(out["prompt_path"]).name


def test_phase_a_flags_large_diff(tmp_repo):
    """When total_lines_changed > threshold, large_diff: true."""
    # Big modification
    (tmp_repo / "huge.py").write_text("x = 1\n" * 3000)
    r = _phase_a("--uncommitted --mode code", tmp_repo)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["large_diff"] is True
    assert out["total_lines_changed"] > 2000


def test_phase_a_emits_summary_fields(tmp_repo):
    """The stdout JSON must include all the fields SKILL.md expects to consume."""
    (tmp_repo / "README.md").write_text("# changed\n")
    r = _phase_a("--uncommitted --mode plan --focus test", tmp_repo)
    out = json.loads(r.stdout)
    for required in ("prompt_path", "state_file", "claude_transcripts_dir",
                     "scope_summary", "mode", "total_lines_changed",
                     "large_diff", "no_codex", "full"):
        assert required in out, f"phase-a stdout missing {required}: {out}"
    assert out["mode"] == "plan"
