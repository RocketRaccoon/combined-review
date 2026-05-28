---
description: "Run Claude pr-review-toolkit + Codex in parallel; merge findings into one report."
argument-hint: "[--pr N | --uncommitted | --base BRANCH | --commit SHA | <files...>] [--mode code|spec|plan|docs] [--focus TEXT] [--full] [--no-codex] [--save PATH] [--force-large] [--keep-worktree]"
allowed-tools: ["Bash", "Read", "Write", "Task", "Monitor"]
---

# Combined Review

> **Allowlist note** — Edit/Glob/Grep are intentionally omitted from `allowed-tools`. This skill is a read-only review flow. Bash drives the orchestrator; Read consumes the rendered prompt; Write is needed only for the one cluster-synthesis JSON file and (optionally) the per-agent Task transcripts; Task dispatches sub-agents; Monitor tracks the background codex Bash. The rendered review prompt's no-edit instructions and `codex exec --sandbox read-only` are the primary protections against state changes — the allowlist is defense in depth.

User invoked `/combined-review` with the literal argument string below.

```
$ARGUMENTS
```

You are now in the `combined-review` skill. Read and follow `~/.claude/skills/combined-review/SKILL.md`. It describes a 6-step sequence; the orchestrator at `$SKILL_DIR/scripts/orchestrate.py` owns everything except interactive confirmation, parallel `Task` dispatch, and the cluster-synthesis Write.

**Do not invent your own pipeline.** Follow SKILL.md step for step.

The argument string above is passed to `orchestrate.py phase-a` via stdin (the orchestrator uses `shlex.split` internally and round-trips shell-quoted values like `--focus "API surface"` correctly). Do NOT pre-process `$ARGUMENTS` or write it to a temp file first — that was the old flow; the new orchestrator handles quoting itself.
