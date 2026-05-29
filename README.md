# combined-review

A Claude Code skill that runs Claude's `pr-review-toolkit` sub-agents and `codex exec --sandbox read-only` in parallel against the same materialized review subject, then synthesizes the findings into one deduped, attributed report.

```
/combined-review --pr 123 --mode plan
```

## Why this exists

Single-LLM reviews miss things. Two LLMs of different lineages reviewing the same code catch a strictly larger set of real bugs — but running them by hand in separate sessions, then de-duplicating their findings, is tedious. `combined-review` collapses that into one slash command: parallel reviewers, schema-validated cluster output, single report.

### Prior art (and what's different here)

Two existing projects do something similar, and the design here owes a lot to both. If their tradeoffs fit your workflow better, use those.

- **[council](https://github.com/ktaletsk/council)** by [@ktaletsk](https://github.com/ktaletsk) — Claude Code skill that runs ensemble reviews across Claude Code / Codex / OpenCode / Cursor CLI and merges findings into `.reviews/COMBINED_REVIEW.md`. Multi-backend (more agents than this skill supports), config-driven via `config.yaml`. Single-shell-script orchestrator.
- **[The Star Chamber](https://blog.mozilla.ai/the-star-chamber-multi-llm-consensus-for-code-quality/)** by Mozilla.ai — multi-LLM consensus tool that classifies findings into Consensus / Majority / Individual tiers; supports a `--debate --rounds N` mode and a formal council-protocol JSON wire format. Provider-agnostic.

Differentiators of `combined-review`:

- **Mode-aware prompts** — separate review briefs for `code`, `spec`, `plan`, and `docs` modes. Spec/plan reviews don't get treated as code reviews.
- **Five scope kinds** — `--uncommitted`, `--base BRANCH`, `--commit SHA`, `--pr N`, and explicit file lists. Auto-detect picks one based on tree state + current branch + PR existence.
- **Worktree isolation with triple-assertion safety gate** — diff-based scopes run in a disposable `git worktree`; teardown via `cleanup-worktree.sh` only proceeds when the path is in `git worktree list --porcelain`, matches the `combined-review-*` prefix, AND is not the repo root.
- **JSON-Schema-validated cluster output with one-shot LLM repair** — the synthesis pass writes a typed cluster JSON; if it fails validation, the orchestrator emits the validator error and Claude gets one chance to rewrite before the report falls back to the raw-findings audit appendix.
- **6-tool-call orchestration** — Claude only does what only Claude can: confirm with the user, dispatch `Task` sub-agents in parallel, and write the cluster synthesis. Everything else is a Python `orchestrate.py` subprocess.

If you want multi-backend, config-driven, or debate-mode reviews, council and Star Chamber are more mature.

## Install

```bash
git clone https://github.com/RocketRaccoon/combined-review.git
cd combined-review
./scripts/install.sh
```

The install script refuses to silently overwrite an existing skill at the same path — if you have an older install, remove it first:

```bash
rm ~/.claude/skills/combined-review ~/.claude/commands/combined-review.md
./scripts/install.sh
```

Then restart Claude Code so it picks up the new slash command.

## Dependencies

- Python 3.11+
- `jsonschema` (installed via `pip install -e ".[dev]"` from this repo)
- `codex` CLI on PATH, logged in: `codex login status`
- `gh` CLI on PATH, authenticated: `gh auth status` — only needed for `--pr` scope

## Usage

```bash
/combined-review                              # auto-detect scope, code mode
/combined-review --pr 152                     # review PR #152
/combined-review --uncommitted --mode spec    # review uncommitted spec changes
/combined-review --commit abc1234             # review a single commit
/combined-review docs/design.md --mode docs   # review one file as a doc
/combined-review --pr 152 --focus "auth surface"  # quoted focus round-trips
/combined-review --no-codex                   # Claude-only (skip codex)
/combined-review --full                       # 6 Claude agents instead of 3
```

Auto-detect picks `--uncommitted` when the tree is dirty, `--pr N` when the current branch has an open PR, or `--base <default>` otherwise. Ambiguous cases (dirty tree + open PR) error and ask you to pass an explicit scope.

## Architecture

Six steps per run (seven if cluster JSON needs one validation-repair round):

1. **phase-a** (Bash) — parse args, resolve scope, codex+gh preflight, materialize, render prompt, write state file
2. **AskUserQuestion** (only if diff > 2000 lines and `--force-large` not passed)
3. **Parallel review** (single message, multiple tool calls): codex background Bash + N `Task` sub-agents
4. **Write transcripts** — save each `Task` return text to the transcripts dir phase-a allocated
5. **phase-c-pre** (Bash) — normalize codex stdout + per-agent transcripts; allocate empty clusters file
6. **Write clusters JSON** — Claude clusters findings semantically and writes the result
7. **phase-c-post** (Bash) — validate JSON; render report (or one-shot repair retry); cleanup

For the full design rationale, see [the refactor spec](https://github.com/REDACTED-AI/REDACTED_ai/blob/main/docs/superpowers/specs/2026-05-26-combined-review-refactor-design.md) and the [original skill spec](https://github.com/REDACTED-AI/REDACTED_ai/blob/main/docs/superpowers/specs/2026-05-11-combined-review-skill-design.md).

## Develop

```bash
pip install -e ".[dev]"
pytest -v          # 116 tests as of this writing
```

`scripts/orchestrate.py` is the orchestrator. Each phase boundary has its own test file under `tests/`. The per-step scripts (`parse-args.py`, `resolve-scope.py`, `materialize-scope.py`, `render-prompt.py`, `run-codex.py`, `normalize-findings.py`, `validate-clusters.py`, `report.py`) are kept as importable single-purpose units with their own CLI surfaces and tests; `orchestrate.py` invokes them via subprocess.

## License

MIT — see [LICENSE](./LICENSE).
