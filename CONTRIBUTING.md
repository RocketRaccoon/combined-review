# Contributing to combined-review

Small personal-tool project — contributions welcome but bear in mind the scope is deliberately narrow (see [README §Why this exists](README.md#why-this-exists) and the refactor spec §3 in the parent repo). If your idea lands in the "deferred" list (multi-provider, debate mode, config.yaml backends, etc.), open an issue first to discuss before writing code.

## Dev setup

```bash
git clone https://github.com/RocketRaccoon/combined-review.git
cd combined-review
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

Tests should pass without `codex` or an authenticated `gh` — the suite uses `--no-codex` by default in phase-a tests and stubs `gh` via the `fake_bin` pytest fixture. One test (`test_phase_a_codex_preflight_fires_when_codex_missing`) self-skips when `codex` IS installed.

## Running the skill locally

Develop against your working copy with `claude --plugin-dir ./plugins/combined-review`, or add the repo as a local marketplace: `/plugin marketplace add ./` then `/plugin install combined-review@rocketraccoon`. Restart Claude Code (or run `/reload-plugins`) after editing the skill so the harness re-reads its frontmatter.

## Style

- Python 3.11+ syntax (`int | None`, `dict[str, ...]`).
- No third-party runtime dependencies (stdlib only); `pytest` for dev. Don't add runtime deps — the plugin runs from a copied cache with no `pip install`.
- Bash scripts use `set -euo pipefail` and pass file paths via `--` where ambiguity is possible.
- Tests live next to the script they cover: `tests/test_<script>.py`. New behavior gets a new test in the same file, not a new test file.
- Don't `mktemp` from Bash — every temp file goes through Python's `tempfile` module via `orchestrate.py`. (The whole point of the refactor was killing the `mktemp -t` portability mess.)

## Anatomy

- **`plugins/combined-review/scripts/orchestrate.py`** — the single-process orchestrator. Five subcommands (phase-a / run-codex / phase-c-pre / phase-c-post / cleanup). Owns every temp file in a run.
- **`plugins/combined-review/scripts/parse-args.py`, `resolve-scope.py`, `materialize-scope.py`, `render-prompt.py`, `run-codex.py`, `normalize-findings.py`, `validate-clusters.py`, `report.py`** — single-purpose units, called by orchestrate.py via subprocess. Each has its own standalone CLI for testing.
- **`plugins/combined-review/scripts/cleanup-worktree.sh`, `gc-worktrees.sh`** — the only Bash. Triple-assertion safety gate before worktree removal.
- **`plugins/combined-review/prompts/{code,spec,plan,docs,_schema}.md`** — mode-specific review briefs + the `---FINDING---` schema appended to every reviewer prompt.
- **`plugins/combined-review/skills/review/SKILL.md`** — the single Claude Code skill (invoked `/combined-review:review`); describes the 6-step orchestration the harness must run. **`plugins/combined-review/.claude-plugin/plugin.json`** + the repo-root **`.claude-plugin/marketplace.json`** are the plugin and self-hosted-marketplace manifests.

## When making a change

- **Touching `orchestrate.py`?** Update or add tests in the matching `tests/test_orchestrate_*.py`.
- **Touching a per-step script?** Update its existing tests (`tests/test_<script>.py`); the orchestrator subprocesses these so contract changes propagate automatically.
- **Touching the skill?** It lives at `plugins/combined-review/skills/review/SKILL.md`. Verify with `grep -n "Agent" plugins/combined-review/skills/review/SKILL.md` that every mention is a "don't call it Agent" warning. `Task` is the actual tool name; misnaming silently degrades the parallel-fanout flow.
- **Adding or renaming a manifest field?** Run `claude plugin validate --strict ./plugins/combined-review` before publishing — the authoritative pre-publish gate. CI runs a lighter pure-Python sanity check (`tests/test_plugin_manifests.py`).

## PRs

CI runs `pytest` on Python 3.11 + 3.12 (Ubuntu). Both must be green before merge.

Use [the PR template](.github/PULL_REQUEST_TEMPLATE.md) — the test-plan checklist is the bar for "ready for review".

## Issues

[Bug](.github/ISSUE_TEMPLATE/bug_report.md) and [feature request](.github/ISSUE_TEMPLATE/feature_request.md) templates exist. Use them.

## License

MIT — see [LICENSE](LICENSE). Contributions land under the same license.
