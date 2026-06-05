---
name: combined-review
description: Use when the user wants a single code/spec/plan review that fuses findings from Claude's pr-review-toolkit sub-agents and Codex CLI in one session. Triggers — PR review, branch-vs-main review, spec/plan review, "review with both tools", "/combined-review".
argument-hint: "[--pr N | --uncommitted | --base BRANCH | --commit SHA | <files...>] [--mode code|spec|plan|docs] [--focus TEXT] [--full] [--no-codex] [--save PATH] [--force-large] [--keep-worktree]"
allowed-tools: ["Bash", "Read", "Write", "Task", "Monitor"]
---

# Combined Review

> **Allowlist note** — Edit/Glob/Grep are intentionally omitted from `allowed-tools`. This skill is a read-only review flow. Bash drives the orchestrator; Read consumes the rendered prompt; Write is needed only for the one cluster-synthesis JSON file and (optionally) the per-agent Task transcripts; Task dispatches sub-agents; Monitor tracks the background codex Bash. The rendered review prompt's no-edit instructions and `codex exec --sandbox read-only` are the primary protections against state changes — the allowlist is defense in depth.

Run Claude pr-review-toolkit sub-agents and Codex (`codex exec --sandbox read-only`) in parallel against the same materialized review subject, then synthesize one deduped, attributed report.

The orchestrator is `${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py` — a single Python process that owns setup, normalization, validation, rendering, and cleanup. **You only do what only you can do**: confirm with the user, dispatch `Task` sub-agents, and write the cluster-synthesis JSON. Invoke it as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py" <phase>` so the call never depends on the cache copy preserving the executable bit, and so a cache path containing spaces still works.

## Sequence — 6 happy-path tool calls; +1 if validation needs repair

### Step 1 — Setup (Bash, one call)

Pass `$ARGUMENTS` via a single-quoted heredoc — **never** via `echo "$ARGUMENTS"`. The single-quoted marker prevents Bash from expanding `$(...)`, backticks, or `$VAR` inside the user's input, so an arg like `--focus "$(touch /tmp/pwned)"` arrives as literal text on stdin instead of running a command. `echo`-style passing is unsafe because Claude must inline the slash command's `$ARGUMENTS` value into the Bash text, and `$(...)` inside that value would execute.

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py" phase-a <<'CR_ARGS_EOF'
$ARGUMENTS
CR_ARGS_EOF
```

Empty `$ARGUMENTS` is allowed — orchestrate.py treats it as "no flags" and falls through to auto-detect (dirty tree → uncommitted; clean branch with open PR → that PR; else base...HEAD).

Parse the stdout JSON into variables: `STATE_FILE`, `PROMPT_PATH`, `TRANSCRIPTS_DIR`, `SCOPE_SUMMARY`, `MODE`, `FOCUS` (null or the user's focus string), `LARGE_DIFF` (bool), `TOTAL_LINES_CHANGED`, `NO_CODEX`, `FULL`.

Exit codes:
- **0** — success, proceed to Step 2.
- **2** — nothing to review (clean tree on default branch, or no diff). Stop. Cleanup already ran inside phase-a; no further action.
- **3** — hard pre-flight failure (not in a git repo / `codex` missing / `gh` not authenticated). Stop, surface the stderr message verbatim.

### Step 2 — Large-diff gate (AskUserQuestion, only when needed)

If `LARGE_DIFF == true` and the user did not pass `--force-large`, ask:

> "Diff is N lines — both reviewers degrade on large inputs. Proceed?"

On **decline**:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py" cleanup --state "$STATE_FILE"
```

then stop. The `cleanup` subcommand is the dedicated abort entry — `phase-c-post` requires `--clusters-file` and cannot serve this path.

### Step 3 — Parallel review (single message, two kinds of tool calls)

Issue in ONE message:

- **Background Bash** (skip if `NO_CODEX == true`):
  ```
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py" run-codex --state "$STATE_FILE"
  ```
  with `run_in_background: true`. Use `Monitor` to know when it completes.

- **One or more `Task` calls** (the tool is literally named `Task` — not "Agent") carrying the rendered prompt. Read `$PROMPT_PATH` once and pass its contents to each `Task`:
  - `MODE == code`, default: 3 `Task` calls with subagent_type=`code-reviewer`, `silent-failure-hunter`, `pr-test-analyzer`.
  - `MODE == code` + `FULL`: add 3 more — `comment-analyzer`, `type-design-analyzer`, `code-simplifier`.
  - `MODE in {spec, plan, docs}`: 1 `Task` call with subagent_type=`document-reviewer` (or `general-purpose` with the document-reviewer brief if that subagent isn't registered).

Wait for the codex background + every `Task` call to return before proceeding.

### Step 4 — Save Task transcripts (Write, one per agent)

Each returned `Task` text goes to `$TRANSCRIPTS_DIR/<agent-name>.txt`. `$TRANSCRIPTS_DIR` was allocated by phase-a (Step 1 stdout) precisely so this Write has a target. Do NOT `mktemp` another directory. Optionally also concatenate everything to `$TRANSCRIPTS_DIR/all.txt` for the audit trail — `phase-c-pre` deliberately skips that name so it isn't double-counted.

### Step 5 — Normalize + alloc clusters file (Bash, one call)

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py" phase-c-pre --state "$STATE_FILE"
```

(No `--claude-transcripts` flag — the dir comes from state.) Parse stdout:

- `NORMALIZED_FINDINGS` — `{codex: [...], claude: {agent: {findings: [...], ...}}}`
- `REVIEWER_SUMMARY` — `{codex: {status, raw_findings, parse_warnings, error?, duration_ms?}, claude: [{agent, status, raw_findings, parse_warnings}]}`
- `CLUSTERS_FILE` — path to the empty file you Write to in Step 6.
- `UNPARSED_CHUNKS` — audit trail of reviewer text that didn't match the finding schema (forward as-is into the cluster JSON's top-level `unparsed_chunks`).

### Step 6 — Synthesize clusters (Write, one call)

Read `NORMALIZED_FINDINGS`. Cluster findings by semantic similarity — read each finding's title + detail + file:line and group ones that are about the same issue. Tag each cluster `agreement` / `claude_only` / `codex_only` / `disagreement`. Write the cluster JSON to `$CLUSTERS_FILE`.

This is the **one Write you do per run.** No other temp files are yours to manage.

Cluster JSON shape (required fields per `validate-clusters.py`):

```json
{
  "scope_summary": "<from phase-a stdout — SCOPE_SUMMARY>",
  "mode": "<from phase-a stdout — MODE>",
  "focus": "<from phase-a stdout — FOCUS; null when the user didn't pass --focus>",
  "reviewer_summary": { /* forward from phase-c-pre */ },
  "clusters": [
    {
      "tag": "agreement|claude_only|codex_only|disagreement",
      "severity": "critical|high|medium|low",
      "file": "path/to/file.py",
      "line": "42" or "42-50",
      "category": "bug|test-gap|perf|security|clarity|style|other",
      "title": "Short cluster title",
      "synthesized_detail": "What the cluster captures + recommended fix.",
      "sources": [
        {"source": "codex", "severity": "high",
         "original_title": "...", "original_detail": "..."},
        {"source": "claude:code-reviewer", "severity": "high",
         "original_title": "...", "original_detail": "..."}
      ],
      "severity_divergence": "(only when sources disagree on severity)"
    }
  ],
  "unparsed_chunks": [ /* forward from phase-c-pre */ ]
}
```

**Anti-patterns — STOP if you catch yourself doing any:**
- Just concatenating findings without clustering.
- Using string-similarity heuristics instead of judgment.
- Skipping synthesis because "it's too hard".
- Summarizing both raw outputs into a prose report instead of clustering.

### Step 7 — Validate + render + cleanup (Bash, one or two calls)

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py" phase-c-post \
  --state "$STATE_FILE" --clusters-file "$CLUSTERS_FILE"
```

Branches on exit code:
- **0**: final report is on stdout. Print it. Cleanup already ran. Done.
- **2**: cluster JSON failed validation on the first attempt; stderr explains the schema violation. **Read the stderr error, rewrite `$CLUSTERS_FILE` addressing it, then re-invoke phase-c-post.** `state.validation_attempts` was bumped, so the second call cannot loop.
- **1**: cluster JSON failed validation on the second attempt; phase-c-post rendered the synthesis-failed report on stdout (preserves the raw-findings audit appendix) and ran cleanup. Print the report. Done.

## Failure handling

- Any non-zero exit from phase-a/run-codex/phase-c-pre/phase-c-post other than the documented codes: surface the error, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/orchestrate.py" cleanup --state "$STATE_FILE"` if a state file exists, stop.
- **Codex non-zero / timeout / SIGKILL**: `phase-c-pre` handles every case (including empty/missing status files — the PR #152 regression-fixed path); report renders with `"codex failed"` in `reviewer_summary`. Don't second-guess it.
- **Individual `Task` agent failure**: continue with the others; the failed agent shows up as `parse_warnings` in the final report.

## Anti-patterns — STOP if any apply

- **Inventing your own scope-detection or pipeline.** `orchestrate.py` owns parse → resolve → materialize → render → normalize → validate → cleanup. Your job is the synthesis Write between Step 5 and Step 7.
- **Calling `mktemp` from Bash, or `Write`-ing JSON to a temp file you allocated.** orchestrate.py manages every temp file. The only Write you do is the cluster-synthesis JSON to the path it gave you in Step 5.
- **Using "Agent" as a tool name.** The tool is `Task`. Misnaming silently falls back to in-context reasoning and skips the parallel fanout — the report would say "claude code-reviewer: 0 findings" with no error.
- **Pre-processing `$ARGUMENTS`.** Pipe it on stdin to `phase-a`; the orchestrator uses `shlex.split` internally and round-trips shell quoting correctly. Writing `$ARGUMENTS` to a file first was the old flow.
- **Skipping cleanup on a non-happy path.** `phase-c-post`'s try/finally handles every post-Step-7 path. The `cleanup` subcommand handles every abort path before that. Every code path in this skill must end with cleanup having run.
