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
        # focus is forwarded so Claude can include it verbatim in the cluster
        # JSON's top-level "focus" field. Without this, SKILL.md's template
        # defaulted to null and focus disappeared from the final report.
        "focus": cfg.get("focus"),
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
        # Empty stdin is valid — corresponds to `/combined-review` with no
        # args, which should auto-detect the scope. shlex.split('') → [].
        # parse-args.py with empty argv → cfg.scope_flag = None → resolve-scope
        # auto-detects from git state. PR #178 follow-up review fix.
        args_string = sys.stdin.read().strip()
        cmd_phase_a(args_string)
        return
    if ns.phase == "run-codex":
        cmd_run_codex(ns.state)
        return
    if ns.phase == "phase-c-pre":
        cmd_phase_c_pre(ns.state)
        return
    if ns.phase == "phase-c-post":
        cmd_phase_c_post(ns.state, ns.clusters_file)
        return
    if ns.phase == "cleanup":
        cmd_cleanup(ns.state)
        return
    raise SystemExit(f"orchestrate.py: unknown subcommand {ns.phase!r}")


def _load_state(state_path: str) -> dict:
    if not os.path.exists(state_path):
        sys.stderr.write(f"error: state file not found: {state_path}\n")
        sys.exit(1)
    with open(state_path) as f:
        return json.load(f)


# ---- T6: phase-c-post + cleanup ----

# Allowlist of state.paths keys that are DIRECTORIES (not files). Anything not
# in this set is treated as a file (Path.unlink). Forces a deliberate choice
# for any future path added to state.paths. PR #178 review fix.
_DIR_PATH_KEYS = {"claude_transcripts_dir"}


def _validate_clusters_subproc(cluster_text: str) -> str | None:
    """Run scripts/validate-clusters.py. Returns None on valid, error string on
    invalid (the validator's stderr message, suitable for both stderr output
    on first-fail AND for --synthesis-failed-file on second-fail)."""
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "validate-clusters.py")],
        input=cluster_text, capture_output=True, text=True,
    )
    if r.returncode == 0:
        return None
    return r.stderr.strip() or f"validate-clusters.py exited {r.returncode}"


def _claude_raw_path(state: dict) -> str:
    """report.py wants a single --claude-raw file containing all transcripts.
    Use $TRANSCRIPTS_DIR/all.txt if Claude wrote it; otherwise concatenate the
    per-agent transcripts on the fly. The temp concat is returned as a path
    that cleanup_all will remove (it's not in state.paths)."""
    transcripts_dir = Path(state["paths"]["claude_transcripts_dir"])
    all_txt = transcripts_dir / "all.txt"
    if all_txt.exists() and all_txt.read_text().strip():
        return str(all_txt)
    # Concat ourselves into a temp file (lives until cleanup)
    fd, tmp = tempfile.mkstemp(prefix="combined-review-claude-raw-", suffix=".txt")
    with os.fdopen(fd, "w") as f:
        for transcript in sorted(transcripts_dir.glob("*.txt")):
            if transcript.name == "all.txt":
                continue
            f.write(f"\n# === {transcript.stem} ===\n\n")
            f.write(transcript.read_text())
            f.write("\n")
    return tmp


def _render_success(state: dict, cluster_text: str) -> str:
    """Run report.py with cluster JSON on stdin; return the rendered markdown."""
    claude_raw = _claude_raw_path(state)
    try:
        cmd = [
            "python3", str(SCRIPTS_DIR / "report.py"),
            "--codex-raw", state["paths"]["codex_stdout"],
            "--codex-stderr", state["paths"]["codex_stderr"],
            "--claude-raw", claude_raw,
        ]
        r = subprocess.run(cmd, input=cluster_text,
                            capture_output=True, text=True, check=True)
        return r.stdout
    finally:
        # Only remove the temp concat — never the audit file in transcripts_dir
        if claude_raw != str(Path(state["paths"]["claude_transcripts_dir"]) / "all.txt"):
            try:
                os.unlink(claude_raw)
            except OSError:
                pass


def _render_synthesis_failed(state: dict, error_msg: str) -> str:
    """Run report.py in --synthesis-failed-file mode. Passes the message via
    a temp file to avoid shell-injection of validator output (which can
    contain backticks/$()/quotes)."""
    fd, err_file = tempfile.mkstemp(
        prefix="combined-review-validate-stderr-", suffix=".txt"
    )
    with os.fdopen(fd, "w") as f:
        f.write(error_msg)
    claude_raw = _claude_raw_path(state)
    try:
        cmd = [
            "python3", str(SCRIPTS_DIR / "report.py"),
            "--codex-raw", state["paths"]["codex_stdout"],
            "--codex-stderr", state["paths"]["codex_stderr"],
            "--claude-raw", claude_raw,
            "--synthesis-failed-file", err_file,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return r.stdout
    finally:
        try:
            os.unlink(err_file)
        except OSError:
            pass
        if claude_raw != str(Path(state["paths"]["claude_transcripts_dir"]) / "all.txt"):
            try:
                os.unlink(claude_raw)
            except OSError:
                pass


def _cleanup_all(state: dict, state_path: str) -> None:
    """Tear down worktree (unless --keep-worktree) + every entry in state.paths
    (files via unlink, dirs via rmtree) + state file itself.

    state.config.save_path is structurally protected — it lives outside
    state.paths so this loop never sees it. PR #178 review fix."""
    # 1. Worktree (reads from state.scope; must run BEFORE state file removed)
    wt = (state.get("scope") or {}).get("worktree_path")
    repo_root = (state.get("scope") or {}).get("repo_root")
    if wt:
        if state["config"].get("keep_worktree"):
            try:
                Path(wt, ".combined-review-keep").touch()
            except OSError:
                pass
        elif repo_root:
            subprocess.run(
                [str(SCRIPTS_DIR / "cleanup-worktree.sh"), repo_root, wt],
                capture_output=True,
            )
    # 2. Every path in state.paths — file vs dir distinction is explicit.
    for key, path in (state.get("paths") or {}).items():
        if not path:
            continue
        try:
            if key in _DIR_PATH_KEYS:
                shutil.rmtree(path, ignore_errors=True)
            else:
                Path(path).unlink(missing_ok=True)
        except OSError:
            pass
    # 3. State file itself
    try:
        Path(state_path).unlink(missing_ok=True)
    except OSError:
        pass


def cmd_phase_c_post(state_path: str, clusters_path: str) -> None:
    """T6 — validate clusters; render report; cleanup (try/finally).

    Three exit branches:
      0: cluster JSON valid → render → cleanup → exit
      2: cluster JSON invalid AND first attempt → bump validation_attempts in
         state; emit validator error on stderr; exit WITHOUT cleanup so Claude
         can read the error, rewrite clusters, and re-invoke this command.
      1: cluster JSON invalid AND second attempt → render error report
         (preserves raw-findings audit appendix); cleanup; exit.
    """
    state = _load_state(state_path)
    try:
        cluster_text = Path(clusters_path).read_text()
    except FileNotFoundError:
        sys.stderr.write(f"error: clusters file not found: {clusters_path}\n")
        _cleanup_all(state, state_path)
        sys.exit(1)
    err = _validate_clusters_subproc(cluster_text)
    if err is not None:
        attempts = state.get("validation_attempts", 0)
        if attempts < 1:
            # First failure — give Claude one shot to repair. CRITICAL: no cleanup.
            state["validation_attempts"] = attempts + 1
            _write_state_atomic(state, state_path)
            sys.stderr.write(
                f"validation failed (attempt {attempts + 1}): {err}\n"
                "Rewrite the clusters JSON addressing this error, "
                "then re-invoke `orchestrate.py phase-c-post --state ... --clusters-file ...`.\n"
            )
            sys.exit(2)
        # Second failure — render the synthesis-failed report and clean up.
        try:
            report_md = _render_synthesis_failed(state, err)
            sys.stdout.write(report_md)
            _maybe_save(state, report_md)
        finally:
            _cleanup_all(state, state_path)
        sys.exit(1)
    # Valid — render, save, cleanup.
    try:
        report_md = _render_success(state, cluster_text)
        sys.stdout.write(report_md)
        _maybe_save(state, report_md)
    finally:
        _cleanup_all(state, state_path)


def _maybe_save(state: dict, report_md: str) -> None:
    save = (state.get("config") or {}).get("save_path")
    if save:
        try:
            Path(save).write_text(report_md)
        except OSError as e:
            sys.stderr.write(f"warning: could not save report to {save}: {e}\n")


def cmd_cleanup(state_path: str) -> None:
    """T6 — standalone cleanup for early-abort paths.

    Used when Claude got phase-a output, then aborted (e.g. user declined
    the large-diff gate). Same teardown as phase-c-post's finally block."""
    try:
        state = _load_state(state_path)
    except SystemExit:
        raise  # _load_state already wrote a clean error
    _cleanup_all(state, state_path)
    sys.exit(0)


def _read_codex_status_safe(status_path: str, *, no_codex: bool) -> dict:
    """Robust read of run-codex.py's status JSON. Handles all four cases
    SKILL.md/spec §5 require:
      - no_codex=True: codex was never invoked → status='skipped'
      - file missing: same outcome as empty (couldn't write)
      - file empty: run-codex.py SIGKILLed before writing (PR #152 HIGH —
        json.loads('') would crash; treat as failure with explanatory error)
      - file present and valid JSON: trust it (run-codex.py wrote a real status)
    """
    if no_codex:
        return {"status": "skipped"}
    try:
        raw = Path(status_path).read_text()
    except FileNotFoundError:
        return {
            "status": "failed",
            "error": "codex did not write a status file (file missing — "
                     "likely killed before reaching the status-write step)",
            "exit_code": -1, "duration_ms": 0,
        }
    if not raw.strip():
        return {
            "status": "failed",
            "error": "codex did not write a status file (file empty — "
                     "likely SIGKILLed mid-run before reaching the status-write step)",
            "exit_code": -1, "duration_ms": 0,
        }
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {
            "status": "failed",
            "error": f"codex status file did not parse as JSON: {e}",
            "exit_code": -1, "duration_ms": 0,
        }


def _normalize_findings_subproc(text: str, source: str) -> dict:
    """Call scripts/normalize-findings.py via subprocess; return parsed JSON
    with findings/parse_warnings/unparsed_chunks."""
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "normalize-findings.py"),
         "--source", source],
        input=text, capture_output=True, text=True,
    )
    if r.returncode != 0:
        # Don't crash phase-c-pre; emit empty findings + a warning
        return {
            "findings": [],
            "parse_warnings": [f"normalize-findings.py exited {r.returncode}: {r.stderr.strip()[:200]}"],
            "unparsed_chunks": [{"source": source, "text": text[:500]}] if text else [],
        }
    return json.loads(r.stdout)


def cmd_phase_c_pre(state_path: str) -> None:
    """T5 — normalize codex + claude reviewer outputs; allocate clusters file.

    Inputs (from state):
      paths.codex_stdout, paths.codex_status, paths.claude_transcripts_dir,
      config.no_codex
    Outputs:
      - state.paths.clusters_file set to a fresh empty file path
      - stdout JSON: normalized_findings, reviewer_summary, clusters_file
    """
    state = _load_state(state_path)
    paths = state["paths"]
    no_codex = state["config"].get("no_codex", False)
    # Codex side
    codex_status = _read_codex_status_safe(paths["codex_status"], no_codex=no_codex)
    codex_findings: list = []
    codex_parse_warnings: list = []
    codex_unparsed: list = []
    if codex_status.get("status") == "ok":
        try:
            codex_text = Path(paths["codex_stdout"]).read_text()
        except FileNotFoundError:
            codex_text = ""
        parsed = _normalize_findings_subproc(codex_text, source="codex")
        codex_findings = parsed.get("findings", [])
        codex_parse_warnings = parsed.get("parse_warnings", [])
        codex_unparsed = parsed.get("unparsed_chunks", [])
    # Claude side
    transcripts_dir = Path(paths["claude_transcripts_dir"])
    claude_normalized: dict = {}
    claude_summary: list = []
    all_unparsed: list = list(codex_unparsed)
    if transcripts_dir.exists():
        for transcript in sorted(transcripts_dir.glob("*.txt")):
            # Skip the all.txt audit concatenation — would double-count findings
            # that already appear in per-agent files.
            if transcript.name == "all.txt":
                continue
            agent = transcript.stem
            parsed = _normalize_findings_subproc(
                transcript.read_text(), source=f"claude:{agent}"
            )
            claude_normalized[agent] = parsed
            claude_summary.append({
                "agent": agent,
                "status": "ok",
                "raw_findings": len(parsed.get("findings", [])),
                "parse_warnings": len(parsed.get("parse_warnings", [])),
            })
            all_unparsed.extend(parsed.get("unparsed_chunks", []))
    # Allocate empty clusters file
    clusters_file = _mktemp_file("combined-review-clusters-", ".json")
    Path(clusters_file).write_text("")  # ensure 0-byte sentinel
    state["paths"]["clusters_file"] = clusters_file
    _write_state_atomic(state, state_path)
    # Reviewer summary for the cluster JSON Claude will Write
    reviewer_summary: dict = {
        "codex": {
            "status": codex_status.get("status", "failed"),
            "raw_findings": len(codex_findings),
            "parse_warnings": len(codex_parse_warnings),
        },
        "claude": claude_summary,
    }
    if codex_status.get("status") != "ok" and codex_status.get("error"):
        reviewer_summary["codex"]["error"] = codex_status["error"]
    if codex_status.get("duration_ms"):
        reviewer_summary["codex"]["duration_ms"] = codex_status["duration_ms"]
    print(json.dumps({
        "clusters_file": clusters_file,
        "normalized_findings": {
            "codex": codex_findings,
            "claude": claude_normalized,
        },
        "reviewer_summary": reviewer_summary,
        "unparsed_chunks": all_unparsed,
    }))


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
