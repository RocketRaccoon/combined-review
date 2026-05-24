---
name: combined-review
description: Use when the user wants a single code/spec/plan review that fuses findings from Claude's pr-review-toolkit sub-agents and Codex CLI in one session. Triggers — PR review, branch-vs-main review, spec/plan review, "review with both tools", "/combined-review".
---

# Combined Review

You are orchestrating a two-tool code review. You will run Claude sub-agents
and Codex (`codex exec --sandbox read-only`) in parallel against the same
materialized review subject, then synthesize a single deduped report.

## Sequence — do NOT skip steps

You are reading this skill at the start of every `/combined-review` invocation.
The user's args arrive as `$ARGUMENTS` from the slash command. Follow Phase
A → B → C → D below in order. **Steps within Phase A are sequential. Phases B
and below also run after A completes.**

Let `SKILL_DIR=$HOME/.claude/skills/combined-review` (or the symlink target if
installed via symlink). Reference scripts as `$SKILL_DIR/scripts/<name>`.

### Phase A — sequential setup

Run as a series of sequential `Bash` tool calls. Do NOT batch these into one
parallel message — each step depends on the previous.

A1. **GC stale worktrees** — `$SKILL_DIR/scripts/gc-worktrees.sh "$(git rev-parse --show-toplevel)"`. Ignore non-zero exits; this is best-effort.

A2. **Write `$ARGUMENTS` to a file using the `Write` tool** (NOT a Bash heredoc — `Write` doesn't shell-interpret, which is the whole point). Path: an orchestrator-owned tmp file `ARGS_FILE` you allocate via `Bash` (`mktemp -t combined-review-args-XXXXXX`). Then **parse args** by Bash:
  ```
  $SKILL_DIR/scripts/parse-args.py --args-file "$ARGS_FILE"
  ```
  Capture stdout as `CONFIG_JSON`. This avoids shell-injection from `$ARGUMENTS` containing quotes, spaces, `$`, backticks, etc.

A3. **Write `CONFIG_JSON` to `CONFIG_FILE`** (Write tool again, no shell interpolation) and **resolve scope**:
  ```
  cat "$CONFIG_FILE" | $SKILL_DIR/scripts/resolve-scope.py
  ```
  Capture stdout as `SCOPE_JSON`. If this errors (dirty+PR ambiguity, default branch + clean tree), surface the error to the user and stop.

A4. **Pre-flight — codex availability**: if the user did NOT pass `--no-codex`, run three checks before continuing:
  - `command -v codex` — must succeed. If not, stop: "Codex not on PATH. Pass --no-codex to run Claude-only, or install codex."
  - `codex login status` (or equivalent) — must succeed. If not, stop: "Codex not authenticated. Pass --no-codex or run `codex login`."
  - `codex exec --help` output must contain `--sandbox` — without this, `run-codex.py` would refuse to run in Phase B and Phase C would have only an error status to render. Catching it in Phase A produces a cleaner user experience. If absent, stop: "Installed codex doesn't advertise `--sandbox`. Update codex or pass --no-codex."

  All three pre-flights are skipped if `--no-codex` was passed.

A5. **Pre-flight — gh authentication when --pr**: if `SCOPE_JSON.kind == "pr"`, run `gh auth status`. Error early if not authenticated.

A6. **Materialize scope** — write `SCOPE_JSON` to `SCOPE_FILE` (Write tool) and run:
  ```
  cat "$SCOPE_FILE" | $SKILL_DIR/scripts/materialize-scope.py
  ```
  Capture stdout as `MAT_JSON`. This creates the worktree if needed and populates the materialized review subject.

A7. **Merge `worktree_path` from `MAT_JSON` back into the scope object IMMEDIATELY** (before any abort gate that could cause an early exit). Re-write `SCOPE_FILE` with the merged object. Pseudocode:

  ```
  merged = parse(SCOPE_JSON)
  merged["worktree_path"] = MAT_JSON.worktree_path  # may be null for uncommitted/files
  Write SCOPE_FILE = serialize(merged)
  ```

  **Why before A8/A9 (not after):** if an abort gate stops execution between materialize and merge, Phase D's `cleanup-worktree.sh "$REPO_ROOT" "$WORKTREE_PATH"` has no path to clean up — the worktree leaks. Doing the merge immediately means every early exit from A8/A9 can run Phase D against a merged scope file and clean up the worktree it created.

A8. **Pre-flight — empty scope**: if `MAT_JSON.has_reviewable_changes == false`, run Phase D cleanup (worktree already recorded in `SCOPE_FILE` from A7) and stop: "Nothing to review."

A9. **Pre-flight — large diff**: if `MAT_JSON.total_lines_changed > 2000` (env override `$COMBINED_REVIEW_LARGE_DIFF_THRESHOLD`):
  - If the user did NOT pass `--force-large`, ASK the user in chat: "Diff is N lines — both reviewers degrade on large diffs. Proceed?" Wait for explicit confirmation. If they decline, run Phase D cleanup (worktree recorded) and stop.
  - If non-interactive, run Phase D cleanup and abort with "Diff is N lines; pass --force-large to bypass."

A10. **Allocate the remaining orchestrator-owned file paths** — single `Bash`:
  ```
  PROMPT=$(mktemp -t combined-review-prompt-XXXXXX)
  CODEX_STDOUT=$(mktemp -t combined-review-codex-stdout-XXXXXX)
  CODEX_STDERR=$(mktemp -t combined-review-codex-stderr-XXXXXX)
  CODEX_STATUS=$(mktemp -t combined-review-codex-status-XXXXXX)
  CLAUDE_TRANSCRIPTS=$(mktemp -d -t combined-review-claude-XXXXXX)
  echo "$PROMPT $CODEX_STDOUT $CODEX_STDERR $CODEX_STATUS $CLAUDE_TRANSCRIPTS"
  ```
  Capture all five paths.

A11. **Render the prompt** — three sub-steps to avoid shell-injecting user content:
  1. Write the materialized blob to `MAT_FILE` using the `Write` tool.
  2. If `CONFIG_JSON.focus` is non-null: write its value to `FOCUS_FILE` (allocate via `mktemp -t combined-review-focus-XXXXXX`) using the `Write` tool. **Do NOT interpolate the focus text into a shell command** — it can contain arbitrary user input including `$(...)`, backticks, and `;` that would execute during the Bash call. Always pass via file.
  3. Bash-invoke render-prompt.py:
     ```
     cat "$MAT_FILE" | $SKILL_DIR/scripts/render-prompt.py \
       --mode <mode-literal> \
       [--focus-file "$FOCUS_FILE"] \
       > "$PROMPT"
     ```
     `<mode-literal>` is one of `code|spec|plan|docs` — these are constants from a known set, not user-provided text, so direct argv substitution is safe. Anything user-provided (focus) goes through a file.

### Phase B — parallel review (ONE message, multiple tool calls)

In a single message, issue:

1. **Codex background Bash** (skip if `--no-codex`):
   ```
   $SKILL_DIR/scripts/run-codex.py \
     --scope "$SCOPE_FILE" \
     --prompt-file "$PROMPT" \
     --stdout "$CODEX_STDOUT" \
     --stderr "$CODEX_STDERR" \
     --status "$CODEX_STATUS"
   ```
   with `run_in_background: true`. `SCOPE_FILE` already contains the merged `worktree_path` from Phase A7.

2. **Claude sub-agent calls** — one Agent call per sub-agent:
   - Mode = code, default: dispatch THREE agents: `code-reviewer`, `silent-failure-hunter`, `pr-test-analyzer` (use the pr-review-toolkit's subagent_type names if available; otherwise general-purpose with a focused prompt).
   - Mode = code, `--full`: add `comment-analyzer`, `type-design-analyzer`, `code-simplifier`.
   - Mode = spec/plan/docs: dispatch ONE agent with the rendered prompt + the document-reviewer brief.
   
   Each Agent call's prompt = the contents of `$PROMPT` (read it once before issuing the parallel batch). The agent must emit findings only in the `---FINDING---` block schema.

After issuing, await all results inline (Agent calls return), and use `Monitor` to know when codex's background process completes.

### Phase C — synthesis and report

C0. **Determine codex outcome.** Branch on `--no-codex` FIRST, then on the status file:
  - **If `--no-codex` was passed:** Phase B never launched codex, so `$CODEX_STATUS` is an empty `mktemp` file and reading it would fail. Set `reviewer_summary.codex = {"status": "skipped"}` directly and skip the C2 codex normalization. Do not read `$CODEX_STATUS`.
  - **Otherwise** read the status file: `cat "$CODEX_STATUS"` → JSON with `status` ∈ `ok|failed|timeout`. Branching:
    - `ok`: proceed to normalize codex output in C2.
    - `failed`: skip codex normalization; build `reviewer_summary.codex = {"status": "failed", "error": "<prefer status.error if present and non-empty, else stderr excerpt from $CODEX_STDERR truncated to ~500 chars>", "exit_code": N, "duration_ms": M}`. Continue with Claude-only.
    - `timeout`: as above with `status: "timeout"` and `error: "codex did not finish within N seconds"`.

    **Prefer-status.error rule**: for hard pre-flight failures inside `run-codex.py` (codex disappeared from PATH between Phase A and Phase B, missing `--sandbox` flag), the script writes the diagnostic to both the status JSON and `$CODEX_STDERR`. Status JSON is the more structured/reliable channel — read it first.

C1. **Write each Agent's transcript to a file**: for each sub-agent N, write its returned text to `$CLAUDE_TRANSCRIPTS/<agent-name>.txt`. Concatenate them into `$CLAUDE_TRANSCRIPTS/all.txt` for the audit trail.

C2. **Normalize each reviewer's output** — one call per reviewer (skip codex if `status != ok`):
   ```
   cat $CODEX_STDOUT | $SKILL_DIR/scripts/normalize-findings.py --source codex
   cat $CLAUDE_TRANSCRIPTS/code-reviewer.txt | $SKILL_DIR/scripts/normalize-findings.py --source claude:code-reviewer
   # ... one per agent
   ```
   Each normalize output is JSON with three fields: `findings`, `parse_warnings`, `unparsed_chunks`. **All three must flow downstream — not just findings.**

   In-session, accumulate:
   - **`all_findings`**: concatenate every reviewer's `findings[]` array. This is what the synthesis pass clusters.
   - **`reviewer_summary[source].parse_warnings`**: count of warnings per reviewer (for the cluster JSON's `reviewer_summary.codex.parse_warnings` / `reviewer_summary.claude[N].parse_warnings` fields).
   - **`reviewer_summary[source].raw_findings`**: length of `findings[]` per reviewer.
   - **`all_unparsed_chunks`**: concatenate every reviewer's `unparsed_chunks[]` (each chunk already tagged with `source`). This goes into the cluster JSON's top-level `unparsed_chunks` so `report.py` can render the "## Parse warnings" section.

   **Anti-pattern (caught in static review): dropping `parse_warnings` and `unparsed_chunks` because the synthesis pass only needs `findings`.** If a reviewer ignored the schema and emitted prose, normalize captures that as an unparsed chunk — losing it here would make schema-noncompliance invisible to the final report, defeating the parse-warnings audit path the spec promises.

C3. **Synthesis pass (in-session, no new agent)**: cluster the findings by semantic similarity. Read each finding's title + detail + file:line. Group into clusters where you'd say "these are about the same issue". Tag each cluster `agreement` / `claude_only` / `codex_only` / `disagreement`. The synthesis result is **a JSON object you compose in this conversation** — there is no `$CLUSTERS_JSON` shell variable. Use the `Write` tool to persist it to a file before downstream scripts can read it.

   Allocate `CLUSTERS_FILE` via Bash (`mktemp -t combined-review-clusters-XXXXXX.json`), then **`Write` the synthesized cluster JSON to that path**. All subsequent steps read from `$CLUSTERS_FILE`.

   **Anti-patterns** — STOP and reconsider if you find yourself doing any of:
   - Just concatenating findings without clustering.
   - Using string similarity heuristics instead of judgment.
   - Skipping the synthesis pass because "it's too hard".
   - Summarizing both raw outputs into a prose report instead of clustering.
   - Piping `"$CLUSTERS_JSON"` into a script (no such variable exists — the synthesis result is conversational text you must Write to a file first).

C4. **Validate the cluster JSON** — read from the file Write'd in C3:
   ```
   $SKILL_DIR/scripts/validate-clusters.py < "$CLUSTERS_FILE" 2> "$VALIDATE_STDERR"
   ```
   Allocate `VALIDATE_STDERR` via `mktemp` first (orchestrator-owned, deleted in Phase D). If exit non-zero: re-prompt yourself once with the validator's error message (read from `$VALIDATE_STDERR`), re-emit corrected JSON, `Write` it back to `$CLUSTERS_FILE` (overwriting), and re-validate. If it STILL fails, proceed to C5 with `--synthesis-failed-file "$VALIDATE_STDERR"` (NOT `--synthesis-failed "<msg>"`).

C5. **Render the report** — read cluster JSON from `$CLUSTERS_FILE`, pass codex stderr so failure diagnostics (auth errors, quota exhaustion, sandbox refusals) end up in the audit trail. **Pass the synthesis-failure message via file**, not argv:
   ```
   $SKILL_DIR/scripts/report.py \
     --codex-raw "$CODEX_STDOUT" \
     --codex-stderr "$CODEX_STDERR" \
     --claude-raw "$CLAUDE_TRANSCRIPTS/all.txt" \
     [--synthesis-failed-file "$VALIDATE_STDERR"] \
     < "$CLUSTERS_FILE"
   ```
   When the `--synthesis-failed-file` flag is set, an empty stdin is fine (report.py only reads stdin in the non-failed path). Why file not argv: the validator's stderr can contain backticks, `$(...)`, or quote characters from the model's malformed output — interpolating that into a Bash command line is the same shell-injection class as the focus-text case. Always file. Print the output to chat. If `--save <path>` was passed, also tee to that path. Phase D will delete `$CLUSTERS_FILE` and `$VALIDATE_STDERR` along with the other orchestrator-owned files.

### Phase D — cleanup (ALWAYS, even on errors)

**Order matters**: worktree teardown reads `worktree_path` from `SCOPE_FILE`, so SCOPE_FILE must still exist when cleanup-worktree.sh runs. Do D1 BEFORE D2.

D1. **Worktree cleanup first** — read the merged scope to get `worktree_path` and `repo_root`, then act:
   - If `worktree_path` is non-null AND `--keep-worktree` was NOT passed:
     ```
     $SKILL_DIR/scripts/cleanup-worktree.sh "$REPO_ROOT" "$WORKTREE_PATH"
     ```
   - If `worktree_path` is non-null AND `--keep-worktree` WAS passed: `touch "$WORKTREE_PATH/.combined-review-keep"` (marker — gc-worktrees.sh will skip it on later runs) and announce the path to the user.
   - If `worktree_path` is null (uncommitted/files scopes): nothing to do here.

   Capture `REPO_ROOT` and `WORKTREE_PATH` into shell variables BEFORE invoking cleanup, in case D2 ordering changes in the future.

D2. **Delete orchestrator-owned files** — only after D1 has read SCOPE_FILE:
   ```
   rm -f "$ARGS_FILE" "$CONFIG_FILE" "$SCOPE_FILE" "$MAT_FILE" "$FOCUS_FILE" \
         "$PROMPT" "$CODEX_STDOUT" "$CODEX_STDERR" "$CODEX_STATUS" \
         "$CLUSTERS_FILE" "$VALIDATE_STDERR"
   rm -rf "$CLAUDE_TRANSCRIPTS"
   ```
   Some variables may be unset if the run didn't get that far — `rm -f` silently ignores those.

D3. Confirm to user: "Combined review complete." Done.

## Failure handling

- Any non-zero exit from a Phase A script: surface error to user, run Phase D cleanup, stop.
- Codex non-zero or timeout (>5min, env `COMBINED_REVIEW_CODEX_TIMEOUT`): report Claude-only, note "codex failed" in the report.
- One Claude sub-agent fails: continue with the others; failed agent shows up in `reviewer_summary` with status=failed.

## Anti-patterns

If you find yourself doing any of these, STOP:

- Running reviewers sequentially instead of in parallel (Phase B is the whole point).
- Skipping the materialize step and feeding raw git state to reviewers.
- Skipping Phase D cleanup "because the report is what matters".
- Concatenating raw outputs into a single section without clustering.
- Inventing your own scope-detection logic instead of using resolve-scope.py.
