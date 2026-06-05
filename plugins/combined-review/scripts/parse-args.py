#!/usr/bin/env python3
"""parse-args.py — turn /combined-review CLI args into a normalized config JSON.

Reads sys.argv[1:] OR, if --args-file <path> is given, reads the raw argument
string from that file and shlex-splits it. The args-file mode exists because
the orchestrator must not shell-substitute $ARGUMENTS directly — quoting
fragility and injection risk. Instead, the slash command writes $ARGUMENTS
to a file and we read it back literally here.

Writes a config object to stdout; returns non-zero on validation errors.
"""
import argparse
import json
import shlex
import sys

VALID_MODES = ("code", "spec", "plan", "docs")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="combined-review", add_help=True)
    p.add_argument("--pr", type=int, dest="pr_number")
    p.add_argument("--uncommitted", action="store_true")
    p.add_argument("--base", dest="base_branch")
    p.add_argument("--commit", dest="commit_sha")
    p.add_argument("--mode", choices=VALID_MODES, default="code")
    p.add_argument("--focus", default=None)
    p.add_argument("--full", action="store_true")
    p.add_argument("--no-codex", action="store_true", dest="no_codex")
    p.add_argument("--force-large", action="store_true", dest="force_large")
    p.add_argument("--keep-worktree", action="store_true", dest="keep_worktree")
    p.add_argument("--save", default=None, dest="save_path")
    p.add_argument("files", nargs="*")
    return p


def normalize(ns: argparse.Namespace) -> dict:
    scope_flags = {
        "pr": ns.pr_number is not None,
        "uncommitted": ns.uncommitted,
        "base": ns.base_branch is not None,
        "commit": ns.commit_sha is not None,
        "files": bool(ns.files),
    }
    selected = [k for k, v in scope_flags.items() if v]
    if len(selected) > 1:
        raise SystemExit(
            f"error: scope flags are mutually exclusive; got {selected}"
        )
    scope_flag = selected[0] if selected else None
    return {
        "scope_flag": scope_flag,
        "pr_number": ns.pr_number,
        "base_branch": ns.base_branch,
        "commit_sha": ns.commit_sha,
        "files": ns.files,
        "mode": ns.mode,
        "focus": ns.focus,
        "full": ns.full,
        "no_codex": ns.no_codex,
        "force_large": ns.force_large,
        "keep_worktree": ns.keep_worktree,
        "save_path": ns.save_path,
    }


def resolve_argv(raw_argv: list[str]) -> list[str]:
    """If --args-file <path> is the only/first pair, read the file and shlex-split.
    Otherwise return raw_argv unchanged."""
    if len(raw_argv) >= 2 and raw_argv[0] == "--args-file":
        path = raw_argv[1]
        with open(path, "r") as f:
            raw_string = f.read().strip()
        return shlex.split(raw_string)
    return raw_argv


def main(argv: list[str]) -> None:
    argv = resolve_argv(argv)
    ns = build_parser().parse_args(argv)
    cfg = normalize(ns)
    json.dump(cfg, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
