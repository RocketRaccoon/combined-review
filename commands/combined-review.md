---
description: Run Claude pr-review-toolkit + Codex in parallel; merge findings into one report.
argument-hint: "[--pr N | --uncommitted | --base BRANCH | --commit SHA | <files...>] [--mode code|spec|plan|docs] [--focus TEXT] [--full] [--no-codex] [--save PATH] [--force-large] [--keep-worktree]"
# Edit is intentionally omitted — this is a read-only review flow. Write is
# needed for orchestrator-owned temp files (prompt, scope, args) and the
# optional --save report path. Bash is unavoidable (the entire pipeline is
# Bash-driven). Removing Edit is defense-in-depth, NOT a hard sandbox: Write
# and Bash can still modify repo files if the model drifts. The primary
# protection against unintended edits is the no-edit instruction inside the
# rendered review prompt + codex's --sandbox read-only enforcement; the
# allowlist trim just removes the most obvious code-modification path.
allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep", "Task", "Monitor"]
---

# Combined Review

User invoked `/combined-review` with the literal argument string below (do NOT
substitute it into a shell command — pass it through the args-file path
described in SKILL.md Phase A2):

```
$ARGUMENTS
```

You are now in the `combined-review` skill. Read and follow
`~/.claude/skills/combined-review/SKILL.md` for the full orchestration pipeline.

**Critical reminders for this run:**

- Phase A is **sequential** — each step depends on the previous. Do NOT batch.
- `$ARGUMENTS` is captured as literal text — write it to a temp file using the `Write` tool, then pass that file's path to `parse-args.py --args-file`. Never shell-substitute `$ARGUMENTS` into a Bash command line.
- Phase B is the **only** phase where parallel tool calls happen (codex background + Agent sub-agents in the same message).
- Phase D cleanup **always** runs, even on errors.
- Codex side uses `codex exec --sandbox read-only` exclusively — never `codex review`.
- Worktree cleanup is gated by `cleanup-worktree.sh`'s triple-assertion check — do not invoke `git worktree remove` directly.

Start with Phase A1 (gc-worktrees).
