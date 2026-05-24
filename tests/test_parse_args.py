# tests/test_parse_args.py
"""Tests for parse-args.py — flag parsing into normalized config JSON."""
import json
from tests.conftest import run_script


def parse(*args):
    r = run_script("parse-args.py", *args)
    assert r.returncode == 0, f"stderr: {r.stderr}"
    return json.loads(r.stdout)


def test_no_args_defaults_to_code_mode():
    cfg = parse()
    assert cfg["mode"] == "code"
    assert cfg["scope_flag"] is None
    assert cfg["files"] == []
    assert cfg["full"] is False


def test_pr_flag():
    cfg = parse("--pr", "105")
    assert cfg["scope_flag"] == "pr"
    assert cfg["pr_number"] == 105


def test_uncommitted_flag():
    cfg = parse("--uncommitted")
    assert cfg["scope_flag"] == "uncommitted"


def test_base_flag():
    cfg = parse("--base", "develop")
    assert cfg["scope_flag"] == "base"
    assert cfg["base_branch"] == "develop"


def test_commit_flag():
    cfg = parse("--commit", "abc1234")
    assert cfg["scope_flag"] == "commit"
    assert cfg["commit_sha"] == "abc1234"


def test_positional_files():
    cfg = parse("docs/spec.md", "plan.md")
    assert cfg["scope_flag"] == "files"
    assert cfg["files"] == ["docs/spec.md", "plan.md"]


def test_mode_and_focus():
    cfg = parse("--mode", "spec", "--focus", "API contract")
    assert cfg["mode"] == "spec"
    assert cfg["focus"] == "API contract"


def test_all_modifier_flags():
    cfg = parse("--full", "--no-codex", "--force-large", "--keep-worktree",
                "--save", "/tmp/report.md")
    assert cfg["full"] is True
    assert cfg["no_codex"] is True
    assert cfg["force_large"] is True
    assert cfg["keep_worktree"] is True
    assert cfg["save_path"] == "/tmp/report.md"


def test_mutually_exclusive_scope_flags_error():
    r = run_script("parse-args.py", "--pr", "1", "--uncommitted")
    assert r.returncode != 0
    assert "mutually exclusive" in r.stderr.lower()


def test_files_with_scope_flag_errors():
    r = run_script("parse-args.py", "--pr", "1", "foo.md")
    assert r.returncode != 0
    assert "mutually exclusive" in r.stderr.lower()


def test_invalid_mode_errors():
    r = run_script("parse-args.py", "--mode", "nonsense")
    assert r.returncode != 0


def test_args_file_mode(tmp_path):
    """Orchestrator writes $ARGUMENTS to a file; parse-args reads + shlex-splits it.
    Necessary because shell-substituting $ARGUMENTS directly is injection-prone."""
    f = tmp_path / "args.txt"
    f.write_text('--pr 105 --focus "API contract changes" --mode spec')
    r = run_script("parse-args.py", "--args-file", str(f))
    assert r.returncode == 0, r.stderr
    cfg = json.loads(r.stdout)
    assert cfg["pr_number"] == 105
    assert cfg["focus"] == "API contract changes"
    assert cfg["mode"] == "spec"


def test_args_file_handles_paths_with_spaces(tmp_path):
    f = tmp_path / "args.txt"
    f.write_text('"docs/path with spaces/spec.md"')
    r = run_script("parse-args.py", "--args-file", str(f))
    assert r.returncode == 0, r.stderr
    cfg = json.loads(r.stdout)
    assert cfg["files"] == ["docs/path with spaces/spec.md"]
