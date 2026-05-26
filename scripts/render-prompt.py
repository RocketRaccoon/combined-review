#!/usr/bin/env python3
"""render-prompt.py — assemble the prompt body for a reviewer.

Inputs:
- --mode {code,spec,plan,docs}
- --focus "<text>" (optional)
- materialized blob on stdin (JSON from materialize-scope.py)

Output: plain-text prompt body on stdout, suitable for piping to a reviewer
(codex via stdin, or pasted into a Claude sub-agent's prompt).
"""
import argparse
import json
import sys
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def fence_for(content: str) -> str:
    """Return a backtick fence longer than any run of backticks already inside
    `content`. CommonMark requires the closing fence be at least as long as
    the opening one, so a fence of length N+1 (where N is the longest run
    inside) will never collide. Without this, embedding a spec/plan that
    itself contains ``` would terminate our outer fence early and swallow
    everything after it — including the finding-schema appendix."""
    longest = 0
    run = 0
    for ch in content:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def fenced(content: str, lang: str = "") -> str:
    fence = fence_for(content)
    return f"{fence}{lang}\n{content.rstrip(chr(10))}\n{fence}"


def render_changed_files(mat: dict) -> str:
    parts = []
    for cf in mat["changed_files"]:
        parts.append(f"\n### {cf['path']}  (status: {cf['status']}, kind: {cf['kind']})")
        if cf.get("old_path"):
            parts.append(f"(renamed from {cf['old_path']})")
        if cf["kind"] == "text" and cf.get("post_content"):
            parts.append(fenced(cf["post_content"]))
        elif cf["status"] == "deleted" and cf.get("pre_content"):
            parts.append("(deleted; previous content was:)")
            parts.append(fenced(cf["pre_content"]))
        elif cf["kind"] == "symlink":
            target = cf.get("symlink_target")
            if target is not None:
                parts.append(f"Symlink target: `{target}`")
            if cf.get("note"):
                parts.append(f"_{cf['note']}_")
        elif cf["kind"] == "submodule":
            pre, post = cf.get("submodule_pre_sha"), cf.get("submodule_post_sha")
            if pre or post:
                parts.append(f"Submodule pointer: `{pre or '(none)'}` → `{post or '(none)'}`")
            if cf.get("note"):
                parts.append(f"_{cf['note']}_")
        elif cf.get("note"):
            parts.append(f"_{cf['note']}_")
    return "\n".join(parts)


def render_doc_files(mat: dict) -> str:
    parts = []
    for d in mat["doc_files"]:
        kind = d.get("kind", "text")
        parts.append(
            f"\n### {d['path']}  (status: {d['status']}, kind: {kind})"
        )
        if d.get("content"):
            parts.append(fenced(d["content"]))
        elif kind == "symlink":
            target = d.get("symlink_target")
            if target is not None:
                parts.append(f"Symlink target: `{target}`")
            if d.get("note"):
                parts.append(f"_{d['note']}_")
        elif kind == "submodule":
            sha = d.get("submodule_sha")
            if sha:
                parts.append(f"Submodule pointer: `{sha}`")
            if d.get("note"):
                parts.append(f"_{d['note']}_")
        elif d.get("note"):
            parts.append(f"_{d['note']}_")
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["code", "spec", "plan", "docs"], required=True)
    # Two ways to pass focus text:
    #   --focus "<text>" — convenient when the text has no shell metacharacters
    #   --focus-file <path> — REQUIRED when the text is user-provided, since
    #     argv interpolation by the orchestrator into a Bash command line
    #     would expose $(...), backticks, and other shell-injection vectors.
    # The skill orchestrator MUST use --focus-file for any user-provided focus.
    ap.add_argument("--focus", default=None)
    ap.add_argument("--focus-file", default=None)
    args = ap.parse_args()
    if args.focus and args.focus_file:
        ap.error("--focus and --focus-file are mutually exclusive")
    focus = args.focus
    if args.focus_file:
        with open(args.focus_file, "r") as f:
            focus = f.read().strip()
    mat = json.load(sys.stdin)

    template = (PROMPTS_DIR / f"{args.mode}.md").read_text()
    schema = (PROMPTS_DIR / "_schema.md").read_text()

    out = [template]
    if focus:
        out.append(f"\n## Additional focus\n\n{focus}\n")
    out.append(f"\n## Review subject\n\n**Scope:** {mat['scope_summary']}\n")
    # Slimming rule: when doc_files is populated (non-code modes on diff scopes,
    # or files-scope), the per-file content already covers everything the diff
    # would show — the diff is mostly `+`-prefixed duplication of the same text.
    # Skipping it cuts the rendered prompt by ~3× on doc-heavy reviews (saw
    # 720KB → ~250KB on the PR #152 smoke), which keeps the prompt under the
    # Claude Agent's effective input window. Code-mode + diff scopes still get
    # the unified diff (no doc_files there).
    if mat.get("unified_diff") and not mat.get("doc_files"):
        out.append("\n### Unified diff\n\n" + fenced(mat["unified_diff"], "diff") + "\n")
    elif mat.get("unified_diff") and mat.get("doc_files"):
        out.append(
            "\n_(unified diff omitted — full file contents below cover the same changes "
            "without the `+`/`-` duplication. See the worktree at the scope's `worktree_path` "
            "if you need to inspect the diff directly.)_\n"
        )
    if mat["changed_files"]:
        out.append("\n### Changed files (full content)\n")
        out.append(render_changed_files(mat))
    if mat["doc_files"]:
        out.append("\n### Document files\n")
        out.append(render_doc_files(mat))
    out.append("\n" + schema)
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
