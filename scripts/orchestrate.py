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
import sys


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="orchestrate.py")
    sub = ap.add_subparsers(dest="phase", required=True)

    p_a = sub.add_parser(
        "phase-a",
        help="setup: parse → resolve → materialize → render prompt; write state",
    )
    p_a.add_argument(
        "--args", required=True,
        help="literal arg string from /combined-review invocation; "
             "parsed via shlex.split() to preserve shell quoting (e.g. "
             '--focus "API surface" round-trips correctly)',
    )

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
    raise SystemExit(
        f"orchestrate.py: subcommand {ns.phase!r} is not yet implemented "
        "(scaffold only; see plan Tasks 3-6)"
    )


if __name__ == "__main__":
    main()
