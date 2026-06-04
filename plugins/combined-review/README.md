# combined-review (plugin)

Runs Claude's `pr-review-toolkit` sub-agents and `codex exec --sandbox read-only`
in parallel against the same materialized review subject, then synthesizes the
findings into one deduped, attributed report.

Invoke with `/combined-review:review` (or let Claude auto-invoke it when you ask
to "review this with both tools").

## Prerequisites

- Python 3.11+ (standard library only — no `pip install` needed)
- `codex` CLI on PATH, logged in: `codex login status`
- `gh` CLI on PATH, authenticated: `gh auth status` — only for `--pr` scope

See the [repository README](https://github.com/RocketRaccoon/combined-review)
for full usage, architecture, and development docs.
