<!-- Replace this comment with a concise summary of the change. Bullets are fine. -->

## Summary

-
-

## Test plan

- [ ] `pytest -q` passes locally
- [ ] If touching orchestrate.py, the relevant phase's test file (`tests/test_orchestrate_*.py`) has been updated/extended
- [ ] If touching the skill (`plugins/combined-review/skills/review/SKILL.md`), the change preserves the 6-tool-call orchestration boundary
- [ ] If touching `plugin.json`/`marketplace.json`, `claude plugin validate --strict ./plugins/combined-review` passes

## Related

<!-- Issue refs, prior PRs, design spec sections, etc. -->
