#!/usr/bin/env bash
# gc-worktrees.sh <repo_root>
#
# Enumerates worktrees via `git worktree list --porcelain`, selects entries
# matching the combined-review-* basename pattern, AND older than 24h
# (by mtime), AND not carrying a .combined-review-keep marker. Each removal
# goes through the same triple-assertion gate as cleanup-worktree.sh.
set -euo pipefail

REPO="${1:-$PWD}"
REPO_ABS="$(cd "$REPO" && pwd)"
AGE_HOURS="${COMBINED_REVIEW_GC_AGE_HOURS:-24}"
NOW="$(date +%s)"
CUTOFF=$(( NOW - (AGE_HOURS * 3600) ))

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Portable mtime helper. Tries GNU `stat -c %Y` first, then BSD `stat -f %m`,
# then Python as a last-resort fallback. Earlier versions of this script tried
# `stat -f %m` first, but on GNU/Linux `-f` means "filesystem mode" (not file)
# and `%m` is the mount point, so the command exits 0 with non-numeric output —
# the GNU `-c %Y` fallback never ran, and the numeric `[[ ]]` comparison broke
# silently, leaving stale worktrees forever.
mtime_of() {
  local p="$1" m
  if m=$(stat -c %Y "$p" 2>/dev/null); then
    echo "$m"
  elif m=$(stat -f %m "$p" 2>/dev/null); then
    echo "$m"
  else
    python3 -c 'import os, sys; print(int(os.stat(sys.argv[1]).st_mtime))' "$p" 2>/dev/null || echo 0
  fi
}

git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2}' \
| while IFS= read -r wt; do
  base="$(basename "$wt")"
  [[ "$base" =~ ^combined-review- ]] || continue
  [[ -f "$wt/.combined-review-keep" ]] && continue
  mtime="$(mtime_of "$wt")"
  # Sanity-check that mtime is a positive integer before arithmetic; on the
  # off chance both stat forms return something non-numeric, treat as "skip"
  # rather than crash the GC loop.
  if [[ "$mtime" =~ ^[0-9]+$ ]] && [[ "$mtime" -lt "$CUTOFF" ]]; then
    "$SCRIPT_DIR/cleanup-worktree.sh" "$REPO_ABS" "$wt" || true
  fi
done
