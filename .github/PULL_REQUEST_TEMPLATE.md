<!-- Replace this comment with a concise summary of the change. Bullets are fine. -->

## Summary

-
-

## Test plan

- [ ] `pytest -v` passes locally
- [ ] If touching orchestrate.py, the relevant phase's test file (`tests/test_orchestrate_*.py`) has been updated/extended
- [ ] If touching SKILL.md or commands/combined-review.md, the change preserves the 6-tool-call boundary documented in the refactor spec
- [ ] If touching install.sh, verified against a fresh `HOME=$(mktemp -d)`

## Related

<!-- Issue refs, prior PRs, design spec sections, etc. -->
