#!/usr/bin/env python3
"""resolve-scope.py — config JSON in → scope object JSON out.

Handles explicit scope flags (uncommitted/base/commit/files) and validates
inputs against git. PR resolution and full auto-detect happen in a later
patch. All ref-shaped inputs are resolved to immutable SHAs here; downstream
steps consume SHAs, never ref names.
"""
import json
import subprocess
import sys
from pathlib import Path


def git(*args, cwd=None, check=True) -> str:
    r = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )
    return r.stdout.strip()


def repo_root(cwd=None) -> str:
    return git("rev-parse", "--show-toplevel", cwd=cwd)


def base_scope_object() -> dict:
    return {
        "kind": None, "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": None,
        "needs_clean_worktree": False,
        "mode": "code", "focus": None, "full": False,
        "no_codex": False, "force_large": False, "keep_worktree": False,
        "save_path": None,
    }


def carry_modifiers(scope: dict, cfg: dict) -> None:
    """Copy modifier flags from cfg into scope so downstream sees one object."""
    for k in ("mode", "focus", "full", "no_codex",
              "force_large", "keep_worktree", "save_path"):
        scope[k] = cfg[k]


def resolve_uncommitted(cfg: dict, root: str) -> dict:
    s = base_scope_object()
    s["kind"] = "uncommitted"
    s["repo_root"] = root
    s["needs_clean_worktree"] = False
    carry_modifiers(s, cfg)
    return s


def resolve_base(cfg: dict, root: str) -> dict:
    base_ref = cfg["base_branch"]
    try:
        base_sha = git("rev-parse", "--verify", f"{base_ref}^{{commit}}", cwd=root)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"error: cannot resolve base ref {base_ref!r}: {e.stderr}")
    head_sha = git("rev-parse", "--verify", "HEAD^{commit}", cwd=root)
    s = base_scope_object()
    s["kind"] = "base"
    s["repo_root"] = root
    s["base_ref_name"] = base_ref
    s["base_sha"] = base_sha
    s["head_sha"] = head_sha
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s


def resolve_commit(cfg: dict, root: str) -> dict:
    try:
        sha = git("rev-parse", "--verify", f"{cfg['commit_sha']}^{{commit}}", cwd=root)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"error: cannot resolve commit {cfg['commit_sha']!r}: {e.stderr}")
    s = base_scope_object()
    s["kind"] = "commit"
    s["repo_root"] = root
    s["commit_sha"] = sha
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s


def _validate_under_root(root: str, paths: list[str]) -> list[str]:
    """Reject absolute paths, `..` escapes, and symlinks whose targets are
    outside repo_root. Return the **user-supplied path, lexically normalized**
    — NOT the resolved target.

    Why we don't return the resolved path: if the user passes an in-repo
    symlink like `innocent-link.md` that points to another in-repo file,
    `.resolve()` follows it to the target. Returning the target would make
    materialize_files() see a regular text file instead of a symlink, and
    the symlink-specific metadata promised in Task 9 (target path) would
    never make it into the prompt. The report would also cite the wrong path.

    Why this is P1: positional file contents are inlined into the review
    prompt and sent to Codex (remote) + Claude sub-agents. Without the
    escape checks, passing `/Users/.../.ssh/id_rsa` or `../../etc/passwd`
    would silently exfiltrate secrets to remote APIs.
    """
    import os.path
    root_abs = Path(root).resolve()
    out = []
    for p in paths:
        if Path(p).is_absolute():
            raise SystemExit(
                f"error: refusing absolute path {p!r} — pass repo-relative paths only"
            )
        # Lexical normalization (does NOT follow symlinks). Rejects `..` escapes.
        lexical = os.path.normpath(p)
        if lexical.startswith("..") or lexical == ".." or "/../" in f"/{lexical}/":
            raise SystemExit(
                f"error: path {p!r} escapes via .. — refusing"
            )
        # Security check: does the resolved (symlink-followed) target land
        # inside the repo? If not, refuse — an in-repo symlink pointing at
        # /etc/passwd would otherwise exfiltrate it.
        try:
            resolved = (root_abs / p).resolve()
            resolved.relative_to(root_abs)
        except ValueError:
            raise SystemExit(
                f"error: path {p!r} resolves outside repo root ({root_abs}); refusing"
            )
        # Existence check using the original path (does not follow symlinks
        # except where the user intended; resolve() check above already
        # validated the target).
        full = root_abs / lexical
        if not full.exists():
            raise SystemExit(f"error: file not found: {p!r}")
        # Reject plain directories: positional files mode reviews file
        # content. A directory passed here would slip through with kind=text
        # + content=None downstream and render as a confusing header with no
        # content. If the user wants to review every file in a directory,
        # they should expand the glob themselves — the skill doesn't recurse
        # implicitly. is_file() returns True for symlinks pointing at regular
        # files, which is the behavior we want (symlinks ARE supported).
        #
        # Exception: submodules are gitlinks — they appear as directories on
        # disk (is_file() is False) but git tracks them as mode 160000.
        # materialize_files() has a kind=submodule branch that produces useful
        # output (the pointer SHA), so we must let these through.
        if not full.is_file():
            ls = subprocess.run(
                ["git", "ls-files", "--stage", "--", lexical],
                cwd=str(root_abs), capture_output=True, text=True,
            )
            is_submodule = ls.stdout.strip().startswith("160000 ")
            if not is_submodule:
                raise SystemExit(
                    f"error: {p!r} is not a regular file "
                    f"(directory or special file — pass file paths only, expand globs yourself)"
                )
        out.append(lexical)
    return out


def resolve_files(cfg: dict, root: str) -> dict:
    files = _validate_under_root(root, cfg["files"])
    s = base_scope_object()
    s["kind"] = "files"
    s["repo_root"] = root
    s["files"] = files
    s["needs_clean_worktree"] = False
    carry_modifiers(s, cfg)
    return s


def is_dirty(cwd: str) -> bool:
    """True if there are staged, unstaged, or untracked changes."""
    out = git("status", "--porcelain", cwd=cwd)
    return bool(out)


def current_branch(cwd: str) -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)


def _ref_resolves(cwd: str, ref: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=cwd, capture_output=True,
    ).returncode == 0


def default_branch(cwd: str) -> str | None:
    """Return a ref name (locally resolvable) for the repository default branch."""
    r = subprocess.run(
        ["gh", "repo", "view", "--json", "defaultBranchRef"],
        cwd=cwd, capture_output=True, text=True,
    )
    if r.returncode == 0:
        try:
            name = json.loads(r.stdout)["defaultBranchRef"]["name"]
            for ref in (name, f"origin/{name}"):
                if _ref_resolves(cwd, ref):
                    return ref
        except (KeyError, json.JSONDecodeError):
            pass
    for candidate in ("main", "master", "origin/main", "origin/master"):
        if _ref_resolves(cwd, candidate):
            return candidate
    return None


def pr_for_current_branch(cwd: str) -> int | None:
    r = subprocess.run(
        ["gh", "pr", "view", "--json", "number"],
        cwd=cwd, capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)["number"]


def resolve_pr(cfg: dict, root: str) -> dict:
    pr = cfg["pr_number"]
    # gh pr view does NOT expose baseRepository (only headRepository). The PR's
    # base repo is whatever repo `gh pr view` is being run against — i.e., the
    # current repo as reported by `gh repo view`. So we fetch them separately
    # and stitch together.
    fields = "number,headRefName,baseRefName,headRefOid,baseRefOid,headRepository"
    r = subprocess.run(
        ["gh", "pr", "view", str(pr), "--json", fields],
        cwd=root, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"error: gh pr view failed: {r.stderr.strip()}")
    meta = json.loads(r.stdout)
    r2 = subprocess.run(
        ["gh", "repo", "view", "--json", "url"],
        cwd=root, capture_output=True, text=True,
    )
    if r2.returncode != 0:
        raise SystemExit(f"error: gh repo view failed (needed for base_repo_url): {r2.stderr.strip()}")
    base_repo_url = json.loads(r2.stdout)["url"]
    s = base_scope_object()
    s["kind"] = "pr"
    s["repo_root"] = root
    s["pr_number"] = meta["number"]
    s["head_ref_name"] = meta["headRefName"]
    s["base_ref_name"] = meta["baseRefName"]
    s["head_sha"] = meta["headRefOid"]
    s["base_sha"] = meta["baseRefOid"]
    s["head_repo_url"] = meta["headRepository"]["url"] if meta.get("headRepository") else base_repo_url
    s["base_repo_url"] = base_repo_url
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s


SCOPE_RESOLVERS = {
    "uncommitted": resolve_uncommitted,
    "base": resolve_base,
    "commit": resolve_commit,
    "files": resolve_files,
    "pr": resolve_pr,
}


def main() -> None:
    cfg = json.load(sys.stdin)
    root = repo_root()
    scope_flag = cfg["scope_flag"]
    if scope_flag is None:
        dirty = is_dirty(root)
        pr_num = pr_for_current_branch(root)
        if dirty and pr_num is not None:
            raise SystemExit(
                "error: ambiguous scope — tree has uncommitted changes and "
                f"current branch has PR #{pr_num}. Pass --uncommitted or --pr {pr_num}."
            )
        if dirty:
            scope_flag = "uncommitted"
        elif pr_num is not None:
            scope_flag = "pr"
            cfg["pr_number"] = pr_num
        else:
            branch = current_branch(root)
            default = default_branch(root)
            if default is None or branch == default:
                raise SystemExit(
                    "error: nothing to review (clean tree, on default branch, no PR)"
                )
            scope_flag = "base"
            cfg["base_branch"] = default
    resolver = SCOPE_RESOLVERS[scope_flag]
    scope = resolver(cfg, root)
    json.dump(scope, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
