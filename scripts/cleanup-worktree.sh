#!/usr/bin/env bash
# cleanup-worktree.sh <repo_root> <worktree_path>
#
# Triple-assertion gate before destructive removal:
#   1. Path appears in `git worktree list --porcelain` for the repo.
#   2. Path matches the combined-review-* mktemp pattern under $TMPDIR or /tmp.
#   3. Path is not the repo root, and not the main worktree.
# Plus: skip if `.combined-review-keep` marker exists at the worktree root.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: cleanup-worktree.sh <repo_root> <worktree_path>" >&2
  exit 2
fi
REPO="$1"
WT="$2"
# Use `pwd -P` (physical) throughout so we compare canonical paths. macOS
# aliases /var -> /private/var; without -P, the worktree's parent (canonical)
# and $TMPDIR (logical) mismatch and the gate refuses a legitimate cleanup.
REPO_ABS="$(cd "$REPO" && pwd -P)"
WT_ABS="$(cd "$(dirname "$WT")" && pwd -P)/$(basename "$WT")"

# 0. Marker check
if [[ -f "$WT_ABS/.combined-review-keep" ]]; then
  echo "refused: marker .combined-review-keep present at $WT_ABS" >&2
  exit 3
fi

# 1. git worktree registry check
if ! git -C "$REPO_ABS" worktree list --porcelain | grep -Fq "worktree $WT_ABS"; then
  echo "refused: $WT_ABS not in git worktree list for $REPO_ABS" >&2
  exit 3
fi

# 2. mktemp pattern check (basename must start with combined-review-)
base="$(basename "$WT_ABS")"
if [[ ! "$base" =~ ^combined-review- ]]; then
  echo "refused: $WT_ABS basename does not match combined-review-* pattern" >&2
  exit 3
fi
parent="$(cd "$(dirname "$WT_ABS")" && pwd -P)"
TMP="${TMPDIR:-/tmp}"
TMP_ABS="$(cd "$TMP" && pwd -P)"
TMP_PHYS="$(cd /tmp && pwd -P)"
if [[ "$parent" != "$TMP_ABS" && "$parent" != "$TMP_PHYS" ]]; then
  echo "refused: $WT_ABS parent ($parent) is not \$TMPDIR ($TMP_ABS) or /tmp ($TMP_PHYS)" >&2
  exit 3
fi

# 3. not repo root, not main worktree
if [[ "$WT_ABS" == "$REPO_ABS" ]]; then
  echo "refused: $WT_ABS is the repo root" >&2
  exit 3
fi
main_wt="$(git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2; exit}')"
if [[ "$WT_ABS" == "$main_wt" ]]; then
  echo "refused: $WT_ABS is the main worktree" >&2
  exit 3
fi

git -C "$REPO_ABS" worktree remove --force "$WT_ABS"
echo "removed: $WT_ABS"
