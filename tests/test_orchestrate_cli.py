# tests/test_orchestrate_cli.py
"""CLI shape contract tests for orchestrate.py.

These run against an unimplemented script body — argparse should still
reject missing required flags before any subcommand body executes. Once
Tasks 3-6 land actual implementations, these tests stay green as a
guard against accidental flag-name changes.
"""
from tests.conftest import run_script


def test_no_subcommand_errors():
    r = run_script("orchestrate.py")
    assert r.returncode != 0
    # argparse prints "choose from" or "required" — either is fine
    assert ("required" in r.stderr.lower()
            or "choose" in r.stderr.lower()
            or "expected" in r.stderr.lower())


def test_phase_a_accepts_stdin_input():
    """phase-a reads the arg string from stdin (NOT --args flag and NOT
    positional). Tried both during PR #178 iterations; argparse rejects
    flag-shaped values in both forms. stdin is immune to that quirk.
    SKILL.md: `orchestrate.py phase-a <<'CR_ARGS_EOF'\\n$ARGUMENTS\\nCR_ARGS_EOF`.

    We only assert that phase-a *accepts* stdin input — the actual
    end-to-end behavior on empty / well-formed inputs lives in
    test_orchestrate_phase_a.py where the test controls git state."""
    # If phase-a had a required --args flag, this would error with
    # "the following arguments are required: --args". With stdin-driven
    # input, parsing argv succeeds and any error comes from later stages.
    r = run_script("orchestrate.py", "phase-a", input="--help")
    assert "the following arguments are required" not in r.stderr.lower()
    assert "required: --args" not in r.stderr


def test_run_codex_requires_state_flag():
    r = run_script("orchestrate.py", "run-codex")
    assert r.returncode != 0
    assert "--state" in r.stderr


def test_phase_c_pre_requires_state():
    """No --claude-transcripts flag — transcripts dir comes from the state
    file's paths.claude_transcripts_dir (allocated in phase-a). Spec §5."""
    r = run_script("orchestrate.py", "phase-c-pre")
    assert r.returncode != 0
    assert "--state" in r.stderr


def test_phase_c_pre_rejects_claude_transcripts_flag():
    """Regression for PR #178 review: an earlier draft passed --claude-transcripts
    here. The dir now comes from state. If a future maintainer re-adds the flag,
    this test fails — they should remove it and read from state instead."""
    r = run_script("orchestrate.py", "phase-c-pre",
                   "--state", "/tmp/nonexistent.json",
                   "--claude-transcripts", "/tmp/whatever")
    assert r.returncode != 0
    # argparse rejects unrecognized arg
    assert "unrecognized" in r.stderr.lower() or "--claude-transcripts" in r.stderr.lower()


def test_phase_c_post_requires_state_and_clusters():
    r = run_script("orchestrate.py", "phase-c-post", "--state", "/tmp/x.json")
    assert r.returncode != 0
    assert "--clusters-file" in r.stderr


def test_cleanup_requires_state():
    r = run_script("orchestrate.py", "cleanup")
    assert r.returncode != 0
    assert "--state" in r.stderr
