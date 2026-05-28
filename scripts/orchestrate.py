#!/usr/bin/env python3
"""orchestrate.py — single-process orchestrator for /combined-review.

Five subcommands, one per phase boundary the Claude harness must own:

  phase-a       Setup: parse args, resolve scope, codex/gh preflight,
                materialize, render prompt. Allocates the
                claude_transcripts_dir Claude writes per-agent transcripts
                into. Writes the state file all subsequent phases consume.

  run-codex     Background codex review. Thin subprocess wrapper around
                scripts/run-codex.py with paths sourced from the state file.

  phase-c-pre   Normalize reviewer outputs (codex stdout + per-agent claude
                transcripts read from state.paths.claude_transcripts_dir).
                Allocates the empty clusters file Claude Writes the
                synthesized cluster JSON into.

  phase-c-post  Validate clusters; render report; cleanup.
                - Valid: render → cleanup → exit 0.
                - Invalid (first attempt): bump state.validation_attempts;
                  emit validator error on stderr; exit 2 WITHOUT cleanup so
                  Claude can rewrite the clusters JSON and re-invoke.
                - Invalid (second attempt): render the error report → cleanup
                  → exit 1.

  cleanup       Cleanup-only entry — used for early-abort paths where Phase
                B/C never run (e.g. user declines the large-diff gate).
                Removes worktree (unless --keep-worktree) + all temp files
                in state.paths + the state file itself. state.config.save_path
                is NEVER swept (lives outside state.paths).

Reference: docs/superpowers/specs/2026-05-26-combined-review-refactor-design.md
"""
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
LARGE_DIFF_THRESHOLD = int(
    os.environ.get("COMBINED_REVIEW_LARGE_DIFF_THRESHOLD", "2000")
)


# --- phase-a helpers ---

def _ensure_git_repo() -> str:
    """A0 — exits 3 with a clean message if cwd is not in a git repo."""
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.stderr.write("error: /combined-review must run inside a git repo\n")
        sys.exit(3)
    return r.stdout.strip()


def _gc_worktrees(repo_root: str) -> None:
    """A1 — best-effort GC of stale worktrees. Never fails the run."""
    subprocess.run(
        [str(SCRIPTS_DIR / "gc-worktrees.sh"), repo_root],
        capture_output=True,
    )


def _subproc_json(cmd: list[str], stdin_data: dict | None = None) -> dict:
    """Run a JSON-on-stdout script. On non-zero exit, propagate stderr and exit."""
    r = subprocess.run(
        cmd,
        input=json.dumps(stdin_data) if stdin_data is not None else None,
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode or 1)
    return json.loads(r.stdout)


def _codex_preflight() -> None:
    """A4 — fail fast if codex is missing/unauthenticated/sandbox-less.
    Exits 3; caller should only invoke when --no-codex was not passed."""
    if shutil.which("codex") is None:
        sys.stderr.write(
            "error: codex not on PATH; pass --no-codex or install codex\n"
        )
        sys.exit(3)
    if subprocess.run(["codex", "login", "status"], capture_output=True).returncode != 0:
        sys.stderr.write(
            "error: codex not authenticated; pass --no-codex or run `codex login`\n"
        )
        sys.exit(3)
    help_out = subprocess.run(
        ["codex", "exec", "--help"], capture_output=True, text=True
    ).stdout
    if "--sandbox" not in help_out:
        sys.stderr.write(
            "error: installed codex doesn't advertise --sandbox; update codex or pass --no-codex\n"
        )
        sys.exit(3)


def _gh_preflight() -> None:
    """A5 — fail fast if gh is unauthenticated. Only called when scope.kind == pr."""
    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        sys.stderr.write(
            "error: gh not authenticated; --pr requires `gh auth login`\n"
        )
        sys.exit(3)


def _scope_summary(scope: dict, mat: dict) -> str:
    """Compact human-readable summary for the report header."""
    kind = scope.get("kind")
    n = mat.get("changed_file_count", 0)
    if kind == "uncommitted":
        return f"uncommitted changes ({n} file{'s' if n != 1 else ''})"
    if kind == "pr":
        base = (scope.get("base_sha") or "?")[:7]
        head = (scope.get("head_sha") or "?")[:7]
        return f"PR #{scope.get('pr_number')} ({base}..{head})"
    if kind == "base":
        return f"{scope.get('base_ref_name', '?')}...HEAD ({n} file{'s' if n != 1 else ''})"
    if kind == "commit":
        sha = (scope.get("commit_sha") or "?")[:7]
        return f"commit {sha} ({n} file{'s' if n != 1 else ''})"
    if kind == "files":
        files = scope.get("files") or []
        head = ", ".join(files[:3])
        more = f" + {len(files) - 3} more" if len(files) > 3 else ""
        return f"files: {head}{more}"
    return f"({kind}) {n} file{'s' if n != 1 else ''}"


def _mktemp_file(prefix: str, suffix: str = "") -> str:
    """Allocate a Python-tempfile-managed file path. Closes the FD immediately;
    caller owns the path. No mktemp(1) subprocess — Python-only, so the
    BSD-vs-GNU `-t` portability divergence (PR #152 HIGH finding) can't bite."""
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(fd)
    return path


def _write_state_atomic(state: dict, state_path: str) -> None:
    """Atomic write: tempfile in same dir + os.replace."""
    parent = os.path.dirname(state_path) or "."
    fd, tmp = tempfile.mkstemp(prefix="combined-review-state-tmp-",
                                suffix=".json", dir=parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f)
        os.replace(tmp, state_path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def cmd_phase_a(args_string: str) -> None:
    repo_root = _ensure_git_repo()  # A0
    _gc_worktrees(repo_root)         # A1
    # A2 — shlex.split (NOT args_string.split) preserves shell-quoted values
    # like --focus "API surface" (PR #178 review fix).
    argv = shlex.split(args_string)
    cfg = _subproc_json(
        ["python3", str(SCRIPTS_DIR / "parse-args.py"), *argv]
    )
    # A3
    scope = _subproc_json(
        ["python3", str(SCRIPTS_DIR / "resolve-scope.py")], stdin_data=cfg
    )
    # A4 — codex preflight (skip if --no-codex)
    if not cfg.get("no_codex"):
        _codex_preflight()
    # A5 — gh preflight (only for pr scope)
    if scope.get("kind") == "pr":
        _gh_preflight()
    # A6
    mat = _subproc_json(
        ["python3", str(SCRIPTS_DIR / "materialize-scope.py")],
        stdin_data=scope,
    )
    # A7 — merge worktree_path back into scope so downstream + cleanup see it
    scope["worktree_path"] = mat.get("worktree_path")
    # A8 — empty scope: cleanup any worktree we created, exit 2
    if not mat.get("has_reviewable_changes"):
        wt = mat.get("worktree_path")
        if wt and not cfg.get("keep_worktree"):
            subprocess.run(
                [str(SCRIPTS_DIR / "cleanup-worktree.sh"), repo_root, wt],
                capture_output=True,
            )
        sys.stderr.write("error: nothing to review (no diff for this scope)\n")
        sys.exit(2)
    # Allocate all paths up-front (so state has a complete inventory)
    state_path = _mktemp_file("combined-review-state-", ".json")
    prompt_path = _mktemp_file("combined-review-prompt-", ".md")
    transcripts_dir = tempfile.mkdtemp(prefix="combined-review-claude-")
    codex_stdout = _mktemp_file("combined-review-codex-stdout-")
    codex_stderr = _mktemp_file("combined-review-codex-stderr-")
    codex_status = _mktemp_file("combined-review-codex-status-", ".json")
    # A11 — render prompt to file. Focus (if present) passes via file to avoid
    # shell injection of user-controlled text.
    render_cmd = ["python3", str(SCRIPTS_DIR / "render-prompt.py"),
                  "--mode", cfg["mode"]]
    focus_path = None
    if cfg.get("focus"):
        focus_path = _mktemp_file("combined-review-focus-", ".txt")
        Path(focus_path).write_text(cfg["focus"])
        render_cmd.extend(["--focus-file", focus_path])
    r = subprocess.run(render_cmd, input=json.dumps(mat),
                       capture_output=True, text=True)
    if focus_path:
        try:
            os.unlink(focus_path)
        except OSError:
            pass
    if r.returncode != 0:
        sys.stderr.write(f"render-prompt failed: {r.stderr}\n")
        sys.exit(r.returncode or 1)
    Path(prompt_path).write_text(r.stdout)
    summary = _scope_summary(scope, mat)
    # Build state
    state = {
        "version": 1,
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "config": cfg,
        "scope": scope,
        "materialized": {
            "worktree_path": mat.get("worktree_path"),
            "total_lines_changed": mat.get("total_lines_changed", 0),
            "changed_file_count": mat.get("changed_file_count", 0),
            "has_reviewable_changes": mat.get("has_reviewable_changes", False),
            "scope_summary": summary,
            "warnings": mat.get("warnings", []),
        },
        "paths": {
            "prompt": prompt_path,
            "codex_stdout": codex_stdout,
            "codex_stderr": codex_stderr,
            "codex_status": codex_status,
            "claude_transcripts_dir": transcripts_dir,
            "clusters_file": None,  # allocated by phase-c-pre
        },
        "validation_attempts": 0,
    }
    _write_state_atomic(state, state_path)
    total = mat.get("total_lines_changed", 0)
    print(json.dumps({
        "prompt_path": prompt_path,
        "state_file": state_path,
        "claude_transcripts_dir": transcripts_dir,
        "scope_summary": summary,
        "mode": cfg["mode"],
        "total_lines_changed": total,
        "large_diff": total > LARGE_DIFF_THRESHOLD,
        "no_codex": cfg.get("no_codex", False),
        "full": cfg.get("full", False),
    }))


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="orchestrate.py")
    sub = ap.add_subparsers(dest="phase", required=True)

    p_a = sub.add_parser(
        "phase-a",
        help="setup: parse → resolve → materialize → render prompt; write state. "
             "Reads the literal arg string from stdin (avoids argparse's refusal "
             "to bind flag-shaped values to --args or positionals).",
    )
    # No --args flag, no positional — args come from stdin. Three things tried
    # in PR #178 review iterations: (1) --args FLAG VALUE — argparse rejects
    # `--args --uncommitted` because the value looks like a flag.
    # (2) positional ARGS — same rejection on flag-shaped positional values.
    # (3) `--args=...` syntax — works but is ugly to template in SKILL.md and
    # easy to forget. stdin (`echo "$ARGUMENTS" | orchestrate.py phase-a`) is
    # immune to argparse's flag-detection heuristics entirely.

    p_rc = sub.add_parser(
        "run-codex",
        help="background codex review (wraps run-codex.py with paths from state)",
    )
    p_rc.add_argument("--state", required=True,
                      help="state file written by phase-a")

    p_cpre = sub.add_parser(
        "phase-c-pre",
        help="normalize codex + claude transcripts; allocate clusters file",
    )
    p_cpre.add_argument("--state", required=True,
                        help="state file (transcripts dir read from "
                             "state.paths.claude_transcripts_dir)")
    # NB: deliberately NO --claude-transcripts flag here. Earlier design had
    # one, but transcripts must be written before phase-c-pre runs, so the
    # dir is allocated by phase-a and persisted in state. See spec §5 and
    # test_phase_c_pre_rejects_claude_transcripts_flag in test_orchestrate_cli.

    p_cpost = sub.add_parser(
        "phase-c-post",
        help="validate clusters; render report; cleanup (try/finally)",
    )
    p_cpost.add_argument("--state", required=True)
    p_cpost.add_argument("--clusters-file", required=True,
                         help="path to the cluster JSON Claude wrote")

    p_cleanup = sub.add_parser(
        "cleanup",
        help="cleanup-only — worktree + temp files (for early-abort paths)",
    )
    p_cleanup.add_argument("--state", required=True)

    return ap


def main() -> None:
    ap = _build_parser()
    ns = ap.parse_args()
    if ns.phase == "phase-a":
        args_string = sys.stdin.read().strip()
        if not args_string:
            sys.stderr.write(
                "error: phase-a reads the argument string from stdin "
                '(e.g. `echo "$ARGUMENTS" | orchestrate.py phase-a`). '
                "Got empty stdin.\n"
            )
            sys.exit(2)
        cmd_phase_a(args_string)
        return
    if ns.phase == "run-codex":
        cmd_run_codex(ns.state)
        return
    raise SystemExit(
        f"orchestrate.py: subcommand {ns.phase!r} is not yet implemented "
        "(see plan Tasks 5-6)"
    )


def _load_state(state_path: str) -> dict:
    if not os.path.exists(state_path):
        sys.stderr.write(f"error: state file not found: {state_path}\n")
        sys.exit(1)
    with open(state_path) as f:
        return json.load(f)


def cmd_run_codex(state_path: str) -> None:
    """T4 — thin wrapper around run-codex.py.

    run-codex.py needs a scope JSON file (it reads worktree_path / repo_root
    to choose cwd). Write a temporary scope file derived from state.scope,
    invoke run-codex.py with state's stdout/stderr/status paths, then clean
    up the temp scope file. run-codex.py always writes a status JSON before
    exiting; phase-c-pre's read_codex_status_safe also handles empty status
    if the wrapper or the codex CLI is SIGKILLed before that write."""
    state = _load_state(state_path)
    if state["config"].get("no_codex"):
        sys.stderr.write(
            "error: run-codex invoked but state.config.no_codex is true. "
            "Skip this Bash call in SKILL.md when --no-codex is passed.\n"
        )
        sys.exit(1)
    scope_fd, scope_path = tempfile.mkstemp(
        prefix="combined-review-runcodex-scope-", suffix=".json"
    )
    try:
        with os.fdopen(scope_fd, "w") as f:
            json.dump(state["scope"], f)
        cmd = [
            "python3", str(SCRIPTS_DIR / "run-codex.py"),
            "--scope", scope_path,
            "--prompt-file", state["paths"]["prompt"],
            "--stdout", state["paths"]["codex_stdout"],
            "--stderr", state["paths"]["codex_stderr"],
            "--status", state["paths"]["codex_status"],
        ]
        # run-codex.py manages its own timeout + writes status; we just wait.
        r = subprocess.run(cmd)
        # run-codex.py always exits 0 except for hard pre-flight failures;
        # propagate its code so caller sees real errors (status file is
        # still authoritative for the codex run's outcome).
        sys.exit(r.returncode)
    finally:
        try:
            os.unlink(scope_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()
