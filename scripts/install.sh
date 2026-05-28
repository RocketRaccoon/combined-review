#!/usr/bin/env bash
# install.sh — link combined-review into ~/.claude/skills and ~/.claude/commands.
#
# Refuses to overwrite anything that isn't already a symlink to this repo.
# To replace an old install at the same path, remove it first:
#   rm ~/.claude/skills/combined-review ~/.claude/commands/combined-review.md
# then re-run this script.
#
# Why no `ln -sfn`: PR #152 review (P2 — install ln -sfn silently overwrites
# existing skill installs). `-f` would replace any prior symlink without
# warning, and on macOS BSD ln it would even replace a real directory at the
# target. Either is too easy to do accidentally.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd -P)"
SKILL_LINK="$HOME/.claude/skills/combined-review"
CMD_LINK="$HOME/.claude/commands/combined-review.md"
SKILL_TARGET="$REPO"
CMD_TARGET="$REPO/commands/combined-review.md"

ensure_parent_dir() {
  local link="$1"
  local parent
  parent="$(dirname "$link")"
  if [[ ! -d "$parent" ]]; then
    echo "creating: $parent"
    mkdir -p "$parent"
  fi
}

install_link() {
  local link="$1" want="$2"
  ensure_parent_dir "$link"
  if [[ -L "$link" ]]; then
    local cur
    cur="$(readlink "$link")"
    # macOS aliases /var -> /private/var so canonicalize before compare
    local cur_real
    cur_real="$(cd "$(dirname "$cur")" 2>/dev/null && pwd -P)/$(basename "$cur")" || cur_real="$cur"
    local want_real
    want_real="$(cd "$(dirname "$want")" 2>/dev/null && pwd -P)/$(basename "$want")" || want_real="$want"
    if [[ "$cur_real" == "$want_real" ]]; then
      echo "ok: $link already points at $want"
      return 0
    fi
    echo "refused: $link is a symlink pointing at:" >&2
    echo "  $cur" >&2
    echo "Not $want. To replace, first run: rm $link" >&2
    exit 1
  fi
  if [[ -e "$link" ]]; then
    echo "refused: $link exists and is NOT a symlink." >&2
    echo "  Refusing to silently overwrite a real file/directory." >&2
    echo "  To replace, first run: rm -rf $link" >&2
    exit 1
  fi
  ln -s "$want" "$link"
  echo "installed: $link -> $want"
}

install_link "$SKILL_LINK" "$SKILL_TARGET"
install_link "$CMD_LINK"   "$CMD_TARGET"

echo
echo "Combined Review installed. Verify with:"
echo "  ls -la $SKILL_LINK $CMD_LINK"
echo "Then in Claude Code, run:  /combined-review --help"
