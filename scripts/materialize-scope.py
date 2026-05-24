#!/usr/bin/env python3
"""materialize-scope.py — scope object in → materialized review subject out.

Produces the concrete diff + per-file content blob that both Codex and the
Claude sub-agents consume. For non-`uncommitted`/`files` scopes, creates the
disposable worktree used by run-codex.py.

This patch handles only the `uncommitted` kind. Other kinds are added in
subsequent patches.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def git(*args, cwd: str, check: bool = True) -> str:
    r = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )
    return r.stdout


def symlink_target(repo: str, path: str) -> str | None:
    """Return the link target string for a symlink in the working tree, or None."""
    full = Path(repo) / path
    try:
        return os.readlink(full)
    except (OSError, FileNotFoundError):
        return None


def submodule_sha_at(repo_or_worktree: str, ref: str, path: str) -> str | None:
    """Return the submodule pointer SHA at a ref.

    For commit refs (HEAD, base_sha, merge_base, parent_sha): read from
    `git ls-tree <ref>` — gives the committed pointer.

    For ref='WORKTREE': read the submodule's actual working-tree HEAD via
    `git -C <submodule-path> rev-parse HEAD`. This is intentionally NOT the
    index pointer from `git ls-files --stage` — if the user `cd`'d into the
    submodule and checked out a different commit but hasn't `git add`'d the
    bump yet, the index still shows the old SHA. The actual working-tree HEAD
    is what the reviewer should see for an unstaged submodule bump. Without
    this, `--uncommitted` would render no real change for the most common
    submodule-update workflow."""
    if ref == "WORKTREE":
        full = Path(repo_or_worktree) / path
        if not full.is_dir():
            return None
        r = subprocess.run(
            ["git", "-C", str(full), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            return None
        sha = r.stdout.strip()
        return sha or None
    r = subprocess.run(
        ["git", "ls-tree", ref, "--", path],
        cwd=repo_or_worktree, capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None
    parts = r.stdout.split()
    if len(parts) < 3 or parts[0] != "160000":
        return None
    return parts[2]


def detect_kind(repo: str, path: str) -> str:
    """Return text|binary|symlink|submodule for a path in the working tree."""
    full = Path(repo) / path
    if full.is_symlink():
        return "symlink"
    # git submodule detection via ls-files --stage (mode 160000)
    out = subprocess.run(
        ["git", "ls-files", "--stage", "--", path],
        cwd=repo, capture_output=True, text=True,
    ).stdout.strip()
    if out.startswith("160000 "):
        return "submodule"
    # Binary detection: git's own attribute check
    chk = subprocess.run(
        ["git", "check-attr", "binary", "--", path],
        cwd=repo, capture_output=True, text=True,
    ).stdout
    if "binary: set" in chk:
        return "binary"
    # Sniff for NUL byte as fallback
    try:
        with full.open("rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return "binary"
    except (FileNotFoundError, IsADirectoryError):
        pass
    return "text"


def safe_read_text(repo: str, path: str) -> str | None:
    p = Path(repo) / path
    if not p.exists() or p.is_dir():
        return None
    try:
        return p.read_text()
    except (UnicodeDecodeError, OSError):
        return None


def detect_kind_at_ref(repo_or_worktree: str, ref: str, path: str) -> str:
    """Determine file kind (text|binary|symlink|submodule) at a specific git
    ref. Used for DELETED files — the working tree no longer has them, so the
    working-tree-based `detect_kind` is wrong (it would default to text and
    then text-decoding a binary blob would either crash or inline garbage)."""
    r = subprocess.run(
        ["git", "ls-tree", ref, "--", path],
        cwd=repo_or_worktree, capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return "text"  # unknown; fall back to text and let read_at_ref decide
    # git ls-tree output: "<mode> <type> <sha>\t<path>"
    parts = r.stdout.split()
    if len(parts) < 3:
        return "text"
    mode, _type, sha = parts[0], parts[1], parts[2]
    if mode == "160000":
        return "submodule"
    if mode == "120000":
        return "symlink"
    # Sniff for binary by reading the blob bytes
    blob = subprocess.run(
        ["git", "cat-file", "blob", sha],
        cwd=repo_or_worktree, capture_output=True,  # bytes, no text=True
    )
    if blob.returncode == 0 and b"\x00" in blob.stdout[:8192]:
        return "binary"
    return "text"


def read_at_ref(repo_or_worktree: str, ref: str, path: str) -> str | None:
    """Read text file content at a ref. Reads bytes and only decodes if valid
    UTF-8. Returns None for missing files, binary content, or decode errors.

    Critical: must NOT use subprocess `text=True` here — that would force
    UTF-8 decoding inside subprocess and raise UnicodeDecodeError for
    binary blobs (deleted PNGs, etc.), crashing materialization."""
    r = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=repo_or_worktree, capture_output=True,  # bytes
    )
    if r.returncode != 0:
        return None
    try:
        return r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def read_at_head(repo: str, path: str) -> str | None:
    """Back-compat wrapper for legacy callers — prefer read_at_ref directly."""
    return read_at_ref(repo, "HEAD", path)


def parse_name_status(out: str) -> list[tuple[str, str, str | None]]:
    """Parse `git diff --name-status` output into (status, path, old_path)."""
    entries = []
    for line in out.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("R") and len(parts) == 3:
            entries.append(("renamed", parts[2], parts[1]))
        elif code == "A":
            entries.append(("added", parts[1], None))
        elif code == "M":
            entries.append(("modified", parts[1], None))
        elif code == "D":
            entries.append(("deleted", parts[1], None))
        elif code == "T":
            entries.append(("typechange", parts[1], None))
        else:
            entries.append((code, parts[1] if len(parts) > 1 else "?", None))
    return entries


def make_worktree(repo: str, ref: str) -> str:
    repo_basename = Path(repo).name
    tmp = tempfile.mkdtemp(
        prefix=f"combined-review-{repo_basename}-", dir=os.environ.get("TMPDIR", "/tmp")
    )
    Path(tmp).rmdir()
    subprocess.run(
        ["git", "worktree", "add", "--detach", tmp, ref],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return tmp


def materialize_diff_in_worktree(
    repo: str, worktree: str, base_sha: str, head_sha: str
) -> tuple[str, list[dict], int]:
    merge_base = subprocess.run(
        ["git", "merge-base", base_sha, head_sha],
        cwd=worktree, capture_output=True, text=True, check=True,
    ).stdout.strip()

    unified = git("diff", f"{base_sha}...{head_sha}", cwd=worktree)
    name_status = git("diff", "--name-status", f"{base_sha}...{head_sha}", cwd=worktree)
    changed: list[dict] = []
    for status, path, old_path in parse_name_status(name_status):
        if status == "deleted":
            kind = detect_kind_at_ref(worktree, merge_base, path)
        else:
            kind = detect_kind(worktree, path)
        entry = {
            "path": path, "old_path": old_path, "status": status, "kind": kind,
            "lines_changed": None, "post_content": None,
            "pre_content": None, "note": None,
        }
        if kind == "text" and status != "deleted":
            entry["post_content"] = safe_read_text(worktree, path)
        if status == "deleted":
            if kind == "text":
                entry["pre_content"] = read_at_ref(worktree, merge_base, path)
            elif kind == "binary":
                entry["note"] = "binary file deleted — content not inlined"
            elif kind == "symlink":
                entry["symlink_target"] = read_at_ref(worktree, merge_base, path)
                entry["note"] = "symlink deleted"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
                entry["submodule_post_sha"] = None
                entry["note"] = "submodule removed"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        elif kind == "symlink":
            entry["symlink_target"] = symlink_target(worktree, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
            entry["submodule_post_sha"] = submodule_sha_at(worktree, head_sha, path)
            entry["note"] = "submodule pointer change"
        changed.append(entry)
    total = sum(
        1 for line in unified.splitlines()
        if (line.startswith("+") or line.startswith("-"))
        and not line.startswith(("+++", "---"))
    )
    return unified, changed, total


def materialize_base(scope: dict) -> dict:
    repo = scope["repo_root"]
    worktree = make_worktree(repo, scope["head_sha"])
    try:
        unified, changed, total = materialize_diff_in_worktree(
            repo, worktree, scope["base_sha"], scope["head_sha"]
        )
        return {
            "scope_kind": "base",
            "scope_summary": (
                f"branch {scope['base_ref_name']}...HEAD "
                f"({scope['base_sha'][:7]}..{scope['head_sha'][:7]})"
            ),
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise


def commit_parent_count(repo_or_worktree: str, sha: str) -> int:
    out = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", sha],
        cwd=repo_or_worktree, capture_output=True, text=True, check=True,
    ).stdout.strip()
    return max(0, len(out.split()) - 1)


def materialize_commit(scope: dict) -> dict:
    repo = scope["repo_root"]
    sha = scope["commit_sha"]
    worktree = make_worktree(repo, sha)
    try:
        n_parents = commit_parent_count(worktree, sha)
        if n_parents == 0:
            raise SystemExit(
                f"error: commit {sha[:7]} is a root commit (no parent); "
                f"v1 does not support reviewing root commits"
            )
        if n_parents >= 2:
            raise SystemExit(
                f"error: commit {sha[:7]} is a merge commit with {n_parents} parents; "
                f"v1 does not support reviewing merge commits — review the "
                f"merged branch's individual commits instead"
            )
        unified = subprocess.run(
            ["git", "show", "--format=", sha],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout
        name_status = subprocess.run(
            ["git", "show", "--format=", "--name-status", sha],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout
        parent_sha = subprocess.run(
            ["git", "rev-parse", f"{sha}^"],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout.strip()
        changed: list[dict] = []
        for status, path, old_path in parse_name_status(name_status):
            if status == "deleted":
                kind = detect_kind_at_ref(worktree, parent_sha, path)
            else:
                kind = detect_kind(worktree, path)
            entry = {
                "path": path, "old_path": old_path, "status": status, "kind": kind,
                "lines_changed": None, "post_content": None,
                "pre_content": None, "note": None,
            }
            if kind == "text" and status != "deleted":
                entry["post_content"] = safe_read_text(worktree, path)
            if status == "deleted":
                if kind == "text":
                    entry["pre_content"] = read_at_ref(worktree, parent_sha, path)
                elif kind == "binary":
                    entry["note"] = "binary file deleted — content not inlined"
                elif kind == "symlink":
                    entry["symlink_target"] = read_at_ref(worktree, parent_sha, path)
                    entry["note"] = "symlink deleted"
                elif kind == "submodule":
                    entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
                    entry["submodule_post_sha"] = None
                    entry["note"] = "submodule removed"
            elif kind == "binary":
                entry["note"] = "binary file — content not inlined"
            elif kind == "symlink":
                entry["symlink_target"] = symlink_target(worktree, path)
                entry["note"] = "symlink"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
                entry["submodule_post_sha"] = submodule_sha_at(worktree, sha, path)
                entry["note"] = "submodule pointer change"
            changed.append(entry)
        total = sum(
            1 for line in unified.splitlines()
            if (line.startswith("+") or line.startswith("-"))
            and not line.startswith(("+++", "---"))
        )
        return {
            "scope_kind": "commit",
            "scope_summary": f"commit {sha[:7]}",
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise


def cat_file_exists(repo_or_worktree: str, sha: str) -> bool:
    r = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=repo_or_worktree, capture_output=True,
    )
    return r.returncode == 0


def materialize_pr(scope: dict) -> dict:
    repo = scope["repo_root"]
    head_sha = scope["head_sha"]
    base_sha = scope["base_sha"]
    base_url = scope["base_repo_url"]
    base_ref = scope["base_ref_name"]
    pr = scope["pr_number"]

    repo_basename = Path(repo).name
    worktree = tempfile.mkdtemp(
        prefix=f"combined-review-{repo_basename}-pr-",
        dir=os.environ.get("TMPDIR", "/tmp"),
    )
    Path(worktree).rmdir()
    subprocess.run(
        ["git", "worktree", "add", "--detach", worktree],
        cwd=repo, check=True, capture_output=True, text=True,
    )

    try:
        r = subprocess.run(
            ["gh", "pr", "checkout", "--detach", str(pr)],
            cwd=worktree, capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise SystemExit(f"error: gh pr checkout failed: {r.stderr.strip()}")

        subprocess.run(
            ["git", "fetch", base_url, base_ref],
            cwd=worktree, capture_output=True, text=True,
        )

        current_head = git("rev-parse", "HEAD", cwd=worktree).strip()
        if current_head != head_sha:
            if not cat_file_exists(worktree, head_sha):
                raise SystemExit(
                    f"error: PR head force-pushed mid-review — recorded {head_sha[:7]} "
                    f"no longer reachable. Rerun /combined-review --pr {pr} to fetch the current snapshot."
                )
            subprocess.run(
                ["git", "reset", "--hard", head_sha],
                cwd=worktree, check=True, capture_output=True, text=True,
            )

        if not cat_file_exists(worktree, base_sha):
            raise SystemExit(
                f"error: PR base SHA {base_sha[:7]} not reachable in worktree. "
                f"Rerun /combined-review --pr {pr} to fetch the current snapshot."
            )

        unified, changed, total = materialize_diff_in_worktree(
            repo, worktree, base_sha, head_sha
        )
        return {
            "scope_kind": "pr",
            "scope_summary": f"PR #{pr} ({base_sha[:7]}..{head_sha[:7]})",
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise


def materialize_uncommitted(scope: dict) -> dict:
    root = scope["repo_root"]
    unified = git("diff", "HEAD", cwd=root)
    name_status = git("diff", "--name-status", "HEAD", cwd=root)
    untracked_raw = git("ls-files", "--others", "--exclude-standard", cwd=root)
    untracked = [p for p in untracked_raw.splitlines() if p]

    changed: list[dict] = []
    total_lines = 0
    for status, path, old_path in parse_name_status(name_status):
        # For DELETED files the working tree no longer has the content, so
        # `detect_kind(root, path)` would read nothing and default to text.
        # Inspect HEAD instead to get the real kind (catches deleted binaries,
        # symlinks, submodules).
        if status == "deleted":
            kind = detect_kind_at_ref(root, "HEAD", path)
        else:
            kind = detect_kind(root, path)
        entry = {
            "path": path, "old_path": old_path, "status": status, "kind": kind,
            "lines_changed": None, "post_content": None,
            "pre_content": None, "note": None,
        }
        if kind == "text" and status != "deleted":
            entry["post_content"] = safe_read_text(root, path)
            entry["lines_changed"] = "(modified)"
        if status == "deleted":
            entry["lines_changed"] = "(deleted)"
            if kind == "text":
                entry["pre_content"] = read_at_ref(root, "HEAD", path)
            elif kind == "binary":
                entry["note"] = "binary file deleted — content not inlined"
            elif kind == "symlink":
                # A symlink blob's content IS the target path, so read_at_ref
                # returns it. Without this, reviewers can't see what the
                # deleted symlink used to point at.
                entry["symlink_target"] = read_at_ref(root, "HEAD", path)
                entry["note"] = "symlink deleted"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
                entry["submodule_post_sha"] = None
                entry["note"] = "submodule removed"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        elif kind == "symlink":
            # Without this, the prompt renderer would print only the header
            # for the symlink change — a reviewer can't judge a target swap
            # they can't see.
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            # For submodule bumps we want both the previous and new pointer
            # SHAs so the reviewer can judge what's actually changing.
            entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer change"
        changed.append(entry)

    for path in untracked:
        kind = detect_kind(root, path)
        post = safe_read_text(root, path) if kind == "text" else None
        line_count = len(post.splitlines()) if post else 0
        entry = {
            "path": path, "old_path": None, "status": "added", "kind": kind,
            "lines_changed": "(new file)" if line_count else "(empty)",
            "post_content": post, "pre_content": None, "note": None,
        }
        # Populate kind-specific metadata so untracked symlinks/submodules are
        # as reviewable as their tracked counterparts. Without this, an
        # untracked symlink renders as a header with no target — same bug
        # earlier rounds fixed for tracked entries.
        if kind == "symlink":
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink (untracked, new)"
        elif kind == "submodule":
            entry["submodule_pre_sha"] = None  # never existed before
            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer (untracked, new)"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        changed.append(entry)
        total_lines += line_count

    # Estimate text-line delta from the unified diff (cheap and good-enough)
    for line in unified.splitlines():
        if (line.startswith("+") or line.startswith("-")) and not line.startswith(("+++", "---")):
            total_lines += 1

    return {
        "scope_kind": "uncommitted",
        "scope_summary": "uncommitted changes",
        "unified_diff": unified if unified else None,
        "changed_files": changed,
        "doc_files": [],
        "total_lines_changed": total_lines,
        "changed_file_count": len(changed),
        "has_reviewable_changes": len(changed) > 0,
        # Uncommitted runs in the user's working tree — no disposable worktree
        # gets created. Explicit None keeps the materialize-output shape stable
        # across kinds so Phase A7's `merged["worktree_path"] = MAT_JSON.worktree_path`
        # works without conditional logic.
        "worktree_path": None,
        "warnings": [],
    }


def materialize_files(scope: dict) -> dict:
    root = scope["repo_root"]
    doc_files: list[dict] = []
    for path in scope["files"]:
        kind = detect_kind(root, path)
        entry: dict = {
            "path": path, "status": "current", "kind": kind,
            "content": None, "note": None,
        }
        if kind == "text":
            entry["content"] = safe_read_text(root, path)
        elif kind == "symlink":
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            entry["submodule_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer (no diff — single snapshot)"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        else:
            entry["note"] = f"non-text ({kind}) — content not inlined"
        doc_files.append(entry)
    return {
        "scope_kind": "files",
        "scope_summary": f"{len(doc_files)} file(s) — current working-tree content",
        "unified_diff": None,
        "changed_files": [],
        "doc_files": doc_files,
        "total_lines_changed": 0,
        "changed_file_count": 0,
        "has_reviewable_changes": len(doc_files) > 0,
        "worktree_path": None, "warnings": [],
    }


def maybe_populate_doc_files(out: dict, scope: dict) -> None:
    if scope["mode"] == "code":
        return
    if scope["kind"] == "files":
        return
    docs = []
    for cf in out["changed_files"]:
        if cf["kind"] != "text":
            continue
        if cf["status"] == "deleted":
            content = cf.get("pre_content")
        else:
            content = cf.get("post_content")
        if content is None:
            continue
        docs.append({"path": cf["path"], "status": cf["status"], "content": content})
    out["doc_files"] = docs


KIND_HANDLERS = {
    "uncommitted": materialize_uncommitted,
    "base": materialize_base,
    "commit": materialize_commit,
    "pr": materialize_pr,
    "files": materialize_files,
}


def main() -> None:
    scope = json.load(sys.stdin)
    handler = KIND_HANDLERS.get(scope["kind"])
    if handler is None:
        raise SystemExit(f"error: materialize for kind={scope['kind']!r} not implemented")
    out = handler(scope)
    maybe_populate_doc_files(out, scope)
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
