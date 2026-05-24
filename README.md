# combined-review

A Claude Code skill that runs Claude's `pr-review-toolkit` sub-agents and
`codex exec --sandbox read-only` in parallel against the same materialized
review subject, then synthesizes the findings into one report.

See `docs/superpowers/specs/2026-05-11-combined-review-skill-design.md`
in the original REDACTED repo for the design rationale.

## Install

```bash
# from this repo's root (~/projects/combined-review)
mkdir -p ~/.claude/skills ~/.claude/commands
ln -sfn "$PWD" ~/.claude/skills/combined-review
ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md

# Verify
ls -la ~/.claude/skills/combined-review
ls -la ~/.claude/commands/combined-review.md
```

## Dependencies

- Python 3.11+
- `jsonschema` (`pip install -e ".[dev]"` from this repo)
- `codex` CLI on PATH, logged in (`codex login status`)
- `gh` CLI on PATH, authenticated (`gh auth status`)

## Run

```
/combined-review              # auto-detect scope, code mode
/combined-review --pr 105
/combined-review --uncommitted
/combined-review --mode spec docs/design.md
```

## Develop

```bash
pip install -e ".[dev]"
pytest -v
```
