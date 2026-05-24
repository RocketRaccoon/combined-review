# tests/test_run_codex.py
"""Tests for run-codex.py — invokes codex exec --sandbox read-only with stdin prompt."""
import json
import subprocess
from pathlib import Path

from tests.conftest import SCRIPTS_DIR


def write_fake_codex(fake_bin, behavior="echo"):
    codex = fake_bin / "codex"
    if behavior == "echo":
        codex.write_text(
            '#!/bin/sh\n'
            '# Echo the args + stdin, plus a fake finding. Advertise --sandbox.\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE   sandbox policy"\n'
            '  exit 0\n'
            'fi\n'
            'echo "ARGS: $*" >&2\n'
            'cat - >/dev/null\n'
            'echo "---FINDING---"\n'
            'echo "severity: low"\n'
            'echo "file: x.py"\n'
            'echo "line: 1"\n'
            'echo "category: style"\n'
            'echo "title: fake codex finding"\n'
            'echo "detail: |"\n'
            'echo "  emitted by fake codex"\n'
            'echo "---END-FINDING---"\n'
        )
    elif behavior == "no-sandbox":
        codex.write_text(
            '#!/bin/sh\n'
            '# --help does NOT advertise --sandbox; run-codex.py should refuse.\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --some-other-flag"\n'
            '  exit 0\n'
            'fi\n'
            'cat - >/dev/null; echo "ok"\n'
        )
    elif behavior == "slow":
        codex.write_text(
            '#!/bin/sh\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE"\n'
            '  exit 0\n'
            'fi\n'
            'sleep 30\n'
        )
    elif behavior == "fail":
        codex.write_text(
            '#!/bin/sh\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE"\n'
            '  exit 0\n'
            'fi\n'
            'echo "codex internal error" >&2; exit 7\n'
        )
    codex.chmod(0o755)


def run_codex(scope_path, prompt_path, stdout_path, stderr_path,
              status_path=None, timeout=None, **kwargs):
    args = ["python3", str(SCRIPTS_DIR / "run-codex.py"),
            "--scope", str(scope_path),
            "--prompt-file", str(prompt_path),
            "--stdout", str(stdout_path),
            "--stderr", str(stderr_path)]
    if status_path:
        args += ["--status", str(status_path)]
    env = kwargs.pop("env", None) or {}
    if timeout is not None:
        env["COMBINED_REVIEW_CODEX_TIMEOUT"] = str(timeout)
    import os as _os
    env = {**_os.environ, **env}
    return subprocess.run(args, capture_output=True, text=True, env=env, **kwargs)


def test_run_codex_writes_to_orchestrator_paths(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "echo")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("review please")
    stdout = tmp_path / "out"; stderr = tmp_path / "err"; status = tmp_path / "status.json"
    r = run_codex(scope, prompt, stdout, stderr, status_path=status)
    assert r.returncode == 0, r.stderr
    assert stdout.exists() and stderr.exists() and status.exists()
    assert "---FINDING---" in stdout.read_text()
    st = json.loads(status.read_text())
    assert st["status"] == "ok"
    assert st["exit_code"] == 0
    # orchestrator-owned files must not be deleted
    assert prompt.exists() and stdout.exists()


def test_run_codex_records_failure(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "fail")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
    # run-codex always exits 0; outcome is in the status file
    assert r.returncode == 0
    st = json.loads(status.read_text())
    assert st["status"] == "failed"
    assert st["exit_code"] == 7


def test_run_codex_records_timeout(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "slow")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e",
                  status_path=status, timeout=2)
    assert r.returncode == 0
    st = json.loads(status.read_text())
    assert st["status"] == "timeout"


def test_run_codex_errors_without_sandbox_support(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "no-sandbox")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
    # Sandbox-flag failure is a HARD error — exits non-zero, no status file written.
    assert r.returncode != 0
    assert "sandbox" in r.stderr.lower()
