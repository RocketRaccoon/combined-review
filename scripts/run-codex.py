#!/usr/bin/env python3
"""run-codex.py — drive `codex exec --sandbox read-only` with a stdin prompt.

Portable across macOS and Linux. GNU `timeout` isn't on macOS by default and
BSD `date` doesn't support `%3N`, so we use Python's subprocess.run(timeout=)
and time.monotonic_ns() instead.

All long-lived files (prompt, stdout, stderr, status) are orchestrator-owned.
This script writes to them but never deletes them. It ALWAYS exits 0 except
for hard pre-flight failures (missing --sandbox support, missing required
args); outcome of the codex run goes into the status JSON so the
orchestrator's background-Bash mechanics don't have to interpret exit codes.
"""
import argparse
import json
import os
import subprocess
import sys
import time


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--stdout", required=True)
    ap.add_argument("--stderr", required=True)
    ap.add_argument("--status", default=None,
                    help="default: <stdout>.status")
    args = ap.parse_args()

    status_path = args.status or f"{args.stdout}.status"

    def write_failed_status(msg: str, exit_code: int) -> None:
        """Write a status JSON AND mirror the message into the orchestrator-
        owned stderr capture for hard failures. Phase C builds its error
        section from $CODEX_STDERR and report.py embeds it in the audit
        trail. Writing only to sys.stderr (this script's own stderr) would
        leave the audit trail empty for missing-sandbox / missing-codex
        cases — invisible to anyone reading the report.

        Two destinations:
          1. status JSON: structured error for Phase C's reviewer_summary
          2. args.stderr: free-form text the audit trail can show verbatim

        Phase A pre-flight should catch these before Phase B launches at
        all, but this still matters for the (narrow) case where codex was
        upgraded or replaced between Phase A and Phase B.
        """
        try:
            with open(status_path, "w") as sf:
                json.dump({
                    "status": "failed", "exit_code": exit_code,
                    "duration_ms": 0, "timeout_seconds": 0,
                    "error": msg,
                }, sf)
        except OSError:
            pass
        try:
            with open(args.stderr, "w") as ef:
                ef.write(f"run-codex.py hard failure: {msg}\n")
        except OSError:
            pass

    # Hard pre-flight: verify codex exec advertises --sandbox before we ever
    # invoke it. Missing the flag means we cannot guarantee read-only mode —
    # refuse to run rather than silently going unsandboxed.
    # Phase A pre-flight should catch this, but check here too in case codex
    # was upgraded/replaced between Phase A and Phase B launch.
    try:
        help_out = subprocess.run(
            ["codex", "exec", "--help"], capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        msg = "codex not on PATH"
        print(f"error: {msg}", file=sys.stderr)
        write_failed_status(msg, 3); sys.exit(3)
    if "--sandbox" not in (help_out.stdout + help_out.stderr):
        msg = "installed codex does not advertise --sandbox; refusing to run unsandboxed"
        print(f"error: {msg}", file=sys.stderr)
        write_failed_status(msg, 3); sys.exit(3)

    # Resolve cwd: prefer worktree_path (diff-based scopes), else repo_root.
    with open(args.scope) as f:
        scope = json.load(f)
    cwd = scope.get("worktree_path") or scope.get("repo_root") or os.getcwd()

    timeout_s = int(os.environ.get("COMBINED_REVIEW_CODEX_TIMEOUT", "300"))

    with open(args.prompt_file, "rb") as pf, \
         open(args.stdout, "wb") as outf, \
         open(args.stderr, "wb") as errf:
        prompt_bytes = pf.read()
        start = time.monotonic_ns()
        status = "ok"; exit_code = 0
        try:
            proc = subprocess.run(
                ["codex", "exec", "--sandbox", "read-only", "-"],
                input=prompt_bytes, stdout=outf, stderr=errf,
                cwd=cwd, timeout=timeout_s,
            )
            exit_code = proc.returncode
            status = "ok" if exit_code == 0 else "failed"
        except subprocess.TimeoutExpired:
            status = "timeout"; exit_code = 124
        except FileNotFoundError:
            # codex disappeared between --help and exec; treat as failure
            status = "failed"; exit_code = 127
            errf.write(b"codex binary not found at exec time\n")
        end = time.monotonic_ns()

    duration_ms = (end - start) // 1_000_000

    with open(status_path, "w") as sf:
        json.dump({
            "status": status,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "timeout_seconds": timeout_s,
        }, sf)


if __name__ == "__main__":
    main()
