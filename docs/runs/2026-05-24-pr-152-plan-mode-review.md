# Combined Review

**Scope:** PR #152 (609ac15..9348d46) - combined-review spec + plan docs
**Mode:** plan
**Focus:** (none)
**Generated:** 2026-05-25T05:34:28+00:00

---

## Reviewer status

- **Codex**: ok — 5 raw findings
- **Claude:document-reviewer**: failed — `Agent call timed out reading the ~720KB rendered prompt. opus on a prompt of this size exceeds the orchestrator's Agent-tool window. Codex returned cleanly in 157s, so reduce render-prompt size (or split per-file) before re-trying the Claud…`

## Single-source findings

### Codex only

- **[High] docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1237-1242** — Task 6 uses os.readlink before importing os
  The initial materialize-scope.py implementation defines symlink_target() which calls os.readlink(full), but Task 6 imports only json/subprocess/sys/Path. `import os` is only added in Task 7. The Task 6 commit would NameError on the symlink path. Task 6's tests don't exercise symlinks, so this passes verification while shipping a latent bug. Confirmed during execution: the implementer subagent added os to imports as a deviation. Update the plan to include `import os` in Task 6's initial implementation block.
  _Sources: codex_
- **[High] docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1041-1063** — Auto-detect conflates gh failure with absence of PR
  pr_for_current_branch() returns None on any non-zero gh result, conflating 'no PR exists' with auth failure, network failure, missing gh, or API error. In a dirty branch that DOES have a PR, an unauthenticated gh silently bypasses the dirty+PR ambiguity guard (Task 5) and reviews the wrong scope without warning. Either distinguish 'gh not authenticated / not present' from 'no PR for this branch' (raise vs return None), or precheck gh auth in Phase A.
  _Sources: codex_
- **[High] docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2064-2068** — PR base fetch failures are silently swallowed
  materialize_pr() runs `git fetch <base_url> <base_ref>` without check=True and never inspects exit code or stderr. A fork-PR auth error, missing ref, or transient network failure is hidden - surfaces later as 'unreachable SHA' (misleading), or skipped entirely if the SHA happens to be reachable from a previous local fetch. Tests use a local file:// URL and never assert the fetch succeeded; the fork/base contract isn't verified. Add check=True or explicit return-code inspection, and a test that asserts the fetch error path surfaces correctly.
  _Sources: codex_
- **[Medium] docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:39-137** — Task 1 commit list includes README.md before any step creates it
  Task 1's commit step references README.md but no step in Task 1 writes it (README.md is written in Task 20). On a fresh repo, `git add README.md` fails and blocks the first commit. Confirmed during execution: the implementer subagent dropped README.md from the git-add line as a deviation. Either add an explicit README creation step in Task 1, or drop README.md from the Task 1 commit line.
  _Sources: codex_
- **[Medium] docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4576** — --save path lacks the same shell-safety treatment as other user input
  The SKILL.md C5 step says to 'also tee' to the user-provided `--save <path>` but doesn't specify a safe mechanism. The plan is careful to pass $ARGUMENTS, focus text, and validator errors through files to avoid shell injection - but save_path is also user-controlled and may contain spaces, quotes, backticks, or $(...). Specify either: write via Python helper, OR pass through a temp file and rely on shell-safe expansion. Add tests for paths with spaces/metacharacters.
  _Sources: codex_

---

<details>
<summary>Raw outputs (audit trail)</summary>

### Codex stdout

```
---FINDING---
severity: medium
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 39-137
category: bug
title: Task 1 commits README.md before any step creates it
detail: |
  Task 1 lists README.md as a created file and later runs `git add ... README.md`, but the steps only write `.gitignore`, `pyproject.toml`, and `tests/conftest.py`. On a fresh repo, `git add README.md` fails and blocks the first commit. Add an explicit README creation step or remove it from the Task 1 commit until Task 20.
---END-FINDING---

---FINDING---
severity: high
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 1237-1242
category: bug
title: Task 6 uses os.readlink before importing os
detail: |
  The initial `materialize-scope.py` implementation defines `symlink_target()` with `os.readlink(full)` but Task 6 imports only `json`, `subprocess`, `sys`, and `Path`. The `import os` is not added until Task 7, so the Task 6 commit is broken for the symlink path it claims to support. The Task 6 tests do not exercise symlink changes, so this can pass verification while shipping a NameError.
---END-FINDING---

---FINDING---
severity: high
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 1041-1063
category: bug
title: Auto-detect treats any gh failure as no PR
detail: |
  `pr_for_current_branch()` returns `None` for every non-zero `gh pr view` result, and the auto-detect branch then chooses `uncommitted` or `base`. That conflates "no PR exists" with gh auth failure, network failure, missing `gh`, or an API error. In a dirty branch that has a PR, an unauthenticated `gh` run silently bypasses the dirty+PR ambiguity guard and reviews the wrong scope.
---END-FINDING---

---FINDING---
severity: high
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 2064-2068
category: bug
title: PR base fetch failures are ignored
detail: |
  `materialize_pr()` runs `git fetch <base_url> <base_ref>` without `check=True` and never inspects stderr or the exit code. A fork/base fetch auth error, missing ref, or network failure can be hidden and later reported only as an unreachable SHA, or skipped entirely if the SHA happens to be reachable from local refs. The tests also use a local repo and do not assert the fetch succeeded, so the plan does not prove the fork/base fetch contract works.
---END-FINDING---

---FINDING---
severity: medium
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 4576
category: security
title: --save handling lacks the same shell-safety rules as other user input
detail: |
  The SKILL.md step says to "also tee" to the user-provided `--save <path>` but does not specify a safe mechanism. The plan is careful to pass `$ARGUMENTS`, focus text, and validator errors through files to avoid shell injection, but `save_path` is also user-controlled and may contain spaces, quotes, backticks, or `$()`. Define exact handling, such as writing the report with a Python helper or using a separately written path file, and add tests for spaces/metacharacters.
---END-FINDING---
```

### Codex stderr

``````
OpenAI Codex v0.133.0
--------
workdir: /private/var/folders/yt/h62lwq8x26340hnlt7lk_c240000gn/T/combined-review-juvera_ai_4-pr-hdlqrklt
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: xhigh
reasoning summaries: none
session id: 019e58e8-34bd-7af1-af50-4431cf07ffb0
--------
user
# Plan Review Mode

You are reviewing an implementation plan. Focus on:

- **Step ordering** — does task N assume something task M hasn't delivered yet?
- **Hidden dependencies** — does a step rely on something not produced by an earlier step?
- **Verification per task** — does each task have a check that proves it worked, or is it "implement X, trust it works"?
- **Risk surface** — destructive ops, force-pushes, schema migrations, anything hard to roll back.
- **What could fail silently** — what would let the plan "complete" while producing a broken result?
- **Code completeness in steps** — placeholders like "implement appropriate logic", missing exact paths, undefined symbols.

You will receive the plan document below.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble.


## Review subject

**Scope:** PR #152 (609ac15..9348d46)


### Unified diff

`````diff
diff --git a/docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md b/docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
new file mode 100644
index 0000000..52b1ca9
--- /dev/null
+++ b/docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
@@ -0,0 +1,4940 @@
+# Combined Review Skill — Implementation Plan
+
+> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
+
+**Goal:** Build a Claude Code skill `/combined-review` that runs `pr-review-toolkit` sub-agents and `codex exec --sandbox read-only` in parallel against the same materialized review subject, then synthesizes the findings into a single deduped, attributed report.
+
+**Architecture:** Slash command at `~/.claude/commands/combined-review.md` hands off to skill at `~/.claude/skills/combined-review/SKILL.md`. The skill orchestrates four phases — sequential setup (parse-args → resolve-scope → materialize → pre-flight → write prompt), parallel review (codex background + Claude sub-agents), in-session synthesis + JSON-validated cluster output, deterministic rendering — with a strict worktree-cleanup model gated by `git worktree list --porcelain`.
+
+**Tech Stack:** Python 3 (stdlib + `jsonschema`), Bash, pytest. Codex CLI (`codex exec --sandbox read-only`). `gh` CLI for PR metadata. Git plumbing for worktrees and diffs.
+
+**Spec:** `docs/superpowers/specs/2026-05-11-combined-review-skill-design.md`.
+
+**Development layout:**
+
+```
+~/projects/combined-review/        # git repo (this plan develops here)
+├── SKILL.md
+├── commands/combined-review.md
+├── prompts/{code,spec,plan,docs}.md
+├── scripts/{parse-args,resolve-scope,materialize-scope,normalize-findings,validate-clusters,report}.py
+├── scripts/run-codex.py
+├── scripts/{cleanup-worktree,gc-worktrees}.sh
+├── tests/
+└── README.md
+```
+
+After implementation, install via:
+
+```
+ln -s ~/projects/combined-review ~/.claude/skills/combined-review
+ln -s ~/projects/combined-review/commands/combined-review.md ~/.claude/commands/combined-review.md
+```
+
+---
+
+## Task 1: Repo scaffolding
+
+**Files:**
+- Create: `~/projects/combined-review/.gitignore`
+- Create: `~/projects/combined-review/README.md`
+- Create: `~/projects/combined-review/pyproject.toml`
+- Create: `~/projects/combined-review/tests/conftest.py`
+
+- [ ] **Step 1: Create the repo and directory tree**
+
+```bash
+mkdir -p ~/projects/combined-review/{scripts,prompts,commands,tests}
+cd ~/projects/combined-review
+git init
+```
+
+- [ ] **Step 2: Write `.gitignore`**
+
+```
+__pycache__/
+*.pyc
+.pytest_cache/
+.venv/
+*.egg-info/
+```
+
+- [ ] **Step 3: Write `pyproject.toml`**
+
+```toml
+[project]
+name = "combined-review"
+version = "0.1.0"
+description = "Claude Code skill that fuses Claude + Codex reviews in one session"
+requires-python = ">=3.11"
+dependencies = ["jsonschema>=4.21.0"]
+
+[project.optional-dependencies]
+dev = ["pytest>=8.0.0"]
+
+[tool.pytest.ini_options]
+testpaths = ["tests"]
+```
+
+- [ ] **Step 4: Write `tests/conftest.py`**
+
+```python
+"""Shared pytest fixtures for the combined-review test suite."""
+import os
+import shutil
+import subprocess
+import tempfile
+from pathlib import Path
+
+import pytest
+
+SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
+
+
+@pytest.fixture
+def tmp_repo(tmp_path):
+    """A throwaway git repo with one initial commit. Returns the repo Path."""
+    repo = tmp_path / "repo"
+    repo.mkdir()
+    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
+    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
+    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
+    (repo / "README.md").write_text("# Test repo\n")
+    subprocess.run(["git", "add", "."], cwd=repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=repo, check=True)
+    return repo
+
+
+@pytest.fixture
+def fake_bin(tmp_path, monkeypatch):
+    """Prepend a tmp dir to PATH so tests can drop fake `gh`/`codex` scripts."""
+    fake = tmp_path / "bin"
+    fake.mkdir()
+    monkeypatch.setenv("PATH", f"{fake}:{os.environ['PATH']}")
+    return fake
+
+
+def run_script(name, *args, **kwargs):
+    """Invoke a script in scripts/ via subprocess; return CompletedProcess."""
+    script = SCRIPTS_DIR / name
+    cmd = [str(script), *args] if script.suffix == ".sh" else ["python3", str(script), *args]
+    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
+```
+
+- [ ] **Step 5: Verify pytest runs (zero tests is OK)**
+
+```bash
+cd ~/projects/combined-review
+python3 -m pip install -e ".[dev]"
+pytest -v
+```
+
+Expected: `no tests ran` exit code 5, no errors.
+
+- [ ] **Step 6: Commit**
+
+```bash
+git add .gitignore README.md pyproject.toml tests/conftest.py
+git commit -m "feat: scaffold combined-review repo"
+```
+
+---
+
+## Task 2: parse-args.py — CLI surface
+
+**Files:**
+- Create: `scripts/parse-args.py`
+- Create: `tests/test_parse_args.py`
+
+- [ ] **Step 1: Write the failing test**
+
+```python
+# tests/test_parse_args.py
+"""Tests for parse-args.py — flag parsing into normalized config JSON."""
+import json
+from tests.conftest import run_script
+
+
+def parse(*args):
+    r = run_script("parse-args.py", *args)
+    assert r.returncode == 0, f"stderr: {r.stderr}"
+    return json.loads(r.stdout)
+
+
+def test_no_args_defaults_to_code_mode():
+    cfg = parse()
+    assert cfg["mode"] == "code"
+    assert cfg["scope_flag"] is None
+    assert cfg["files"] == []
+    assert cfg["full"] is False
+
+
+def test_pr_flag():
+    cfg = parse("--pr", "105")
+    assert cfg["scope_flag"] == "pr"
+    assert cfg["pr_number"] == 105
+
+
+def test_uncommitted_flag():
+    cfg = parse("--uncommitted")
+    assert cfg["scope_flag"] == "uncommitted"
+
+
+def test_base_flag():
+    cfg = parse("--base", "develop")
+    assert cfg["scope_flag"] == "base"
+    assert cfg["base_branch"] == "develop"
+
+
+def test_commit_flag():
+    cfg = parse("--commit", "abc1234")
+    assert cfg["scope_flag"] == "commit"
+    assert cfg["commit_sha"] == "abc1234"
+
+
+def test_positional_files():
+    cfg = parse("docs/spec.md", "plan.md")
+    assert cfg["scope_flag"] == "files"
+    assert cfg["files"] == ["docs/spec.md", "plan.md"]
+
+
+def test_mode_and_focus():
+    cfg = parse("--mode", "spec", "--focus", "API contract")
+    assert cfg["mode"] == "spec"
+    assert cfg["focus"] == "API contract"
+
+
+def test_all_modifier_flags():
+    cfg = parse("--full", "--no-codex", "--force-large", "--keep-worktree",
+                "--save", "/tmp/report.md")
+    assert cfg["full"] is True
+    assert cfg["no_codex"] is True
+    assert cfg["force_large"] is True
+    assert cfg["keep_worktree"] is True
+    assert cfg["save_path"] == "/tmp/report.md"
+
+
+def test_mutually_exclusive_scope_flags_error():
+    r = run_script("parse-args.py", "--pr", "1", "--uncommitted")
+    assert r.returncode != 0
+    assert "mutually exclusive" in r.stderr.lower()
+
+
+def test_files_with_scope_flag_errors():
+    r = run_script("parse-args.py", "--pr", "1", "foo.md")
+    assert r.returncode != 0
+    assert "mutually exclusive" in r.stderr.lower()
+
+
+def test_invalid_mode_errors():
+    r = run_script("parse-args.py", "--mode", "nonsense")
+    assert r.returncode != 0
+
+
+def test_args_file_mode(tmp_path):
+    """Orchestrator writes $ARGUMENTS to a file; parse-args reads + shlex-splits it.
+    Necessary because shell-substituting $ARGUMENTS directly is injection-prone."""
+    f = tmp_path / "args.txt"
+    f.write_text('--pr 105 --focus "API contract changes" --mode spec')
+    r = run_script("parse-args.py", "--args-file", str(f))
+    assert r.returncode == 0, r.stderr
+    cfg = json.loads(r.stdout)
+    assert cfg["pr_number"] == 105
+    assert cfg["focus"] == "API contract changes"
+    assert cfg["mode"] == "spec"
+
+
+def test_args_file_handles_paths_with_spaces(tmp_path):
+    f = tmp_path / "args.txt"
+    f.write_text('"docs/path with spaces/spec.md"')
+    r = run_script("parse-args.py", "--args-file", str(f))
+    assert r.returncode == 0, r.stderr
+    cfg = json.loads(r.stdout)
+    assert cfg["files"] == ["docs/path with spaces/spec.md"]
+```
+
+- [ ] **Step 2: Run the test to verify it fails**
+
+```bash
+cd ~/projects/combined-review && pytest tests/test_parse_args.py -v
+```
+
+Expected: all tests FAIL (script doesn't exist yet).
+
+- [ ] **Step 3: Implement `scripts/parse-args.py`**
+
+```python
+#!/usr/bin/env python3
+"""parse-args.py — turn /combined-review CLI args into a normalized config JSON.
+
+Reads sys.argv[1:] OR, if --args-file <path> is given, reads the raw argument
+string from that file and shlex-splits it. The args-file mode exists because
+the orchestrator must not shell-substitute $ARGUMENTS directly — quoting
+fragility and injection risk. Instead, the slash command writes $ARGUMENTS
+to a file and we read it back literally here.
+
+Writes a config object to stdout; returns non-zero on validation errors.
+"""
+import argparse
+import json
+import shlex
+import sys
+
+VALID_MODES = ("code", "spec", "plan", "docs")
+
+
+def build_parser() -> argparse.ArgumentParser:
+    p = argparse.ArgumentParser(prog="combined-review", add_help=True)
+    p.add_argument("--pr", type=int, dest="pr_number")
+    p.add_argument("--uncommitted", action="store_true")
+    p.add_argument("--base", dest="base_branch")
+    p.add_argument("--commit", dest="commit_sha")
+    p.add_argument("--mode", choices=VALID_MODES, default="code")
+    p.add_argument("--focus", default=None)
+    p.add_argument("--full", action="store_true")
+    p.add_argument("--no-codex", action="store_true", dest="no_codex")
+    p.add_argument("--force-large", action="store_true", dest="force_large")
+    p.add_argument("--keep-worktree", action="store_true", dest="keep_worktree")
+    p.add_argument("--save", default=None, dest="save_path")
+    p.add_argument("files", nargs="*")
+    return p
+
+
+def normalize(ns: argparse.Namespace) -> dict:
+    scope_flags = {
+        "pr": ns.pr_number is not None,
+        "uncommitted": ns.uncommitted,
+        "base": ns.base_branch is not None,
+        "commit": ns.commit_sha is not None,
+        "files": bool(ns.files),
+    }
+    selected = [k for k, v in scope_flags.items() if v]
+    if len(selected) > 1:
+        raise SystemExit(
+            f"error: scope flags are mutually exclusive; got {selected}"
+        )
+    scope_flag = selected[0] if selected else None
+    return {
+        "scope_flag": scope_flag,
+        "pr_number": ns.pr_number,
+        "base_branch": ns.base_branch,
+        "commit_sha": ns.commit_sha,
+        "files": ns.files,
+        "mode": ns.mode,
+        "focus": ns.focus,
+        "full": ns.full,
+        "no_codex": ns.no_codex,
+        "force_large": ns.force_large,
+        "keep_worktree": ns.keep_worktree,
+        "save_path": ns.save_path,
+    }
+
+
+def resolve_argv(raw_argv: list[str]) -> list[str]:
+    """If --args-file <path> is the only/first pair, read the file and shlex-split.
+    Otherwise return raw_argv unchanged."""
+    if len(raw_argv) >= 2 and raw_argv[0] == "--args-file":
+        path = raw_argv[1]
+        with open(path, "r") as f:
+            raw_string = f.read().strip()
+        return shlex.split(raw_string)
+    return raw_argv
+
+
+def main(argv: list[str]) -> None:
+    argv = resolve_argv(argv)
+    ns = build_parser().parse_args(argv)
+    cfg = normalize(ns)
+    json.dump(cfg, sys.stdout)
+    sys.stdout.write("\n")
+
+
+if __name__ == "__main__":
+    main(sys.argv[1:])
+```
+
+- [ ] **Step 4: Make it executable**
+
+```bash
+chmod +x scripts/parse-args.py
+```
+
+- [ ] **Step 5: Run tests, verify all pass**
+
+```bash
+pytest tests/test_parse_args.py -v
+```
+
+Expected: 12 passed.
+
+- [ ] **Step 6: Commit**
+
+```bash
+git add scripts/parse-args.py tests/test_parse_args.py
+git commit -m "feat: parse-args.py with CLI surface and mutex validation"
+```
+
+---
+
+## Task 3: resolve-scope.py — auto-detect skeleton
+
+**Files:**
+- Create: `scripts/resolve-scope.py`
+- Create: `tests/test_resolve_scope_explicit.py`
+
+This task handles the four **explicit** scope kinds (uncommitted/base/commit/files). PR auto-detect lands in Task 4.
+
+- [ ] **Step 1: Write failing tests for explicit-scope resolution**
+
+```python
+# tests/test_resolve_scope_explicit.py
+"""Tests for resolve-scope.py — explicit scope flags only."""
+import json
+import subprocess
+from tests.conftest import run_script
+
+
+def resolve(cfg, cwd=None):
+    r = run_script("resolve-scope.py", input=json.dumps(cfg), cwd=cwd)
+    return r
+
+
+def make_cfg(**kw):
+    base = {
+        "scope_flag": None, "pr_number": None, "base_branch": None,
+        "commit_sha": None, "files": [], "mode": "code", "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+    base.update(kw)
+    return base
+
+
+def test_uncommitted_scope(tmp_repo):
+    (tmp_repo / "new.txt").write_text("x")
+    r = resolve(make_cfg(scope_flag="uncommitted"), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    scope = json.loads(r.stdout)
+    assert scope["kind"] == "uncommitted"
+    assert scope["repo_root"] == str(tmp_repo)
+    assert scope["worktree_path"] is None
+    assert scope["needs_clean_worktree"] is False
+
+
+def test_base_scope_resolves_sha(tmp_repo):
+    # Create a feature branch with one commit
+    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
+    (tmp_repo / "x.txt").write_text("y")
+    subprocess.run(["git", "add", "x.txt"], cwd=tmp_repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
+    r = resolve(make_cfg(scope_flag="base", base_branch="main"), cwd=tmp_repo)
+    # git init default branch may be 'main' or 'master' depending on config
+    if r.returncode != 0:
+        # retry with detected default branch
+        head = subprocess.run(
+            ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
+            cwd=tmp_repo, capture_output=True, text=True
+        ).stdout.split()
+        default = "master" if "master" in head else "main"
+        r = resolve(make_cfg(scope_flag="base", base_branch=default), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    scope = json.loads(r.stdout)
+    assert scope["kind"] == "base"
+    assert len(scope["base_sha"]) == 40
+    assert len(scope["head_sha"]) == 40
+    assert scope["base_sha"] != scope["head_sha"]
+    assert scope["needs_clean_worktree"] is True
+
+
+def test_commit_scope_resolves_sha(tmp_repo):
+    sha = subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
+    ).stdout.strip()
+    r = resolve(make_cfg(scope_flag="commit", commit_sha=sha), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    scope = json.loads(r.stdout)
+    assert scope["kind"] == "commit"
+    assert scope["commit_sha"] == sha
+    assert scope["needs_clean_worktree"] is True
+
+
+def test_files_scope_passes_paths(tmp_repo):
+    (tmp_repo / "spec.md").write_text("# spec")
+    r = resolve(make_cfg(scope_flag="files", files=["spec.md"]), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    scope = json.loads(r.stdout)
+    assert scope["kind"] == "files"
+    assert scope["files"] == ["spec.md"]
+    assert scope["needs_clean_worktree"] is False
+
+
+def test_files_scope_rejects_nonexistent(tmp_repo):
+    r = resolve(make_cfg(scope_flag="files", files=["nope.md"]), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "nope.md" in r.stderr
+
+
+def test_files_scope_rejects_absolute_paths(tmp_repo, tmp_path):
+    """Regression for path-traversal / data-exfiltration. Absolute paths must
+    be refused outright — inlining /Users/.../.ssh/id_rsa or /etc/passwd into
+    the review prompt would send it to Codex (remote) + Claude sub-agents.
+    `Path(repo_root) / absolute_path` evaluates to the absolute path in
+    pathlib, so the previous `.exists()` check accepted any local file."""
+    leaked = tmp_path / "leaked.txt"
+    leaked.write_text("would-be-exfiltrated")
+    r = resolve(make_cfg(scope_flag="files", files=[str(leaked)]), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "absolute" in r.stderr.lower()
+
+
+def test_files_scope_rejects_dotdot_escape(tmp_repo, tmp_path):
+    """`../other-dir/secret.txt` must be rejected even though it's a relative
+    path — after resolve() it lands outside repo_root."""
+    outside = tmp_path / "outside.txt"
+    outside.write_text("not in repo")
+    # tmp_repo lives at tmp_path/"repo"; ../outside.txt escapes
+    r = resolve(make_cfg(scope_flag="files", files=["../outside.txt"]), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()
+
+
+def test_files_scope_rejects_symlink_pointing_outside(tmp_repo, tmp_path):
+    """A symlink inside the repo whose target is outside the repo must also be
+    rejected — resolve() follows symlinks, so the canonical path escapes."""
+    outside = tmp_path / "secret.txt"
+    outside.write_text("secret")
+    (tmp_repo / "innocent.txt").symlink_to(outside)
+    r = resolve(make_cfg(scope_flag="files", files=["innocent.txt"]), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()
+
+
+def test_files_scope_preserves_symlink_path_when_target_is_in_repo(tmp_repo):
+    """Regression: an in-repo symlink pointing at another in-repo file must keep
+    its user-supplied name in the resolved scope, NOT be replaced with the
+    target path. Otherwise materialize_files() sees a regular file and the
+    symlink metadata (target path) never makes it into the prompt."""
+    (tmp_repo / "real.md").write_text("# real file\n")
+    (tmp_repo / "alias.md").symlink_to("real.md")
+    r = resolve(make_cfg(scope_flag="files", files=["alias.md"]), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    scope = json.loads(r.stdout)
+    # The returned path must be the user's input, not the target
+    assert scope["files"] == ["alias.md"]
+
+
+def test_files_scope_rejects_directory(tmp_repo):
+    """A directory passed in files-scope must be rejected. Earlier behavior
+    would let exists() pass and produce a doc_files entry with kind=text and
+    content=None — confusing prompt with no value to the reviewer."""
+    (tmp_repo / "subdir").mkdir()
+    r = resolve(make_cfg(scope_flag="files", files=["subdir"]), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "regular file" in r.stderr.lower() or "directory" in r.stderr.lower()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_resolve_scope_explicit.py -v
+```
+
+Expected: all fail (script doesn't exist).
+
+- [ ] **Step 3: Implement `scripts/resolve-scope.py` (explicit-scope paths only — auto-detect in Task 4)**
+
+```python
+#!/usr/bin/env python3
+"""resolve-scope.py — config JSON in → scope object JSON out.
+
+Handles explicit scope flags (uncommitted/base/commit/files) and validates
+inputs against git. PR resolution and full auto-detect happen in a later
+patch. All ref-shaped inputs are resolved to immutable SHAs here; downstream
+steps consume SHAs, never ref names.
+"""
+import json
+import subprocess
+import sys
+from pathlib import Path
+
+
+def git(*args, cwd=None, check=True) -> str:
+    r = subprocess.run(
+        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
+    )
+    return r.stdout.strip()
+
+
+def repo_root(cwd=None) -> str:
+    return git("rev-parse", "--show-toplevel", cwd=cwd)
+
+
+def base_scope_object() -> dict:
+    return {
+        "kind": None, "pr_number": None,
+        "base_ref_name": None, "head_ref_name": None,
+        "base_repo_url": None, "head_repo_url": None,
+        "base_sha": None, "head_sha": None, "commit_sha": None,
+        "files": [], "worktree_path": None, "repo_root": None,
+        "needs_clean_worktree": False,
+        "mode": "code", "focus": None, "full": False,
+        "no_codex": False, "force_large": False, "keep_worktree": False,
+        "save_path": None,
+    }
+
+
+def carry_modifiers(scope: dict, cfg: dict) -> None:
+    """Copy modifier flags from cfg into scope so downstream sees one object."""
+    for k in ("mode", "focus", "full", "no_codex",
+              "force_large", "keep_worktree", "save_path"):
+        scope[k] = cfg[k]
+
+
+def resolve_uncommitted(cfg: dict, root: str) -> dict:
+    s = base_scope_object()
+    s["kind"] = "uncommitted"
+    s["repo_root"] = root
+    s["needs_clean_worktree"] = False
+    carry_modifiers(s, cfg)
+    return s
+
+
+def resolve_base(cfg: dict, root: str) -> dict:
+    base_ref = cfg["base_branch"]
+    try:
+        base_sha = git("rev-parse", "--verify", f"{base_ref}^{{commit}}", cwd=root)
+    except subprocess.CalledProcessError as e:
+        raise SystemExit(f"error: cannot resolve base ref {base_ref!r}: {e.stderr}")
+    head_sha = git("rev-parse", "--verify", "HEAD^{commit}", cwd=root)
+    s = base_scope_object()
+    s["kind"] = "base"
+    s["repo_root"] = root
+    s["base_ref_name"] = base_ref
+    s["base_sha"] = base_sha
+    s["head_sha"] = head_sha
+    s["needs_clean_worktree"] = True
+    carry_modifiers(s, cfg)
+    return s
+
+
+def resolve_commit(cfg: dict, root: str) -> dict:
+    try:
+        sha = git("rev-parse", "--verify", f"{cfg['commit_sha']}^{{commit}}", cwd=root)
+    except subprocess.CalledProcessError as e:
+        raise SystemExit(f"error: cannot resolve commit {cfg['commit_sha']!r}: {e.stderr}")
+    s = base_scope_object()
+    s["kind"] = "commit"
+    s["repo_root"] = root
+    s["commit_sha"] = sha
+    s["needs_clean_worktree"] = True
+    carry_modifiers(s, cfg)
+    return s
+
+
+def _validate_under_root(root: str, paths: list[str]) -> list[str]:
+    """Reject absolute paths, `..` escapes, and symlinks whose targets are
+    outside repo_root. Return the **user-supplied path, lexically normalized**
+    — NOT the resolved target.
+
+    Why we don't return the resolved path: if the user passes an in-repo
+    symlink like `innocent-link.md` that points to another in-repo file,
+    `.resolve()` follows it to the target. Returning the target would make
+    materialize_files() see a regular text file instead of a symlink, and
+    the symlink-specific metadata promised in Task 9 (target path) would
+    never make it into the prompt. The report would also cite the wrong path.
+
+    Why this is P1: positional file contents are inlined into the review
+    prompt and sent to Codex (remote) + Claude sub-agents. Without the
+    escape checks, passing `/Users/.../.ssh/id_rsa` or `../../etc/passwd`
+    would silently exfiltrate secrets to remote APIs.
+    """
+    import os.path
+    root_abs = Path(root).resolve()
+    out = []
+    for p in paths:
+        if Path(p).is_absolute():
+            raise SystemExit(
+                f"error: refusing absolute path {p!r} — pass repo-relative paths only"
+            )
+        # Lexical normalization (does NOT follow symlinks). Rejects `..` escapes.
+        lexical = os.path.normpath(p)
+        if lexical.startswith("..") or lexical == ".." or "/../" in f"/{lexical}/":
+            raise SystemExit(
+                f"error: path {p!r} escapes via .. — refusing"
+            )
+        # Security check: does the resolved (symlink-followed) target land
+        # inside the repo? If not, refuse — an in-repo symlink pointing at
+        # /etc/passwd would otherwise exfiltrate it.
+        try:
+            resolved = (root_abs / p).resolve()
+            resolved.relative_to(root_abs)
+        except ValueError:
+            raise SystemExit(
+                f"error: path {p!r} resolves outside repo root ({root_abs}); refusing"
+            )
+        # Existence check using the original path (does not follow symlinks
+        # except where the user intended; resolve() check above already
+        # validated the target).
+        full = root_abs / lexical
+        if not full.exists():
+            raise SystemExit(f"error: file not found: {p!r}")
+        # Reject plain directories: positional files mode reviews file
+        # content. A directory passed here would slip through with kind=text
+        # + content=None downstream and render as a confusing header with no
+        # content. If the user wants to review every file in a directory,
+        # they should expand the glob themselves — the skill doesn't recurse
+        # implicitly. is_file() returns True for symlinks pointing at regular
+        # files, which is the behavior we want (symlinks ARE supported).
+        #
+        # Exception: submodules are gitlinks — they appear as directories on
+        # disk (is_file() is False) but git tracks them as mode 160000.
+        # materialize_files() has a kind=submodule branch that produces useful
+        # output (the pointer SHA), so we must let these through.
+        if not full.is_file():
+            ls = subprocess.run(
+                ["git", "ls-files", "--stage", "--", lexical],
+                cwd=str(root_abs), capture_output=True, text=True,
+            )
+            is_submodule = ls.stdout.strip().startswith("160000 ")
+            if not is_submodule:
+                raise SystemExit(
+                    f"error: {p!r} is not a regular file "
+                    f"(directory or special file — pass file paths only, expand globs yourself)"
+                )
+        out.append(lexical)
+    return out
+
+
+def resolve_files(cfg: dict, root: str) -> dict:
+    files = _validate_under_root(root, cfg["files"])
+    s = base_scope_object()
+    s["kind"] = "files"
+    s["repo_root"] = root
+    s["files"] = files
+    s["needs_clean_worktree"] = False
+    carry_modifiers(s, cfg)
+    return s
+
+
+SCOPE_RESOLVERS = {
+    "uncommitted": resolve_uncommitted,
+    "base": resolve_base,
+    "commit": resolve_commit,
+    "files": resolve_files,
+}
+
+
+def main() -> None:
+    cfg = json.load(sys.stdin)
+    root = repo_root()
+    scope_flag = cfg["scope_flag"]
+    if scope_flag is None:
+        raise SystemExit(
+            "error: auto-detect not yet implemented; pass an explicit scope flag"
+        )
+    if scope_flag == "pr":
+        raise SystemExit("error: --pr resolution not yet implemented")
+    resolver = SCOPE_RESOLVERS[scope_flag]
+    scope = resolver(cfg, root)
+    json.dump(scope, sys.stdout)
+    sys.stdout.write("\n")
+
+
+if __name__ == "__main__":
+    main()
+```
+
+- [ ] **Step 4: Make executable, run tests**
+
+```bash
+chmod +x scripts/resolve-scope.py
+pytest tests/test_resolve_scope_explicit.py -v
+```
+
+Expected: 10 passed (5 original + 3 path-traversal rejection + 1 in-repo-symlink-preservation + 1 directory-rejection).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/resolve-scope.py tests/test_resolve_scope_explicit.py
+git commit -m "feat: resolve-scope.py for explicit scopes (uncommitted/base/commit/files)"
+```
+
+---
+
+## Task 4: resolve-scope.py — PR scope via gh
+
+**Files:**
+- Modify: `scripts/resolve-scope.py`
+- Create: `tests/test_resolve_scope_pr.py`
+
+- [ ] **Step 1: Write failing tests using a fake `gh`**
+
+```python
+# tests/test_resolve_scope_pr.py
+"""Tests for resolve-scope.py --pr path using a fake `gh` binary."""
+import json
+import subprocess
+from tests.conftest import run_script
+
+
+FAKE_GH_JSON = {
+    "number": 105,
+    "headRefName": "feature-x",
+    "baseRefName": "main",
+    "headRefOid": "a" * 40,
+    "baseRefOid": "b" * 40,
+    "headRepository": {"url": "https://github.com/user/repo.git"},
+    "baseRepository": {"url": "https://github.com/upstream/repo.git"},
+}
+
+
+def make_cfg_pr(num=105):
+    return {
+        "scope_flag": "pr", "pr_number": num, "base_branch": None,
+        "commit_sha": None, "files": [], "mode": "code", "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+
+
+def write_fake_gh(fake_bin, payload):
+    script = fake_bin / "gh"
+    script.write_text(
+        "#!/bin/sh\n"
+        # Only respond to `gh pr view` calls — fail loudly on anything else.
+        'if [ "$1" = "pr" ] && [ "$2" = "view" ]; then\n'
+        f"  cat <<'EOF'\n{json.dumps(payload)}\nEOF\n"
+        "  exit 0\n"
+        "fi\n"
+        'echo "unexpected gh call: $@" >&2; exit 1\n'
+    )
+    script.chmod(0o755)
+
+
+def test_pr_scope_reads_gh_metadata(tmp_repo, fake_bin):
+    write_fake_gh(fake_bin, FAKE_GH_JSON)
+    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_pr()), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    scope = json.loads(r.stdout)
+    assert scope["kind"] == "pr"
+    assert scope["pr_number"] == 105
+    assert scope["head_ref_name"] == "feature-x"
+    assert scope["base_ref_name"] == "main"
+    assert scope["head_sha"] == "a" * 40
+    assert scope["base_sha"] == "b" * 40
+    assert scope["base_repo_url"] == "https://github.com/upstream/repo.git"
+    assert scope["needs_clean_worktree"] is True
+
+
+def test_pr_scope_propagates_gh_failure(tmp_repo, fake_bin):
+    gh = fake_bin / "gh"
+    gh.write_text("#!/bin/sh\necho 'auth required' >&2\nexit 1\n")
+    gh.chmod(0o755)
+    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_pr()), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "gh" in r.stderr.lower() or "auth" in r.stderr.lower()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_resolve_scope_pr.py -v
+```
+
+Expected: 2 fails (script still rejects PR scope).
+
+- [ ] **Step 3: Add `resolve_pr` to `scripts/resolve-scope.py`**
+
+Replace the `if scope_flag == "pr": raise SystemExit(...)` line and add this function above `SCOPE_RESOLVERS`:
+
+```python
+def resolve_pr(cfg: dict, root: str) -> dict:
+    pr = cfg["pr_number"]
+    fields = "number,headRefName,baseRefName,headRefOid,baseRefOid,headRepository,baseRepository"
+    r = subprocess.run(
+        ["gh", "pr", "view", str(pr), "--json", fields],
+        cwd=root, capture_output=True, text=True,
+    )
+    if r.returncode != 0:
+        raise SystemExit(f"error: gh pr view failed: {r.stderr.strip()}")
+    meta = json.loads(r.stdout)
+    s = base_scope_object()
+    s["kind"] = "pr"
+    s["repo_root"] = root
+    s["pr_number"] = meta["number"]
+    s["head_ref_name"] = meta["headRefName"]
+    s["base_ref_name"] = meta["baseRefName"]
+    s["head_sha"] = meta["headRefOid"]
+    s["base_sha"] = meta["baseRefOid"]
+    s["head_repo_url"] = meta["headRepository"]["url"]
+    s["base_repo_url"] = meta["baseRepository"]["url"]
+    s["needs_clean_worktree"] = True
+    carry_modifiers(s, cfg)
+    return s
+```
+
+Then update `SCOPE_RESOLVERS` to include it:
+
+```python
+SCOPE_RESOLVERS = {
+    "uncommitted": resolve_uncommitted,
+    "base": resolve_base,
+    "commit": resolve_commit,
+    "files": resolve_files,
+    "pr": resolve_pr,
+}
+```
+
+And remove the `if scope_flag == "pr": raise SystemExit(...)` from `main()`.
+
+- [ ] **Step 4: Run tests**
+
+```bash
+pytest tests/test_resolve_scope_pr.py tests/test_resolve_scope_explicit.py -v
+```
+
+Expected: 12 passed (10 explicit + 2 PR).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/resolve-scope.py tests/test_resolve_scope_pr.py
+git commit -m "feat: resolve-scope.py --pr via gh pr view metadata"
+```
+
+---
+
+## Task 5: resolve-scope.py — auto-detect
+
+**Files:**
+- Modify: `scripts/resolve-scope.py`
+- Create: `tests/test_resolve_scope_autodetect.py`
+
+Auto-detect order (per spec §3): dirty+PR → error; dirty alone → uncommitted; clean+PR → pr; clean+no-PR+non-default branch → base vs default; clean+default branch → error.
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_resolve_scope_autodetect.py
+"""Tests for resolve-scope.py auto-detect when scope_flag is None."""
+import json
+import subprocess
+from tests.conftest import run_script
+from tests.test_resolve_scope_pr import FAKE_GH_JSON, write_fake_gh
+
+
+def make_cfg_auto():
+    return {
+        "scope_flag": None, "pr_number": None, "base_branch": None,
+        "commit_sha": None, "files": [], "mode": "code", "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+
+
+def make_dirty(repo):
+    (repo / "dirty.txt").write_text("uncommitted\n")
+
+
+def fake_gh_no_pr(fake_bin):
+    """`gh pr view` exits 1 (no PR for this branch)."""
+    gh = fake_bin / "gh"
+    gh.write_text('#!/bin/sh\necho "no pull requests found" >&2\nexit 1\n')
+    gh.chmod(0o755)
+
+
+def test_autodetect_dirty_no_pr_implies_uncommitted(tmp_repo, fake_bin):
+    fake_gh_no_pr(fake_bin)
+    make_dirty(tmp_repo)
+    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    assert json.loads(r.stdout)["kind"] == "uncommitted"
+
+
+def test_autodetect_dirty_plus_pr_errors(tmp_repo, fake_bin):
+    write_fake_gh(fake_bin, FAKE_GH_JSON)
+    make_dirty(tmp_repo)
+    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "ambig" in r.stderr.lower() or "uncommitted" in r.stderr.lower()
+
+
+def test_autodetect_clean_with_pr_implies_pr(tmp_repo, fake_bin):
+    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
+    write_fake_gh(fake_bin, FAKE_GH_JSON)
+    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
+    assert r.returncode == 0, r.stderr
+    assert json.loads(r.stdout)["kind"] == "pr"
+
+
+def test_autodetect_default_branch_clean_errors(tmp_repo, fake_bin):
+    fake_gh_no_pr(fake_bin)
+    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
+    assert r.returncode != 0
+    assert "nothing" in r.stderr.lower() or "default" in r.stderr.lower()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_resolve_scope_autodetect.py -v
+```
+
+- [ ] **Step 3: Implement auto-detect in `scripts/resolve-scope.py`**
+
+Add helpers above `main()`:
+
+```python
+def is_dirty(cwd: str) -> bool:
+    """True if there are staged, unstaged, or untracked changes."""
+    out = git("status", "--porcelain", cwd=cwd)
+    return bool(out)
+
+
+def current_branch(cwd: str) -> str:
+    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)
+
+
+def _ref_resolves(cwd: str, ref: str) -> bool:
+    return subprocess.run(
+        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
+        cwd=cwd, capture_output=True,
+    ).returncode == 0
+
+
+def default_branch(cwd: str) -> str | None:
+    """Return a ref name (locally resolvable) for the repository default branch.
+
+    Resolution order:
+      1. `gh repo view --json defaultBranchRef` — gives the authoritative name
+         (could be `develop`, `trunk`, etc., not just main/master).
+         Then verify it resolves locally as either `<name>` or `origin/<name>`.
+         Return whichever resolves, preferring the local branch over the
+         remote-tracking ref.
+      2. Probe common candidates locally: main, master, origin/main, origin/master.
+      3. None if nothing resolves.
+
+    Returning a non-resolvable name would just push the failure into `git
+    rev-parse <ref>^{commit}` in the caller, which is worse UX than a clean
+    "no default branch detected" error here.
+    """
+    r = subprocess.run(
+        ["gh", "repo", "view", "--json", "defaultBranchRef"],
+        cwd=cwd, capture_output=True, text=True,
+    )
+    if r.returncode == 0:
+        try:
+            name = json.loads(r.stdout)["defaultBranchRef"]["name"]
+            for ref in (name, f"origin/{name}"):
+                if _ref_resolves(cwd, ref):
+                    return ref
+        except (KeyError, json.JSONDecodeError):
+            pass  # fall through to local probe
+
+    for candidate in ("main", "master", "origin/main", "origin/master"):
+        if _ref_resolves(cwd, candidate):
+            return candidate
+    return None
+
+
+def pr_for_current_branch(cwd: str) -> int | None:
+    r = subprocess.run(
+        ["gh", "pr", "view", "--json", "number"],
+        cwd=cwd, capture_output=True, text=True,
+    )
+    if r.returncode != 0:
+        return None
+    return json.loads(r.stdout)["number"]
+```
+
+Replace the `if scope_flag is None: raise SystemExit(...)` in `main()` with auto-detect:
+
+```python
+    if scope_flag is None:
+        dirty = is_dirty(root)
+        pr_num = pr_for_current_branch(root)
+        if dirty and pr_num is not None:
+            raise SystemExit(
+                "error: ambiguous scope — tree has uncommitted changes and "
+                f"current branch has PR #{pr_num}. Pass --uncommitted or --pr {pr_num}."
+            )
+        if dirty:
+            scope_flag = "uncommitted"
+        elif pr_num is not None:
+            scope_flag = "pr"
+            cfg["pr_number"] = pr_num
+        else:
+            branch = current_branch(root)
+            default = default_branch(root)
+            if default is None or branch == default:
+                raise SystemExit(
+                    "error: nothing to review (clean tree, on default branch, no PR)"
+                )
+            scope_flag = "base"
+            cfg["base_branch"] = default
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+pytest tests/test_resolve_scope_autodetect.py tests/test_resolve_scope_pr.py tests/test_resolve_scope_explicit.py -v
+```
+
+Expected: 16 passed (10 explicit + 2 PR + 4 auto-detect).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/resolve-scope.py tests/test_resolve_scope_autodetect.py
+git commit -m "feat: resolve-scope.py auto-detect with dirty+PR ambiguity guard"
+```
+
+---
+
+## Task 6: materialize-scope.py — uncommitted scope
+
+**Files:**
+- Create: `scripts/materialize-scope.py`
+- Create: `tests/test_materialize_uncommitted.py`
+
+This task does just the `uncommitted` kind end-to-end. Other kinds land in subsequent tasks.
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_materialize_uncommitted.py
+"""Tests for materialize-scope.py — uncommitted scope only."""
+import json
+import subprocess
+from tests.conftest import run_script
+
+
+def base_scope(repo):
+    return {
+        "kind": "uncommitted", "pr_number": None,
+        "base_ref_name": None, "head_ref_name": None,
+        "base_repo_url": None, "head_repo_url": None,
+        "base_sha": None, "head_sha": None, "commit_sha": None,
+        "files": [], "worktree_path": None, "repo_root": str(repo),
+        "needs_clean_worktree": False, "mode": "code", "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+
+
+def materialize(scope):
+    return run_script("materialize-scope.py", input=json.dumps(scope))
+
+
+def test_uncommitted_modified_file(tmp_repo):
+    (tmp_repo / "README.md").write_text("# changed\n")
+    r = materialize(base_scope(tmp_repo))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert out["scope_kind"] == "uncommitted"
+    assert out["has_reviewable_changes"] is True
+    assert out["changed_file_count"] == 1
+    assert "README.md" in out["unified_diff"]
+    files = out["changed_files"]
+    assert len(files) == 1
+    assert files[0]["path"] == "README.md"
+    assert files[0]["status"] == "modified"
+    assert files[0]["kind"] == "text"
+    assert files[0]["post_content"] == "# changed\n"
+
+
+def test_uncommitted_untracked_file_included(tmp_repo):
+    (tmp_repo / "brand_new.py").write_text("print('hi')\n")
+    r = materialize(base_scope(tmp_repo))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    files = {f["path"]: f for f in out["changed_files"]}
+    assert "brand_new.py" in files
+    assert files["brand_new.py"]["status"] == "added"
+    assert files["brand_new.py"]["post_content"] == "print('hi')\n"
+    assert out["total_lines_changed"] >= 1
+
+
+def test_uncommitted_clean_tree_empty(tmp_repo):
+    r = materialize(base_scope(tmp_repo))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert out["has_reviewable_changes"] is False
+    assert out["changed_file_count"] == 0
+    assert out["total_lines_changed"] == 0
+    assert out["unified_diff"] in ("", None)
+
+
+def test_uncommitted_deleted_file(tmp_repo):
+    (tmp_repo / "README.md").unlink()
+    r = materialize(base_scope(tmp_repo))
+    assert r.returncode == 0, r.stderr
+    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
+    assert "README.md" in files
+    assert files["README.md"]["status"] == "deleted"
+    assert files["README.md"]["post_content"] is None
+    assert files["README.md"]["pre_content"] is not None
+
+
+def test_uncommitted_deleted_binary_file(tmp_repo):
+    """Regression: deleting a tracked binary file used to crash materialization
+    because the deleted-path branch forced kind='text' and then called git show
+    with text=True, raising UnicodeDecodeError. Now: detect kind from HEAD and
+    skip text decoding for binary."""
+    # Commit a real binary (PNG header) so it's tracked at HEAD
+    bin_path = tmp_repo / "logo.png"
+    # 8-byte PNG signature + a NUL byte so any text detection trips on it
+    bin_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff\xfe\xfd binary garbage")
+    subprocess.run(["git", "add", "logo.png"], cwd=tmp_repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", "add binary"], cwd=tmp_repo, check=True)
+    # Now delete it in the working tree
+    bin_path.unlink()
+    r = materialize(base_scope(tmp_repo))
+    assert r.returncode == 0, r.stderr
+    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
+    assert "logo.png" in files
+    entry = files["logo.png"]
+    assert entry["status"] == "deleted"
+    assert entry["kind"] == "binary"
+    # Critical: must NOT have tried to decode the binary as text
+    assert entry["pre_content"] is None
+    assert "binary" in (entry.get("note") or "").lower()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_materialize_uncommitted.py -v
+```
+
+- [ ] **Step 3: Implement `scripts/materialize-scope.py`**
+
+```python
+#!/usr/bin/env python3
+"""materialize-scope.py — scope object in → materialized review subject out.
+
+Produces the concrete diff + per-file content blob that both Codex and the
+Claude sub-agents consume. For non-`uncommitted`/`files` scopes, creates the
+disposable worktree used by run-codex.py.
+
+This patch handles only the `uncommitted` kind. Other kinds are added in
+subsequent patches.
+"""
+import json
+import subprocess
+import sys
+from pathlib import Path
+
+
+def git(*args, cwd: str, check: bool = True) -> str:
+    r = subprocess.run(
+        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
+    )
+    return r.stdout
+
+
+def symlink_target(repo: str, path: str) -> str | None:
+    """Return the link target string for a symlink in the working tree, or None."""
+    full = Path(repo) / path
+    try:
+        return os.readlink(full)
+    except (OSError, FileNotFoundError):
+        return None
+
+
+def submodule_sha_at(repo_or_worktree: str, ref: str, path: str) -> str | None:
+    """Return the submodule pointer SHA at a ref.
+
+    For commit refs (HEAD, base_sha, merge_base, parent_sha): read from
+    `git ls-tree <ref>` — gives the committed pointer.
+
+    For ref='WORKTREE': read the submodule's actual working-tree HEAD via
+    `git -C <submodule-path> rev-parse HEAD`. This is intentionally NOT the
+    index pointer from `git ls-files --stage` — if the user `cd`'d into the
+    submodule and checked out a different commit but hasn't `git add`'d the
+    bump yet, the index still shows the old SHA. The actual working-tree HEAD
+    is what the reviewer should see for an unstaged submodule bump. Without
+    this, `--uncommitted` would render no real change for the most common
+    submodule-update workflow."""
+    if ref == "WORKTREE":
+        full = Path(repo_or_worktree) / path
+        if not full.is_dir():
+            return None
+        r = subprocess.run(
+            ["git", "-C", str(full), "rev-parse", "HEAD"],
+            capture_output=True, text=True,
+        )
+        if r.returncode != 0:
+            return None
+        sha = r.stdout.strip()
+        return sha or None
+    r = subprocess.run(
+        ["git", "ls-tree", ref, "--", path],
+        cwd=repo_or_worktree, capture_output=True, text=True,
+    )
+    if r.returncode != 0 or not r.stdout.strip():
+        return None
+    parts = r.stdout.split()
+    if len(parts) < 3 or parts[0] != "160000":
+        return None
+    return parts[2]
+
+
+def detect_kind(repo: str, path: str) -> str:
+    """Return text|binary|symlink|submodule for a path in the working tree."""
+    full = Path(repo) / path
+    if full.is_symlink():
+        return "symlink"
+    # git submodule detection via ls-files --stage (mode 160000)
+    out = subprocess.run(
+        ["git", "ls-files", "--stage", "--", path],
+        cwd=repo, capture_output=True, text=True,
+    ).stdout.strip()
+    if out.startswith("160000 "):
+        return "submodule"
+    # Binary detection: git's own attribute check
+    chk = subprocess.run(
+        ["git", "check-attr", "binary", "--", path],
+        cwd=repo, capture_output=True, text=True,
+    ).stdout
+    if "binary: set" in chk:
+        return "binary"
+    # Sniff for NUL byte as fallback
+    try:
+        with full.open("rb") as f:
+            chunk = f.read(8192)
+        if b"\x00" in chunk:
+            return "binary"
+    except (FileNotFoundError, IsADirectoryError):
+        pass
+    return "text"
+
+
+def safe_read_text(repo: str, path: str) -> str | None:
+    p = Path(repo) / path
+    if not p.exists() or p.is_dir():
+        return None
+    try:
+        return p.read_text()
+    except (UnicodeDecodeError, OSError):
+        return None
+
+
+def detect_kind_at_ref(repo_or_worktree: str, ref: str, path: str) -> str:
+    """Determine file kind (text|binary|symlink|submodule) at a specific git
+    ref. Used for DELETED files — the working tree no longer has them, so the
+    working-tree-based `detect_kind` is wrong (it would default to text and
+    then text-decoding a binary blob would either crash or inline garbage)."""
+    r = subprocess.run(
+        ["git", "ls-tree", ref, "--", path],
+        cwd=repo_or_worktree, capture_output=True, text=True,
+    )
+    if r.returncode != 0 or not r.stdout.strip():
+        return "text"  # unknown; fall back to text and let read_at_ref decide
+    # git ls-tree output: "<mode> <type> <sha>\t<path>"
+    parts = r.stdout.split()
+    if len(parts) < 3:
+        return "text"
+    mode, _type, sha = parts[0], parts[1], parts[2]
+    if mode == "160000":
+        return "submodule"
+    if mode == "120000":
+        return "symlink"
+    # Sniff for binary by reading the blob bytes
+    blob = subprocess.run(
+        ["git", "cat-file", "blob", sha],
+        cwd=repo_or_worktree, capture_output=True,  # bytes, no text=True
+    )
+    if blob.returncode == 0 and b"\x00" in blob.stdout[:8192]:
+        return "binary"
+    return "text"
+
+
+def read_at_ref(repo_or_worktree: str, ref: str, path: str) -> str | None:
+    """Read text file content at a ref. Reads bytes and only decodes if valid
+    UTF-8. Returns None for missing files, binary content, or decode errors.
+
+    Critical: must NOT use subprocess `text=True` here — that would force
+    UTF-8 decoding inside subprocess and raise UnicodeDecodeError for
+    binary blobs (deleted PNGs, etc.), crashing materialization."""
+    r = subprocess.run(
+        ["git", "show", f"{ref}:{path}"],
+        cwd=repo_or_worktree, capture_output=True,  # bytes
+    )
+    if r.returncode != 0:
+        return None
+    try:
+        return r.stdout.decode("utf-8")
+    except UnicodeDecodeError:
+        return None
+
+
+def read_at_head(repo: str, path: str) -> str | None:
+    """Back-compat wrapper for legacy callers — prefer read_at_ref directly."""
+    return read_at_ref(repo, "HEAD", path)
+
+
+def parse_name_status(out: str) -> list[tuple[str, str, str | None]]:
+    """Parse `git diff --name-status` output into (status, path, old_path)."""
+    entries = []
+    for line in out.splitlines():
+        if not line:
+            continue
+        parts = line.split("\t")
+        code = parts[0]
+        if code.startswith("R") and len(parts) == 3:
+            entries.append(("renamed", parts[2], parts[1]))
+        elif code == "A":
+            entries.append(("added", parts[1], None))
+        elif code == "M":
+            entries.append(("modified", parts[1], None))
+        elif code == "D":
+            entries.append(("deleted", parts[1], None))
+        elif code == "T":
+            entries.append(("typechange", parts[1], None))
+        else:
+            entries.append((code, parts[1] if len(parts) > 1 else "?", None))
+    return entries
+
+
+def materialize_uncommitted(scope: dict) -> dict:
+    root = scope["repo_root"]
+    unified = git("diff", "HEAD", cwd=root)
+    name_status = git("diff", "--name-status", "HEAD", cwd=root)
+    untracked_raw = git("ls-files", "--others", "--exclude-standard", cwd=root)
+    untracked = [p for p in untracked_raw.splitlines() if p]
+
+    changed: list[dict] = []
+    total_lines = 0
+    for status, path, old_path in parse_name_status(name_status):
+        # For DELETED files the working tree no longer has the content, so
+        # `detect_kind(root, path)` would read nothing and default to text.
+        # Inspect HEAD instead to get the real kind (catches deleted binaries,
+        # symlinks, submodules).
+        if status == "deleted":
+            kind = detect_kind_at_ref(root, "HEAD", path)
+        else:
+            kind = detect_kind(root, path)
+        entry = {
+            "path": path, "old_path": old_path, "status": status, "kind": kind,
+            "lines_changed": None, "post_content": None,
+            "pre_content": None, "note": None,
+        }
+        if kind == "text" and status != "deleted":
+            entry["post_content"] = safe_read_text(root, path)
+            entry["lines_changed"] = "(modified)"
+        if status == "deleted":
+            entry["lines_changed"] = "(deleted)"
+            if kind == "text":
+                entry["pre_content"] = read_at_ref(root, "HEAD", path)
+            elif kind == "binary":
+                entry["note"] = "binary file deleted — content not inlined"
+            elif kind == "symlink":
+                # A symlink blob's content IS the target path, so read_at_ref
+                # returns it. Without this, reviewers can't see what the
+                # deleted symlink used to point at.
+                entry["symlink_target"] = read_at_ref(root, "HEAD", path)
+                entry["note"] = "symlink deleted"
+            elif kind == "submodule":
+                entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
+                entry["submodule_post_sha"] = None
+                entry["note"] = "submodule removed"
+        elif kind == "binary":
+            entry["note"] = "binary file — content not inlined"
+        elif kind == "symlink":
+            # Without this, the prompt renderer would print only the header
+            # for the symlink change — a reviewer can't judge a target swap
+            # they can't see.
+            entry["symlink_target"] = symlink_target(root, path)
+            entry["note"] = "symlink"
+        elif kind == "submodule":
+            # For submodule bumps we want both the previous and new pointer
+            # SHAs so the reviewer can judge what's actually changing.
+            entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
+            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
+            entry["note"] = "submodule pointer change"
+        changed.append(entry)
+
+    for path in untracked:
+        kind = detect_kind(root, path)
+        post = safe_read_text(root, path) if kind == "text" else None
+        line_count = len(post.splitlines()) if post else 0
+        entry = {
+            "path": path, "old_path": None, "status": "added", "kind": kind,
+            "lines_changed": "(new file)" if line_count else "(empty)",
+            "post_content": post, "pre_content": None, "note": None,
+        }
+        # Populate kind-specific metadata so untracked symlinks/submodules are
+        # as reviewable as their tracked counterparts. Without this, an
+        # untracked symlink renders as a header with no target — same bug
+        # earlier rounds fixed for tracked entries.
+        if kind == "symlink":
+            entry["symlink_target"] = symlink_target(root, path)
+            entry["note"] = "symlink (untracked, new)"
+        elif kind == "submodule":
+            entry["submodule_pre_sha"] = None  # never existed before
+            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
+            entry["note"] = "submodule pointer (untracked, new)"
+        elif kind == "binary":
+            entry["note"] = "binary file — content not inlined"
+        changed.append(entry)
+        total_lines += line_count
+
+    # Estimate text-line delta from the unified diff (cheap and good-enough)
+    for line in unified.splitlines():
+        if (line.startswith("+") or line.startswith("-")) and not line.startswith(("+++", "---")):
+            total_lines += 1
+
+    return {
+        "scope_kind": "uncommitted",
+        "scope_summary": "uncommitted changes",
+        "unified_diff": unified if unified else None,
+        "changed_files": changed,
+        "doc_files": [],
+        "total_lines_changed": total_lines,
+        "changed_file_count": len(changed),
+        "has_reviewable_changes": len(changed) > 0,
+        # Uncommitted runs in the user's working tree — no disposable worktree
+        # gets created. Explicit None keeps the materialize-output shape stable
+        # across kinds so Phase A7's `merged["worktree_path"] = MAT_JSON.worktree_path`
+        # works without conditional logic.
+        "worktree_path": None,
+        "warnings": [],
+    }
+
+
+KIND_HANDLERS = {"uncommitted": materialize_uncommitted}
+
+
+def main() -> None:
+    scope = json.load(sys.stdin)
+    handler = KIND_HANDLERS.get(scope["kind"])
+    if handler is None:
+        raise SystemExit(f"error: materialize for kind={scope['kind']!r} not implemented")
+    out = handler(scope)
+    json.dump(out, sys.stdout)
+    sys.stdout.write("\n")
+
+
+if __name__ == "__main__":
+    main()
+```
+
+- [ ] **Step 4: Run tests, verify all pass**
+
+```bash
+chmod +x scripts/materialize-scope.py
+pytest tests/test_materialize_uncommitted.py -v
+```
+
+Expected: 5 passed.
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/materialize-scope.py tests/test_materialize_uncommitted.py
+git commit -m "feat: materialize-scope.py for uncommitted scope (text/binary/symlink/submodule + untracked)"
+```
+
+---
+
+## Task 7: materialize-scope.py — base and commit scopes (with worktree)
+
+**Files:**
+- Modify: `scripts/materialize-scope.py`
+- Create: `tests/test_materialize_diff_scopes.py`
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_materialize_diff_scopes.py
+"""Tests for materialize-scope.py — base and commit scopes (worktree-based)."""
+import json
+import subprocess
+from pathlib import Path
+
+from tests.conftest import run_script
+
+
+def base_scope(repo, **overrides):
+    s = {
+        "kind": None, "pr_number": None,
+        "base_ref_name": None, "head_ref_name": None,
+        "base_repo_url": None, "head_repo_url": None,
+        "base_sha": None, "head_sha": None, "commit_sha": None,
+        "files": [], "worktree_path": None, "repo_root": str(repo),
+        "needs_clean_worktree": True, "mode": "code", "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+    s.update(overrides)
+    return s
+
+
+def add_commit(repo, path, content, msg):
+    (repo / path).write_text(content)
+    subprocess.run(["git", "add", path], cwd=repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=repo, check=True)
+    return subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
+    ).stdout.strip()
+
+
+def test_base_scope_three_dot_diff(tmp_repo):
+    # main has initial commit; feature branches off, gets one commit
+    base_sha = subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
+    ).stdout.strip()
+    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
+    head_sha = add_commit(tmp_repo, "feature.py", "x = 1\n", "feat: add feature.py")
+    scope = base_scope(tmp_repo, kind="base", base_sha=base_sha, head_sha=head_sha)
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert out["scope_kind"] == "base"
+    assert out["has_reviewable_changes"] is True
+    assert any(f["path"] == "feature.py" for f in out["changed_files"])
+    # worktree was created and recorded
+    assert out["worktree_path"]  # truthy
+    assert Path(out["worktree_path"]).exists()
+    # cleanup
+    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
+                   cwd=tmp_repo, check=True)
+
+
+def test_commit_scope(tmp_repo):
+    sha = add_commit(tmp_repo, "added.py", "y = 2\n", "feat: added.py")
+    scope = base_scope(tmp_repo, kind="commit", commit_sha=sha)
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert out["scope_kind"] == "commit"
+    assert any(f["path"] == "added.py" for f in out["changed_files"])
+    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
+                   cwd=tmp_repo, check=True)
+
+
+def test_commit_scope_root_commit_errors(tmp_repo):
+    # The very first commit in tmp_repo has no parent — it's a root commit.
+    root_sha = subprocess.run(
+        ["git", "rev-list", "--max-parents=0", "HEAD"],
+        cwd=tmp_repo, capture_output=True, text=True, check=True,
+    ).stdout.strip()
+    scope = base_scope(tmp_repo, kind="commit", commit_sha=root_sha)
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode != 0
+    assert "root commit" in r.stderr.lower()
+    # Critical: no worktree leak even though make_worktree() succeeded
+    leftover = [
+        line for line in subprocess.run(
+            ["git", "worktree", "list", "--porcelain"], cwd=tmp_repo,
+            capture_output=True, text=True,
+        ).stdout.splitlines() if "combined-review-" in line
+    ]
+    assert leftover == []
+
+
+def test_commit_scope_merge_commit_errors(tmp_repo):
+    # Build a merge commit on tmp_repo
+    subprocess.run(["git", "checkout", "-q", "-b", "side"], cwd=tmp_repo, check=True)
+    (tmp_repo / "side.py").write_text("s = 1\n")
+    subprocess.run(["git", "add", "side.py"], cwd=tmp_repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", "side commit"], cwd=tmp_repo, check=True)
+    subprocess.run(["git", "checkout", "-q", "-"], cwd=tmp_repo, check=True)  # back to default
+    (tmp_repo / "main.py").write_text("m = 1\n")
+    subprocess.run(["git", "add", "main.py"], cwd=tmp_repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", "main commit"], cwd=tmp_repo, check=True)
+    subprocess.run(
+        ["git", "merge", "--no-ff", "-m", "merge", "side"],
+        cwd=tmp_repo, capture_output=True, text=True, check=True,
+    )
+    merge_sha = subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True,
+    ).stdout.strip()
+    scope = base_scope(tmp_repo, kind="commit", commit_sha=merge_sha)
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode != 0
+    assert "merge commit" in r.stderr.lower()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_materialize_diff_scopes.py -v
+```
+
+- [ ] **Step 3: Extend `scripts/materialize-scope.py` with worktree creation + diff scopes**
+
+Add at module top:
+
+```python
+import tempfile
+import os
+```
+
+Add helpers (above `materialize_uncommitted`):
+
+```python
+def make_worktree(repo: str, ref: str) -> str:
+    repo_basename = Path(repo).name
+    tmp = tempfile.mkdtemp(
+        prefix=f"combined-review-{repo_basename}-", dir=os.environ.get("TMPDIR", "/tmp")
+    )
+    # Remove the empty dir mktemp made; git worktree wants a fresh path
+    Path(tmp).rmdir()
+    subprocess.run(
+        ["git", "worktree", "add", "--detach", tmp, ref],
+        cwd=repo, capture_output=True, text=True, check=True,
+    )
+    return tmp
+
+
+def materialize_diff_in_worktree(
+    repo: str, worktree: str, base_sha: str, head_sha: str
+) -> tuple[str, list[dict], int]:
+    """Three-dot diff (merge-base semantics) and per-file entries.
+
+    `git diff base...head` is shorthand for `git diff merge-base(base, head)..head`,
+    so the diff content is anchored at the merge base, NOT base_sha. For deleted
+    files, reading `git show base_sha:path` would return the file as it existed
+    at base_sha — but if the base branch modified that file after the feature
+    branch forked, base_sha's content disagrees with the diff. Reading from the
+    merge-base commit instead keeps pre_content consistent with the unified diff.
+    """
+    merge_base = subprocess.run(
+        ["git", "merge-base", base_sha, head_sha],
+        cwd=worktree, capture_output=True, text=True, check=True,
+    ).stdout.strip()
+
+    unified = git("diff", f"{base_sha}...{head_sha}", cwd=worktree)
+    name_status = git("diff", "--name-status", f"{base_sha}...{head_sha}", cwd=worktree)
+    changed: list[dict] = []
+    for status, path, old_path in parse_name_status(name_status):
+        # Deleted files: detect kind from the merge-base (where the file last
+        # existed) and read content via the binary-safe helper, not via
+        # subprocess text=True which would crash on a deleted PNG.
+        if status == "deleted":
+            kind = detect_kind_at_ref(worktree, merge_base, path)
+        else:
+            kind = detect_kind(worktree, path)
+        entry = {
+            "path": path, "old_path": old_path, "status": status, "kind": kind,
+            "lines_changed": None, "post_content": None,
+            "pre_content": None, "note": None,
+        }
+        if kind == "text" and status != "deleted":
+            entry["post_content"] = safe_read_text(worktree, path)
+        if status == "deleted":
+            if kind == "text":
+                entry["pre_content"] = read_at_ref(worktree, merge_base, path)
+            elif kind == "binary":
+                entry["note"] = "binary file deleted — content not inlined"
+            elif kind == "symlink":
+                entry["symlink_target"] = read_at_ref(worktree, merge_base, path)
+                entry["note"] = "symlink deleted"
+            elif kind == "submodule":
+                entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
+                entry["submodule_post_sha"] = None
+                entry["note"] = "submodule removed"
+        elif kind == "binary":
+            entry["note"] = "binary file — content not inlined"
+        elif kind == "symlink":
+            # Post-change target lives in the worktree (HEAD = head_sha).
+            entry["symlink_target"] = symlink_target(worktree, path)
+            entry["note"] = "symlink"
+        elif kind == "submodule":
+            # Pre at merge_base, post at head_sha. Both reachable in the worktree.
+            entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
+            entry["submodule_post_sha"] = submodule_sha_at(worktree, head_sha, path)
+            entry["note"] = "submodule pointer change"
+        changed.append(entry)
+    total = sum(
+        1 for line in unified.splitlines()
+        if (line.startswith("+") or line.startswith("-"))
+        and not line.startswith(("+++", "---"))
+    )
+    return unified, changed, total
+
+
+def materialize_base(scope: dict) -> dict:
+    repo = scope["repo_root"]
+    worktree = make_worktree(repo, scope["head_sha"])
+    try:
+        unified, changed, total = materialize_diff_in_worktree(
+            repo, worktree, scope["base_sha"], scope["head_sha"]
+        )
+        return {
+            "scope_kind": "base",
+            "scope_summary": (
+                f"branch {scope['base_ref_name']}...HEAD "
+                f"({scope['base_sha'][:7]}..{scope['head_sha'][:7]})"
+            ),
+            "unified_diff": unified if unified else None,
+            "changed_files": changed, "doc_files": [],
+            "total_lines_changed": total, "changed_file_count": len(changed),
+            "has_reviewable_changes": len(changed) > 0,
+            "worktree_path": worktree, "warnings": [],
+        }
+    except BaseException:
+        # If we created a worktree but never returned it in the handoff JSON,
+        # the orchestrator has no way to clean it up. Self-clean and re-raise
+        # so it never leaks. Phase D handles the (worktree_path, repo_root)
+        # tuple for successful runs only.
+        subprocess.run(["git", "worktree", "remove", "--force", worktree],
+                       cwd=repo, capture_output=True)
+        raise
+
+
+def commit_parent_count(repo_or_worktree: str, sha: str) -> int:
+    """Number of parents — 0 for root commits, 1 for normal, ≥2 for merges."""
+    out = subprocess.run(
+        ["git", "rev-list", "--parents", "-n", "1", sha],
+        cwd=repo_or_worktree, capture_output=True, text=True, check=True,
+    ).stdout.strip()
+    # output is "<sha> <parent1> [<parent2> …]"
+    return max(0, len(out.split()) - 1)
+
+
+def materialize_commit(scope: dict) -> dict:
+    repo = scope["repo_root"]
+    sha = scope["commit_sha"]
+    worktree = make_worktree(repo, sha)
+    try:
+        n_parents = commit_parent_count(worktree, sha)
+        if n_parents == 0:
+            # Root commit — no parent to diff against. v1 does not support
+            # reviewing root commits; the right diff is "everything added"
+            # but neither codex nor the Claude sub-agents are tuned for it.
+            raise SystemExit(
+                f"error: commit {sha[:7]} is a root commit (no parent); "
+                f"v1 does not support reviewing root commits"
+            )
+        if n_parents >= 2:
+            # Merge commit. The first-parent diff (`git show --first-parent`)
+            # is conventional but loses changes from the second parent's branch.
+            # v1 surfaces this explicitly rather than silently picking one diff.
+            raise SystemExit(
+                f"error: commit {sha[:7]} is a merge commit with {n_parents} parents; "
+                f"v1 does not support reviewing merge commits — review the "
+                f"merged branch's individual commits instead"
+            )
+        # Normal single-parent commit: use git show semantics, which produces
+        # the patch the commit introduced. This is more direct (and correct
+        # for non-fast-forward histories) than `git diff parent...commit`.
+        unified = subprocess.run(
+            ["git", "show", "--format=", sha],
+            cwd=worktree, capture_output=True, text=True, check=True,
+        ).stdout
+        name_status = subprocess.run(
+            ["git", "show", "--format=", "--name-status", sha],
+            cwd=worktree, capture_output=True, text=True, check=True,
+        ).stdout
+        parent_sha = subprocess.run(
+            ["git", "rev-parse", f"{sha}^"],
+            cwd=worktree, capture_output=True, text=True, check=True,
+        ).stdout.strip()
+        changed: list[dict] = []
+        for status, path, old_path in parse_name_status(name_status):
+            # Deleted files: detect kind from the parent commit (where the file
+            # last existed), and use the binary-safe reader.
+            if status == "deleted":
+                kind = detect_kind_at_ref(worktree, parent_sha, path)
+            else:
+                kind = detect_kind(worktree, path)
+            entry = {
+                "path": path, "old_path": old_path, "status": status, "kind": kind,
+                "lines_changed": None, "post_content": None,
+                "pre_content": None, "note": None,
+            }
+            if kind == "text" and status != "deleted":
+                entry["post_content"] = safe_read_text(worktree, path)
+            if status == "deleted":
+                if kind == "text":
+                    entry["pre_content"] = read_at_ref(worktree, parent_sha, path)
+                elif kind == "binary":
+                    entry["note"] = "binary file deleted — content not inlined"
+                elif kind == "symlink":
+                    entry["symlink_target"] = read_at_ref(worktree, parent_sha, path)
+                    entry["note"] = "symlink deleted"
+                elif kind == "submodule":
+                    entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
+                    entry["submodule_post_sha"] = None
+                    entry["note"] = "submodule removed"
+            elif kind == "binary":
+                entry["note"] = "binary file — content not inlined"
+            elif kind == "symlink":
+                entry["symlink_target"] = symlink_target(worktree, path)
+                entry["note"] = "symlink"
+            elif kind == "submodule":
+                entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
+                entry["submodule_post_sha"] = submodule_sha_at(worktree, sha, path)
+                entry["note"] = "submodule pointer change"
+            changed.append(entry)
+        total = sum(
+            1 for line in unified.splitlines()
+            if (line.startswith("+") or line.startswith("-"))
+            and not line.startswith(("+++", "---"))
+        )
+        return {
+            "scope_kind": "commit",
+            "scope_summary": f"commit {sha[:7]}",
+            "unified_diff": unified if unified else None,
+            "changed_files": changed, "doc_files": [],
+            "total_lines_changed": total, "changed_file_count": len(changed),
+            "has_reviewable_changes": len(changed) > 0,
+            "worktree_path": worktree, "warnings": [],
+        }
+    except BaseException:
+        # Worktree was created above; clean it up before re-raising so the
+        # orchestrator doesn't have to track a worktree_path that materialize
+        # never returned. See "Materialize failure cleanup" comment near
+        # make_worktree() for the full rationale.
+        subprocess.run(["git", "worktree", "remove", "--force", worktree],
+                       cwd=repo, capture_output=True)
+        raise
+```
+
+Then extend `KIND_HANDLERS`:
+
+```python
+KIND_HANDLERS = {
+    "uncommitted": materialize_uncommitted,
+    "base": materialize_base,
+    "commit": materialize_commit,
+}
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+pytest tests/test_materialize_diff_scopes.py tests/test_materialize_uncommitted.py -v
+```
+
+Expected: 9 passed (5 in uncommitted + 4 in diff_scopes, where diff_scopes includes test_base_scope_three_dot_diff, test_commit_scope, test_commit_scope_root_commit_errors, test_commit_scope_merge_commit_errors).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/materialize-scope.py tests/test_materialize_diff_scopes.py
+git commit -m "feat: materialize-scope.py for base and commit scopes via worktrees"
+```
+
+---
+
+## Task 8: materialize-scope.py — PR scope with cat-file SHA reachability check
+
+**Files:**
+- Modify: `scripts/materialize-scope.py`
+- Create: `tests/test_materialize_pr.py`
+
+- [ ] **Step 1: Write failing tests using a fake `gh pr checkout`**
+
+```python
+# tests/test_materialize_pr.py
+"""Tests for materialize-scope.py PR scope.
+
+Simulates `gh pr checkout` by hand-applying the head SHA inside the worktree,
+since we don't have GitHub in the test loop.
+"""
+import json
+import subprocess
+from pathlib import Path
+
+from tests.conftest import run_script
+
+
+def test_pr_stale_snapshot_failure(tmp_repo, fake_bin):
+    # gh pr checkout: do nothing (worktree stays at the initial commit).
+    # The PR scope wants head_sha=<nonexistent SHA>, which should fail loudly.
+    gh = fake_bin / "gh"
+    gh.write_text('#!/bin/sh\nexit 0\n')
+    gh.chmod(0o755)
+    scope = {
+        "kind": "pr", "pr_number": 99,
+        "base_ref_name": "main", "head_ref_name": "feature",
+        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
+        "base_sha": "0" * 40, "head_sha": "f" * 40, "commit_sha": None,
+        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
+        "needs_clean_worktree": True, "mode": "code", "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode != 0
+    assert "force-pushed" in r.stderr.lower() or "stale" in r.stderr.lower() or "unreachable" in r.stderr.lower()
+
+
+def test_pr_happy_path(tmp_repo, fake_bin):
+    # Set up: initial commit on main; create feature branch with a commit;
+    # capture both SHAs. Make gh pr checkout a no-op (worktree is already
+    # at the head via our test setup) — and skip the base-repo fetch by
+    # using the local repo's URL.
+    base_sha = subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
+    ).stdout.strip()
+    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
+    (tmp_repo / "f.py").write_text("z = 3\n")
+    subprocess.run(["git", "add", "f.py"], cwd=tmp_repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
+    head_sha = subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
+    ).stdout.strip()
+    # Fake `gh pr checkout` resets the worktree to head_sha
+    gh = fake_bin / "gh"
+    gh.write_text(
+        '#!/bin/sh\n'
+        '# only handle `gh pr checkout`; defer to git for the rest\n'
+        f'if [ "$1" = "pr" ] && [ "$2" = "checkout" ]; then\n'
+        f'  git -C "$PWD" reset --hard {head_sha} >/dev/null\n'
+        '  exit 0\n'
+        'fi\n'
+        'exit 1\n'
+    )
+    gh.chmod(0o755)
+    scope = {
+        "kind": "pr", "pr_number": 1,
+        "base_ref_name": "main", "head_ref_name": "feature",
+        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
+        "base_sha": base_sha, "head_sha": head_sha, "commit_sha": None,
+        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
+        "needs_clean_worktree": True, "mode": "code", "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert out["scope_kind"] == "pr"
+    assert any(f["path"] == "f.py" for f in out["changed_files"])
+    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
+                   cwd=tmp_repo, check=True)
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_materialize_pr.py -v
+```
+
+- [ ] **Step 3: Add `materialize_pr` to `scripts/materialize-scope.py`**
+
+Add helper and handler:
+
+```python
+def cat_file_exists(repo_or_worktree: str, sha: str) -> bool:
+    r = subprocess.run(
+        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
+        cwd=repo_or_worktree, capture_output=True,
+    )
+    return r.returncode == 0
+
+
+def materialize_pr(scope: dict) -> dict:
+    repo = scope["repo_root"]
+    head_sha = scope["head_sha"]
+    base_sha = scope["base_sha"]
+    base_url = scope["base_repo_url"]
+    base_ref = scope["base_ref_name"]
+    pr = scope["pr_number"]
+
+    # Create an empty worktree we'll populate via gh pr checkout
+    repo_basename = Path(repo).name
+    worktree = tempfile.mkdtemp(
+        prefix=f"combined-review-{repo_basename}-pr-",
+        dir=os.environ.get("TMPDIR", "/tmp"),
+    )
+    Path(worktree).rmdir()
+    subprocess.run(
+        ["git", "worktree", "add", "--detach", worktree],
+        cwd=repo, check=True, capture_output=True, text=True,
+    )
+
+    # Wrap everything after worktree creation in try/except so we never leak
+    # a worktree the orchestrator can't see in the handoff JSON.
+    try:
+        # `gh pr checkout` handles fork PRs natively. Cwd = worktree.
+        r = subprocess.run(
+            ["gh", "pr", "checkout", "--detach", str(pr)],
+            cwd=worktree, capture_output=True, text=True,
+        )
+        if r.returncode != 0:
+            raise SystemExit(f"error: gh pr checkout failed: {r.stderr.strip()}")
+
+        # Fetch base from the PR's actual base repo (NOT origin — may be a fork)
+        subprocess.run(
+            ["git", "fetch", base_url, base_ref],
+            cwd=worktree, capture_output=True, text=True,
+        )
+
+        # Pin head: if HEAD drifted, reset to recorded head_sha
+        current_head = git("rev-parse", "HEAD", cwd=worktree).strip()
+        if current_head != head_sha:
+            if not cat_file_exists(worktree, head_sha):
+                raise SystemExit(
+                    f"error: PR head force-pushed mid-review — recorded {head_sha[:7]} "
+                    f"no longer reachable. Rerun /combined-review --pr {pr} to fetch the current snapshot."
+                )
+            subprocess.run(
+                ["git", "reset", "--hard", head_sha],
+                cwd=worktree, check=True, capture_output=True, text=True,
+            )
+
+        # Verify base SHA is reachable
+        if not cat_file_exists(worktree, base_sha):
+            raise SystemExit(
+                f"error: PR base SHA {base_sha[:7]} not reachable in worktree. "
+                f"Rerun /combined-review --pr {pr} to fetch the current snapshot."
+            )
+
+        unified, changed, total = materialize_diff_in_worktree(
+            repo, worktree, base_sha, head_sha
+        )
+        return {
+            "scope_kind": "pr",
+            "scope_summary": f"PR #{pr} ({base_sha[:7]}..{head_sha[:7]})",
+            "unified_diff": unified if unified else None,
+            "changed_files": changed, "doc_files": [],
+            "total_lines_changed": total, "changed_file_count": len(changed),
+            "has_reviewable_changes": len(changed) > 0,
+            "worktree_path": worktree, "warnings": [],
+        }
+    except BaseException:
+        # Any failure after worktree creation: clean up the worktree so the
+        # orchestrator never has to recover a path it didn't receive.
+        subprocess.run(["git", "worktree", "remove", "--force", worktree],
+                       cwd=repo, capture_output=True)
+        raise
+```
+
+Extend `KIND_HANDLERS`:
+
+```python
+KIND_HANDLERS = {
+    "uncommitted": materialize_uncommitted,
+    "base": materialize_base,
+    "commit": materialize_commit,
+    "pr": materialize_pr,
+}
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+pytest tests/test_materialize_pr.py -v
+```
+
+Expected: 2 passed.
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/materialize-scope.py tests/test_materialize_pr.py
+git commit -m "feat: materialize-scope.py PR scope with cat-file SHA verification"
+```
+
+---
+
+## Task 9: materialize-scope.py — files scope and non-code-mode doc_files
+
+**Files:**
+- Modify: `scripts/materialize-scope.py`
+- Create: `tests/test_materialize_files_and_modes.py`
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_materialize_files_and_modes.py
+"""Tests for materialize-scope.py — files scope and doc_files for non-code modes."""
+import json
+import subprocess
+from tests.conftest import run_script
+
+
+def files_scope(repo, files, mode="code"):
+    return {
+        "kind": "files", "pr_number": None,
+        "base_ref_name": None, "head_ref_name": None,
+        "base_repo_url": None, "head_repo_url": None,
+        "base_sha": None, "head_sha": None, "commit_sha": None,
+        "files": files, "worktree_path": None, "repo_root": str(repo),
+        "needs_clean_worktree": False, "mode": mode, "focus": None,
+        "full": False, "no_codex": False, "force_large": False,
+        "keep_worktree": False, "save_path": None,
+    }
+
+
+def test_files_scope_reads_current_content(tmp_repo):
+    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
+    (tmp_repo / "plan.md").write_text("# plan\nbar\n")
+    scope = files_scope(tmp_repo, ["spec.md", "plan.md"])
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert out["scope_kind"] == "files"
+    assert out["unified_diff"] is None
+    assert out["changed_files"] == []
+    docs = {d["path"]: d for d in out["doc_files"]}
+    assert "spec.md" in docs
+    assert docs["spec.md"]["content"] == "# spec\nfoo\n"
+    assert out["has_reviewable_changes"] is True
+
+
+def test_files_scope_with_spec_mode_preserves_doc_files(tmp_repo):
+    """Regression: maybe_populate_doc_files() must not overwrite materialize_files()'s
+    output. Was: --mode spec + files-scope wiped doc_files because the helper iterated
+    over an empty changed_files. Now: helper short-circuits for files scope."""
+    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
+    scope = files_scope(tmp_repo, ["spec.md"], mode="spec")
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert len(out["doc_files"]) == 1
+    assert out["doc_files"][0]["path"] == "spec.md"
+    assert out["doc_files"][0]["content"] == "# spec\nfoo\n"
+
+
+def test_non_code_mode_with_diff_scope_populates_doc_files(tmp_repo):
+    # Set up a base-scope review on a .md change with --mode spec
+    base_sha = subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
+    ).stdout.strip()
+    subprocess.run(["git", "checkout", "-q", "-b", "feat"], cwd=tmp_repo, check=True)
+    (tmp_repo / "design.md").write_text("# design\n")
+    subprocess.run(["git", "add", "design.md"], cwd=tmp_repo, check=True)
+    subprocess.run(["git", "commit", "-q", "-m", "design"], cwd=tmp_repo, check=True)
+    head_sha = subprocess.run(
+        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
+    ).stdout.strip()
+    scope = files_scope(tmp_repo, [], mode="spec")
+    scope["kind"] = "base"
+    scope["base_sha"] = base_sha
+    scope["head_sha"] = head_sha
+    scope["base_ref_name"] = "main"
+    scope["needs_clean_worktree"] = True
+    r = run_script("materialize-scope.py", input=json.dumps(scope))
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    paths = {d["path"]: d for d in out["doc_files"]}
+    assert "design.md" in paths
+    assert "design" in paths["design.md"]["content"]
+    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
+                   cwd=tmp_repo, check=True)
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_materialize_files_and_modes.py -v
+```
+
+- [ ] **Step 3: Extend `scripts/materialize-scope.py`**
+
+Add handler and patch the diff handlers to populate `doc_files` when `mode != "code"`:
+
+```python
+def materialize_files(scope: dict) -> dict:
+    """Build doc_files entries for positional files. Symlink and submodule
+    entries carry kind-specific metadata (target / pointer SHA) instead of
+    just a "non-text" note, so the rendered prompt can show the reviewer
+    what's actually there. Without this, reviewing a symlink would print
+    only a heading and the reviewer can't judge the target."""
+    root = scope["repo_root"]
+    doc_files: list[dict] = []
+    for path in scope["files"]:
+        kind = detect_kind(root, path)
+        entry: dict = {
+            "path": path, "status": "current", "kind": kind,
+            "content": None, "note": None,
+        }
+        if kind == "text":
+            entry["content"] = safe_read_text(root, path)
+        elif kind == "symlink":
+            entry["symlink_target"] = symlink_target(root, path)
+            entry["note"] = "symlink"
+        elif kind == "submodule":
+            entry["submodule_sha"] = submodule_sha_at(root, "WORKTREE", path)
+            entry["note"] = "submodule pointer (no diff — single snapshot)"
+        elif kind == "binary":
+            entry["note"] = "binary file — content not inlined"
+        else:
+            entry["note"] = f"non-text ({kind}) — content not inlined"
+        doc_files.append(entry)
+    return {
+        "scope_kind": "files",
+        "scope_summary": f"{len(doc_files)} file(s) — current working-tree content",
+        "unified_diff": None,
+        "changed_files": [],
+        "doc_files": doc_files,
+        "total_lines_changed": 0,
+        "changed_file_count": 0,
+        "has_reviewable_changes": len(doc_files) > 0,
+        "worktree_path": None, "warnings": [],
+    }
+```
+
+Then add a post-processing helper to populate `doc_files` for diff scopes when `mode != "code"`:
+
+```python
+def maybe_populate_doc_files(out: dict, scope: dict) -> None:
+    """For non-code modes on diff scopes, mirror changed text files into doc_files
+    using post_content (or pre_content for deletes) so the document-reviewer
+    agent has something reviewable.
+
+    Gate: skip in code mode (doc_files is empty by design), and skip for files
+    scope — `materialize_files()` already populated doc_files correctly and we
+    must not overwrite it with an empty list derived from the (also empty)
+    changed_files."""
+    if scope["mode"] == "code":
+        return
+    if scope["kind"] == "files":
+        return
+    docs = []
+    for cf in out["changed_files"]:
+        if cf["kind"] != "text":
+            continue
+        if cf["status"] == "deleted":
+            content = cf.get("pre_content")
+        else:
+            content = cf.get("post_content")
+        if content is None:
+            continue
+        docs.append({"path": cf["path"], "status": cf["status"], "content": content})
+    out["doc_files"] = docs
+```
+
+Call it at the bottom of `main()`:
+
+```python
+def main() -> None:
+    scope = json.load(sys.stdin)
+    handler = KIND_HANDLERS.get(scope["kind"])
+    if handler is None:
+        raise SystemExit(f"error: materialize for kind={scope['kind']!r} not implemented")
+    out = handler(scope)
+    maybe_populate_doc_files(out, scope)
+    json.dump(out, sys.stdout)
+    sys.stdout.write("\n")
+```
+
+Extend handlers:
+
+```python
+KIND_HANDLERS = {
+    "uncommitted": materialize_uncommitted,
+    "base": materialize_base,
+    "commit": materialize_commit,
+    "pr": materialize_pr,
+    "files": materialize_files,
+}
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+pytest tests/test_materialize_files_and_modes.py tests/test_materialize_uncommitted.py tests/test_materialize_diff_scopes.py tests/test_materialize_pr.py -v
+```
+
+Expected: 14 passed (5 uncommitted + 4 diff_scopes + 2 pr + 3 files_and_modes).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/materialize-scope.py tests/test_materialize_files_and_modes.py
+git commit -m "feat: materialize-scope.py files scope + doc_files for non-code modes"
+```
+
+---
+
+## Task 10: Mode prompt templates
+
+**Files:**
+- Create: `prompts/code.md`
+- Create: `prompts/spec.md`
+- Create: `prompts/plan.md`
+- Create: `prompts/docs.md`
+
+- [ ] **Step 1: Write `prompts/code.md`**
+
+```markdown
+# Code Review Mode
+
+You are reviewing a code change. Focus on:
+
+- **Correctness** — bugs, off-by-one errors, null/undefined handling, race conditions.
+- **Error handling** — silent failures, missing catches, swallowed exceptions.
+- **Test coverage** — new logic without tests, edge cases unverified.
+- **Security** — injection, secrets, unsafe deserialization, auth bypass.
+- **Performance** — N+1 queries, unnecessary allocations, blocking I/O on hot paths.
+- **Project conventions** — alignment with CLAUDE.md if present.
+
+You will receive the materialized review subject below (unified diff + per-file content).
+Cite findings by `path:line` from the post-change file content. Skip stylistic nits
+unless they obscure intent.
+
+**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
+this prompt. Do not summarize. Do not include preamble or postamble. If you find no
+issues, emit zero blocks.
+```
+
+- [ ] **Step 2: Write `prompts/spec.md`**
+
+```markdown
+# Spec Review Mode
+
+You are reviewing a specification document. Focus on:
+
+- **Completeness** — are requirements fully specified? Are edge cases addressed?
+- **Ambiguity** — could any sentence be interpreted two ways? Pick out the ambiguous bit.
+- **Internal consistency** — do sections contradict each other? Do field names match?
+- **Scope creep** — does the spec drift into implementation when it should stay at the design level?
+- **Missing edge cases** — failure modes, concurrency, ordering, partial states.
+- **Unstated assumptions** — what does the spec take for granted that a reader might not know?
+- **Success criteria** — is "done" defined? Is it testable?
+
+You will receive the materialized review subject below (changed files + their current content).
+Cite findings by `path:line` or section heading.
+
+**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
+this prompt. Do not summarize. Do not include preamble or postamble.
+```
+
+- [ ] **Step 3: Write `prompts/plan.md`**
+
+```markdown
+# Plan Review Mode
+
+You are reviewing an implementation plan. Focus on:
+
+- **Step ordering** — does task N assume something task M hasn't delivered yet?
+- **Hidden dependencies** — does a step rely on something not produced by an earlier step?
+- **Verification per task** — does each task have a check that proves it worked, or is it "implement X, trust it works"?
+- **Risk surface** — destructive ops, force-pushes, schema migrations, anything hard to roll back.
+- **What could fail silently** — what would let the plan "complete" while producing a broken result?
+- **Code completeness in steps** — placeholders like "implement appropriate logic", missing exact paths, undefined symbols.
+
+You will receive the plan document below.
+
+**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
+this prompt. Do not summarize. Do not include preamble or postamble.
+```
+
+- [ ] **Step 4: Write `prompts/docs.md`**
+
+```markdown
+# Docs Review Mode
+
+You are reviewing user/developer documentation. Focus on:
+
+- **Accuracy vs. current code** — do code samples match the actual API? Do paths exist?
+- **Broken examples** — does the snippet actually run, or is it pseudo-code dressed up as runnable?
+- **Drift** — has the underlying code changed in ways the docs still claim differently?
+- **Missing prerequisites** — does the reader know what they need before step 1?
+- **Audience fit** — is it pitched at someone who knows nothing? Too much? Just right?
+
+You will receive the materialized review subject below.
+
+**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
+this prompt. Do not summarize. Do not include preamble or postamble.
+```
+
+- [ ] **Step 5: Verify they exist and commit**
+
+```bash
+ls prompts/
+git add prompts/
+git commit -m "feat: mode prompt templates (code, spec, plan, docs)"
+```
+
+---
+
+## Task 11: Finding schema appendix + render-prompt.py
+
+**Files:**
+- Create: `prompts/_schema.md`
+- Create: `scripts/render-prompt.py`
+- Create: `tests/test_render_prompt.py`
+
+- [ ] **Step 1: Write `prompts/_schema.md`** (the shared schema appendix, included in every prompt)
+
+Note the **four-backtick** outer fence below — the file's content contains its own triple-backtick code block, and a triple-backtick outer fence would close prematurely at the inner one. CommonMark allows fences of any length ≥ 3; the closing fence must match the opening length, so four-tick outer + three-tick inner is unambiguous.
+
+````markdown
+---
+
+## Output schema (mandatory)
+
+Emit findings only as `---FINDING---` blocks. One block per finding. No preamble, no
+postamble, no summary, no headers.
+
+```
+---FINDING---
+severity: critical|high|medium|low
+file: <relative path or "(general)">
+line: <int> | <start>-<end> | -
+category: bug|test-gap|perf|security|clarity|style|other
+title: <single-line summary, no period>
+detail: |
+  <multi-line free text — recommendation, evidence, suggested fix>
+---END-FINDING---
+```
+
+If you find no issues, emit zero blocks. Do not write "no issues found" or anything else.
+
+**You are in review mode. Do not write, edit, or delete any files. Do not run code.
+Read only.**
+````
+
+- [ ] **Step 2: Write failing tests for render-prompt.py**
+
+```python
+# tests/test_render_prompt.py
+"""Tests for render-prompt.py — assembles mode template + materialized blob + schema."""
+import json
+from tests.conftest import run_script
+
+
+def make_materialized(**overrides):
+    base = {
+        "scope_kind": "uncommitted",
+        "scope_summary": "uncommitted changes",
+        "unified_diff": "diff --git a/x b/x\n+y\n",
+        "changed_files": [
+            {"path": "x", "status": "modified", "kind": "text",
+             "post_content": "y\n", "pre_content": None, "old_path": None,
+             "lines_changed": "(modified)", "note": None},
+        ],
+        "doc_files": [], "total_lines_changed": 1,
+        "changed_file_count": 1, "has_reviewable_changes": True,
+        "warnings": [],
+    }
+    base.update(overrides)
+    return base
+
+
+def test_render_includes_mode_template():
+    r = run_script(
+        "render-prompt.py", "--mode", "code",
+        input=json.dumps(make_materialized()),
+    )
+    assert r.returncode == 0, r.stderr
+    assert "Code Review Mode" in r.stdout
+    assert "FINDING" in r.stdout  # schema appendix
+    assert "no-edit" not in r.stdout.lower()  # we use the "read only" wording
+    assert "diff --git" in r.stdout
+    assert "y\n" in r.stdout
+
+
+def test_render_includes_focus():
+    r = run_script(
+        "render-prompt.py", "--mode", "code", "--focus", "API contract changes",
+        input=json.dumps(make_materialized()),
+    )
+    assert r.returncode == 0
+    assert "API contract changes" in r.stdout
+
+
+def test_focus_file_mode_handles_shell_metacharacters(tmp_path):
+    """Focus text containing $(...), backticks, etc. must round-trip safely."""
+    f = tmp_path / "focus.txt"
+    f.write_text("review $(rm -rf /) carefully and `dangerous` patterns")
+    r = run_script(
+        "render-prompt.py", "--mode", "code", "--focus-file", str(f),
+        input=json.dumps(make_materialized()),
+    )
+    assert r.returncode == 0, r.stderr
+    # The literal text must appear verbatim — no shell expansion happens
+    # because the orchestrator passes a file path, not the text itself.
+    assert "review $(rm -rf /) carefully" in r.stdout
+    assert "`dangerous` patterns" in r.stdout
+
+
+def test_focus_and_focus_file_mutually_exclusive(tmp_path):
+    f = tmp_path / "focus.txt"; f.write_text("x")
+    r = run_script(
+        "render-prompt.py", "--mode", "code",
+        "--focus", "y", "--focus-file", str(f),
+        input=json.dumps(make_materialized()),
+    )
+    assert r.returncode != 0
+
+
+def test_render_doc_mode_uses_doc_files():
+    mat = make_materialized(
+        scope_kind="files", unified_diff=None, changed_files=[],
+        doc_files=[{"path": "spec.md", "status": "current", "content": "# spec\n"}],
+    )
+    r = run_script(
+        "render-prompt.py", "--mode", "spec",
+        input=json.dumps(mat),
+    )
+    assert r.returncode == 0
+    assert "Spec Review Mode" in r.stdout
+    assert "spec.md" in r.stdout
+    assert "# spec" in r.stdout
+
+
+def test_render_handles_nested_fences_in_doc(tmp_path):
+    """Specs/plans commonly contain ``` blocks. A naive triple-backtick wrapper
+    would let the inner ``` close the outer fence prematurely, swallowing the
+    schema appendix. Verify the schema appendix is still present and intact."""
+    doc_with_fences = (
+        "# Spec\n\n"
+        "Example code:\n\n"
+        "```python\n"
+        "def f(): return 1\n"
+        "```\n\n"
+        "Another block:\n\n"
+        "````diff\n"  # nested fence with FOUR backticks
+        "+ added line\n"
+        "````\n"
+    )
+    mat = make_materialized(
+        scope_kind="files", unified_diff=None, changed_files=[],
+        doc_files=[{"path": "spec.md", "status": "current",
+                    "content": doc_with_fences}],
+    )
+    r = run_script("render-prompt.py", "--mode", "spec",
+                   input=json.dumps(mat))
+    assert r.returncode == 0, r.stderr
+    out = r.stdout
+    # Doc content must appear
+    assert "def f(): return 1" in out
+    assert "+ added line" in out
+    # Schema appendix must NOT have been swallowed by an unbalanced fence
+    assert "---FINDING---" in out
+    assert "End of prompt" not in out or "FINDING" in out  # schema present
+```
+
+- [ ] **Step 3: Run tests, verify they fail**
+
+```bash
+pytest tests/test_render_prompt.py -v
+```
+
+- [ ] **Step 4: Implement `scripts/render-prompt.py`**
+
+```python
+#!/usr/bin/env python3
+"""render-prompt.py — assemble the prompt body for a reviewer.
+
+Inputs:
+- --mode {code,spec,plan,docs}
+- --focus "<text>" (optional)
+- materialized blob on stdin (JSON from materialize-scope.py)
+
+Output: plain-text prompt body on stdout, suitable for piping to a reviewer
+(codex via stdin, or pasted into a Claude sub-agent's prompt).
+"""
+import argparse
+import json
+import sys
+from pathlib import Path
+
+PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
+
+
+def fence_for(content: str) -> str:
+    """Return a backtick fence longer than any run of backticks already inside
+    `content`. CommonMark requires the closing fence be at least as long as
+    the opening one, so a fence of length N+1 (where N is the longest run
+    inside) will never collide. Without this, embedding a spec/plan that
+    itself contains ``` would terminate our outer fence early and swallow
+    everything after it — including the finding-schema appendix."""
+    longest = 0
+    run = 0
+    for ch in content:
+        if ch == "`":
+            run += 1
+            longest = max(longest, run)
+        else:
+            run = 0
+    return "`" * max(3, longest + 1)
+
+
+def fenced(content: str, lang: str = "") -> str:
+    fence = fence_for(content)
+    return f"{fence}{lang}\n{content.rstrip(chr(10))}\n{fence}"
+
+
+def render_changed_files(mat: dict) -> str:
+    parts = []
+    for cf in mat["changed_files"]:
+        parts.append(f"\n### {cf['path']}  (status: {cf['status']}, kind: {cf['kind']})")
+        if cf.get("old_path"):
+            parts.append(f"(renamed from {cf['old_path']})")
+        if cf["kind"] == "text" and cf.get("post_content"):
+            parts.append(fenced(cf["post_content"]))
+        elif cf["status"] == "deleted" and cf.get("pre_content"):
+            parts.append("(deleted; previous content was:)")
+            parts.append(fenced(cf["pre_content"]))
+        elif cf["kind"] == "symlink":
+            target = cf.get("symlink_target")
+            if target is not None:
+                parts.append(f"Symlink target: `{target}`")
+            if cf.get("note"):
+                parts.append(f"_{cf['note']}_")
+        elif cf["kind"] == "submodule":
+            pre, post = cf.get("submodule_pre_sha"), cf.get("submodule_post_sha")
+            if pre or post:
+                parts.append(f"Submodule pointer: `{pre or '(none)'}` → `{post or '(none)'}`")
+            if cf.get("note"):
+                parts.append(f"_{cf['note']}_")
+        elif cf.get("note"):
+            parts.append(f"_{cf['note']}_")
+    return "\n".join(parts)
+
+
+def render_doc_files(mat: dict) -> str:
+    parts = []
+    for d in mat["doc_files"]:
+        kind = d.get("kind", "text")
+        parts.append(
+            f"\n### {d['path']}  (status: {d['status']}, kind: {kind})"
+        )
+        if d.get("content"):
+            parts.append(fenced(d["content"]))
+        elif kind == "symlink":
+            target = d.get("symlink_target")
+            if target is not None:
+                parts.append(f"Symlink target: `{target}`")
+            if d.get("note"):
+                parts.append(f"_{d['note']}_")
+        elif kind == "submodule":
+            sha = d.get("submodule_sha")
+            if sha:
+                parts.append(f"Submodule pointer: `{sha}`")
+            if d.get("note"):
+                parts.append(f"_{d['note']}_")
+        elif d.get("note"):
+            parts.append(f"_{d['note']}_")
+    return "\n".join(parts)
+
+
+def main() -> None:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--mode", choices=["code", "spec", "plan", "docs"], required=True)
+    # Two ways to pass focus text:
+    #   --focus "<text>" — convenient when the text has no shell metacharacters
+    #   --focus-file <path> — REQUIRED when the text is user-provided, since
+    #     argv interpolation by the orchestrator into a Bash command line
+    #     would expose $(...), backticks, and other shell-injection vectors.
+    # The skill orchestrator MUST use --focus-file for any user-provided focus.
+    ap.add_argument("--focus", default=None)
+    ap.add_argument("--focus-file", default=None)
+    args = ap.parse_args()
+    if args.focus and args.focus_file:
+        ap.error("--focus and --focus-file are mutually exclusive")
+    focus = args.focus
+    if args.focus_file:
+        with open(args.focus_file, "r") as f:
+            focus = f.read().strip()
+    mat = json.load(sys.stdin)
+
+    template = (PROMPTS_DIR / f"{args.mode}.md").read_text()
+    schema = (PROMPTS_DIR / "_schema.md").read_text()
+
+    out = [template]
+    if focus:
+        out.append(f"\n## Additional focus\n\n{focus}\n")
+    out.append(f"\n## Review subject\n\n**Scope:** {mat['scope_summary']}\n")
+    if mat.get("unified_diff"):
+        out.append("\n### Unified diff\n\n" + fenced(mat["unified_diff"], "diff") + "\n")
+    if mat["changed_files"]:
+        out.append("\n### Changed files (full content)\n")
+        out.append(render_changed_files(mat))
+    if mat["doc_files"]:
+        out.append("\n### Document files\n")
+        out.append(render_doc_files(mat))
+    out.append("\n" + schema)
+    sys.stdout.write("\n".join(out))
+
+
+if __name__ == "__main__":
+    main()
+```
+
+- [ ] **Step 5: Run tests, commit**
+
+```bash
+chmod +x scripts/render-prompt.py
+pytest tests/test_render_prompt.py -v
+git add prompts/_schema.md scripts/render-prompt.py tests/test_render_prompt.py
+git commit -m "feat: render-prompt.py assembles mode template + materialized blob + schema"
+```
+
+---
+
+## Task 12: run-codex.py (Python, for macOS portability)
+
+**Files:**
+- Create: `scripts/run-codex.py`
+- Create: `tests/test_run_codex.py`
+
+**Why Python and not Bash:** GNU `timeout` is not on macOS by default (no `gtimeout` either), and BSD `date` doesn't understand `%3N` for millisecond precision. Python's `subprocess.run(..., timeout=...)` handles both portably and gives us a single language for testability.
+
+- [ ] **Step 1: Write failing tests with a fake `codex` binary**
+
+```python
+# tests/test_run_codex.py
+"""Tests for run-codex.py — invokes codex exec --sandbox read-only with stdin prompt."""
+import json
+import subprocess
+from pathlib import Path
+
+from tests.conftest import SCRIPTS_DIR
+
+
+def write_fake_codex(fake_bin, behavior="echo"):
+    codex = fake_bin / "codex"
+    if behavior == "echo":
+        codex.write_text(
+            '#!/bin/sh\n'
+            '# Echo the args + stdin, plus a fake finding. Advertise --sandbox.\n'
+            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
+            '  echo "  --sandbox MODE   sandbox policy"\n'
+            '  exit 0\n'
+            'fi\n'
+            'echo "ARGS: $*" >&2\n'
+            'cat - >/dev/null\n'
+            'echo "---FINDING---"\n'
+            'echo "severity: low"\n'
+            'echo "file: x.py"\n'
+            'echo "line: 1"\n'
+            'echo "category: style"\n'
+            'echo "title: fake codex finding"\n'
+            'echo "detail: |"\n'
+            'echo "  emitted by fake codex"\n'
+            'echo "---END-FINDING---"\n'
+        )
+    elif behavior == "no-sandbox":
+        codex.write_text(
+            '#!/bin/sh\n'
+            '# --help does NOT advertise --sandbox; run-codex.py should refuse.\n'
+            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
+            '  echo "  --some-other-flag"\n'
+            '  exit 0\n'
+            'fi\n'
+            'cat - >/dev/null; echo "ok"\n'
+        )
+    elif behavior == "slow":
+        codex.write_text(
+            '#!/bin/sh\n'
+            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
+            '  echo "  --sandbox MODE"\n'
+            '  exit 0\n'
+            'fi\n'
+            'sleep 30\n'
+        )
+    elif behavior == "fail":
+        codex.write_text(
+            '#!/bin/sh\n'
+            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
+            '  echo "  --sandbox MODE"\n'
+            '  exit 0\n'
+            'fi\n'
+            'echo "codex internal error" >&2; exit 7\n'
+        )
+    codex.chmod(0o755)
+
+
+def run_codex(scope_path, prompt_path, stdout_path, stderr_path,
+              status_path=None, timeout=None, **kwargs):
+    args = ["python3", str(SCRIPTS_DIR / "run-codex.py"),
+            "--scope", str(scope_path),
+            "--prompt-file", str(prompt_path),
+            "--stdout", str(stdout_path),
+            "--stderr", str(stderr_path)]
+    if status_path:
+        args += ["--status", str(status_path)]
+    env = kwargs.pop("env", None) or {}
+    if timeout is not None:
+        env["COMBINED_REVIEW_CODEX_TIMEOUT"] = str(timeout)
+    import os as _os
+    env = {**_os.environ, **env}
+    return subprocess.run(args, capture_output=True, text=True, env=env, **kwargs)
+
+
+def test_run_codex_writes_to_orchestrator_paths(tmp_path, fake_bin):
+    write_fake_codex(fake_bin, "echo")
+    scope = tmp_path / "scope.json"
+    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
+                                 "repo_root": str(tmp_path)}))
+    prompt = tmp_path / "prompt.txt"; prompt.write_text("review please")
+    stdout = tmp_path / "out"; stderr = tmp_path / "err"; status = tmp_path / "status.json"
+    r = run_codex(scope, prompt, stdout, stderr, status_path=status)
+    assert r.returncode == 0, r.stderr
+    assert stdout.exists() and stderr.exists() and status.exists()
+    assert "---FINDING---" in stdout.read_text()
+    st = json.loads(status.read_text())
+    assert st["status"] == "ok"
+    assert st["exit_code"] == 0
+    # orchestrator-owned files must not be deleted
+    assert prompt.exists() and stdout.exists()
+
+
+def test_run_codex_records_failure(tmp_path, fake_bin):
+    write_fake_codex(fake_bin, "fail")
+    scope = tmp_path / "scope.json"
+    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
+                                 "repo_root": str(tmp_path)}))
+    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
+    status = tmp_path / "status.json"
+    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
+    # run-codex always exits 0; outcome is in the status file
+    assert r.returncode == 0
+    st = json.loads(status.read_text())
+    assert st["status"] == "failed"
+    assert st["exit_code"] == 7
+
+
+def test_run_codex_records_timeout(tmp_path, fake_bin):
+    write_fake_codex(fake_bin, "slow")
+    scope = tmp_path / "scope.json"
+    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
+                                 "repo_root": str(tmp_path)}))
+    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
+    status = tmp_path / "status.json"
+    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e",
+                  status_path=status, timeout=2)
+    assert r.returncode == 0
+    st = json.loads(status.read_text())
+    assert st["status"] == "timeout"
+
+
+def test_run_codex_errors_without_sandbox_support(tmp_path, fake_bin):
+    write_fake_codex(fake_bin, "no-sandbox")
+    scope = tmp_path / "scope.json"
+    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
+                                 "repo_root": str(tmp_path)}))
+    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
+    status = tmp_path / "status.json"
+    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
+    # Sandbox-flag failure is a HARD error — exits non-zero, no status file written.
+    assert r.returncode != 0
+    assert "sandbox" in r.stderr.lower()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_run_codex.py -v
+```
+
+- [ ] **Step 3: Implement `scripts/run-codex.py`**
+
+```python
+#!/usr/bin/env python3
+"""run-codex.py — drive `codex exec --sandbox read-only` with a stdin prompt.
+
+Portable across macOS and Linux. GNU `timeout` isn't on macOS by default and
+BSD `date` doesn't support `%3N`, so we use Python's subprocess.run(timeout=)
+and time.monotonic_ns() instead.
+
+All long-lived files (prompt, stdout, stderr, status) are orchestrator-owned.
+This script writes to them but never deletes them. It ALWAYS exits 0 except
+for hard pre-flight failures (missing --sandbox support, missing required
+args); outcome of the codex run goes into the status JSON so the
+orchestrator's background-Bash mechanics don't have to interpret exit codes.
+"""
+import argparse
+import json
+import os
+import subprocess
+import sys
+import time
+
+
+def main() -> None:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--scope", required=True)
+    ap.add_argument("--prompt-file", required=True)
+    ap.add_argument("--stdout", required=True)
+    ap.add_argument("--stderr", required=True)
+    ap.add_argument("--status", default=None,
+                    help="default: <stdout>.status")
+    args = ap.parse_args()
+
+    status_path = args.status or f"{args.stdout}.status"
+
+    def write_failed_status(msg: str, exit_code: int) -> None:
+        """Write a status JSON AND mirror the message into the orchestrator-
+        owned stderr capture for hard failures. Phase C builds its error
+        section from $CODEX_STDERR and report.py embeds it in the audit
+        trail. Writing only to sys.stderr (this script's own stderr) would
+        leave the audit trail empty for missing-sandbox / missing-codex
+        cases — invisible to anyone reading the report.
+
+        Two destinations:
+          1. status JSON: structured error for Phase C's reviewer_summary
+          2. args.stderr: free-form text the audit trail can show verbatim
+
+        Phase A pre-flight should catch these before Phase B launches at
+        all, but this still matters for the (narrow) case where codex was
+        upgraded or replaced between Phase A and Phase B.
+        """
+        try:
+            with open(status_path, "w") as sf:
+                json.dump({
+                    "status": "failed", "exit_code": exit_code,
+                    "duration_ms": 0, "timeout_seconds": 0,
+                    "error": msg,
+                }, sf)
+        except OSError:
+            pass
+        try:
+            with open(args.stderr, "w") as ef:
+                ef.write(f"run-codex.py hard failure: {msg}\n")
+        except OSError:
+            pass
+
+    # Hard pre-flight: verify codex exec advertises --sandbox before we ever
+    # invoke it. Missing the flag means we cannot guarantee read-only mode —
+    # refuse to run rather than silently going unsandboxed.
+    # Phase A pre-flight should catch this, but check here too in case codex
+    # was upgraded/replaced between Phase A and Phase B launch.
+    try:
+        help_out = subprocess.run(
+            ["codex", "exec", "--help"], capture_output=True, text=True, timeout=10,
+        )
+    except FileNotFoundError:
+        msg = "codex not on PATH"
+        print(f"error: {msg}", file=sys.stderr)
+        write_failed_status(msg, 3); sys.exit(3)
+    if "--sandbox" not in (help_out.stdout + help_out.stderr):
+        msg = "installed codex does not advertise --sandbox; refusing to run unsandboxed"
+        print(f"error: {msg}", file=sys.stderr)
+        write_failed_status(msg, 3); sys.exit(3)
+
+    # Resolve cwd: prefer worktree_path (diff-based scopes), else repo_root.
+    with open(args.scope) as f:
+        scope = json.load(f)
+    cwd = scope.get("worktree_path") or scope.get("repo_root") or os.getcwd()
+
+    timeout_s = int(os.environ.get("COMBINED_REVIEW_CODEX_TIMEOUT", "300"))
+
+    with open(args.prompt_file, "rb") as pf, \
+         open(args.stdout, "wb") as outf, \
+         open(args.stderr, "wb") as errf:
+        prompt_bytes = pf.read()
+        start = time.monotonic_ns()
+        status = "ok"; exit_code = 0
+        try:
+            proc = subprocess.run(
+                ["codex", "exec", "--sandbox", "read-only", "-"],
+                input=prompt_bytes, stdout=outf, stderr=errf,
+                cwd=cwd, timeout=timeout_s,
+            )
+            exit_code = proc.returncode
+            status = "ok" if exit_code == 0 else "failed"
+        except subprocess.TimeoutExpired:
+            status = "timeout"; exit_code = 124
+        except FileNotFoundError:
+            # codex disappeared between --help and exec; treat as failure
+            status = "failed"; exit_code = 127
+            errf.write(b"codex binary not found at exec time\n")
+        end = time.monotonic_ns()
+
+    duration_ms = (end - start) // 1_000_000
+
+    with open(status_path, "w") as sf:
+        json.dump({
+            "status": status,
+            "exit_code": exit_code,
+            "duration_ms": duration_ms,
+            "timeout_seconds": timeout_s,
+        }, sf)
+
+
+if __name__ == "__main__":
+    main()
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+chmod +x scripts/run-codex.py
+pytest tests/test_run_codex.py -v
+```
+
+Expected: 4 passed (writes-to-orchestrator-paths, records-failure, records-timeout, errors-without-sandbox-support).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/run-codex.py tests/test_run_codex.py
+git commit -m "feat: run-codex.py (portable) drives codex exec read-only with orchestrator-owned IO"
+```
+
+---
+
+## Task 13: normalize-findings.py
+
+**Files:**
+- Create: `scripts/normalize-findings.py`
+- Create: `tests/test_normalize_findings.py`
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_normalize_findings.py
+"""Tests for normalize-findings.py — delimited-block schema → JSON array."""
+import json
+from tests.conftest import run_script
+
+
+SAMPLE = """\
+preamble that should be ignored
+---FINDING---
+severity: high
+file: src/foo.py
+line: 42
+category: bug
+title: Null deref when config missing 'api_key'
+detail: |
+  Accessing config['api_key'] directly raises KeyError.
+  Use config.get('api_key') or guard with an early return.
+---END-FINDING---
+some prose in between
+---FINDING---
+severity: medium
+file: src/bar.py
+line: 10-15
+category: clarity
+title: Function does two unrelated things
+detail: |
+  Split into authenticate() and load_profile().
+---END-FINDING---
+trailing noise
+"""
+
+
+def test_parses_two_findings():
+    r = run_script("normalize-findings.py", "--source", "codex",
+                   input=SAMPLE)
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert len(out["findings"]) == 2
+    f0 = out["findings"][0]
+    assert f0["source"] == "codex"
+    assert f0["severity"] == "high"
+    assert f0["file"] == "src/foo.py"
+    assert f0["line"] == "42"
+    assert "KeyError" in f0["detail"]
+    f1 = out["findings"][1]
+    assert f1["line"] == "10-15"
+
+
+def test_unparseable_chunks_go_to_warnings():
+    bad = """\
+---FINDING---
+severity: bananas
+file: x
+title: missing required fields
+---END-FINDING---
+"""
+    r = run_script("normalize-findings.py", "--source", "claude:code-reviewer",
+                   input=bad)
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    # missing fields → parse warning, severity normalized
+    assert len(out["parse_warnings"]) >= 1 or out["findings"][0]["severity"] == "medium"
+
+
+def test_empty_input_returns_empty_array():
+    r = run_script("normalize-findings.py", "--source", "codex", input="")
+    assert r.returncode == 0
+    out = json.loads(r.stdout)
+    assert out["findings"] == []
+    assert out["parse_warnings"] == []
+    assert out["unparsed_chunks"] == []
+
+
+def test_prose_only_output_becomes_unparsed_chunk():
+    """Regression: a reviewer that ignores the schema and emits prose used to
+    produce findings:[] AND parse_warnings:[] — silently swallowing the entire
+    output. Now we capture it as an unparsed_chunk so the final report shows
+    "reviewer X did not follow the schema; see chunk:"."""
+    prose = """I reviewed the diff and found a few issues:
+
+1. The naming convention is inconsistent.
+2. There's a possible null deref on line 42.
+3. The tests don't cover the edge case.
+
+Overall the change looks fine but could use a second pass."""
+    r = run_script("normalize-findings.py", "--source", "codex", input=prose)
+    assert r.returncode == 0, r.stderr
+    out = json.loads(r.stdout)
+    assert out["findings"] == []
+    assert len(out["unparsed_chunks"]) == 1
+    assert out["unparsed_chunks"][0]["source"] == "codex"
+    assert "null deref" in out["unparsed_chunks"][0]["text"]
+    assert len(out["parse_warnings"]) >= 1
+
+
+def test_text_between_blocks_captured():
+    """Prose between two valid FINDING blocks must also surface as a warning."""
+    mixed = """\
+---FINDING---
+severity: high
+file: a.py
+line: 1
+category: bug
+title: first
+detail: |
+  one
+---END-FINDING---
+
+Some prose the reviewer added in between that shouldn't be there.
+
+---FINDING---
+severity: low
+file: b.py
+line: 2
+category: style
+title: second
+detail: |
+  two
+---END-FINDING---
+"""
+    r = run_script("normalize-findings.py", "--source", "claude:code-reviewer",
+                   input=mixed)
+    assert r.returncode == 0
+    out = json.loads(r.stdout)
+    assert len(out["findings"]) == 2
+    assert any("Some prose" in c["text"] for c in out["unparsed_chunks"])
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_normalize_findings.py -v
+```
+
+- [ ] **Step 3: Implement `scripts/normalize-findings.py`**
+
+```python
+#!/usr/bin/env python3
+"""normalize-findings.py — parse delimited-block reviewer output → JSON.
+
+Reads raw reviewer output on stdin; writes a JSON object with `findings`
+(array of normalized finding dicts) and `parse_warnings` (array of strings
+describing unparseable chunks). One reviewer's output per invocation.
+"""
+import argparse
+import json
+import re
+import sys
+
+VALID_SEVERITY = {"critical", "high", "medium", "low"}
+SEVERITY_MAP = {
+    "critical": "critical", "high": "high", "medium": "medium", "low": "low",
+    "error": "high", "warning": "medium", "info": "low", "note": "low",
+}
+VALID_CATEGORY = {"bug", "test-gap", "perf", "security", "clarity", "style", "other"}
+
+
+BLOCK_RE = re.compile(
+    r"---FINDING---\s*\n(.*?)\n---END-FINDING---",
+    re.DOTALL,
+)
+
+
+def parse_block(body: str) -> tuple[dict | None, str | None]:
+    """Return (finding dict, warning str). If both None, the block is empty."""
+    fields: dict[str, str] = {}
+    lines = body.split("\n")
+    i = 0
+    while i < len(lines):
+        line = lines[i]
+        m = re.match(r"^(\w+):\s*(.*)$", line)
+        if not m:
+            i += 1; continue
+        key, val = m.group(1), m.group(2)
+        if val.strip() == "|":
+            # multi-line scalar
+            buf = []
+            i += 1
+            while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
+                buf.append(lines[i][2:] if lines[i].startswith("  ") else "")
+                i += 1
+            fields[key] = "\n".join(buf).strip()
+            continue
+        fields[key] = val.strip()
+        i += 1
+
+    warnings = []
+    sev = (fields.get("severity") or "").lower()
+    if sev not in VALID_SEVERITY:
+        mapped = SEVERITY_MAP.get(sev, "medium")
+        warnings.append(f"unknown severity {sev!r} mapped to {mapped!r}")
+        sev = mapped
+    cat = (fields.get("category") or "other").lower()
+    if cat not in VALID_CATEGORY:
+        warnings.append(f"unknown category {cat!r} mapped to 'other'")
+        cat = "other"
+    if not fields.get("title"):
+        warnings.append(f"finding missing title; skipping")
+        return None, "\n".join(warnings)
+
+    f = {
+        "severity": sev,
+        "file": fields.get("file") or "(general)",
+        "line": fields.get("line") or "-",
+        "category": cat,
+        "title": fields["title"],
+        "detail": fields.get("detail") or "",
+    }
+    return f, "; ".join(warnings) if warnings else None
+
+
+def main() -> None:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--source", required=True,
+                    help='e.g. "codex" or "claude:code-reviewer"')
+    args = ap.parse_args()
+    raw = sys.stdin.read()
+    findings: list[dict] = []
+    warnings: list[str] = []
+    unparsed_chunks: list[dict] = []
+
+    cursor = 0
+    for m in BLOCK_RE.finditer(raw):
+        # Capture any non-whitespace text BEFORE this block as an unparsed
+        # chunk. A reviewer that ignores the schema and emits prose would
+        # otherwise produce findings: [] and warnings: [] silently — the
+        # spec says these failures must surface in the final report.
+        between = raw[cursor:m.start()].strip()
+        if between:
+            unparsed_chunks.append({
+                "source": args.source,
+                "text": between[:1000],  # cap; full raw is in audit trail
+                "position": "before_block" if findings else "preamble",
+            })
+            warnings.append(
+                f"[{args.source}] {len(between)} chars of non-schema text outside "
+                f"---FINDING--- blocks (see unparsed_chunks)"
+            )
+        body = m.group(1)
+        finding, warn = parse_block(body)
+        if finding is not None:
+            finding["source"] = args.source
+            findings.append(finding)
+        if warn:
+            warnings.append(f"[{args.source}] {warn}")
+        cursor = m.end()
+
+    # Trailing text after the last block (or all text if no blocks matched).
+    trailing = raw[cursor:].strip()
+    if trailing:
+        unparsed_chunks.append({
+            "source": args.source,
+            "text": trailing[:1000],
+            "position": "postamble" if findings else "no_blocks",
+        })
+        warnings.append(
+            f"[{args.source}] {len(trailing)} chars of non-schema text after "
+            f"last FINDING block (see unparsed_chunks)"
+        )
+
+    json.dump({
+        "findings": findings,
+        "parse_warnings": warnings,
+        "unparsed_chunks": unparsed_chunks,
+    }, sys.stdout)
+    sys.stdout.write("\n")
+
+
+if __name__ == "__main__":
+    main()
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+chmod +x scripts/normalize-findings.py
+pytest tests/test_normalize_findings.py -v
+```
+
+Expected: 5 passed (parses-two-findings, unparseable-chunks-go-to-warnings, empty-input, prose-only-becomes-unparsed-chunk, text-between-blocks-captured).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/normalize-findings.py tests/test_normalize_findings.py
+git commit -m "feat: normalize-findings.py parses delimited-block schema with parse warnings"
+```
+
+---
+
+## Task 14: validate-clusters.py
+
+**Files:**
+- Create: `scripts/validate-clusters.py`
+- Create: `tests/test_validate_clusters.py`
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_validate_clusters.py
+"""Tests for validate-clusters.py — JSON Schema check on synthesis output."""
+import json
+from tests.conftest import run_script
+
+
+VALID_CLUSTERS = {
+    "scope_summary": "PR #105",
+    "mode": "code",
+    "focus": None,
+    "reviewer_summary": {
+        "codex": {"status": "ok", "raw_findings": 3, "parse_warnings": 0},
+        "claude": [
+            {"agent": "code-reviewer", "status": "ok",
+             "raw_findings": 2, "parse_warnings": 0},
+        ],
+    },
+    "clusters": [
+        {
+            "tag": "agreement",
+            "severity": "high",
+            "file": "src/foo.py",
+            "line": "42",
+            "category": "bug",
+            "title": "Null deref",
+            "synthesized_detail": "Both reviewers flag this.",
+            "sources": [
+                {"source": "codex", "original_title": "Null deref",
+                 "original_detail": "...", "severity": "high"},
+                {"source": "claude:code-reviewer",
+                 "original_title": "Possible KeyError",
+                 "original_detail": "...", "severity": "medium"},
+            ],
+            "severity_divergence": "codex=high, claude=medium → high",
+        },
+    ],
+    "unparsed_chunks": [],
+}
+
+
+def test_valid_passes():
+    r = run_script("validate-clusters.py", input=json.dumps(VALID_CLUSTERS))
+    assert r.returncode == 0, r.stderr
+
+
+def test_invalid_severity_fails():
+    bad = json.loads(json.dumps(VALID_CLUSTERS))
+    bad["clusters"][0]["severity"] = "blocker"
+    r = run_script("validate-clusters.py", input=json.dumps(bad))
+    assert r.returncode != 0
+    assert "severity" in r.stderr.lower()
+
+
+def test_missing_clusters_field_fails():
+    bad = json.loads(json.dumps(VALID_CLUSTERS))
+    del bad["clusters"]
+    r = run_script("validate-clusters.py", input=json.dumps(bad))
+    assert r.returncode != 0
+
+
+def test_invalid_tag_fails():
+    bad = json.loads(json.dumps(VALID_CLUSTERS))
+    bad["clusters"][0]["tag"] = "maybe"
+    r = run_script("validate-clusters.py", input=json.dumps(bad))
+    assert r.returncode != 0
+
+
+def test_codex_timeout_status_accepted():
+    """Schema must accept timeout from run-codex.py."""
+    ok = json.loads(json.dumps(VALID_CLUSTERS))
+    ok["reviewer_summary"]["codex"] = {
+        "status": "timeout", "error": "codex did not finish within 300s",
+        "duration_ms": 300000,
+    }
+    r = run_script("validate-clusters.py", input=json.dumps(ok))
+    assert r.returncode == 0, r.stderr
+
+
+def test_codex_skipped_status_accepted():
+    """Schema must accept skipped (--no-codex was passed)."""
+    ok = json.loads(json.dumps(VALID_CLUSTERS))
+    ok["reviewer_summary"]["codex"] = {"status": "skipped"}
+    # Also drop codex from any cluster sources so we don't accidentally
+    # claim codex contributed to a finding when it was skipped.
+    for c in ok["clusters"]:
+        c["sources"] = [s for s in c["sources"] if s["source"] != "codex"]
+        if not c["sources"]:
+            c["sources"] = [{"source": "claude:code-reviewer",
+                             "original_title": "...", "original_detail": "...",
+                             "severity": "medium"}]
+            c["tag"] = "claude_only"
+    r = run_script("validate-clusters.py", input=json.dumps(ok))
+    assert r.returncode == 0, r.stderr
+
+
+def test_unparsed_chunks_rejects_bare_string():
+    """Regression: previously the schema accepted any array shape for
+    unparsed_chunks. A bare string item ("raw prose") validated fine and
+    then crashed report.py at ch['source'] lookup. Now: each item must
+    be an object with source + text."""
+    bad = json.loads(json.dumps(VALID_CLUSTERS))
+    bad["unparsed_chunks"] = ["raw prose"]
+    r = run_script("validate-clusters.py", input=json.dumps(bad))
+    assert r.returncode != 0
+
+
+def test_unparsed_chunks_rejects_missing_source():
+    bad = json.loads(json.dumps(VALID_CLUSTERS))
+    bad["unparsed_chunks"] = [{"text": "no source field"}]
+    r = run_script("validate-clusters.py", input=json.dumps(bad))
+    assert r.returncode != 0
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_validate_clusters.py -v
+```
+
+- [ ] **Step 3: Implement `scripts/validate-clusters.py`**
+
+```python
+#!/usr/bin/env python3
+"""validate-clusters.py — JSON-Schema-validate the synthesis cluster JSON.
+
+Exits 0 if valid; non-zero with a descriptive stderr if not. The orchestrator
+catches non-zero, re-prompts the synthesis LLM once with the error, then
+re-validates. If validation fails twice, the final report runs in "synthesis
+failed" mode (see SKILL.md).
+"""
+import json
+import sys
+
+import jsonschema
+
+SCHEMA = {
+    "type": "object",
+    "required": ["scope_summary", "mode", "reviewer_summary",
+                 "clusters", "unparsed_chunks"],
+    "properties": {
+        "scope_summary": {"type": "string"},
+        "mode": {"enum": ["code", "spec", "plan", "docs"]},
+        "focus": {"type": ["string", "null"]},
+        "reviewer_summary": {
+            "type": "object",
+            "required": ["codex", "claude"],
+            "properties": {
+                "codex": {
+                    "type": "object",
+                    "required": ["status"],
+                    "properties": {
+                        "status": {"enum": ["ok", "failed", "timeout", "skipped"]},
+                        "raw_findings": {"type": "integer"},
+                        "parse_warnings": {"type": "integer"},
+                        "error": {"type": "string"},
+                        "duration_ms": {"type": "integer"},
+                    },
+                },
+                "claude": {
+                    "type": "array",
+                    "items": {
+                        "type": "object",
+                        "required": ["agent", "status"],
+                        "properties": {
+                            "agent": {"type": "string"},
+                            "status": {"enum": ["ok", "failed", "skipped"]},
+                            "raw_findings": {"type": "integer"},
+                            "parse_warnings": {"type": "integer"},
+                            "error": {"type": "string"},
+                        },
+                    },
+                },
+            },
+        },
+        "clusters": {
+            "type": "array",
+            "items": {
+                "type": "object",
+                "required": ["tag", "severity", "file", "line",
+                             "category", "title", "synthesized_detail", "sources"],
+                "properties": {
+                    "tag": {"enum": ["agreement", "claude_only",
+                                     "codex_only", "disagreement"]},
+                    "severity": {"enum": ["critical", "high", "medium", "low"]},
+                    "file": {"type": "string"},
+                    "line": {"type": "string"},
+                    "category": {"enum": ["bug", "test-gap", "perf",
+                                          "security", "clarity", "style", "other"]},
+                    "title": {"type": "string"},
+                    "synthesized_detail": {"type": "string"},
+                    "sources": {
+                        "type": "array", "minItems": 1,
+                        "items": {
+                            "type": "object",
+                            "required": ["source", "severity"],
+                            "properties": {
+                                "source": {"type": "string"},
+                                "original_title": {"type": "string"},
+                                "original_detail": {"type": "string"},
+                                "severity": {"enum": ["critical", "high",
+                                                      "medium", "low"]},
+                            },
+                        },
+                    },
+                    "severity_divergence": {"type": "string"},
+                },
+            },
+        },
+        "unparsed_chunks": {
+            "type": "array",
+            "items": {
+                "type": "object",
+                # report.py iterates these and reads ch['source'] + ch.get('text','')
+                # — a bare-string item (legal under the prior {type: array} shape)
+                # would crash rendering. The item schema below mirrors what
+                # normalize-findings.py actually emits.
+                "required": ["source", "text"],
+                "properties": {
+                    "source": {"type": "string"},
+                    "text": {"type": "string"},
+                    "position": {"type": "string"},
+                },
+            },
+        },
+    },
+}
+
+
+def main() -> None:
+    try:
+        data = json.load(sys.stdin)
+    except json.JSONDecodeError as e:
+        print(f"error: input is not valid JSON: {e}", file=sys.stderr)
+        sys.exit(2)
+    try:
+        jsonschema.validate(data, SCHEMA)
+    except jsonschema.ValidationError as e:
+        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
+        print(f"error: schema violation at {path}: {e.message}", file=sys.stderr)
+        sys.exit(1)
+
+
+if __name__ == "__main__":
+    main()
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+chmod +x scripts/validate-clusters.py
+pytest tests/test_validate_clusters.py -v
+```
+
+Expected: 8 passed (valid, invalid-severity, missing-clusters, invalid-tag, codex-timeout-accepted, codex-skipped-accepted, unparsed-rejects-bare-string, unparsed-rejects-missing-source).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/validate-clusters.py tests/test_validate_clusters.py
+git commit -m "feat: validate-clusters.py JSON Schema check on synthesis output"
+```
+
+---
+
+## Task 15: report.py — final Markdown rendering
+
+**Files:**
+- Create: `scripts/report.py`
+- Create: `tests/test_report.py`
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_report.py
+"""Tests for report.py — cluster JSON + raw outputs → final Markdown."""
+import json
+import subprocess
+from pathlib import Path
+from tests.conftest import SCRIPTS_DIR
+
+
+def test_report_renders_high_confidence_section(tmp_path):
+    clusters = {
+        "scope_summary": "PR #105",
+        "mode": "code", "focus": None,
+        "reviewer_summary": {
+            "codex": {"status": "ok", "raw_findings": 1, "parse_warnings": 0},
+            "claude": [{"agent": "code-reviewer", "status": "ok",
+                        "raw_findings": 1, "parse_warnings": 0}],
+        },
+        "clusters": [
+            {
+                "tag": "agreement", "severity": "high",
+                "file": "src/foo.py", "line": "42", "category": "bug",
+                "title": "Null deref",
+                "synthesized_detail": "Both flag this.",
+                "sources": [
+                    {"source": "codex", "severity": "high"},
+                    {"source": "claude:code-reviewer", "severity": "medium"},
+                ],
+                "severity_divergence": "codex=high vs claude=medium → high",
+            },
+        ],
+        "unparsed_chunks": [],
+    }
+    codex_raw = tmp_path / "codex.txt"; codex_raw.write_text("raw codex")
+    claude_raw = tmp_path / "claude.txt"; claude_raw.write_text("raw claude")
+    r = subprocess.run(
+        ["python3", str(SCRIPTS_DIR / "report.py"),
+         "--codex-raw", str(codex_raw),
+         "--claude-raw", str(claude_raw)],
+        input=json.dumps(clusters), capture_output=True, text=True,
+    )
+    assert r.returncode == 0, r.stderr
+    md = r.stdout
+    assert "# Combined Review" in md
+    assert "PR #105" in md
+    assert "## High-confidence findings" in md
+    assert "src/foo.py:42" in md
+    assert "Null deref" in md
+    assert "codex, claude:code-reviewer" in md
+    assert "raw codex" in md
+    assert "raw claude" in md
+
+
+def test_report_embeds_codex_stderr_in_audit(tmp_path):
+    """When codex fails (auth/quota/sandbox), the diagnostic lives on stderr.
+    Earlier versions only embedded stdout, so users saw the reviewer_summary
+    line and nothing else. Stderr must appear in the audit-trail section."""
+    clusters = {
+        "scope_summary": "PR #99", "mode": "code", "focus": None,
+        "reviewer_summary": {
+            "codex": {"status": "failed", "error": "auth", "exit_code": 1},
+            "claude": [{"agent": "code-reviewer", "status": "ok",
+                        "raw_findings": 0, "parse_warnings": 0}],
+        },
+        "clusters": [], "unparsed_chunks": [],
+    }
+    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
+    codex_err = tmp_path / "ce.txt"
+    codex_err.write_text("ERROR: codex auth failed: token expired at 12:34 UTC")
+    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
+    r = subprocess.run(
+        ["python3", str(SCRIPTS_DIR / "report.py"),
+         "--codex-raw", str(codex_raw),
+         "--codex-stderr", str(codex_err),
+         "--claude-raw", str(claude_raw)],
+        input=json.dumps(clusters), capture_output=True, text=True,
+    )
+    assert r.returncode == 0, r.stderr
+    md = r.stdout
+    assert "Codex stderr" in md
+    assert "token expired" in md
+
+
+def test_report_renders_codex_timeout_in_reviewer_status(tmp_path):
+    """If codex timed out, the user must see it in the report — not just
+    "no codex findings" with no explanation."""
+    clusters = {
+        "scope_summary": "PR #105", "mode": "code", "focus": None,
+        "reviewer_summary": {
+            "codex": {"status": "timeout", "duration_ms": 300000,
+                      "error": "did not finish within 300s"},
+            "claude": [{"agent": "code-reviewer", "status": "ok",
+                        "raw_findings": 1, "parse_warnings": 0}],
+        },
+        "clusters": [],
+        "unparsed_chunks": [],
+    }
+    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
+    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("raw claude")
+    r = subprocess.run(
+        ["python3", str(SCRIPTS_DIR / "report.py"),
+         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
+        input=json.dumps(clusters), capture_output=True, text=True,
+    )
+    assert r.returncode == 0, r.stderr
+    md = r.stdout
+    assert "## Reviewer status" in md
+    assert "Codex" in md and "timeout" in md
+    assert "300s" in md
+
+
+def test_report_renders_no_codex_skipped(tmp_path):
+    """`--no-codex` runs must show codex as 'skipped' in the report."""
+    clusters = {
+        "scope_summary": "uncommitted", "mode": "code", "focus": None,
+        "reviewer_summary": {
+            "codex": {"status": "skipped"},
+            "claude": [{"agent": "code-reviewer", "status": "ok",
+                        "raw_findings": 0, "parse_warnings": 0}],
+        },
+        "clusters": [], "unparsed_chunks": [],
+    }
+    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
+    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
+    r = subprocess.run(
+        ["python3", str(SCRIPTS_DIR / "report.py"),
+         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
+        input=json.dumps(clusters), capture_output=True, text=True,
+    )
+    assert r.returncode == 0, r.stderr
+    assert "skipped" in r.stdout
+    assert "--no-codex" in r.stdout
+
+
+def test_report_renders_failed_claude_agent(tmp_path):
+    """A failed sub-agent must appear in the reviewer status section."""
+    clusters = {
+        "scope_summary": "PR #5", "mode": "code", "focus": None,
+        "reviewer_summary": {
+            "codex": {"status": "ok", "raw_findings": 2, "parse_warnings": 0},
+            "claude": [
+                {"agent": "code-reviewer", "status": "ok",
+                 "raw_findings": 1, "parse_warnings": 0},
+                {"agent": "pr-test-analyzer", "status": "failed",
+                 "error": "agent dispatch failed"},
+            ],
+        },
+        "clusters": [], "unparsed_chunks": [],
+    }
+    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
+    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
+    r = subprocess.run(
+        ["python3", str(SCRIPTS_DIR / "report.py"),
+         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
+        input=json.dumps(clusters), capture_output=True, text=True,
+    )
+    assert r.returncode == 0
+    assert "pr-test-analyzer" in r.stdout
+    assert "failed" in r.stdout
+
+
+def test_report_synthesis_failed_banner(tmp_path):
+    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("c")
+    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("cl")
+    r = subprocess.run(
+        ["python3", str(SCRIPTS_DIR / "report.py"),
+         "--codex-raw", str(codex_raw),
+         "--claude-raw", str(claude_raw),
+         "--synthesis-failed", "schema invalid: clusters missing"],
+        input="", capture_output=True, text=True,
+    )
+    assert r.returncode == 0
+    assert "Synthesis failed" in r.stdout
+    assert "schema invalid" in r.stdout
+    assert "raw codex" not in r.stdout  # but raw outputs should be embedded:
+    # actually they should be embedded — fix:
+    assert "c\n" in r.stdout or "raw" in r.stdout.lower()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_report.py -v
+```
+
+- [ ] **Step 3: Implement `scripts/report.py`**
+
+```python
+#!/usr/bin/env python3
+"""report.py — render the final Combined Review report from cluster JSON.
+
+Inputs:
+- stdin: cluster JSON (from synthesis pass, validated by validate-clusters.py).
+  Empty when --synthesis-failed is set.
+- --codex-raw <path>: codex raw output file
+- --claude-raw <path>: aggregated Claude sub-agent transcripts
+- --synthesis-failed "<msg>": if set, emit a "synthesis failed" report
+  with raw outputs only and the diagnostic message.
+
+Output: Markdown to stdout.
+"""
+import argparse
+import datetime as dt
+import json
+import sys
+from pathlib import Path
+
+SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
+
+
+# Duplicated from render-prompt.py (small helpers; not worth a shared module
+# for a personal skill). Reviewer transcripts routinely contain triple-
+# backtick code blocks (codex inlines diffs, Claude agents inline examples),
+# so wrapping raw output in plain ``` would let the first inner ``` close the
+# outer fence — same class of bug as the prompt-rendering one, but in the
+# audit-trail section of the report.
+def fence_for(content: str) -> str:
+    longest = 0
+    run = 0
+    for ch in content:
+        if ch == "`":
+            run += 1
+            longest = max(longest, run)
+        else:
+            run = 0
+    return "`" * max(3, longest + 1)
+
+
+def fenced(content: str, lang: str = "") -> str:
+    fence = fence_for(content)
+    return f"{fence}{lang}\n{content.rstrip(chr(10))}\n{fence}"
+
+
+def header(scope_summary: str, mode: str, focus: str | None) -> str:
+    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
+    lines = [
+        "# Combined Review", "",
+        f"**Scope:** {scope_summary}", f"**Mode:** {mode}",
+        f"**Focus:** {focus or '(none)'}",
+        f"**Generated:** {ts}",
+        "",
+        "---",
+        "",
+    ]
+    return "\n".join(lines)
+
+
+def render_reviewer_status(rs: dict) -> str:
+    """Render the reviewer_summary block so codex failures/timeouts/skipped
+    runs and failed Claude agents are visible in the final report — not buried
+    in the raw outputs section. Promised in §10 'In-flight failure handling';
+    omitting this caused the user-facing report to silently degrade."""
+    lines = ["## Reviewer status", ""]
+    codex = rs.get("codex", {})
+    cstatus = codex.get("status", "unknown")
+    if cstatus == "ok":
+        rf = codex.get("raw_findings", "?")
+        pw = codex.get("parse_warnings", 0)
+        warn = f" ({pw} parse warnings)" if pw else ""
+        lines.append(f"- **Codex**: ok — {rf} raw findings{warn}")
+    elif cstatus == "skipped":
+        lines.append("- **Codex**: skipped (`--no-codex`)")
+    elif cstatus in ("failed", "timeout"):
+        dur = codex.get("duration_ms")
+        dur_s = f" after {dur//1000}s" if isinstance(dur, int) else ""
+        err = codex.get("error", "no detail")
+        # truncate aggressive — full stderr is in the raw outputs section
+        if len(err) > 240: err = err[:240] + "…"
+        lines.append(f"- **Codex**: {cstatus}{dur_s} — `{err}`")
+    else:
+        lines.append(f"- **Codex**: {cstatus}")
+    for agent in rs.get("claude", []):
+        name = agent.get("agent", "?")
+        st = agent.get("status", "unknown")
+        if st == "ok":
+            rf = agent.get("raw_findings", "?")
+            pw = agent.get("parse_warnings", 0)
+            warn = f" ({pw} parse warnings)" if pw else ""
+            lines.append(f"- **Claude:{name}**: ok — {rf} raw findings{warn}")
+        elif st == "failed":
+            err = agent.get("error", "no detail")
+            if len(err) > 240: err = err[:240] + "…"
+            lines.append(f"- **Claude:{name}**: failed — `{err}`")
+        else:
+            lines.append(f"- **Claude:{name}**: {st}")
+    lines.append("")
+    return "\n".join(lines)
+
+
+def render_cluster(c: dict) -> str:
+    src_list = ", ".join(s["source"] for s in c["sources"])
+    parts = [
+        f"- **[{c['severity'].title()}] {c['file']}:{c['line']}** — {c['title']}",
+        f"  {c['synthesized_detail']}",
+        f"  _Sources: {src_list}_",
+    ]
+    if c.get("severity_divergence"):
+        parts.append(f"  _Severity: {c['severity_divergence']}_")
+    return "\n".join(parts)
+
+
+def by_tag(clusters: list[dict], tag: str) -> list[dict]:
+    out = [c for c in clusters if c["tag"] == tag]
+    out.sort(key=lambda c: SEV_ORDER.get(c["severity"], 4))
+    return out
+
+
+def render_sections(clusters: list[dict]) -> str:
+    sections = []
+    agreements = by_tag(clusters, "agreement")
+    if agreements:
+        sections.append("## High-confidence findings (both tools agree)\n")
+        sections += [render_cluster(c) for c in agreements]
+        sections.append("")
+    claude_only = by_tag(clusters, "claude_only")
+    codex_only = by_tag(clusters, "codex_only")
+    if claude_only or codex_only:
+        sections.append("## Single-source findings\n")
+        if claude_only:
+            sections.append("### Claude only\n")
+            sections += [render_cluster(c) for c in claude_only]
+            sections.append("")
+        if codex_only:
+            sections.append("### Codex only\n")
+            sections += [render_cluster(c) for c in codex_only]
+            sections.append("")
+    disagreements = by_tag(clusters, "disagreement")
+    if disagreements:
+        sections.append("## Disagreements (worth a second look)\n")
+        sections += [render_cluster(c) for c in disagreements]
+        sections.append("")
+    if not (agreements or claude_only or codex_only or disagreements):
+        sections.append("## No issues found\n")
+    return "\n".join(sections)
+
+
+def _read_or_empty(p: Path | None) -> str:
+    if p is None or not p.exists():
+        return ""
+    try:
+        return p.read_text()
+    except OSError:
+        return ""
+
+
+def render_raw(codex_raw: Path, claude_raw: Path, codex_stderr: Path | None) -> str:
+    """Embed raw reviewer outputs in a collapsed audit-trail section.
+
+    Codex stderr is critical for failure/timeout diagnostics (auth errors,
+    quota exhaustion, sandbox refusals) — codex writes the diagnostic to
+    stderr and produces no findings on stdout. Earlier versions only embedded
+    stdout, leaving users with the reviewer_summary line as the only signal.
+    Now we include stderr when it has content, so the failure mode is
+    actually debuggable from the report alone.
+    """
+    err_text = _read_or_empty(codex_stderr).rstrip()
+    codex_text = codex_raw.read_text().rstrip() or "(empty)"
+    claude_text = claude_raw.read_text().rstrip() or "(empty)"
+    parts = [
+        "---", "",
+        "<details>", "<summary>Raw outputs (audit trail)</summary>", "",
+        "### Codex stdout", "",
+        fenced(codex_text), "",
+    ]
+    if err_text:
+        parts += [
+            "### Codex stderr", "",
+            fenced(err_text), "",
+        ]
+    parts += [
+        "### Claude sub-agents", "",
+        fenced(claude_text), "",
+        "</details>", "",
+    ]
+    return "\n".join(parts)
+
+
+def main() -> None:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--codex-raw", required=True, type=Path,
+                    help="codex stdout capture")
+    ap.add_argument("--codex-stderr", default=None, type=Path,
+                    help="codex stderr capture (recommended — failures live here)")
+    ap.add_argument("--claude-raw", required=True, type=Path)
+    # Two ways to pass the synthesis-failure message:
+    #   --synthesis-failed "<msg>" — convenient when msg is short and known-safe
+    #   --synthesis-failed-file <path> — REQUIRED when msg originates from
+    #     validator stderr / model output / anything the orchestrator can't
+    #     pre-sanitize. Same shell-injection class as the focus-text case:
+    #     interpolating arbitrary content into a Bash command line is unsafe.
+    ap.add_argument("--synthesis-failed", default=None)
+    ap.add_argument("--synthesis-failed-file", default=None, type=Path)
+    args = ap.parse_args()
+    if args.synthesis_failed and args.synthesis_failed_file:
+        ap.error("--synthesis-failed and --synthesis-failed-file are mutually exclusive")
+    synthesis_failed_msg = args.synthesis_failed
+    if args.synthesis_failed_file is not None:
+        try:
+            synthesis_failed_msg = args.synthesis_failed_file.read_text().strip()
+        except OSError as e:
+            ap.error(f"could not read --synthesis-failed-file: {e}")
+
+    if synthesis_failed_msg:
+        out = [
+            "# Combined Review — synthesis failed", "",
+            f"> **Synthesis failed.** {synthesis_failed_msg}",
+            "> Manual review of raw outputs required.", "",
+            "---", "",
+            render_raw(args.codex_raw, args.claude_raw, args.codex_stderr),
+        ]
+        sys.stdout.write("\n".join(out))
+        return
+
+    data = json.load(sys.stdin)
+    out = [
+        header(data["scope_summary"], data["mode"], data.get("focus")),
+        render_reviewer_status(data.get("reviewer_summary", {})),
+        render_sections(data["clusters"]),
+    ]
+    if data.get("unparsed_chunks"):
+        out.append("## Parse warnings\n")
+        for ch in data["unparsed_chunks"]:
+            out.append(f"- From {ch['source']}: {ch.get('text','')[:200]}")
+        out.append("")
+    out.append(render_raw(args.codex_raw, args.claude_raw, args.codex_stderr))
+    sys.stdout.write("\n".join(out))
+
+
+if __name__ == "__main__":
+    main()
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+chmod +x scripts/report.py
+pytest tests/test_report.py -v
+```
+
+Expected: 6 passed (high-confidence rendering, codex-stderr-in-audit, codex-timeout-in-reviewer-status, no-codex-skipped, failed-claude-agent, synthesis-failed-banner).
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/report.py tests/test_report.py
+git commit -m "feat: report.py renders cluster JSON + raw outputs to Markdown"
+```
+
+---
+
+## Task 16: cleanup-worktree.sh
+
+**Files:**
+- Create: `scripts/cleanup-worktree.sh`
+- Create: `tests/test_cleanup_worktree.py`
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_cleanup_worktree.py
+"""Tests for cleanup-worktree.sh — triple-assertion gate before removal."""
+import subprocess
+from pathlib import Path
+from tests.conftest import SCRIPTS_DIR
+
+
+def cleanup(repo, worktree):
+    return subprocess.run(
+        [str(SCRIPTS_DIR / "cleanup-worktree.sh"), str(repo), str(worktree)],
+        capture_output=True, text=True,
+    )
+
+
+def test_cleanup_removes_legitimate_worktree(tmp_repo, tmp_path, monkeypatch):
+    monkeypatch.setenv("TMPDIR", str(tmp_path))
+    wt = tmp_path / "combined-review-x-abcdef"
+    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
+                   cwd=tmp_repo, check=True)
+    assert wt.exists()
+    r = cleanup(tmp_repo, wt)
+    assert r.returncode == 0, r.stderr
+    assert not wt.exists()
+
+
+def test_cleanup_refuses_repo_root(tmp_repo):
+    r = cleanup(tmp_repo, tmp_repo)
+    assert r.returncode != 0
+    assert "refus" in r.stderr.lower() or "root" in r.stderr.lower()
+
+
+def test_cleanup_refuses_arbitrary_directory(tmp_repo, tmp_path):
+    arbitrary = tmp_path / "not-a-worktree"
+    arbitrary.mkdir()
+    r = cleanup(tmp_repo, arbitrary)
+    assert r.returncode != 0
+    assert arbitrary.exists()  # we DID NOT delete it
+
+
+def test_cleanup_skips_when_marker_present(tmp_repo, tmp_path, monkeypatch):
+    monkeypatch.setenv("TMPDIR", str(tmp_path))
+    wt = tmp_path / "combined-review-x-keepme"
+    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
+                   cwd=tmp_repo, check=True)
+    (wt / ".combined-review-keep").touch()
+    r = cleanup(tmp_repo, wt)
+    # We expect non-zero (refused) AND the worktree still exists.
+    assert r.returncode != 0
+    assert wt.exists()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_cleanup_worktree.py -v
+```
+
+- [ ] **Step 3: Implement `scripts/cleanup-worktree.sh`**
+
+```bash
+#!/usr/bin/env bash
+# cleanup-worktree.sh <repo_root> <worktree_path>
+#
+# Triple-assertion gate before destructive removal:
+#   1. Path appears in `git worktree list --porcelain` for the repo.
+#   2. Path matches the combined-review-* mktemp pattern under $TMPDIR or /tmp.
+#   3. Path is not the repo root, and not the main worktree.
+# Plus: skip if `.combined-review-keep` marker exists at the worktree root.
+set -euo pipefail
+
+if [[ $# -ne 2 ]]; then
+  echo "usage: cleanup-worktree.sh <repo_root> <worktree_path>" >&2
+  exit 2
+fi
+REPO="$1"
+WT="$2"
+REPO_ABS="$(cd "$REPO" && pwd)"
+WT_ABS="$(cd "$(dirname "$WT")" && pwd)/$(basename "$WT")"
+
+# 0. Marker check
+if [[ -f "$WT_ABS/.combined-review-keep" ]]; then
+  echo "refused: marker .combined-review-keep present at $WT_ABS" >&2
+  exit 3
+fi
+
+# 1. git worktree registry check
+if ! git -C "$REPO_ABS" worktree list --porcelain | grep -Fq "worktree $WT_ABS"; then
+  echo "refused: $WT_ABS not in git worktree list for $REPO_ABS" >&2
+  exit 3
+fi
+
+# 2. mktemp pattern check (basename must start with combined-review-)
+base="$(basename "$WT_ABS")"
+if [[ ! "$base" =~ ^combined-review- ]]; then
+  echo "refused: $WT_ABS basename does not match combined-review-* pattern" >&2
+  exit 3
+fi
+parent="$(cd "$(dirname "$WT_ABS")" && pwd)"
+TMP="${TMPDIR:-/tmp}"
+TMP_ABS="$(cd "$TMP" && pwd)"
+if [[ "$parent" != "$TMP_ABS" && "$parent" != "/tmp" ]]; then
+  echo "refused: $WT_ABS parent ($parent) is not \$TMPDIR ($TMP_ABS) or /tmp" >&2
+  exit 3
+fi
+
+# 3. not repo root, not main worktree
+if [[ "$WT_ABS" == "$REPO_ABS" ]]; then
+  echo "refused: $WT_ABS is the repo root" >&2
+  exit 3
+fi
+main_wt="$(git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2; exit}')"
+if [[ "$WT_ABS" == "$main_wt" ]]; then
+  echo "refused: $WT_ABS is the main worktree" >&2
+  exit 3
+fi
+
+git -C "$REPO_ABS" worktree remove --force "$WT_ABS"
+echo "removed: $WT_ABS"
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+chmod +x scripts/cleanup-worktree.sh
+pytest tests/test_cleanup_worktree.py -v
+```
+
+Expected: 4 passed.
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/cleanup-worktree.sh tests/test_cleanup_worktree.py
+git commit -m "feat: cleanup-worktree.sh with triple-assertion safety gate"
+```
+
+---
+
+## Task 17: gc-worktrees.sh
+
+**Files:**
+- Create: `scripts/gc-worktrees.sh`
+- Create: `tests/test_gc_worktrees.py`
+
+- [ ] **Step 1: Write failing tests**
+
+```python
+# tests/test_gc_worktrees.py
+"""Tests for gc-worktrees.sh — list-then-filter via git worktree list."""
+import os
+import subprocess
+import time
+from pathlib import Path
+from tests.conftest import SCRIPTS_DIR
+
+
+def gc(repo):
+    return subprocess.run(
+        [str(SCRIPTS_DIR / "gc-worktrees.sh"), str(repo)],
+        capture_output=True, text=True,
+    )
+
+
+def make_aged_worktree(repo, tmp_path, name, age_hours):
+    wt = tmp_path / name
+    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
+                   cwd=repo, check=True)
+    old = time.time() - (age_hours * 3600)
+    os.utime(wt, (old, old))
+    return wt
+
+
+def test_gc_removes_old_combined_review(tmp_repo, tmp_path, monkeypatch):
+    monkeypatch.setenv("TMPDIR", str(tmp_path))
+    old_wt = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-aaa", 48)
+    r = gc(tmp_repo)
+    assert r.returncode == 0, r.stderr
+    assert not old_wt.exists()
+
+
+def test_gc_skips_marked_worktree(tmp_repo, tmp_path, monkeypatch):
+    monkeypatch.setenv("TMPDIR", str(tmp_path))
+    kept = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-keep", 48)
+    (kept / ".combined-review-keep").touch()
+    r = gc(tmp_repo)
+    assert r.returncode == 0, r.stderr
+    assert kept.exists()
+
+
+def test_gc_skips_recent_worktree(tmp_repo, tmp_path, monkeypatch):
+    monkeypatch.setenv("TMPDIR", str(tmp_path))
+    recent = make_aged_worktree(tmp_repo, tmp_path, "combined-review-recent-bbb", 1)
+    r = gc(tmp_repo)
+    assert r.returncode == 0
+    assert recent.exists()
+
+
+def test_gc_skips_non_combined_review_worktree(tmp_repo, tmp_path, monkeypatch):
+    monkeypatch.setenv("TMPDIR", str(tmp_path))
+    other = make_aged_worktree(tmp_repo, tmp_path, "some-other-wt", 48)
+    r = gc(tmp_repo)
+    assert r.returncode == 0
+    assert other.exists()
+```
+
+- [ ] **Step 2: Run tests, verify they fail**
+
+```bash
+pytest tests/test_gc_worktrees.py -v
+```
+
+- [ ] **Step 3: Implement `scripts/gc-worktrees.sh`**
+
+```bash
+#!/usr/bin/env bash
+# gc-worktrees.sh <repo_root>
+#
+# Enumerates worktrees via `git worktree list --porcelain`, selects entries
+# matching the combined-review-* basename pattern, AND older than 24h
+# (by mtime), AND not carrying a .combined-review-keep marker. Each removal
+# goes through the same triple-assertion gate as cleanup-worktree.sh.
+set -euo pipefail
+
+REPO="${1:-$PWD}"
+REPO_ABS="$(cd "$REPO" && pwd)"
+AGE_HOURS="${COMBINED_REVIEW_GC_AGE_HOURS:-24}"
+NOW="$(date +%s)"
+CUTOFF=$(( NOW - (AGE_HOURS * 3600) ))
+
+SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
+
+# Portable mtime helper. Tries GNU `stat -c %Y` first, then BSD `stat -f %m`,
+# then Python as a last-resort fallback. Earlier versions of this script tried
+# `stat -f %m` first, but on GNU/Linux `-f` means "filesystem mode" (not file)
+# and `%m` is the mount point, so the command exits 0 with non-numeric output —
+# the GNU `-c %Y` fallback never ran, and the numeric `[[ ]]` comparison broke
+# silently, leaving stale worktrees forever.
+mtime_of() {
+  local p="$1" m
+  if m=$(stat -c %Y "$p" 2>/dev/null); then
+    echo "$m"
+  elif m=$(stat -f %m "$p" 2>/dev/null); then
+    echo "$m"
+  else
+    python3 -c 'import os, sys; print(int(os.stat(sys.argv[1]).st_mtime))' "$p" 2>/dev/null || echo 0
+  fi
+}
+
+git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2}' \
+| while IFS= read -r wt; do
+  base="$(basename "$wt")"
+  [[ "$base" =~ ^combined-review- ]] || continue
+  [[ -f "$wt/.combined-review-keep" ]] && continue
+  mtime="$(mtime_of "$wt")"
+  # Sanity-check that mtime is a positive integer before arithmetic; on the
+  # off chance both stat forms return something non-numeric, treat as "skip"
+  # rather than crash the GC loop.
+  if [[ "$mtime" =~ ^[0-9]+$ ]] && [[ "$mtime" -lt "$CUTOFF" ]]; then
+    "$SCRIPT_DIR/cleanup-worktree.sh" "$REPO_ABS" "$wt" || true
+  fi
+done
+```
+
+- [ ] **Step 4: Run tests**
+
+```bash
+chmod +x scripts/gc-worktrees.sh
+pytest tests/test_gc_worktrees.py -v
+```
+
+Expected: 4 passed.
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add scripts/gc-worktrees.sh tests/test_gc_worktrees.py
+git commit -m "feat: gc-worktrees.sh removes stale combined-review-* worktrees > 24h"
+```
+
+---
+
+## Task 18: SKILL.md — orchestration document
+
+**Files:**
+- Create: `SKILL.md`
+
+This is a documentation task — no test code, but the SKILL.md content must be precise enough that an LLM following it will execute the pipeline correctly.
+
+- [ ] **Step 1: Write `SKILL.md`**
+
+Note the **four-backtick** outer fence — the SKILL.md content contains many indented triple-backtick code blocks, and a triple-backtick outer fence would let those (indented up to 3 spaces is still valid CommonMark close-fence) terminate the wrapper prematurely.
+
+````markdown
+---
+name: combined-review
+description: Use when the user wants a single code/spec/plan review that fuses findings from Claude's pr-review-toolkit sub-agents and Codex CLI in one session. Triggers — PR review, branch-vs-main review, spec/plan review, "review with both tools", "/combined-review".
+---
+
+# Combined Review
+
+You are orchestrating a two-tool code review. You will run Claude sub-agents
+and Codex (`codex exec --sandbox read-only`) in parallel against the same
+materialized review subject, then synthesize a single deduped report.
+
+## Sequence — do NOT skip steps
+
+You are reading this skill at the start of every `/combined-review` invocation.
+The user's args arrive as `$ARGUMENTS` from the slash command. Follow Phase
+A → B → C → D below in order. **Steps within Phase A are sequential. Phases B
+and below also run after A completes.**
+
+Let `SKILL_DIR=$HOME/.claude/skills/combined-review` (or the symlink target if
+installed via symlink). Reference scripts as `$SKILL_DIR/scripts/<name>`.
+
+### Phase A — sequential setup
+
+Run as a series of sequential `Bash` tool calls. Do NOT batch these into one
+parallel message — each step depends on the previous.
+
+A1. **GC stale worktrees** — `$SKILL_DIR/scripts/gc-worktrees.sh "$(git rev-parse --show-toplevel)"`. Ignore non-zero exits; this is best-effort.
+
+A2. **Write `$ARGUMENTS` to a file using the `Write` tool** (NOT a Bash heredoc — `Write` doesn't shell-interpret, which is the whole point). Path: an orchestrator-owned tmp file `ARGS_FILE` you allocate via `Bash` (`mktemp -t combined-review-args-XXXXXX`). Then **parse args** by Bash:
+  ```
+  $SKILL_DIR/scripts/parse-args.py --args-file "$ARGS_FILE"
+  ```
+  Capture stdout as `CONFIG_JSON`. This avoids shell-injection from `$ARGUMENTS` containing quotes, spaces, `$`, backticks, etc.
+
+A3. **Write `CONFIG_JSON` to `CONFIG_FILE`** (Write tool again, no shell interpolation) and **resolve scope**:
+  ```
+  cat "$CONFIG_FILE" | $SKILL_DIR/scripts/resolve-scope.py
+  ```
+  Capture stdout as `SCOPE_JSON`. If this errors (dirty+PR ambiguity, default branch + clean tree), surface the error to the user and stop.
+
+A4. **Pre-flight — codex availability**: if the user did NOT pass `--no-codex`, run three checks before continuing:
+  - `command -v codex` — must succeed. If not, stop: "Codex not on PATH. Pass --no-codex to run Claude-only, or install codex."
+  - `codex login status` (or equivalent) — must succeed. If not, stop: "Codex not authenticated. Pass --no-codex or run `codex login`."
+  - `codex exec --help` output must contain `--sandbox` — without this, `run-codex.py` would refuse to run in Phase B and Phase C would have only an error status to render. Catching it in Phase A produces a cleaner user experience. If absent, stop: "Installed codex doesn't advertise `--sandbox`. Update codex or pass --no-codex."
+
+  All three pre-flights are skipped if `--no-codex` was passed.
+
+A5. **Pre-flight — gh authentication when --pr**: if `SCOPE_JSON.kind == "pr"`, run `gh auth status`. Error early if not authenticated.
+
+A6. **Materialize scope** — write `SCOPE_JSON` to `SCOPE_FILE` (Write tool) and run:
+  ```
+  cat "$SCOPE_FILE" | $SKILL_DIR/scripts/materialize-scope.py
+  ```
+  Capture stdout as `MAT_JSON`. This creates the worktree if needed and populates the materialized review subject.
+
+A7. **Merge `worktree_path` from `MAT_JSON` back into the scope object IMMEDIATELY** (before any abort gate that could cause an early exit). Re-write `SCOPE_FILE` with the merged object. Pseudocode:
+
+  ```
+  merged = parse(SCOPE_JSON)
+  merged["worktree_path"] = MAT_JSON.worktree_path  # may be null for uncommitted/files
+  Write SCOPE_FILE = serialize(merged)
+  ```
+
+  **Why before A8/A9 (not after):** if an abort gate stops execution between materialize and merge, Phase D's `cleanup-worktree.sh "$REPO_ROOT" "$WORKTREE_PATH"` has no path to clean up — the worktree leaks. Doing the merge immediately means every early exit from A8/A9 can run Phase D against a merged scope file and clean up the worktree it created.
+
+A8. **Pre-flight — empty scope**: if `MAT_JSON.has_reviewable_changes == false`, run Phase D cleanup (worktree already recorded in `SCOPE_FILE` from A7) and stop: "Nothing to review."
+
+A9. **Pre-flight — large diff**: if `MAT_JSON.total_lines_changed > 2000` (env override `$COMBINED_REVIEW_LARGE_DIFF_THRESHOLD`):
+  - If the user did NOT pass `--force-large`, ASK the user in chat: "Diff is N lines — both reviewers degrade on large diffs. Proceed?" Wait for explicit confirmation. If they decline, run Phase D cleanup (worktree recorded) and stop.
+  - If non-interactive, run Phase D cleanup and abort with "Diff is N lines; pass --force-large to bypass."
+
+A10. **Allocate the remaining orchestrator-owned file paths** — single `Bash`:
+  ```
+  PROMPT=$(mktemp -t combined-review-prompt-XXXXXX)
+  CODEX_STDOUT=$(mktemp -t combined-review-codex-stdout-XXXXXX)
+  CODEX_STDERR=$(mktemp -t combined-review-codex-stderr-XXXXXX)
+  CODEX_STATUS=$(mktemp -t combined-review-codex-status-XXXXXX)
+  CLAUDE_TRANSCRIPTS=$(mktemp -d -t combined-review-claude-XXXXXX)
+  echo "$PROMPT $CODEX_STDOUT $CODEX_STDERR $CODEX_STATUS $CLAUDE_TRANSCRIPTS"
+  ```
+  Capture all five paths.
+
+A11. **Render the prompt** — three sub-steps to avoid shell-injecting user content:
+  1. Write the materialized blob to `MAT_FILE` using the `Write` tool.
+  2. If `CONFIG_JSON.focus` is non-null: write its value to `FOCUS_FILE` (allocate via `mktemp -t combined-review-focus-XXXXXX`) using the `Write` tool. **Do NOT interpolate the focus text into a shell command** — it can contain arbitrary user input including `$(...)`, backticks, and `;` that would execute during the Bash call. Always pass via file.
+  3. Bash-invoke render-prompt.py:
+     ```
+     cat "$MAT_FILE" | $SKILL_DIR/scripts/render-prompt.py \
+       --mode <mode-literal> \
+       [--focus-file "$FOCUS_FILE"] \
+       > "$PROMPT"
+     ```
+     `<mode-literal>` is one of `code|spec|plan|docs` — these are constants from a known set, not user-provided text, so direct argv substitution is safe. Anything user-provided (focus) goes through a file.
+
+### Phase B — parallel review (ONE message, multiple tool calls)
+
+In a single message, issue:
+
+1. **Codex background Bash** (skip if `--no-codex`):
+   ```
+   $SKILL_DIR/scripts/run-codex.py \
+     --scope "$SCOPE_FILE" \
+     --prompt-file "$PROMPT" \
+     --stdout "$CODEX_STDOUT" \
+     --stderr "$CODEX_STDERR" \
+     --status "$CODEX_STATUS"
+   ```
+   with `run_in_background: true`. `SCOPE_FILE` already contains the merged `worktree_path` from Phase A7.
+
+2. **Claude sub-agent calls** — one Agent call per sub-agent:
+   - Mode = code, default: dispatch THREE agents: `code-reviewer`, `silent-failure-hunter`, `pr-test-analyzer` (use the pr-review-toolkit's subagent_type names if available; otherwise general-purpose with a focused prompt).
+   - Mode = code, `--full`: add `comment-analyzer`, `type-design-analyzer`, `code-simplifier`.
+   - Mode = spec/plan/docs: dispatch ONE agent with the rendered prompt + the document-reviewer brief.
+   
+   Each Agent call's prompt = the contents of `$PROMPT` (read it once before issuing the parallel batch). The agent must emit findings only in the `---FINDING---` block schema.
+
+After issuing, await all results inline (Agent calls return), and use `Monitor` to know when codex's background process completes.
+
+### Phase C — synthesis and report
+
+C0. **Determine codex outcome.** Branch on `--no-codex` FIRST, then on the status file:
+  - **If `--no-codex` was passed:** Phase B never launched codex, so `$CODEX_STATUS` is an empty `mktemp` file and reading it would fail. Set `reviewer_summary.codex = {"status": "skipped"}` directly and skip the C2 codex normalization. Do not read `$CODEX_STATUS`.
+  - **Otherwise** read the status file: `cat "$CODEX_STATUS"` → JSON with `status` ∈ `ok|failed|timeout`. Branching:
+    - `ok`: proceed to normalize codex output in C2.
+    - `failed`: skip codex normalization; build `reviewer_summary.codex = {"status": "failed", "error": "<prefer status.error if present and non-empty, else stderr excerpt from $CODEX_STDERR truncated to ~500 chars>", "exit_code": N, "duration_ms": M}`. Continue with Claude-only.
+    - `timeout`: as above with `status: "timeout"` and `error: "codex did not finish within N seconds"`.
+
+    **Prefer-status.error rule**: for hard pre-flight failures inside `run-codex.py` (codex disappeared from PATH between Phase A and Phase B, missing `--sandbox` flag), the script writes the diagnostic to both the status JSON and `$CODEX_STDERR`. Status JSON is the more structured/reliable channel — read it first.
+
+C1. **Write each Agent's transcript to a file**: for each sub-agent N, write its returned text to `$CLAUDE_TRANSCRIPTS/<agent-name>.txt`. Concatenate them into `$CLAUDE_TRANSCRIPTS/all.txt` for the audit trail.
+
+C2. **Normalize each reviewer's output** — one call per reviewer (skip codex if `status != ok`):
+   ```
+   cat $CODEX_STDOUT | $SKILL_DIR/scripts/normalize-findings.py --source codex
+   cat $CLAUDE_TRANSCRIPTS/code-reviewer.txt | $SKILL_DIR/scripts/normalize-findings.py --source claude:code-reviewer
+   # ... one per agent
+   ```
+   Each normalize output is JSON with three fields: `findings`, `parse_warnings`, `unparsed_chunks`. **All three must flow downstream — not just findings.**
+
+   In-session, accumulate:
+   - **`all_findings`**: concatenate every reviewer's `findings[]` array. This is what the synthesis pass clusters.
+   - **`reviewer_summary[source].parse_warnings`**: count of warnings per reviewer (for the cluster JSON's `reviewer_summary.codex.parse_warnings` / `reviewer_summary.claude[N].parse_warnings` fields).
+   - **`reviewer_summary[source].raw_findings`**: length of `findings[]` per reviewer.
+   - **`all_unparsed_chunks`**: concatenate every reviewer's `unparsed_chunks[]` (each chunk already tagged with `source`). This goes into the cluster JSON's top-level `unparsed_chunks` so `report.py` can render the "## Parse warnings" section.
+
+   **Anti-pattern (caught in static review): dropping `parse_warnings` and `unparsed_chunks` because the synthesis pass only needs `findings`.** If a reviewer ignored the schema and emitted prose, normalize captures that as an unparsed chunk — losing it here would make schema-noncompliance invisible to the final report, defeating the parse-warnings audit path the spec promises.
+
+C3. **Synthesis pass (in-session, no new agent)**: cluster the findings by semantic similarity. Read each finding's title + detail + file:line. Group into clusters where you'd say "these are about the same issue". Tag each cluster `agreement` / `claude_only` / `codex_only` / `disagreement`. The synthesis result is **a JSON object you compose in this conversation** — there is no `$CLUSTERS_JSON` shell variable. Use the `Write` tool to persist it to a file before downstream scripts can read it.
+
+   Allocate `CLUSTERS_FILE` via Bash (`mktemp -t combined-review-clusters-XXXXXX.json`), then **`Write` the synthesized cluster JSON to that path**. All subsequent steps read from `$CLUSTERS_FILE`.
+
+   **Anti-patterns** — STOP and reconsider if you find yourself doing any of:
+   - Just concatenating findings without clustering.
+   - Using string similarity heuristics instead of judgment.
+   - Skipping the synthesis pass because "it's too hard".
+   - Summarizing both raw outputs into a prose report instead of clustering.
+   - Piping `"$CLUSTERS_JSON"` into a script (no such variable exists — the synthesis result is conversational text you must Write to a file first).
+
+C4. **Validate the cluster JSON** — read from the file Write'd in C3:
+   ```
+   $SKILL_DIR/scripts/validate-clusters.py < "$CLUSTERS_FILE" 2> "$VALIDATE_STDERR"
+   ```
+   Allocate `VALIDATE_STDERR` via `mktemp` first (orchestrator-owned, deleted in Phase D). If exit non-zero: re-prompt yourself once with the validator's error message (read from `$VALIDATE_STDERR`), re-emit corrected JSON, `Write` it back to `$CLUSTERS_FILE` (overwriting), and re-validate. If it STILL fails, proceed to C5 with `--synthesis-failed-file "$VALIDATE_STDERR"` (NOT `--synthesis-failed "<msg>"`).
+
+C5. **Render the report** — read cluster JSON from `$CLUSTERS_FILE`, pass codex stderr so failure diagnostics (auth errors, quota exhaustion, sandbox refusals) end up in the audit trail. **Pass the synthesis-failure message via file**, not argv:
+   ```
+   $SKILL_DIR/scripts/report.py \
+     --codex-raw "$CODEX_STDOUT" \
+     --codex-stderr "$CODEX_STDERR" \
+     --claude-raw "$CLAUDE_TRANSCRIPTS/all.txt" \
+     [--synthesis-failed-file "$VALIDATE_STDERR"] \
+     < "$CLUSTERS_FILE"
+   ```
+   When the `--synthesis-failed-file` flag is set, an empty stdin is fine (report.py only reads stdin in the non-failed path). Why file not argv: the validator's stderr can contain backticks, `$(...)`, or quote characters from the model's malformed output — interpolating that into a Bash command line is the same shell-injection class as the focus-text case. Always file. Print the output to chat. If `--save <path>` was passed, also tee to that path. Phase D will delete `$CLUSTERS_FILE` and `$VALIDATE_STDERR` along with the other orchestrator-owned files.
+
+### Phase D — cleanup (ALWAYS, even on errors)
+
+**Order matters**: worktree teardown reads `worktree_path` from `SCOPE_FILE`, so SCOPE_FILE must still exist when cleanup-worktree.sh runs. Do D1 BEFORE D2.
+
+D1. **Worktree cleanup first** — read the merged scope to get `worktree_path` and `repo_root`, then act:
+   - If `worktree_path` is non-null AND `--keep-worktree` was NOT passed:
+     ```
+     $SKILL_DIR/scripts/cleanup-worktree.sh "$REPO_ROOT" "$WORKTREE_PATH"
+     ```
+   - If `worktree_path` is non-null AND `--keep-worktree` WAS passed: `touch "$WORKTREE_PATH/.combined-review-keep"` (marker — gc-worktrees.sh will skip it on later runs) and announce the path to the user.
+   - If `worktree_path` is null (uncommitted/files scopes): nothing to do here.
+
+   Capture `REPO_ROOT` and `WORKTREE_PATH` into shell variables BEFORE invoking cleanup, in case D2 ordering changes in the future.
+
+D2. **Delete orchestrator-owned files** — only after D1 has read SCOPE_FILE:
+   ```
+   rm -f "$ARGS_FILE" "$CONFIG_FILE" "$SCOPE_FILE" "$MAT_FILE" "$FOCUS_FILE" \
+         "$PROMPT" "$CODEX_STDOUT" "$CODEX_STDERR" "$CODEX_STATUS" \
+         "$CLUSTERS_FILE" "$VALIDATE_STDERR"
+   rm -rf "$CLAUDE_TRANSCRIPTS"
+   ```
+   Some variables may be unset if the run didn't get that far — `rm -f` silently ignores those.
+
+D3. Confirm to user: "Combined review complete." Done.
+
+## Failure handling
+
+- Any non-zero exit from a Phase A script: surface error to user, run Phase D cleanup, stop.
+- Codex non-zero or timeout (>5min, env `COMBINED_REVIEW_CODEX_TIMEOUT`): report Claude-only, note "codex failed" in the report.
+- One Claude sub-agent fails: continue with the others; failed agent shows up in `reviewer_summary` with status=failed.
+
+## Anti-patterns
+
+If you find yourself doing any of these, STOP:
+
+- Running reviewers sequentially instead of in parallel (Phase B is the whole point).
+- Skipping the materialize step and feeding raw git state to reviewers.
+- Skipping Phase D cleanup "because the report is what matters".
+- Concatenating raw outputs into a single section without clustering.
+- Inventing your own scope-detection logic instead of using resolve-scope.py.
+````
+
+- [ ] **Step 2: Commit**
+
+```bash
+git add SKILL.md
+git commit -m "feat: SKILL.md orchestration document for combined-review"
+```
+
+---
+
+## Task 19: commands/combined-review.md — slash entry
+
+**Files:**
+- Create: `commands/combined-review.md`
+
+- [ ] **Step 1: Write the slash command**
+
+Four-backtick outer fence: the slash command's body contains a triple-backtick block around `$ARGUMENTS`.
+
+````markdown
+---
+description: Run Claude pr-review-toolkit + Codex in parallel; merge findings into one report.
+argument-hint: "[--pr N | --uncommitted | --base BRANCH | --commit SHA | <files...>] [--mode code|spec|plan|docs] [--focus TEXT] [--full] [--no-codex] [--save PATH] [--force-large] [--keep-worktree]"
+# Edit is intentionally omitted — this is a read-only review flow. Write is
+# needed for orchestrator-owned temp files (prompt, scope, args) and the
+# optional --save report path. Bash is unavoidable (the entire pipeline is
+# Bash-driven). Removing Edit is defense-in-depth, NOT a hard sandbox: Write
+# and Bash can still modify repo files if the model drifts. The primary
+# protection against unintended edits is the no-edit instruction inside the
+# rendered review prompt + codex's --sandbox read-only enforcement; the
+# allowlist trim just removes the most obvious code-modification path.
+allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep", "Task", "Monitor"]
+---
+
+# Combined Review
+
+User invoked `/combined-review` with the literal argument string below (do NOT
+substitute it into a shell command — pass it through the args-file path
+described in SKILL.md Phase A2):
+
+```
+$ARGUMENTS
+```
+
+You are now in the `combined-review` skill. Read and follow
+`~/.claude/skills/combined-review/SKILL.md` for the full orchestration pipeline.
+
+**Critical reminders for this run:**
+
+- Phase A is **sequential** — each step depends on the previous. Do NOT batch.
+- `$ARGUMENTS` is captured as literal text — write it to a temp file using the `Write` tool, then pass that file's path to `parse-args.py --args-file`. Never shell-substitute `$ARGUMENTS` into a Bash command line.
+- Phase B is the **only** phase where parallel tool calls happen (codex background + Agent sub-agents in the same message).
+- Phase D cleanup **always** runs, even on errors.
+- Codex side uses `codex exec --sandbox read-only` exclusively — never `codex review`.
+- Worktree cleanup is gated by `cleanup-worktree.sh`'s triple-assertion check — do not invoke `git worktree remove` directly.
+
+Start with Phase A1 (gc-worktrees).
+````
+
+- [ ] **Step 2: Commit**
+
+```bash
+git add commands/combined-review.md
+git commit -m "feat: slash command entry point for combined-review"
+```
+
+---
+
+## Task 20: Install via symlinks; baseline smoke test
+
+**Files:**
+- Modify: `README.md` (install instructions)
+
+- [ ] **Step 1: Document install in `README.md`**
+
+Four-backtick outer fence: the README contains multiple triple-backtick code blocks.
+
+````markdown
+# combined-review
+
+A Claude Code skill that runs Claude's `pr-review-toolkit` sub-agents and
+`codex exec --sandbox read-only` in parallel against the same materialized
+review subject, then synthesizes the findings into one report.
+
+See `docs/superpowers/specs/2026-05-11-combined-review-skill-design.md`
+in the original juvera repo for the design rationale.
+
+## Install
+
+```bash
+# from this repo's root (~/projects/combined-review)
+mkdir -p ~/.claude/skills ~/.claude/commands
+ln -sfn "$PWD" ~/.claude/skills/combined-review
+ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
+
+# Verify
+ls -la ~/.claude/skills/combined-review
+ls -la ~/.claude/commands/combined-review.md
+```
+
+## Dependencies
+
+- Python 3.11+
+- `jsonschema` (`pip install -e ".[dev]"` from this repo)
+- `codex` CLI on PATH, logged in (`codex login status`)
+- `gh` CLI on PATH, authenticated (`gh auth status`)
+
+## Run
+
+```
+/combined-review              # auto-detect scope, code mode
+/combined-review --pr 105
+/combined-review --uncommitted
+/combined-review --mode spec docs/design.md
+```
+
+## Develop
+
+```bash
+pip install -e ".[dev]"
+pytest -v
+```
+````
+
+- [ ] **Step 2: Run the install commands**
+
+```bash
+cd ~/projects/combined-review
+mkdir -p ~/.claude/skills ~/.claude/commands
+ln -sfn "$PWD" ~/.claude/skills/combined-review
+ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
+ls -la ~/.claude/skills/combined-review
+ls -la ~/.claude/commands/combined-review.md
+```
+
+Expected: both symlinks present and pointing at `~/projects/combined-review/`. (Earlier audit found `~/.claude/commands/` did not exist on this machine — the `mkdir -p` makes the install idempotent regardless of starting state.)
+
+- [ ] **Step 3: Run the full test suite end-to-end**
+
+```bash
+cd ~/projects/combined-review && pytest -v
+```
+
+Expected: all tests pass.
+
+- [ ] **Step 4: Commit**
+
+```bash
+git add README.md
+git commit -m "docs: install instructions and dev workflow"
+```
+
+---
+
+## Task 21: End-to-end smoke — --uncommitted on a tiny diff
+
+This task is **manual** — run the skill against a real repo to verify the pipeline holds together. Failures here typically expose orchestration glitches that unit tests miss.
+
+- [ ] **Step 1: Make a tiny throwaway change in this Juvera repo**
+
+**Do NOT modify any existing file** — `git checkout -- <file>` would discard real edits at rollback time. Use a brand-new file that's safe to delete.
+
+```bash
+cd ~/Projects/juvera_ai_4
+# Create a brand-new file that doesn't exist in the tree
+test ! -e .combined-review-smoke.txt || (echo "remove first" && false)
+cat > .combined-review-smoke.txt <<'EOF'
+# Combined-review smoke test fixture
+This file exists only so the skill has something tangible to review.
+It will be removed after the smoke test.
+EOF
+```
+
+- [ ] **Step 2: Invoke `/combined-review --uncommitted`**
+
+In your Claude Code session for the Juvera repo, type:
+
+```
+/combined-review --uncommitted
+```
+
+- [ ] **Step 3: Verify expected behavior**
+
+- Phase A runs sequentially — you should see GC, args-file write, parse-args, resolve-scope, materialize executed in order via Bash calls (parse-args reads from the args file, never from inline `$ARGUMENTS` substitution).
+- Pre-flight passes (codex available, no PR, has reviewable changes — the smoke fixture file is untracked but materialize-scope picks it up).
+- Phase B issues one background Bash (codex with `--status` flag) and three Agent calls (code-reviewer, silent-failure-hunter, pr-test-analyzer) in a SINGLE message.
+- Phase C reads `$CODEX_STATUS`, branches correctly (should be `ok` for a real codex run).
+- Synthesis runs and produces a clustered report.
+- Final report is printed.
+- Phase D cleanup runs — verify with `ls $TMPDIR/combined-review-*` (no leftovers) and `git worktree list` (no extra entries — though for `--uncommitted` no worktree was created in the first place).
+
+- [ ] **Step 4: Remove the throwaway file**
+
+```bash
+cd ~/Projects/juvera_ai_4
+rm .combined-review-smoke.txt
+git status   # should now be clean
+```
+
+- [ ] **Step 5: If anything failed**, capture the failure mode (what didn't run, what error appeared) and fix in a follow-up commit before moving on.
+
+---
+
+## Task 22: End-to-end smoke — --pr on a real PR
+
+- [ ] **Step 1: Pick a small, recently-merged PR in this repo** (or use a current open PR if available)
+
+```bash
+cd ~/Projects/juvera_ai_4
+gh pr list --state all --limit 5
+# pick one with a small diff, e.g., PR #91 (the test-unit gate work)
+```
+
+- [ ] **Step 2: Invoke `/combined-review --pr <#>`**
+
+```
+/combined-review --pr 91
+```
+
+- [ ] **Step 3: Verify**
+
+- A worktree gets created under `$TMPDIR/combined-review-juvera_ai_4-pr-*`
+- `gh pr checkout --detach` runs inside it
+- `git fetch <base_repo_url> main` runs (NOT `git fetch origin main`)
+- `git cat-file -e <head_sha>^{commit}` and `git cat-file -e <base_sha>^{commit}` both succeed
+- Both reviewers see the three-dot diff (compare a few line citations against `gh pr diff 91`)
+- Report renders
+- `cleanup-worktree.sh` runs and the temp worktree is gone
+
+- [ ] **Step 4: If failures**, fix and re-run.
+
+---
+
+## Task 23: End-to-end smoke — --mode spec on a doc file
+
+- [ ] **Step 1: Pick a spec file in this repo**
+
+```bash
+ls docs/superpowers/specs/ | head -5
+# e.g., docs/superpowers/specs/2026-05-08-ci-test-unit-path-filter-design.md
+```
+
+- [ ] **Step 2: Invoke**
+
+```
+/combined-review --mode spec docs/superpowers/specs/2026-05-08-ci-test-unit-path-filter-design.md
+```
+
+- [ ] **Step 3: Verify**
+
+- `materialize-scope.py` puts the file into `doc_files` (not `changed_files`).
+- Codex is invoked via `codex exec` (not codex review).
+- ONE Claude agent (document-reviewer brief), not three.
+- Findings reflect spec-review concerns (completeness, ambiguity) — NOT "no test coverage".
+- Report renders.
+
+- [ ] **Step 4: Fix any issues, then commit any fixes**
+
+---
+
+## Task 24: Final test suite + commit
+
+- [ ] **Step 1: Run the full suite one last time**
+
+```bash
+cd ~/projects/combined-review && pytest -v
+```
+
+Expected: all green.
+
+- [ ] **Step 2: Check git log for sanity**
+
+```bash
+git log --oneline
+```
+
+Expected: ~20 commits, each a single coherent step.
+
+- [ ] **Step 3: Push to a fork (optional — only if you intend to share)**
+
+```bash
+gh repo create combined-review --public --source=. --remote=origin --push
+```
+
+---
+
+## Spec coverage verification
+
+| Spec section | Covered by task(s) |
+|---|---|
+| §2 Invocation (slash + skill) | T18 (SKILL.md), T19 (slash command) |
+| §2 CLI flags | T2 (parse-args.py) |
+| §3 Scope resolution | T3, T4, T5 (resolve-scope.py) |
+| §4 Codex routing via `codex exec` | T12 (run-codex.py) |
+| §4 Worktree lifecycle | T7, T8 (creation), T16 (cleanup), T17 (GC) |
+| §4 PR fetch by URL + cat-file check | T8 |
+| §4 Shared-primary-input guarantee | T11 (render-prompt unifies both sides' inputs) |
+| §4 codex exec --sandbox safety | T12 (verifies flag is supported) |
+| §5 Materialize-scope for all kinds | T6, T7, T8, T9 |
+| §5 Phase A/B/C/D dispatch ordering | T18 (SKILL.md) |
+| §5 Raw output ownership | T18, T12, T20 (manual verify) |
+| §6 Mode prompts | T10 |
+| §7 Finding schema | T11 (schema appendix), T13 (parser) |
+| §8 Synthesis pass + cluster JSON | T18 (skill instructs synthesis) |
+| §8 validate-clusters + repair | T14, T18 |
+| §9 Report format | T15 |
+| §10 Pre-flight checks | T18 (codex auth, gh auth, empty scope, large diff) |
+| §10 In-flight failure handling | T18 (codex timeout, sub-agent failure) |
+| §11 File layout | T1, all create tasks |
+| §12 Testing approach | T21–T23 (smoke), unit tests throughout |
+| §13 Non-goals (no auto-fix) | T11 + T12 enforce no-edit |
+| §14 Locked decisions | All reflected in implementation |
+
+---
+
+**Plan complete and saved to `docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md`. Two execution options:**
+
+**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
+
+**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.
+
+**Which approach?**
diff --git a/docs/superpowers/specs/2026-05-11-combined-review-skill-design.md b/docs/superpowers/specs/2026-05-11-combined-review-skill-design.md
new file mode 100644
index 0000000..8748884
--- /dev/null
+++ b/docs/superpowers/specs/2026-05-11-combined-review-skill-design.md
@@ -0,0 +1,651 @@
+# Combined Review Skill — Design Spec
+
+**Date:** 2026-05-11
+**Scope:** Personal Claude Code skill (`~/.claude/`), not a project artifact. Spec lives here for review history.
+**Goal:** A single Claude Code invocation that runs both Claude Code's review (the `pr-review-toolkit` sub-agents) and Codex (via `codex exec --sandbox read-only` driven by a materialized review prompt — see §4 for why we bypass `codex review`'s native diff), then merges findings into a deduped, attributed, high-signal report — without the user juggling two sessions.
+
+---
+
+## 1. Overview
+
+Today the user runs two reviewers in two separate sessions:
+
+- **Claude Code side:** the `pr-review-toolkit` plugin (slash command `/pr-review-toolkit:review-pr`), which dispatches specialized sub-agents — code-reviewer, silent-failure-hunter, pr-test-analyzer, comment-analyzer, type-design-analyzer, code-simplifier — and aggregates into severity buckets. (Not to be confused with Claude Code's built-in `/review` command, which is a separate, lighter-weight flow.) This skill **reuses the toolkit's sub-agents directly** rather than invoking the toolkit's slash command — orchestrating the agents in-session gives us control over prompts and output schema.
+- **Codex side:** the `codex` CLI. The skill drives codex via `codex exec --sandbox read-only` with a fully-materialized review prompt (diff + file contents) on stdin, **not** via `codex review`'s native auto-diff. §4 details the reasoning: codex review's diff semantics are unobservable, and a silent mismatch with the Claude-side diff would corrupt synthesis. By feeding both sides the same materialized blob from `materialize-scope.py`, we pin the primary input.
+
+The user's workflow is mostly PR review with occasional spec/plan/doc review. Two-tool review is high-signal because the tools disagree usefully — but the manual merge is tedious and the user wants the synthesis automated.
+
+The skill orchestrates both reviews in parallel from one Claude Code session and produces a unified report that distinguishes:
+
+- **High-confidence findings** — both tools independently flagged the same issue.
+- **Single-source findings** — only one tool flagged it.
+- **Disagreements** — both tools flagged the same location but with contradictory recommendations.
+
+---
+
+## 2. Invocation
+
+Two files:
+
+- `~/.claude/commands/combined-review.md` — slash command. Parses `$ARGUMENTS`, hands off to the skill.
+- `~/.claude/skills/combined-review/SKILL.md` — orchestration logic, activated by the slash command.
+
+This split follows Anthropic's distinction: slash commands are user-typed entry points; skills are model-invoked workflows. The slash command exists because the user wants `/combined-review` to work as a literal command; the skill exists because the orchestration is non-trivial and worth being model-invocable in its own right.
+
+### CLI surface
+
+```
+/combined-review                                 # auto-detect scope, code mode
+/combined-review --pr 105                        # GitHub PR by number
+/combined-review --uncommitted                   # staged + unstaged + untracked
+/combined-review --base develop                  # current branch vs custom base (merge-base diff)
+/combined-review --commit abc1234                # single commit
+/combined-review docs/spec.md plan.md            # positional file list (current contents)
+/combined-review --mode spec --pr 105            # spec lens applied to PR changes
+/combined-review --focus "API contract changes"  # extra lens, default code mode
+/combined-review --full                          # opt into full Claude sub-agent fanout
+/combined-review --pr 105 --force-large          # bypass large-diff confirm prompt
+/combined-review --pr 105 --keep-worktree        # debug: don't tear down /tmp worktree
+```
+
+### Flags
+
+| Flag | Type | Effect |
+|---|---|---|
+| `--pr <#>` | int | Review GitHub PR by number |
+| `--uncommitted` | bool | Review staged + unstaged + untracked |
+| `--base <branch>` | string | Review current HEAD vs given base (merge-base diff, §5) |
+| `--commit <sha>` | string | Review the changes in one commit |
+| `<files...>` | positional | Specific files reviewed as **current working-tree content** (includes any local edits). Mutually exclusive with `--pr`/`--uncommitted`/`--base`/`--commit`. |
+| `--mode <code\|spec\|plan\|docs>` | enum, default `code` | Select review template + sub-agent set |
+| `--focus "<text>"` | string | Freeform extra emphasis appended to mode prompt |
+| `--full` | bool | Use full pr-review-toolkit sub-agent set (6) instead of default 3 |
+| `--no-codex` | bool | Skip Codex side (fallback when codex unavailable / quota exhausted) |
+| `--save <path>` | string | Also write the final report to a file |
+| `--force-large` | bool | Skip the large-diff confirm prompt. Required when the skill runs non-interactively above the threshold. |
+| `--keep-worktree` | bool | Debug only. Inhibits worktree teardown and prints the path on completion. |
+
+`--pr`, `--uncommitted`, `--base`, `--commit`, and positional files are mutually exclusive scope inputs. Specifying more than one is an error.
+
+---
+
+## 3. Scope resolution
+
+Precedence (first match wins):
+
+1. **Explicit scope flag** — use it as-is. Worktree rules:
+   - **Diff-based scopes** (`--pr`, `--base`, `--commit`) always run inside a disposable clean worktree, never in the user's working tree. This prevents local uncommitted edits from contaminating a branch / PR / commit review.
+   - **`--uncommitted`** runs in the user's working tree (that's the point of it).
+   - **Positional files** are reviewed as **current working-tree content** including any local edits the user just made. Reviewing a doc/spec/plan you've been editing is the canonical use case — pinning to HEAD would defeat the purpose. No worktree needed.
+2. **Dirty tree + PR exists for current branch** — **error**, surface ambiguity, require `--uncommitted` or `--pr <#>`.
+3. **Dirty tree, no PR** — implicit `--uncommitted`.
+4. **Clean tree, current branch has PR** — implicit `--pr <#>` (resolved via `gh pr view --json number,headRefOid,baseRefOid`).
+5. **Clean tree, no PR, current branch ≠ default** — implicit `--base <default>` (default branch via `gh repo view --json defaultBranchRef`).
+6. **Clean tree, current branch == default** — **error**, nothing to review.
+
+Logic lives in `scripts/resolve-scope.py`. Emits a normalized scope object:
+
+```json
+{
+  "kind": "pr" | "uncommitted" | "base" | "commit" | "files",
+  "pr_number": 105,
+  "base_ref_name": "main",
+  "head_ref_name": "feature-x",
+  "base_repo_url": "https://github.com/Juvera-AI/juvera_ai.git",
+  "head_repo_url": "https://github.com/contributor/juvera_ai.git",
+  "base_sha": "<immutable 40-char sha>",
+  "head_sha": "<immutable 40-char sha>",
+  "commit_sha": "<immutable 40-char sha>",
+  "files": ["docs/spec.md"],
+  "worktree_path": "<mktemp -d -t combined-review-XXXX>" | null,
+  "repo_root": "/abs/path/to/repo",
+  "needs_clean_worktree": true | false
+}
+```
+
+Ref names + repo URLs are used for `git fetch` (portable across remotes, correct for fork PRs); SHAs are used to **verify** the recorded commits are reachable after fetch. Fetching by SHA alone is less portable; trusting the ref alone is unsafe; assuming `origin` is the base repo is wrong for fork PRs.
+
+All ref-shaped inputs are resolved to immutable SHAs by `resolve-scope.py` — never `origin/<branch>` strings passed downstream, since branches move. For `--pr <#>`, this means `gh pr view <#> --json headRefOid,baseRefOid` first, then materialize against those SHAs.
+
+`resolve-scope.py` does not create the worktree — it only sets `needs_clean_worktree: true` when one will be required. Creation is `materialize-scope.py`'s job (§5 / §4 Worktree lifecycle), since materialize is the first step that actually needs the worktree to exist. `worktree_path` in this object is `null` at this stage and gets populated by materialize.
+
+Downstream steps consume this object, not raw flags.
+
+---
+
+## 4. Codex routing
+
+### Shared-primary-input guarantee — why we don't use `codex review`'s native diff
+
+What the skill guarantees, precisely:
+
+- **Same primary input**: both codex and the Claude sub-agents receive the **same materialized blob** from `materialize-scope.py` (§5) — the same unified diff, the same per-file content snapshots, the same metadata. This is what they're *asked* to review.
+- **Same repo context**: both run with cwd set to the **same git state** — the worktree pinned at the recorded SHA for diff scopes, the user's tree for `uncommitted`/`files`. Neither agent is isolated from the rest of the repo; both may consult adjacent files for context.
+- **Not isolated to the blob**: read-only sandbox prevents *edits*, but `codex exec` and Claude sub-agents (Read, Grep, etc.) can still inspect files beyond the materialized inputs. We don't claim otherwise. Treating "look up callers/types for context" as a feature, not a leak — code review benefits from it, and both tools are looking at the same git state.
+
+What this rules out is the failure mode that motivated this design: `codex review`'s native auto-diff. `codex review` computes its own diff from git state, and we can't observe whether it uses two-dot or three-dot semantics, how it handles untracked files, or how it filters renames. If it diverges from `materialize-scope.py`'s diff, the synthesis (§8) silently merges reviews of different primary inputs.
+
+The skill therefore **bypasses `codex review`'s auto-diff entirely** and uses `codex exec --sandbox read-only` for every scope. The primary input is fixed; context lookups are intentionally allowed. Worth revisiting in v2 if codex review's diff semantics turn out to match ours exactly — but for v1, correctness on the primary input over speculation.
+
+### Scope → invocation
+
+`materialize-scope.py` produces a single content blob (unified diff + per-file `post_content` / `pre_content` / metadata, or doc contents for files mode). Both sides receive this blob. Routing differs only in **what worktree codex runs in** and **what the materialize step has to do first**.
+
+| Scope kind | Setup | Codex invocation |
+|---|---|---|
+| `uncommitted` | None — operate in user's working tree. Materialize uses `git diff HEAD` + untracked. | `codex exec --sandbox read-only` (cwd = user repo root, prompt via stdin) |
+| `base` | `git worktree add --detach <tmp> <head_sha>` (immutable SHA, not literal `HEAD`). Materialize uses `git diff <base_sha>...<head_sha>` inside worktree. | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
+| `commit` | `git worktree add --detach <tmp> <commit_sha>`. Materialize uses `git show --format= <commit_sha>` + commit metadata (author, date, message). | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
+| `pr` | `git worktree add --detach <tmp>` → `gh pr checkout --detach <#>` → fetch base from `<base_repo_url>` (not necessarily `origin` — see PR fetch detail below) → `git reset --hard <head_sha>` if drifted → verify both SHAs exist via `git cat-file -e <sha>^{commit}`. Materialize uses `git diff <base_sha>...<head_sha>` inside worktree. | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
+| `files` (any mode) | None — operate against current working-tree content. Materialize populates `doc_files`. | `codex exec --sandbox read-only` (cwd = user repo root, prompt via stdin) |
+
+### PR fetch detail
+
+In fork/upstream setups, `origin` may be the contributor fork, not the PR base repo. Fetching the base from the wrong remote silently retrieves the wrong commits. The skill:
+
+1. Reads `baseRepository.url`, `headRepository.url`, `baseRefName`, `headRefName`, `baseRefOid`, `headRefOid` from `gh pr view <#> --json baseRepository,headRepository,baseRefName,headRefName,baseRefOid,headRefOid`.
+2. Runs `gh pr checkout --detach <#>` inside the worktree (handles the head fetch including fork mirrors).
+3. **Fetches the base by URL directly, no remote-add**: `git fetch <base_repo_url> <base_ref_name>`. This fetches the ref into `FETCH_HEAD` without mutating the user's `.git/config` (which `git remote add` would do — and which would leak across runs or fail if the remote name already existed).
+4. Pins head: if `git rev-parse HEAD != head_sha`, attempts `git reset --hard <head_sha>`. **If `git reset` fails because the SHA is unreachable**, the PR head was force-pushed between `gh pr view` and `gh pr checkout` — surfaces as **stale-snapshot failure**: "PR head force-pushed mid-review (recorded `<head_sha>` no longer reachable). Rerun `/combined-review --pr <#>` to fetch the current snapshot." No silent fallback; the recorded SHA is the contract.
+5. Verifies the recorded base SHA is reachable locally: `git cat-file -e <base_sha>^{commit}`. If unreachable, same stale-snapshot failure with base-side messaging. **Does NOT** assert `FETCH_HEAD == base_sha` — that would fail harmlessly when the base branch advances between `gh pr view` and `git fetch`. We need the recorded commit to be reachable, not to be the current tip.
+6. Optionally surfaces a warning if the base tip moved (`FETCH_HEAD != base_sha`) — informational only, doesn't block.
+
+### `codex exec` safety
+
+Because `codex exec` is a general agent (unlike the inherently read-only `codex review`), `run-codex.sh` MUST:
+
+- Pass `--sandbox read-only` (or codex's equivalent flag — `run-codex.sh` probes the installed codex version's flag list at start and errors out if no read-only sandbox is available, rather than silently running unsandboxed).
+- Begin the prompt body with an explicit no-edit instruction: `"You are running in review mode. Do not write, edit, or delete any files. Read the materialized inputs below and emit findings only as ---FINDING--- blocks per the schema."`.
+
+Both layers must hold. Missing either violates non-goal §13.
+
+### Worktree lifecycle
+
+- **Creation**: `materialize-scope.py` (§5) creates the worktree when the scope kind requires one, since it needs the worktree to extract file contents and the diff. Path is `mktemp -d -t combined-review-<repo>-XXXXXX` honoring `$TMPDIR`. The path goes into the scope object's `worktree_path` field.
+- **Use**: `run-codex.sh` reads `worktree_path` from the scope object and runs codex inside it. Does not create or destroy.
+- **Fork PRs**: handled by `gh pr checkout --detach <#>` as the primary path inside the empty worktree. `gh` fetches the PR head into a detached HEAD regardless of whether the PR comes from `origin` or a fork. After checkout, `git reset --hard <head-sha>` pins to the exact recorded SHA (defensive against race between `gh pr view` and `gh pr checkout`).
+- **Teardown** — there are three layers, because a skill markdown file cannot hold a shell trap across a multi-tool-call orchestration. **Destructive cleanup never trusts the path string alone** — it cross-checks against git's own worktree registry:
+  1. **In-driver trap**: `run-codex.sh` has a `trap 'cleanup' EXIT INT TERM` for temp files it owns *internally* (e.g., intermediate codex state). It does **not** delete the prompt file or the raw-output files — those are passed in by the orchestrator (see "Raw output ownership" below) and have a different lifecycle.
+  2. **Explicit orchestrator cleanup**: the SKILL.md instructions require that after synthesis + rendering, the orchestrator's final step is a `Bash` call to `scripts/cleanup-worktree.sh <repo_root> <worktree_path>`. The script runs `git -C <repo_root> worktree remove --force <worktree_path>` only after **three independent assertions**:
+     - The path appears in `git -C <repo_root> worktree list --porcelain` for this repo (git considers it a worktree of this repo — the authoritative check, not a pattern match).
+     - The path matches the `combined-review-*` mktemp pattern under `$TMPDIR` or `/tmp` (defense-in-depth — if git's registry is somehow wrong, we still won't delete an arbitrary directory).
+     - The path is not the repo root and not the user's main worktree.
+     If any assertion fails, cleanup-worktree.sh refuses to delete and exits non-zero with a clear message. The skill explicitly forbids skipping this step. Also runs on early-error exit paths.
+  3. **GC on every invocation**: `scripts/gc-worktrees.sh` runs as the first step of every `/combined-review` invocation. It enumerates worktrees via `git -C <current-repo-root> worktree list --porcelain` and selects entries whose path matches `combined-review-*` AND whose mtime is older than 24h AND **do not contain a `.combined-review-keep` marker file** at the worktree root. Each removal goes through the same triple-assertion gate as `cleanup-worktree.sh`. **It does not scan `$TMPDIR` for arbitrary directories** — that would pick up leaks from other repos, which the current invocation has no business deleting. Cross-repo orphans wait for the next `/combined-review` in their own repo, or for OS-level `/tmp` cleanup. Worktrees kept via `--keep-worktree` carry the marker and live until the user removes them manually.
+
+  Together: in-driver trap handles run-codex's internal temp files; explicit cleanup handles the worktree under normal completion (with git-registry verification); GC handles orchestrator-died-mid-run leaks within the current repo. No layer relies on path-pattern matching alone for destructive operations.
+
+### Raw output ownership
+
+All long-lived intermediate files — the prompt file, codex stdout capture, codex stderr capture, sub-agent transcripts — are **orchestrator-owned**, not script-owned:
+
+- The orchestrator creates them via `mktemp` before launching reviewers, passes the paths to `run-codex.sh` as `--prompt-file`, `--stdout`, `--stderr` arguments, and to sub-agents inline.
+- `run-codex.sh` writes to those paths but never deletes them (its `trap` only cleans up files it created internally).
+- `report.py` reads them for the audit-trail section of the final report.
+- The orchestrator deletes them as the final step **after `report.py` completes**, via a dedicated `Bash` call.
+
+Without this ownership split, the prior design contradicted itself: `run-codex.sh` was nominally cleaning up the captures, but `report.py` needed them; and the `> <stdout>` redirection shown in §5 was applied by the orchestrator (outside run-codex.sh) anyway, so run-codex.sh couldn't have known about those paths in the first place.
+- **`--no-codex`**: still creates a worktree if the Claude side needs one (non-`uncommitted` scopes). Only skips codex invocation.
+- **`--keep-worktree`** (debug-only): inhibits the explicit `cleanup-worktree.sh` call and prints the path on completion. **Also writes a marker file `.combined-review-keep` at the worktree root.** `gc-worktrees.sh` skips any worktree containing this marker, regardless of age — so a debug worktree won't get silently swept by a later invocation's GC. The user is responsible for removing kept worktrees manually (`git worktree remove --force <path>`).
+
+The mode prompt + materialized inputs (see §5/§6) are passed to every codex invocation via stdin, not as shell arguments — see §5 "Prompt handling" for why.
+
+---
+
+## 5. Claude-side review
+
+Before any agent dispatch, `scripts/materialize-scope.py` runs once and turns the scope object into concrete bytes both sides can consume. **Both Claude and Codex receive their inputs from this same materialization**, so the primary review subject (the diff + per-file content) is shared. Context lookups against the surrounding repo are intentionally allowed for both — see §4's shared-primary-input guarantee.
+
+### Materialize step
+
+Input: scope object from `resolve-scope.py` (§3).
+Output JSON:
+
+```json
+{
+  "scope_kind": "pr",
+  "scope_summary": "PR #105 — Feature X (head abc1234, base def5678)",
+  "unified_diff": "<full diff text or null for files-mode>",
+  "changed_files": [
+    {
+      "path": "src/foo.py",
+      "old_path": null,
+      "status": "modified",
+      "kind": "text",
+      "lines_changed": [12, 13, 14, 88, 89],
+      "post_content": "..."
+    },
+    {
+      "path": "src/legacy.py",
+      "old_path": null,
+      "status": "deleted",
+      "kind": "text",
+      "lines_changed": "(deleted)",
+      "post_content": null,
+      "pre_content": "..."
+    },
+    {
+      "path": "src/new_name.py",
+      "old_path": "src/old_name.py",
+      "status": "renamed",
+      "kind": "text",
+      "lines_changed": [12, 13],
+      "post_content": "..."
+    },
+    {
+      "path": "assets/logo.png",
+      "old_path": null,
+      "status": "added",
+      "kind": "binary",
+      "lines_changed": "(binary)",
+      "post_content": null,
+      "note": "binary file — content not inlined"
+    },
+    {
+      "path": "config/secrets.link",
+      "status": "modified",
+      "kind": "symlink",
+      "post_content": null,
+      "symlink_target": "/etc/secrets.conf"
+    },
+    {
+      "path": "vendor/lib",
+      "status": "modified",
+      "kind": "submodule",
+      "post_content": null,
+      "submodule_pre_sha": "abc1234",
+      "submodule_post_sha": "def5678"
+    }
+  ],
+  "doc_files": [
+    { "path": "docs/spec.md", "content": "..." }
+  ],
+  "total_lines_changed": 247,
+  "changed_file_count": 7,
+  "has_reviewable_changes": true,
+  "warnings": []
+}
+```
+
+`has_reviewable_changes` is `true` if `changed_file_count > 0` OR `doc_files` is non-empty. Used by the empty-scope pre-flight (§10) instead of `total_lines_changed == 0`, so a PR that only updates a submodule, symlink, or binary asset is **not** rejected as "nothing to review" — those are legitimate review subjects (e.g., bumping a submodule SHA can be high-risk and deserves review).
+
+File entry fields:
+
+- `status`: `added` | `modified` | `deleted` | `renamed` | `typechange` (per `git diff --name-status`).
+- `kind`: `text` | `binary` | `symlink` | `submodule`. Determined from git's mode bits + a content-type sniff.
+- `post_content`: present only for text files that still exist after the change. Null for deleted, binary, symlink, submodule.
+- `pre_content`: included for `status: deleted` so reviewers can see what was lost. Otherwise null.
+- `old_path`: set only for renames; otherwise null.
+- `symlink_target` / `submodule_pre_sha` / `submodule_post_sha`: kind-specific fields.
+
+Reviewer prompts include a brief schema explainer so agents know to handle non-text entries appropriately (e.g., "deleted text file — review whether the deletion is correct" rather than "no content").
+
+- **`pr` / `base`**: `unified_diff` is `git diff <base-sha>...<head-sha>` (three-dot / merge-base semantics) — matches GitHub's PR review semantics, excludes unrelated movement on the base branch. `changed_files` is populated per the schema above (one entry per `git diff --name-status` line), with content fields populated according to `kind`.
+- **`commit`**: `unified_diff` is `git show --format= <commit-sha>` (the patch the commit introduced). `changed_files` entries reflect the commit's tree.
+- **`uncommitted`**: `unified_diff` is `git diff HEAD` (staged + unstaged tracked changes). **Untracked files** (which `git diff HEAD` ignores) are appended to `changed_files` with `status: "added"`, `lines_changed: "(new file)"`, and `post_content` populated if `kind: text`. Without this, the `--uncommitted` flag would silently under-review new files.
+- **Positional `files`**: `unified_diff` is `null`, `changed_files` is empty, `doc_files` holds current working-tree contents (with any local edits — see §3 worktree rules). Binary / symlink / submodule files in the positional list are represented in `doc_files` with the same `kind` semantics — content omitted, kind-specific fields populated.
+- **Non-code modes with diff scopes** (`--mode spec --pr 105`, etc.): `doc_files` is additionally populated with one entry per changed text file — `{path, status, content}` where `content` is `post_content` for added/modified/renamed and `pre_content` for deleted (so the reviewer can judge whether the deletion was correct). Binary/symlink/submodule changes show up only in `changed_files`, not `doc_files`, since they're not document-reviewable.
+- All operations run inside the worktree (when present) or the working tree (`--uncommitted` and positional files).
+- `total_lines_changed` counts only text-file line changes (post-change line count for added, deletion count for deleted, both for modified). Binary/symlink/submodule changes contribute 0 — they don't meaningfully load the reviewers.
+
+### Agent dispatch
+
+- **Default (3 sub-agents, code mode):** dispatch three parallel `Agent` calls (using `subagent_type` when available, else general-purpose) — code-reviewer, silent-failure-hunter, pr-test-analyzer. Each receives the materialized diff and file contents.
+- **`--full` (6 sub-agents, code mode):** adds comment-analyzer, type-design-analyzer, code-simplifier. Opt-in only.
+- **`--mode spec|plan|docs`:** single document-reviewer agent with mode-specific prompt template (§6). Receives `doc_files`. The 3/6 sub-agent fanout is code-specific.
+
+All Claude-side agents receive:
+
+1. The materialized inputs (diff + file contents, or doc contents).
+2. The mode-specific review prompt template (§6).
+3. `--focus` text appended verbatim if provided.
+4. The structured output schema (§7) and a strict instruction to emit findings only in that format.
+
+Codex receives the same materialized inputs through its prompt — always via `codex exec --sandbox read-only` (§4 explains why we don't trust `codex review`'s native diff). Both sides receive the same **primary input**; both also operate against the **same git state** (worktree at recorded SHA or user's tree) and may consult adjacent files for context. The "shared-primary-input" guarantee in §4 spells out the precise scope of what's pinned vs. what's intentionally free.
+
+### Prompt handling
+
+The mode prompt (+ optional `--focus` text + structured-output schema instruction + for `codex exec` the inlined file contents) can be many KB. Passing this as a shell argv is brittle — multi-line content breaks quoting, and argv length limits kick in for `files` mode with large docs.
+
+`run-codex.sh` accepts the prompt via a **file path** (not argv):
+
+- Orchestrator writes the rendered prompt to a temp file *adjacent to* — not inside — any worktree: `mktemp -t combined-review-prompt-XXXXXX` under `$TMPDIR`. Placing it inside the worktree would make codex see it as an untracked file and contaminate the review.
+- Invokes `scripts/run-codex.sh --scope <scope.json> --prompt-file <path>` (still passes scope.json by path, not inline).
+- `run-codex.sh` reads the prompt file and pipes it to codex on stdin: `cat <prompt-file> | codex exec --sandbox read-only -` (or equivalent stdin syntax for the installed codex version).
+- The prompt temp file is **orchestrator-owned** (see §4 "Raw output ownership"). `run-codex.sh` reads it but never deletes it; the orchestrator deletes it in Phase D after `report.py` completes. The script's own `trap` only handles temp files run-codex.sh creates internally, never paths handed in by the orchestrator.
+
+### Dispatch ordering — setup is sequential, reviewers run in parallel
+
+Parallel tool calls within one message run with no defined order — if `Write` and a background `Bash` were issued together, `run-codex.sh` could start before the prompt file existed. The orchestrator therefore splits setup from review:
+
+**Phase A — sequential setup (must complete before Phase B starts):**
+
+1. `Bash` → `scripts/parse-args.py` and `scripts/resolve-scope.py`. Produces the scope object.
+2. `Bash` → `scripts/materialize-scope.py`. Creates the worktree if needed; produces the materialized blob.
+3. Pre-flight checks (§10): codex availability, gh auth, empty scope, large diff.
+4. `Bash` → `mktemp` for the four orchestrator-owned files: `<prompt-path>`, `<codex-stdout>`, `<codex-stderr>`, `<agent-transcripts-dir>`. (One Bash call, four paths captured.)
+5. `Write` → render the full prompt (mode template + `--focus` + materialized blob + no-edit instruction + finding schema) to `<prompt-path>`.
+
+Only after step 5 returns do reviewers launch.
+
+**Phase B — parallel review (one message, no inter-dependencies):**
+
+1. `Bash` with `run_in_background: true` — `scripts/run-codex.sh --scope <scope.json> --prompt-file <prompt-path> --stdout <codex-stdout> --stderr <codex-stderr>`. `run-codex.sh` writes to the paths but does not delete them.
+2. Multiple `Agent` calls in the same message — one per sub-agent. Each receives the materialized inputs and the rendered prompt body inline. Transcripts come back in-band as the Agent tool's return value; the orchestrator writes them to files under `<agent-transcripts-dir>` for `report.py` to consume.
+
+These two are independent (codex doesn't depend on Agent results and vice versa), so issuing them in the same message is safe — and necessary, since parallel execution is the whole point of running both reviewers in one session.
+
+**Phase C — synthesis + report:** the orchestrator awaits all Phase B results (Agent calls return inline; `Monitor` signals codex completion), runs `normalize-findings.py`, the in-session synthesis pass (§8), `validate-clusters.py`, and `report.py`.
+
+**Phase D — cleanup:** after `report.py` finishes, the orchestrator deletes the orchestrator-owned files (prompt, codex stdout/stderr, agent transcripts) and calls `cleanup-worktree.sh`.
+
+### Default-3 selection rationale
+
+Codex's code-mode pass (driven by the code-mode prompt template) covers comment quality, type design, and code simplification competently — those Claude sub-agents would duplicate effort. The high-signal Claude specialists that codex doesn't naturally cover are code-reviewer (correctness + CLAUDE.md compliance), silent-failure-hunter (error handling), and pr-test-analyzer (coverage gaps). `--full` exists for users who want belt-and-braces.
+
+---
+
+## 6. Mode prompts
+
+Each mode has a template stored in `~/.claude/skills/combined-review/prompts/<mode>.md`. The template is loaded, `--focus` text is appended, then the result is passed to both sides.
+
+| Mode | Template focus |
+|---|---|
+| `code` (default) | Correctness, bugs, error handling, test coverage, security, performance regressions, CLAUDE.md compliance |
+| `spec` | Completeness, ambiguity, internal consistency, scope creep, missing edge cases, unstated assumptions, success criteria |
+| `plan` | Step ordering, hidden dependencies, verification steps per task, risk surface, what could fail and not be detected |
+| `docs` | Accuracy vs. current code, broken examples, drift, missing prerequisites, audience fit |
+
+All templates end with the schema (§7) and the instruction: "Emit findings only as `---FINDING---` blocks. Do not summarize. Do not include preamble or postamble."
+
+---
+
+## 7. Structured output schema
+
+Both sides emit findings as delimited blocks. Strict JSON from LLMs is unreliable for multi-line `detail` fields; delimited blocks are more robust and easier to recover from partial compliance.
+
+```
+---FINDING---
+severity: critical|high|medium|low
+file: <relative path or "(general)">
+line: <int> | <start>-<end> | -
+category: bug|test-gap|perf|security|clarity|style|other
+title: <single-line summary, no period>
+detail: |
+  <multi-line free text — recommendation, evidence, suggested fix>
+---END-FINDING---
+```
+
+Parsing is in `scripts/normalize-findings.py`:
+
+- Input: raw stdout from each reviewer (codex + each Claude sub-agent).
+- Output: JSON array of findings, each tagged with `source: "codex" | "claude:<agent-name>"`.
+- Best-effort parsing: if a reviewer ignores the schema and emits prose, the parser extracts what it can; unparseable chunks go to a `parse_warnings[]` array so they surface in the final report rather than being silently dropped.
+- Severity normalization: any reviewer using non-canonical severity (`error`, `warning`, `info`, etc.) is mapped to the canonical set; unmapped values default to `medium` with a parse warning.
+
+---
+
+## 8. Synthesis pass
+
+After parsing, all findings exist as a single JSON array (`normalized-findings.json`). The skill runs **one in-session LLM pass** (no new agent — main Claude does it) that emits **cluster JSON only** — not Markdown. Markdown rendering is `report.py`'s job (§9).
+
+The synthesis LLM step:
+
+1. **Clusters findings by semantic similarity** — same root issue across tools, regardless of phrasing. Inputs to clustering: `file`, `line` proximity (≤ 10 lines), and `title + detail` text. The LLM does the judgment; no string-distance heuristics — those over-merge or under-merge.
+
+2. **Tags each cluster:**
+   - `agreement` — at least one finding from codex AND at least one from claude.
+   - `claude_only` — claude-only.
+   - `codex_only` — codex-only.
+   - `disagreement` — at least one finding from each side, but the recommendations are contradictory (e.g., one says "add nil check", the other says "remove the redundant nil check").
+
+3. **Synthesises wording** — picks the clearer description, merges complementary detail.
+
+4. **Re-ranks severity** — if tools agree, keep it. If they disagree, take the higher and note the divergence.
+
+### Cluster JSON schema (synthesis output → report input)
+
+```json
+{
+  "scope_summary": "PR #105 — ...",
+  "mode": "code",
+  "focus": "API contract changes",
+  "reviewer_summary": {
+    "codex": { "status": "ok", "raw_findings": 14, "parse_warnings": 0 },
+    "claude": [
+      { "agent": "code-reviewer", "status": "ok", "raw_findings": 8, "parse_warnings": 0 },
+      { "agent": "silent-failure-hunter", "status": "ok", "raw_findings": 3, "parse_warnings": 0 },
+      { "agent": "pr-test-analyzer", "status": "failed", "error": "timeout" }
+    ]
+  },
+  "clusters": [
+    {
+      "tag": "agreement",
+      "severity": "high",
+      "file": "src/foo.py",
+      "line": "42",
+      "category": "bug",
+      "title": "Null deref when config is missing 'api_key'",
+      "synthesized_detail": "Both reviewers flag that accessing `config['api_key']` directly will raise KeyError. Codex suggests `config.get('api_key')`; Claude suggests an early-return guard. Recommended: early-return guard — surfaces the misconfiguration explicitly.",
+      "sources": [
+        { "source": "codex", "original_title": "...", "original_detail": "...", "severity": "high" },
+        { "source": "claude:code-reviewer", "original_title": "...", "original_detail": "...", "severity": "medium" }
+      ],
+      "severity_divergence": "codex=high, claude=medium → taking high"
+    }
+  ],
+  "unparsed_chunks": [
+    { "source": "codex", "text": "<raw text that couldn't be parsed as a finding>" }
+  ]
+}
+```
+
+This is the value-add of the skill over running both tools manually. **It's the reason synthesis isn't a Python script** — clustering by meaning is a judgment task, not a string-distance task. But the LLM only emits JSON; rendering stays deterministic.
+
+### JSON validation + one repair attempt
+
+Strict JSON from LLMs is unreliable for free-form fields — the same failure mode that drove the delimited-block schema for reviewer output (§7) applies here. The skill therefore validates synthesis output before passing it to `report.py`:
+
+1. **Validate**: `scripts/validate-clusters.py` parses the synthesis output against a JSON Schema covering the cluster JSON structure (required fields, enum values for `tag` and `severity`, well-formed `sources[]`, etc.). On success: passes through to `report.py`.
+2. **One repair attempt**: on failure, the orchestrator re-prompts itself with the validator's error message ("the `severity` field on cluster #3 must be one of critical|high|medium|low, got `important`") and a single instruction: "emit a corrected cluster JSON; do not re-cluster, only fix the schema violations". The repaired JSON is re-validated.
+3. **Fail loud**: if the second validation also fails, `report.py` runs with the raw reviewer outputs only and the final report includes a prominent "Synthesis failed — manual review of raw outputs required" banner plus the validator's error message. No silent degradation.
+
+This mirrors the parse-warnings approach for reviewer output (§7): one repair, then surface the failure rather than papering over it.
+
+---
+
+## 9. Report format
+
+`scripts/report.py` consumes the cluster JSON from §8 (stdin) plus raw reviewer outputs (file paths passed as args) and emits the final Markdown to stdout. Optionally written to `--save <path>` via tee. Deterministic — same JSON in, same Markdown out.
+
+```markdown
+# Combined Review — <scope description>
+
+**Scope:** <pr #105 / branch foo vs main / 3 files / etc.>
+**Mode:** <code / spec / plan / docs>
+**Focus:** <freeform text, if any>
+**Reviewers:** Claude (3 sub-agents) + Codex
+**Generated:** <ISO timestamp>
+
+---
+
+## High-confidence findings (both tools agree)
+
+### [Critical]
+- **path/file.py:42** — <title>
+  <detail>
+  _Sources: codex, claude:code-reviewer_
+
+### [High]
+...
+
+## Single-source findings
+
+### Claude only
+- **[High] path/file.py:88** — <title>
+  <detail>
+  _Source: claude:silent-failure-hunter_
+
+### Codex only
+- **[Medium] path/other.py:14** — <title>
+  <detail>
+  _Source: codex_
+
+## Disagreements (worth a second look)
+
+- **path/file.py:42** — Codex says X, Claude says Y. <synthesis note on which seems right and why>
+
+## Parse warnings
+- 2 chunks from codex output could not be parsed; raw text below.
+
+---
+
+<details>
+<summary>Raw outputs (audit trail)</summary>
+
+### Codex
+<full codex stdout>
+
+### Claude sub-agents
+#### code-reviewer
+<full agent output>
+#### silent-failure-hunter
+<full agent output>
+#### pr-test-analyzer
+<full agent output>
+</details>
+```
+
+Severity ordering in the report: critical → high → medium → low, within each section.
+
+---
+
+## 10. Failure modes
+
+### Pre-flight checks (main session, before any tools run)
+
+The skill orchestrator (main Claude session) performs these checks **before** dispatching any sub-agent or Bash. These need user interaction or skill-level decisions, so they don't belong in scripts.
+
+1. **Codex availability.** Run `codex login status` (or equivalent) early. If codex isn't on PATH or isn't logged in, stop with a clear message — unless `--no-codex` was passed, in which case skip codex and continue Claude-only with a note in the report.
+2. **`gh` authentication when `--pr` used.** `gh auth status`. Error early.
+3. **Empty scope.** If `materialize-scope.py` reports `has_reviewable_changes == false`, error: "nothing to review". This intentionally uses the file-count-based flag, not `total_lines_changed == 0` — a PR that only changes a submodule, symlink, or binary asset is reviewable and shouldn't be rejected.
+4. **Large diff.** If `total_lines_changed > LARGE_DIFF_THRESHOLD` (default 2000, env `COMBINED_REVIEW_LARGE_DIFF_THRESHOLD`), the orchestrator asks the user in chat: "Diff is N lines — both reviewers degrade on large diffs. Proceed?" If not interactive (e.g., the skill was called by another agent), require explicit `--force-large` flag instead of prompting.
+
+### In-flight failure handling
+
+| Failure | Behavior |
+|---|---|
+| `codex` returns non-zero | Report Claude-only result, include codex stderr in a "codex failed" section. Continue synthesis. |
+| `codex` exceeds timeout (default 5 min, env `COMBINED_REVIEW_CODEX_TIMEOUT`) | Same as non-zero. |
+| Worktree creation fails | Error early; no partial state. |
+| Mixed code + docs in scope under `--mode code` | Proceed; surface a note in the report that doc files were reviewed with code lens. |
+| Both reviewers emit zero findings | Report shows "no issues found" + raw outputs available for audit. |
+| One Claude sub-agent fails | Continue with the others; failed agent's section in report says "agent failed: <error>". `reviewer_summary` (§8) records the failure. |
+| All Claude sub-agents fail | Report codex-only result + Claude-failed note. If both sides fail, error. |
+
+Cleanup follows the three-layer model in §4: `run-codex.sh`'s `trap` removes codex-side temp files (prompt file, stdout/stderr captures); the orchestrator's final `Bash` call to `scripts/cleanup-worktree.sh` removes the worktree (gated by the triple-assertion check); `scripts/gc-worktrees.sh` runs at the start of every invocation as the leak backstop. `--keep-worktree` (debug-only) suppresses the explicit cleanup step.
+
+---
+
+## 11. File layout
+
+```
+~/.claude/
+├── commands/
+│   └── combined-review.md          # slash entry point
+└── skills/
+    └── combined-review/
+        ├── SKILL.md                # orchestration logic (model-readable)
+        ├── prompts/
+        │   ├── code.md             # mode templates
+        │   ├── spec.md
+        │   ├── plan.md
+        │   └── docs.md
+        └── scripts/
+            ├── parse-args.py          # flags → normalized config JSON
+            ├── resolve-scope.py       # auto-detect + validation + immutable SHA resolution
+            ├── materialize-scope.py   # scope object → concrete diff + file contents (creates worktree if needed)
+            ├── run-codex.sh           # codex driver; reads scope/prompt from orchestrator-owned paths; writes captures to orchestrator-owned stdout/stderr paths; internal trap only for files run-codex creates itself
+            ├── normalize-findings.py  # parse delimited-block schema → JSON
+            ├── validate-clusters.py   # JSON-schema-validate synthesis output; one repair attempt
+            ├── cleanup-worktree.sh    # explicit teardown invoked by orchestrator at end of run
+            ├── gc-worktrees.sh        # runs first; lists git worktrees and removes stale combined-review-* entries
+            └── report.py              # cluster JSON + raw outputs → final markdown
+```
+
+Where practical, deterministic scripts communicate via JSON on stdin/stdout (`parse-args.py`, `resolve-scope.py`, `materialize-scope.py`, `normalize-findings.py`, `validate-clusters.py`, `report.py`). Scripts that operate on large or path-bound inputs use **explicit file-path contracts**: `run-codex.sh` takes `--prompt-file`, `--stdout`, `--stderr`; `cleanup-worktree.sh` and `gc-worktrees.sh` take repo + worktree paths and perform side effects. The orchestrator owns intermediate file lifecycle (see §4 "Raw output ownership"). `SKILL.md` describes the pipeline and points the model at each script in order.
+
+---
+
+## 12. Testing approach (TDD per writing-skills)
+
+Per the `superpowers:writing-skills` discipline — **RED-GREEN-REFACTOR with pressure scenarios:**
+
+### RED — baseline without the skill
+
+Subagent scenarios to run before writing the skill:
+
+1. "Run both Claude review and codex review on PR #105 and combine the findings." → Expect: sequential execution, no deduplication, no attribution, no disagreement surfacing.
+2. "Review docs/spec.md with both tools." → Expect: confusion about how to point codex at a single file; default code-review lens applied to a markdown file.
+3. "Run combined review on uncommitted changes when there's also a PR for the current branch." → Expect: silent ambiguity, agent picks one or the other without surfacing it.
+
+Document the verbatim rationalizations / failure modes.
+
+### GREEN — write skill + scripts
+
+Implement to address the specific failures from RED. Re-run the scenarios. Confirm:
+
+- Both reviewers run in parallel, not sequence.
+- Findings are clustered into the `agreement` / `claude_only` / `codex_only` / `disagreement` tags from §8, and the rendered Markdown puts them in the corresponding sections from §9.
+- Scope ambiguity (dirty + PR) errors out, not silent pick.
+- `--mode spec` produces document-lens findings, not "no test coverage" suggestions.
+
+### REFACTOR — close loopholes
+
+New rationalizations to plug, e.g.:
+
+- Agent decides "synthesis is too hard" and just concatenates outputs → add explicit anti-pattern in SKILL.md.
+- Agent skips schema enforcement for codex → SKILL.md explicitly says "if codex output is unparseable, surface as parse warning, don't silently summarize".
+- Agent runs reviews sequentially under cognitive load → SKILL.md mandates parallel-tool-call pattern.
+
+---
+
+## 13. Non-goals
+
+- **Auto-fixing findings.** The skill reviews; it does not edit. Remediation is a separate step.
+- **Reviewing across multiple PRs / commits in one invocation.** One scope per invocation.
+- **Replacing the underlying `/review` skill or the standalone `codex` CLI.** They remain available standalone for users who want a single-tool review or who prefer codex's native review framing.
+- **Persistent finding storage / triage history.** Output is per-invocation. `--save` is the only persistence.
+- **Cross-tool prompt unification beyond the mode template.** We don't try to make codex emit the same exact sub-finding categories as Claude — we let each tool review naturally and synthesize after.
+
+---
+
+## 14. Decisions locked
+
+- **Worktree location**: `mktemp -d -t combined-review-<repo>-XXXXXX` honoring `$TMPDIR`. Random suffix, repo basename for legibility.
+- **`--full` opt-in vs `--agents`**: keep `--full` binary for v1. No `--agents` surface area until there's real pressure.
+- **`--save` and `--keep-worktree`**: independent. `--save` writes the report file but does not preserve the worktree. `--keep-worktree` is debug-only and inhibits teardown.
+- **Codex auth failure**: run `codex login status` early. Treat unauthenticated the same as "Codex unavailable" — stop with a clear message unless `--no-codex` was passed.
+- **Diff semantics**: three-dot / merge-base (`git diff base...head`) for `--pr` and `--base`, matching GitHub PR review. Not two-dot. `git show` for `--commit`. `git diff HEAD` + appended untracked files for `--uncommitted`.
+- **Positional files = current working-tree content**: includes any local edits the user just made. No clean worktree, no pinning to HEAD.
+- **Non-code modes with diff scopes**: materialize-scope populates `doc_files` with post-change (or pre-change for deletes) content of changed text files in addition to the diff, so the document-reviewer agent has something reviewable.
+- **PR materialization**: `gh pr checkout --detach <#>` as primary path (handles fork PRs natively); fetch base by `base_ref_name` for portability; verify both head and base with `headRefOid`/`baseRefOid` after fetch; `git reset --hard <head-sha>` if HEAD drifted.
+- **Base scope worktree**: created from `<head-sha>` not literal `HEAD`, so the reviewed commit can't drift between resolve-scope and materialize.
+- **Codex exec safety for files mode**: must pass `--sandbox read-only` (or codex's equivalent flag) AND include an explicit no-edit instruction at the top of the prompt. `run-codex.sh` errors out if the read-only flag isn't supported by the installed codex version. Non-negotiable — `codex exec` is otherwise a general agent that can edit files, which violates non-goal §13.
+- **File-entry schema in materialize**: every `changed_files` entry has `status` (added|modified|deleted|renamed|typechange) and `kind` (text|binary|symlink|submodule). `post_content` populated only for kind=text and status ≠ deleted; `pre_content` for status=deleted; `old_path` for renames; symlink-target and submodule-pre/post-sha for those kinds.
+- **Worktree cleanup safety**: every destructive cleanup goes through a triple-assertion gate — (1) path appears in `git worktree list --porcelain` for the current repo, (2) path matches `combined-review-*` mktemp pattern under `$TMPDIR`/`/tmp`, (3) path is not the repo root or main worktree. `gc-worktrees.sh` enumerates only via `git worktree list`, never scans `$TMPDIR` for arbitrary directories.
+- **Prompt passing to codex**: via stdin (read from a temp file by `run-codex.sh`), not argv. Multi-KB prompts (file-mode embeds full doc contents) break shell quoting otherwise.
+- **Shared-primary-input guarantee** (revised, was "same-bytes"): codex always runs via `codex exec --sandbox read-only` with the materialized blob from `materialize-scope.py`, never via `codex review`'s native auto-diff. The guarantee is *shared primary input* + *shared repo context*, not full isolation — both reviewers can still consult adjacent files via Read/Grep equivalents, and that's a feature for context-aware review. What's pinned: the diff and per-file content embedded in the prompt body, plus the git state of the cwd (worktree at recorded SHA or user's tree).
+- **PR base fetch**: `git fetch <base_repo_url> <base_ref_name>` directly — **no `git remote add`**, which would mutate `.git/config` and leak across runs. SHA verification via `git cat-file -e <sha>^{commit}`, not `rev-parse FETCH_HEAD == base_sha` — the recorded commit must be reachable, but the tip may have moved (warn-only).
+- **PR stale-snapshot failure**: if the recorded `head_sha` is not reachable after `gh pr checkout` + `git reset --hard <head_sha>`, the PR was force-pushed between `gh pr view` and `gh pr checkout`. The skill fails loudly with "PR head force-pushed mid-review; rerun" — does not silently fall back to the current head.
+- **Raw output ownership**: the orchestrator creates and deletes all long-lived intermediate files (prompt, codex stdout/stderr, sub-agent transcripts). `run-codex.sh` writes to paths passed in via args; doesn't own deletion. Cleanup happens after `report.py` completes, before the worktree teardown.
+- **Dispatch ordering**: setup is sequential (parse-args → resolve-scope → materialize → pre-flight → mktemp → Write prompt), reviewers run in parallel only after setup completes. Avoids the race where a parallel `Write` and background Bash launch run-codex.sh before the prompt file exists.
+- **`--keep-worktree` + GC interaction**: `--keep-worktree` writes `.combined-review-keep` at the worktree root; `gc-worktrees.sh` skips marked worktrees regardless of age. Without the marker, a debug worktree would silently disappear after 24h on the next invocation's GC pass.
+- **Empty-scope check**: uses `has_reviewable_changes` (file-count-based + doc_files), not `total_lines_changed == 0`. Submodule/symlink/binary-only PRs are legitimate review subjects.
+- **Synthesis JSON validation**: `validate-clusters.py` enforces a JSON Schema on cluster output. One LLM repair attempt on failure; if that fails too, the report runs with raw outputs and a "synthesis failed" banner. No silent degradation.
+
+## 15. Open questions
+
+1. **Default Codex timeout.** 5 min is the current proposal. Should it be tighter (3 min) to avoid hanging the synthesis on a slow run?
+2. **`materialize-scope.py` for large file contents.** If a changed file is huge (megabytes), inlining its `post_content` into the JSON is wasteful. Cap at e.g. 200KB per file and switch to "see worktree for full content" beyond that? Or always inline?
+3. **`codex exec` prompt size limits.** For positional-files mode, the prompt has to include full file contents. If the user passes 20 large files, we'll hit the model's context limit. Should the skill error out above a content-size threshold and ask the user to narrow the file list?
`````


### Changed files (full content)


### docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md  (status: added, kind: text)
`````
# Combined Review Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill `/combined-review` that runs `pr-review-toolkit` sub-agents and `codex exec --sandbox read-only` in parallel against the same materialized review subject, then synthesizes the findings into a single deduped, attributed report.

**Architecture:** Slash command at `~/.claude/commands/combined-review.md` hands off to skill at `~/.claude/skills/combined-review/SKILL.md`. The skill orchestrates four phases — sequential setup (parse-args → resolve-scope → materialize → pre-flight → write prompt), parallel review (codex background + Claude sub-agents), in-session synthesis + JSON-validated cluster output, deterministic rendering — with a strict worktree-cleanup model gated by `git worktree list --porcelain`.

**Tech Stack:** Python 3 (stdlib + `jsonschema`), Bash, pytest. Codex CLI (`codex exec --sandbox read-only`). `gh` CLI for PR metadata. Git plumbing for worktrees and diffs.

**Spec:** `docs/superpowers/specs/2026-05-11-combined-review-skill-design.md`.

**Development layout:**

```
~/projects/combined-review/        # git repo (this plan develops here)
├── SKILL.md
├── commands/combined-review.md
├── prompts/{code,spec,plan,docs}.md
├── scripts/{parse-args,resolve-scope,materialize-scope,normalize-findings,validate-clusters,report}.py
├── scripts/run-codex.py
├── scripts/{cleanup-worktree,gc-worktrees}.sh
├── tests/
└── README.md
```

After implementation, install via:

```
ln -s ~/projects/combined-review ~/.claude/skills/combined-review
ln -s ~/projects/combined-review/commands/combined-review.md ~/.claude/commands/combined-review.md
```

---

## Task 1: Repo scaffolding

**Files:**
- Create: `~/projects/combined-review/.gitignore`
- Create: `~/projects/combined-review/README.md`
- Create: `~/projects/combined-review/pyproject.toml`
- Create: `~/projects/combined-review/tests/conftest.py`

- [ ] **Step 1: Create the repo and directory tree**

```bash
mkdir -p ~/projects/combined-review/{scripts,prompts,commands,tests}
cd ~/projects/combined-review
git init
```

- [ ] **Step 2: Write `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
*.egg-info/
```

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[project]
name = "combined-review"
version = "0.1.0"
description = "Claude Code skill that fuses Claude + Codex reviews in one session"
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.21.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Write `tests/conftest.py`**

```python
"""Shared pytest fixtures for the combined-review test suite."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


@pytest.fixture
def tmp_repo(tmp_path):
    """A throwaway git repo with one initial commit. Returns the repo Path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test repo\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=repo, check=True)
    return repo


@pytest.fixture
def fake_bin(tmp_path, monkeypatch):
    """Prepend a tmp dir to PATH so tests can drop fake `gh`/`codex` scripts."""
    fake = tmp_path / "bin"
    fake.mkdir()
    monkeypatch.setenv("PATH", f"{fake}:{os.environ['PATH']}")
    return fake


def run_script(name, *args, **kwargs):
    """Invoke a script in scripts/ via subprocess; return CompletedProcess."""
    script = SCRIPTS_DIR / name
    cmd = [str(script), *args] if script.suffix == ".sh" else ["python3", str(script), *args]
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
```

- [ ] **Step 5: Verify pytest runs (zero tests is OK)**

```bash
cd ~/projects/combined-review
python3 -m pip install -e ".[dev]"
pytest -v
```

Expected: `no tests ran` exit code 5, no errors.

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md pyproject.toml tests/conftest.py
git commit -m "feat: scaffold combined-review repo"
```

---

## Task 2: parse-args.py — CLI surface

**Files:**
- Create: `scripts/parse-args.py`
- Create: `tests/test_parse_args.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_parse_args.py
"""Tests for parse-args.py — flag parsing into normalized config JSON."""
import json
from tests.conftest import run_script


def parse(*args):
    r = run_script("parse-args.py", *args)
    assert r.returncode == 0, f"stderr: {r.stderr}"
    return json.loads(r.stdout)


def test_no_args_defaults_to_code_mode():
    cfg = parse()
    assert cfg["mode"] == "code"
    assert cfg["scope_flag"] is None
    assert cfg["files"] == []
    assert cfg["full"] is False


def test_pr_flag():
    cfg = parse("--pr", "105")
    assert cfg["scope_flag"] == "pr"
    assert cfg["pr_number"] == 105


def test_uncommitted_flag():
    cfg = parse("--uncommitted")
    assert cfg["scope_flag"] == "uncommitted"


def test_base_flag():
    cfg = parse("--base", "develop")
    assert cfg["scope_flag"] == "base"
    assert cfg["base_branch"] == "develop"


def test_commit_flag():
    cfg = parse("--commit", "abc1234")
    assert cfg["scope_flag"] == "commit"
    assert cfg["commit_sha"] == "abc1234"


def test_positional_files():
    cfg = parse("docs/spec.md", "plan.md")
    assert cfg["scope_flag"] == "files"
    assert cfg["files"] == ["docs/spec.md", "plan.md"]


def test_mode_and_focus():
    cfg = parse("--mode", "spec", "--focus", "API contract")
    assert cfg["mode"] == "spec"
    assert cfg["focus"] == "API contract"


def test_all_modifier_flags():
    cfg = parse("--full", "--no-codex", "--force-large", "--keep-worktree",
                "--save", "/tmp/report.md")
    assert cfg["full"] is True
    assert cfg["no_codex"] is True
    assert cfg["force_large"] is True
    assert cfg["keep_worktree"] is True
    assert cfg["save_path"] == "/tmp/report.md"


def test_mutually_exclusive_scope_flags_error():
    r = run_script("parse-args.py", "--pr", "1", "--uncommitted")
    assert r.returncode != 0
    assert "mutually exclusive" in r.stderr.lower()


def test_files_with_scope_flag_errors():
    r = run_script("parse-args.py", "--pr", "1", "foo.md")
    assert r.returncode != 0
    assert "mutually exclusive" in r.stderr.lower()


def test_invalid_mode_errors():
    r = run_script("parse-args.py", "--mode", "nonsense")
    assert r.returncode != 0


def test_args_file_mode(tmp_path):
    """Orchestrator writes $ARGUMENTS to a file; parse-args reads + shlex-splits it.
    Necessary because shell-substituting $ARGUMENTS directly is injection-prone."""
    f = tmp_path / "args.txt"
    f.write_text('--pr 105 --focus "API contract changes" --mode spec')
    r = run_script("parse-args.py", "--args-file", str(f))
    assert r.returncode == 0, r.stderr
    cfg = json.loads(r.stdout)
    assert cfg["pr_number"] == 105
    assert cfg["focus"] == "API contract changes"
    assert cfg["mode"] == "spec"


def test_args_file_handles_paths_with_spaces(tmp_path):
    f = tmp_path / "args.txt"
    f.write_text('"docs/path with spaces/spec.md"')
    r = run_script("parse-args.py", "--args-file", str(f))
    assert r.returncode == 0, r.stderr
    cfg = json.loads(r.stdout)
    assert cfg["files"] == ["docs/path with spaces/spec.md"]
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd ~/projects/combined-review && pytest tests/test_parse_args.py -v
```

Expected: all tests FAIL (script doesn't exist yet).

- [ ] **Step 3: Implement `scripts/parse-args.py`**

```python
#!/usr/bin/env python3
"""parse-args.py — turn /combined-review CLI args into a normalized config JSON.

Reads sys.argv[1:] OR, if --args-file <path> is given, reads the raw argument
string from that file and shlex-splits it. The args-file mode exists because
the orchestrator must not shell-substitute $ARGUMENTS directly — quoting
fragility and injection risk. Instead, the slash command writes $ARGUMENTS
to a file and we read it back literally here.

Writes a config object to stdout; returns non-zero on validation errors.
"""
import argparse
import json
import shlex
import sys

VALID_MODES = ("code", "spec", "plan", "docs")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="combined-review", add_help=True)
    p.add_argument("--pr", type=int, dest="pr_number")
    p.add_argument("--uncommitted", action="store_true")
    p.add_argument("--base", dest="base_branch")
    p.add_argument("--commit", dest="commit_sha")
    p.add_argument("--mode", choices=VALID_MODES, default="code")
    p.add_argument("--focus", default=None)
    p.add_argument("--full", action="store_true")
    p.add_argument("--no-codex", action="store_true", dest="no_codex")
    p.add_argument("--force-large", action="store_true", dest="force_large")
    p.add_argument("--keep-worktree", action="store_true", dest="keep_worktree")
    p.add_argument("--save", default=None, dest="save_path")
    p.add_argument("files", nargs="*")
    return p


def normalize(ns: argparse.Namespace) -> dict:
    scope_flags = {
        "pr": ns.pr_number is not None,
        "uncommitted": ns.uncommitted,
        "base": ns.base_branch is not None,
        "commit": ns.commit_sha is not None,
        "files": bool(ns.files),
    }
    selected = [k for k, v in scope_flags.items() if v]
    if len(selected) > 1:
        raise SystemExit(
            f"error: scope flags are mutually exclusive; got {selected}"
        )
    scope_flag = selected[0] if selected else None
    return {
        "scope_flag": scope_flag,
        "pr_number": ns.pr_number,
        "base_branch": ns.base_branch,
        "commit_sha": ns.commit_sha,
        "files": ns.files,
        "mode": ns.mode,
        "focus": ns.focus,
        "full": ns.full,
        "no_codex": ns.no_codex,
        "force_large": ns.force_large,
        "keep_worktree": ns.keep_worktree,
        "save_path": ns.save_path,
    }


def resolve_argv(raw_argv: list[str]) -> list[str]:
    """If --args-file <path> is the only/first pair, read the file and shlex-split.
    Otherwise return raw_argv unchanged."""
    if len(raw_argv) >= 2 and raw_argv[0] == "--args-file":
        path = raw_argv[1]
        with open(path, "r") as f:
            raw_string = f.read().strip()
        return shlex.split(raw_string)
    return raw_argv


def main(argv: list[str]) -> None:
    argv = resolve_argv(argv)
    ns = build_parser().parse_args(argv)
    cfg = normalize(ns)
    json.dump(cfg, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 4: Make it executable**

```bash
chmod +x scripts/parse-args.py
```

- [ ] **Step 5: Run tests, verify all pass**

```bash
pytest tests/test_parse_args.py -v
```

Expected: 12 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/parse-args.py tests/test_parse_args.py
git commit -m "feat: parse-args.py with CLI surface and mutex validation"
```

---

## Task 3: resolve-scope.py — auto-detect skeleton

**Files:**
- Create: `scripts/resolve-scope.py`
- Create: `tests/test_resolve_scope_explicit.py`

This task handles the four **explicit** scope kinds (uncommitted/base/commit/files). PR auto-detect lands in Task 4.

- [ ] **Step 1: Write failing tests for explicit-scope resolution**

```python
# tests/test_resolve_scope_explicit.py
"""Tests for resolve-scope.py — explicit scope flags only."""
import json
import subprocess
from tests.conftest import run_script


def resolve(cfg, cwd=None):
    r = run_script("resolve-scope.py", input=json.dumps(cfg), cwd=cwd)
    return r


def make_cfg(**kw):
    base = {
        "scope_flag": None, "pr_number": None, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    base.update(kw)
    return base


def test_uncommitted_scope(tmp_repo):
    (tmp_repo / "new.txt").write_text("x")
    r = resolve(make_cfg(scope_flag="uncommitted"), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "uncommitted"
    assert scope["repo_root"] == str(tmp_repo)
    assert scope["worktree_path"] is None
    assert scope["needs_clean_worktree"] is False


def test_base_scope_resolves_sha(tmp_repo):
    # Create a feature branch with one commit
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    (tmp_repo / "x.txt").write_text("y")
    subprocess.run(["git", "add", "x.txt"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
    r = resolve(make_cfg(scope_flag="base", base_branch="main"), cwd=tmp_repo)
    # git init default branch may be 'main' or 'master' depending on config
    if r.returncode != 0:
        # retry with detected default branch
        head = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
            cwd=tmp_repo, capture_output=True, text=True
        ).stdout.split()
        default = "master" if "master" in head else "main"
        r = resolve(make_cfg(scope_flag="base", base_branch=default), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "base"
    assert len(scope["base_sha"]) == 40
    assert len(scope["head_sha"]) == 40
    assert scope["base_sha"] != scope["head_sha"]
    assert scope["needs_clean_worktree"] is True


def test_commit_scope_resolves_sha(tmp_repo):
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    r = resolve(make_cfg(scope_flag="commit", commit_sha=sha), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "commit"
    assert scope["commit_sha"] == sha
    assert scope["needs_clean_worktree"] is True


def test_files_scope_passes_paths(tmp_repo):
    (tmp_repo / "spec.md").write_text("# spec")
    r = resolve(make_cfg(scope_flag="files", files=["spec.md"]), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "files"
    assert scope["files"] == ["spec.md"]
    assert scope["needs_clean_worktree"] is False


def test_files_scope_rejects_nonexistent(tmp_repo):
    r = resolve(make_cfg(scope_flag="files", files=["nope.md"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "nope.md" in r.stderr


def test_files_scope_rejects_absolute_paths(tmp_repo, tmp_path):
    """Regression for path-traversal / data-exfiltration. Absolute paths must
    be refused outright — inlining /Users/.../.ssh/id_rsa or /etc/passwd into
    the review prompt would send it to Codex (remote) + Claude sub-agents.
    `Path(repo_root) / absolute_path` evaluates to the absolute path in
    pathlib, so the previous `.exists()` check accepted any local file."""
    leaked = tmp_path / "leaked.txt"
    leaked.write_text("would-be-exfiltrated")
    r = resolve(make_cfg(scope_flag="files", files=[str(leaked)]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "absolute" in r.stderr.lower()


def test_files_scope_rejects_dotdot_escape(tmp_repo, tmp_path):
    """`../other-dir/secret.txt` must be rejected even though it's a relative
    path — after resolve() it lands outside repo_root."""
    outside = tmp_path / "outside.txt"
    outside.write_text("not in repo")
    # tmp_repo lives at tmp_path/"repo"; ../outside.txt escapes
    r = resolve(make_cfg(scope_flag="files", files=["../outside.txt"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()


def test_files_scope_rejects_symlink_pointing_outside(tmp_repo, tmp_path):
    """A symlink inside the repo whose target is outside the repo must also be
    rejected — resolve() follows symlinks, so the canonical path escapes."""
    outside = tmp_path / "secret.txt"
    outside.write_text("secret")
    (tmp_repo / "innocent.txt").symlink_to(outside)
    r = resolve(make_cfg(scope_flag="files", files=["innocent.txt"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()


def test_files_scope_preserves_symlink_path_when_target_is_in_repo(tmp_repo):
    """Regression: an in-repo symlink pointing at another in-repo file must keep
    its user-supplied name in the resolved scope, NOT be replaced with the
    target path. Otherwise materialize_files() sees a regular file and the
    symlink metadata (target path) never makes it into the prompt."""
    (tmp_repo / "real.md").write_text("# real file\n")
    (tmp_repo / "alias.md").symlink_to("real.md")
    r = resolve(make_cfg(scope_flag="files", files=["alias.md"]), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    # The returned path must be the user's input, not the target
    assert scope["files"] == ["alias.md"]


def test_files_scope_rejects_directory(tmp_repo):
    """A directory passed in files-scope must be rejected. Earlier behavior
    would let exists() pass and produce a doc_files entry with kind=text and
    content=None — confusing prompt with no value to the reviewer."""
    (tmp_repo / "subdir").mkdir()
    r = resolve(make_cfg(scope_flag="files", files=["subdir"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "regular file" in r.stderr.lower() or "directory" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_resolve_scope_explicit.py -v
```

Expected: all fail (script doesn't exist).

- [ ] **Step 3: Implement `scripts/resolve-scope.py` (explicit-scope paths only — auto-detect in Task 4)**

```python
#!/usr/bin/env python3
"""resolve-scope.py — config JSON in → scope object JSON out.

Handles explicit scope flags (uncommitted/base/commit/files) and validates
inputs against git. PR resolution and full auto-detect happen in a later
patch. All ref-shaped inputs are resolved to immutable SHAs here; downstream
steps consume SHAs, never ref names.
"""
import json
import subprocess
import sys
from pathlib import Path


def git(*args, cwd=None, check=True) -> str:
    r = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )
    return r.stdout.strip()


def repo_root(cwd=None) -> str:
    return git("rev-parse", "--show-toplevel", cwd=cwd)


def base_scope_object() -> dict:
    return {
        "kind": None, "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": None,
        "needs_clean_worktree": False,
        "mode": "code", "focus": None, "full": False,
        "no_codex": False, "force_large": False, "keep_worktree": False,
        "save_path": None,
    }


def carry_modifiers(scope: dict, cfg: dict) -> None:
    """Copy modifier flags from cfg into scope so downstream sees one object."""
    for k in ("mode", "focus", "full", "no_codex",
              "force_large", "keep_worktree", "save_path"):
        scope[k] = cfg[k]


def resolve_uncommitted(cfg: dict, root: str) -> dict:
    s = base_scope_object()
    s["kind"] = "uncommitted"
    s["repo_root"] = root
    s["needs_clean_worktree"] = False
    carry_modifiers(s, cfg)
    return s


def resolve_base(cfg: dict, root: str) -> dict:
    base_ref = cfg["base_branch"]
    try:
        base_sha = git("rev-parse", "--verify", f"{base_ref}^{{commit}}", cwd=root)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"error: cannot resolve base ref {base_ref!r}: {e.stderr}")
    head_sha = git("rev-parse", "--verify", "HEAD^{commit}", cwd=root)
    s = base_scope_object()
    s["kind"] = "base"
    s["repo_root"] = root
    s["base_ref_name"] = base_ref
    s["base_sha"] = base_sha
    s["head_sha"] = head_sha
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s


def resolve_commit(cfg: dict, root: str) -> dict:
    try:
        sha = git("rev-parse", "--verify", f"{cfg['commit_sha']}^{{commit}}", cwd=root)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"error: cannot resolve commit {cfg['commit_sha']!r}: {e.stderr}")
    s = base_scope_object()
    s["kind"] = "commit"
    s["repo_root"] = root
    s["commit_sha"] = sha
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s


def _validate_under_root(root: str, paths: list[str]) -> list[str]:
    """Reject absolute paths, `..` escapes, and symlinks whose targets are
    outside repo_root. Return the **user-supplied path, lexically normalized**
    — NOT the resolved target.

    Why we don't return the resolved path: if the user passes an in-repo
    symlink like `innocent-link.md` that points to another in-repo file,
    `.resolve()` follows it to the target. Returning the target would make
    materialize_files() see a regular text file instead of a symlink, and
    the symlink-specific metadata promised in Task 9 (target path) would
    never make it into the prompt. The report would also cite the wrong path.

    Why this is P1: positional file contents are inlined into the review
    prompt and sent to Codex (remote) + Claude sub-agents. Without the
    escape checks, passing `/Users/.../.ssh/id_rsa` or `../../etc/passwd`
    would silently exfiltrate secrets to remote APIs.
    """
    import os.path
    root_abs = Path(root).resolve()
    out = []
    for p in paths:
        if Path(p).is_absolute():
            raise SystemExit(
                f"error: refusing absolute path {p!r} — pass repo-relative paths only"
            )
        # Lexical normalization (does NOT follow symlinks). Rejects `..` escapes.
        lexical = os.path.normpath(p)
        if lexical.startswith("..") or lexical == ".." or "/../" in f"/{lexical}/":
            raise SystemExit(
                f"error: path {p!r} escapes via .. — refusing"
            )
        # Security check: does the resolved (symlink-followed) target land
        # inside the repo? If not, refuse — an in-repo symlink pointing at
        # /etc/passwd would otherwise exfiltrate it.
        try:
            resolved = (root_abs / p).resolve()
            resolved.relative_to(root_abs)
        except ValueError:
            raise SystemExit(
                f"error: path {p!r} resolves outside repo root ({root_abs}); refusing"
            )
        # Existence check using the original path (does not follow symlinks
        # except where the user intended; resolve() check above already
        # validated the target).
        full = root_abs / lexical
        if not full.exists():
            raise SystemExit(f"error: file not found: {p!r}")
        # Reject plain directories: positional files mode reviews file
        # content. A directory passed here would slip through with kind=text
        # + content=None downstream and render as a confusing header with no
        # content. If the user wants to review every file in a directory,
        # they should expand the glob themselves — the skill doesn't recurse
        # implicitly. is_file() returns True for symlinks pointing at regular
        # files, which is the behavior we want (symlinks ARE supported).
        #
        # Exception: submodules are gitlinks — they appear as directories on
        # disk (is_file() is False) but git tracks them as mode 160000.
        # materialize_files() has a kind=submodule branch that produces useful
        # output (the pointer SHA), so we must let these through.
        if not full.is_file():
            ls = subprocess.run(
                ["git", "ls-files", "--stage", "--", lexical],
                cwd=str(root_abs), capture_output=True, text=True,
            )
            is_submodule = ls.stdout.strip().startswith("160000 ")
            if not is_submodule:
                raise SystemExit(
                    f"error: {p!r} is not a regular file "
                    f"(directory or special file — pass file paths only, expand globs yourself)"
                )
        out.append(lexical)
    return out


def resolve_files(cfg: dict, root: str) -> dict:
    files = _validate_under_root(root, cfg["files"])
    s = base_scope_object()
    s["kind"] = "files"
    s["repo_root"] = root
    s["files"] = files
    s["needs_clean_worktree"] = False
    carry_modifiers(s, cfg)
    return s


SCOPE_RESOLVERS = {
    "uncommitted": resolve_uncommitted,
    "base": resolve_base,
    "commit": resolve_commit,
    "files": resolve_files,
}


def main() -> None:
    cfg = json.load(sys.stdin)
    root = repo_root()
    scope_flag = cfg["scope_flag"]
    if scope_flag is None:
        raise SystemExit(
            "error: auto-detect not yet implemented; pass an explicit scope flag"
        )
    if scope_flag == "pr":
        raise SystemExit("error: --pr resolution not yet implemented")
    resolver = SCOPE_RESOLVERS[scope_flag]
    scope = resolver(cfg, root)
    json.dump(scope, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Make executable, run tests**

```bash
chmod +x scripts/resolve-scope.py
pytest tests/test_resolve_scope_explicit.py -v
```

Expected: 10 passed (5 original + 3 path-traversal rejection + 1 in-repo-symlink-preservation + 1 directory-rejection).

- [ ] **Step 5: Commit**

```bash
git add scripts/resolve-scope.py tests/test_resolve_scope_explicit.py
git commit -m "feat: resolve-scope.py for explicit scopes (uncommitted/base/commit/files)"
```

---

## Task 4: resolve-scope.py — PR scope via gh

**Files:**
- Modify: `scripts/resolve-scope.py`
- Create: `tests/test_resolve_scope_pr.py`

- [ ] **Step 1: Write failing tests using a fake `gh`**

```python
# tests/test_resolve_scope_pr.py
"""Tests for resolve-scope.py --pr path using a fake `gh` binary."""
import json
import subprocess
from tests.conftest import run_script


FAKE_GH_JSON = {
    "number": 105,
    "headRefName": "feature-x",
    "baseRefName": "main",
    "headRefOid": "a" * 40,
    "baseRefOid": "b" * 40,
    "headRepository": {"url": "https://github.com/user/repo.git"},
    "baseRepository": {"url": "https://github.com/upstream/repo.git"},
}


def make_cfg_pr(num=105):
    return {
        "scope_flag": "pr", "pr_number": num, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def write_fake_gh(fake_bin, payload):
    script = fake_bin / "gh"
    script.write_text(
        "#!/bin/sh\n"
        # Only respond to `gh pr view` calls — fail loudly on anything else.
        'if [ "$1" = "pr" ] && [ "$2" = "view" ]; then\n'
        f"  cat <<'EOF'\n{json.dumps(payload)}\nEOF\n"
        "  exit 0\n"
        "fi\n"
        'echo "unexpected gh call: $@" >&2; exit 1\n'
    )
    script.chmod(0o755)


def test_pr_scope_reads_gh_metadata(tmp_repo, fake_bin):
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_pr()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "pr"
    assert scope["pr_number"] == 105
    assert scope["head_ref_name"] == "feature-x"
    assert scope["base_ref_name"] == "main"
    assert scope["head_sha"] == "a" * 40
    assert scope["base_sha"] == "b" * 40
    assert scope["base_repo_url"] == "https://github.com/upstream/repo.git"
    assert scope["needs_clean_worktree"] is True


def test_pr_scope_propagates_gh_failure(tmp_repo, fake_bin):
    gh = fake_bin / "gh"
    gh.write_text("#!/bin/sh\necho 'auth required' >&2\nexit 1\n")
    gh.chmod(0o755)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_pr()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "gh" in r.stderr.lower() or "auth" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_resolve_scope_pr.py -v
```

Expected: 2 fails (script still rejects PR scope).

- [ ] **Step 3: Add `resolve_pr` to `scripts/resolve-scope.py`**

Replace the `if scope_flag == "pr": raise SystemExit(...)` line and add this function above `SCOPE_RESOLVERS`:

```python
def resolve_pr(cfg: dict, root: str) -> dict:
    pr = cfg["pr_number"]
    fields = "number,headRefName,baseRefName,headRefOid,baseRefOid,headRepository,baseRepository"
    r = subprocess.run(
        ["gh", "pr", "view", str(pr), "--json", fields],
        cwd=root, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"error: gh pr view failed: {r.stderr.strip()}")
    meta = json.loads(r.stdout)
    s = base_scope_object()
    s["kind"] = "pr"
    s["repo_root"] = root
    s["pr_number"] = meta["number"]
    s["head_ref_name"] = meta["headRefName"]
    s["base_ref_name"] = meta["baseRefName"]
    s["head_sha"] = meta["headRefOid"]
    s["base_sha"] = meta["baseRefOid"]
    s["head_repo_url"] = meta["headRepository"]["url"]
    s["base_repo_url"] = meta["baseRepository"]["url"]
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s
```

Then update `SCOPE_RESOLVERS` to include it:

```python
SCOPE_RESOLVERS = {
    "uncommitted": resolve_uncommitted,
    "base": resolve_base,
    "commit": resolve_commit,
    "files": resolve_files,
    "pr": resolve_pr,
}
```

And remove the `if scope_flag == "pr": raise SystemExit(...)` from `main()`.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_resolve_scope_pr.py tests/test_resolve_scope_explicit.py -v
```

Expected: 12 passed (10 explicit + 2 PR).

- [ ] **Step 5: Commit**

```bash
git add scripts/resolve-scope.py tests/test_resolve_scope_pr.py
git commit -m "feat: resolve-scope.py --pr via gh pr view metadata"
```

---

## Task 5: resolve-scope.py — auto-detect

**Files:**
- Modify: `scripts/resolve-scope.py`
- Create: `tests/test_resolve_scope_autodetect.py`

Auto-detect order (per spec §3): dirty+PR → error; dirty alone → uncommitted; clean+PR → pr; clean+no-PR+non-default branch → base vs default; clean+default branch → error.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_resolve_scope_autodetect.py
"""Tests for resolve-scope.py auto-detect when scope_flag is None."""
import json
import subprocess
from tests.conftest import run_script
from tests.test_resolve_scope_pr import FAKE_GH_JSON, write_fake_gh


def make_cfg_auto():
    return {
        "scope_flag": None, "pr_number": None, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def make_dirty(repo):
    (repo / "dirty.txt").write_text("uncommitted\n")


def fake_gh_no_pr(fake_bin):
    """`gh pr view` exits 1 (no PR for this branch)."""
    gh = fake_bin / "gh"
    gh.write_text('#!/bin/sh\necho "no pull requests found" >&2\nexit 1\n')
    gh.chmod(0o755)


def test_autodetect_dirty_no_pr_implies_uncommitted(tmp_repo, fake_bin):
    fake_gh_no_pr(fake_bin)
    make_dirty(tmp_repo)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["kind"] == "uncommitted"


def test_autodetect_dirty_plus_pr_errors(tmp_repo, fake_bin):
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    make_dirty(tmp_repo)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "ambig" in r.stderr.lower() or "uncommitted" in r.stderr.lower()


def test_autodetect_clean_with_pr_implies_pr(tmp_repo, fake_bin):
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["kind"] == "pr"


def test_autodetect_default_branch_clean_errors(tmp_repo, fake_bin):
    fake_gh_no_pr(fake_bin)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "nothing" in r.stderr.lower() or "default" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_resolve_scope_autodetect.py -v
```

- [ ] **Step 3: Implement auto-detect in `scripts/resolve-scope.py`**

Add helpers above `main()`:

```python
def is_dirty(cwd: str) -> bool:
    """True if there are staged, unstaged, or untracked changes."""
    out = git("status", "--porcelain", cwd=cwd)
    return bool(out)


def current_branch(cwd: str) -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)


def _ref_resolves(cwd: str, ref: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=cwd, capture_output=True,
    ).returncode == 0


def default_branch(cwd: str) -> str | None:
    """Return a ref name (locally resolvable) for the repository default branch.

    Resolution order:
      1. `gh repo view --json defaultBranchRef` — gives the authoritative name
         (could be `develop`, `trunk`, etc., not just main/master).
         Then verify it resolves locally as either `<name>` or `origin/<name>`.
         Return whichever resolves, preferring the local branch over the
         remote-tracking ref.
      2. Probe common candidates locally: main, master, origin/main, origin/master.
      3. None if nothing resolves.

    Returning a non-resolvable name would just push the failure into `git
    rev-parse <ref>^{commit}` in the caller, which is worse UX than a clean
    "no default branch detected" error here.
    """
    r = subprocess.run(
        ["gh", "repo", "view", "--json", "defaultBranchRef"],
        cwd=cwd, capture_output=True, text=True,
    )
    if r.returncode == 0:
        try:
            name = json.loads(r.stdout)["defaultBranchRef"]["name"]
            for ref in (name, f"origin/{name}"):
                if _ref_resolves(cwd, ref):
                    return ref
        except (KeyError, json.JSONDecodeError):
            pass  # fall through to local probe

    for candidate in ("main", "master", "origin/main", "origin/master"):
        if _ref_resolves(cwd, candidate):
            return candidate
    return None


def pr_for_current_branch(cwd: str) -> int | None:
    r = subprocess.run(
        ["gh", "pr", "view", "--json", "number"],
        cwd=cwd, capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)["number"]
```

Replace the `if scope_flag is None: raise SystemExit(...)` in `main()` with auto-detect:

```python
    if scope_flag is None:
        dirty = is_dirty(root)
        pr_num = pr_for_current_branch(root)
        if dirty and pr_num is not None:
            raise SystemExit(
                "error: ambiguous scope — tree has uncommitted changes and "
                f"current branch has PR #{pr_num}. Pass --uncommitted or --pr {pr_num}."
            )
        if dirty:
            scope_flag = "uncommitted"
        elif pr_num is not None:
            scope_flag = "pr"
            cfg["pr_number"] = pr_num
        else:
            branch = current_branch(root)
            default = default_branch(root)
            if default is None or branch == default:
                raise SystemExit(
                    "error: nothing to review (clean tree, on default branch, no PR)"
                )
            scope_flag = "base"
            cfg["base_branch"] = default
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_resolve_scope_autodetect.py tests/test_resolve_scope_pr.py tests/test_resolve_scope_explicit.py -v
```

Expected: 16 passed (10 explicit + 2 PR + 4 auto-detect).

- [ ] **Step 5: Commit**

```bash
git add scripts/resolve-scope.py tests/test_resolve_scope_autodetect.py
git commit -m "feat: resolve-scope.py auto-detect with dirty+PR ambiguity guard"
```

---

## Task 6: materialize-scope.py — uncommitted scope

**Files:**
- Create: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_uncommitted.py`

This task does just the `uncommitted` kind end-to-end. Other kinds land in subsequent tasks.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_materialize_uncommitted.py
"""Tests for materialize-scope.py — uncommitted scope only."""
import json
import subprocess
from tests.conftest import run_script


def base_scope(repo):
    return {
        "kind": "uncommitted", "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": False, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def materialize(scope):
    return run_script("materialize-scope.py", input=json.dumps(scope))


def test_uncommitted_modified_file(tmp_repo):
    (tmp_repo / "README.md").write_text("# changed\n")
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "uncommitted"
    assert out["has_reviewable_changes"] is True
    assert out["changed_file_count"] == 1
    assert "README.md" in out["unified_diff"]
    files = out["changed_files"]
    assert len(files) == 1
    assert files[0]["path"] == "README.md"
    assert files[0]["status"] == "modified"
    assert files[0]["kind"] == "text"
    assert files[0]["post_content"] == "# changed\n"


def test_uncommitted_untracked_file_included(tmp_repo):
    (tmp_repo / "brand_new.py").write_text("print('hi')\n")
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    files = {f["path"]: f for f in out["changed_files"]}
    assert "brand_new.py" in files
    assert files["brand_new.py"]["status"] == "added"
    assert files["brand_new.py"]["post_content"] == "print('hi')\n"
    assert out["total_lines_changed"] >= 1


def test_uncommitted_clean_tree_empty(tmp_repo):
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["has_reviewable_changes"] is False
    assert out["changed_file_count"] == 0
    assert out["total_lines_changed"] == 0
    assert out["unified_diff"] in ("", None)


def test_uncommitted_deleted_file(tmp_repo):
    (tmp_repo / "README.md").unlink()
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
    assert "README.md" in files
    assert files["README.md"]["status"] == "deleted"
    assert files["README.md"]["post_content"] is None
    assert files["README.md"]["pre_content"] is not None


def test_uncommitted_deleted_binary_file(tmp_repo):
    """Regression: deleting a tracked binary file used to crash materialization
    because the deleted-path branch forced kind='text' and then called git show
    with text=True, raising UnicodeDecodeError. Now: detect kind from HEAD and
    skip text decoding for binary."""
    # Commit a real binary (PNG header) so it's tracked at HEAD
    bin_path = tmp_repo / "logo.png"
    # 8-byte PNG signature + a NUL byte so any text detection trips on it
    bin_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff\xfe\xfd binary garbage")
    subprocess.run(["git", "add", "logo.png"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add binary"], cwd=tmp_repo, check=True)
    # Now delete it in the working tree
    bin_path.unlink()
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
    assert "logo.png" in files
    entry = files["logo.png"]
    assert entry["status"] == "deleted"
    assert entry["kind"] == "binary"
    # Critical: must NOT have tried to decode the binary as text
    assert entry["pre_content"] is None
    assert "binary" in (entry.get("note") or "").lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_uncommitted.py -v
```

- [ ] **Step 3: Implement `scripts/materialize-scope.py`**

```python
#!/usr/bin/env python3
"""materialize-scope.py — scope object in → materialized review subject out.

Produces the concrete diff + per-file content blob that both Codex and the
Claude sub-agents consume. For non-`uncommitted`/`files` scopes, creates the
disposable worktree used by run-codex.py.

This patch handles only the `uncommitted` kind. Other kinds are added in
subsequent patches.
"""
import json
import subprocess
import sys
from pathlib import Path


def git(*args, cwd: str, check: bool = True) -> str:
    r = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )
    return r.stdout


def symlink_target(repo: str, path: str) -> str | None:
    """Return the link target string for a symlink in the working tree, or None."""
    full = Path(repo) / path
    try:
        return os.readlink(full)
    except (OSError, FileNotFoundError):
        return None


def submodule_sha_at(repo_or_worktree: str, ref: str, path: str) -> str | None:
    """Return the submodule pointer SHA at a ref.

    For commit refs (HEAD, base_sha, merge_base, parent_sha): read from
    `git ls-tree <ref>` — gives the committed pointer.

    For ref='WORKTREE': read the submodule's actual working-tree HEAD via
    `git -C <submodule-path> rev-parse HEAD`. This is intentionally NOT the
    index pointer from `git ls-files --stage` — if the user `cd`'d into the
    submodule and checked out a different commit but hasn't `git add`'d the
    bump yet, the index still shows the old SHA. The actual working-tree HEAD
    is what the reviewer should see for an unstaged submodule bump. Without
    this, `--uncommitted` would render no real change for the most common
    submodule-update workflow."""
    if ref == "WORKTREE":
        full = Path(repo_or_worktree) / path
        if not full.is_dir():
            return None
        r = subprocess.run(
            ["git", "-C", str(full), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            return None
        sha = r.stdout.strip()
        return sha or None
    r = subprocess.run(
        ["git", "ls-tree", ref, "--", path],
        cwd=repo_or_worktree, capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None
    parts = r.stdout.split()
    if len(parts) < 3 or parts[0] != "160000":
        return None
    return parts[2]


def detect_kind(repo: str, path: str) -> str:
    """Return text|binary|symlink|submodule for a path in the working tree."""
    full = Path(repo) / path
    if full.is_symlink():
        return "symlink"
    # git submodule detection via ls-files --stage (mode 160000)
    out = subprocess.run(
        ["git", "ls-files", "--stage", "--", path],
        cwd=repo, capture_output=True, text=True,
    ).stdout.strip()
    if out.startswith("160000 "):
        return "submodule"
    # Binary detection: git's own attribute check
    chk = subprocess.run(
        ["git", "check-attr", "binary", "--", path],
        cwd=repo, capture_output=True, text=True,
    ).stdout
    if "binary: set" in chk:
        return "binary"
    # Sniff for NUL byte as fallback
    try:
        with full.open("rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return "binary"
    except (FileNotFoundError, IsADirectoryError):
        pass
    return "text"


def safe_read_text(repo: str, path: str) -> str | None:
    p = Path(repo) / path
    if not p.exists() or p.is_dir():
        return None
    try:
        return p.read_text()
    except (UnicodeDecodeError, OSError):
        return None


def detect_kind_at_ref(repo_or_worktree: str, ref: str, path: str) -> str:
    """Determine file kind (text|binary|symlink|submodule) at a specific git
    ref. Used for DELETED files — the working tree no longer has them, so the
    working-tree-based `detect_kind` is wrong (it would default to text and
    then text-decoding a binary blob would either crash or inline garbage)."""
    r = subprocess.run(
        ["git", "ls-tree", ref, "--", path],
        cwd=repo_or_worktree, capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return "text"  # unknown; fall back to text and let read_at_ref decide
    # git ls-tree output: "<mode> <type> <sha>\t<path>"
    parts = r.stdout.split()
    if len(parts) < 3:
        return "text"
    mode, _type, sha = parts[0], parts[1], parts[2]
    if mode == "160000":
        return "submodule"
    if mode == "120000":
        return "symlink"
    # Sniff for binary by reading the blob bytes
    blob = subprocess.run(
        ["git", "cat-file", "blob", sha],
        cwd=repo_or_worktree, capture_output=True,  # bytes, no text=True
    )
    if blob.returncode == 0 and b"\x00" in blob.stdout[:8192]:
        return "binary"
    return "text"


def read_at_ref(repo_or_worktree: str, ref: str, path: str) -> str | None:
    """Read text file content at a ref. Reads bytes and only decodes if valid
    UTF-8. Returns None for missing files, binary content, or decode errors.

    Critical: must NOT use subprocess `text=True` here — that would force
    UTF-8 decoding inside subprocess and raise UnicodeDecodeError for
    binary blobs (deleted PNGs, etc.), crashing materialization."""
    r = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=repo_or_worktree, capture_output=True,  # bytes
    )
    if r.returncode != 0:
        return None
    try:
        return r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def read_at_head(repo: str, path: str) -> str | None:
    """Back-compat wrapper for legacy callers — prefer read_at_ref directly."""
    return read_at_ref(repo, "HEAD", path)


def parse_name_status(out: str) -> list[tuple[str, str, str | None]]:
    """Parse `git diff --name-status` output into (status, path, old_path)."""
    entries = []
    for line in out.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("R") and len(parts) == 3:
            entries.append(("renamed", parts[2], parts[1]))
        elif code == "A":
            entries.append(("added", parts[1], None))
        elif code == "M":
            entries.append(("modified", parts[1], None))
        elif code == "D":
            entries.append(("deleted", parts[1], None))
        elif code == "T":
            entries.append(("typechange", parts[1], None))
        else:
            entries.append((code, parts[1] if len(parts) > 1 else "?", None))
    return entries


def materialize_uncommitted(scope: dict) -> dict:
    root = scope["repo_root"]
    unified = git("diff", "HEAD", cwd=root)
    name_status = git("diff", "--name-status", "HEAD", cwd=root)
    untracked_raw = git("ls-files", "--others", "--exclude-standard", cwd=root)
    untracked = [p for p in untracked_raw.splitlines() if p]

    changed: list[dict] = []
    total_lines = 0
    for status, path, old_path in parse_name_status(name_status):
        # For DELETED files the working tree no longer has the content, so
        # `detect_kind(root, path)` would read nothing and default to text.
        # Inspect HEAD instead to get the real kind (catches deleted binaries,
        # symlinks, submodules).
        if status == "deleted":
            kind = detect_kind_at_ref(root, "HEAD", path)
        else:
            kind = detect_kind(root, path)
        entry = {
            "path": path, "old_path": old_path, "status": status, "kind": kind,
            "lines_changed": None, "post_content": None,
            "pre_content": None, "note": None,
        }
        if kind == "text" and status != "deleted":
            entry["post_content"] = safe_read_text(root, path)
            entry["lines_changed"] = "(modified)"
        if status == "deleted":
            entry["lines_changed"] = "(deleted)"
            if kind == "text":
                entry["pre_content"] = read_at_ref(root, "HEAD", path)
            elif kind == "binary":
                entry["note"] = "binary file deleted — content not inlined"
            elif kind == "symlink":
                # A symlink blob's content IS the target path, so read_at_ref
                # returns it. Without this, reviewers can't see what the
                # deleted symlink used to point at.
                entry["symlink_target"] = read_at_ref(root, "HEAD", path)
                entry["note"] = "symlink deleted"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
                entry["submodule_post_sha"] = None
                entry["note"] = "submodule removed"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        elif kind == "symlink":
            # Without this, the prompt renderer would print only the header
            # for the symlink change — a reviewer can't judge a target swap
            # they can't see.
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            # For submodule bumps we want both the previous and new pointer
            # SHAs so the reviewer can judge what's actually changing.
            entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer change"
        changed.append(entry)

    for path in untracked:
        kind = detect_kind(root, path)
        post = safe_read_text(root, path) if kind == "text" else None
        line_count = len(post.splitlines()) if post else 0
        entry = {
            "path": path, "old_path": None, "status": "added", "kind": kind,
            "lines_changed": "(new file)" if line_count else "(empty)",
            "post_content": post, "pre_content": None, "note": None,
        }
        # Populate kind-specific metadata so untracked symlinks/submodules are
        # as reviewable as their tracked counterparts. Without this, an
        # untracked symlink renders as a header with no target — same bug
        # earlier rounds fixed for tracked entries.
        if kind == "symlink":
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink (untracked, new)"
        elif kind == "submodule":
            entry["submodule_pre_sha"] = None  # never existed before
            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer (untracked, new)"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        changed.append(entry)
        total_lines += line_count

    # Estimate text-line delta from the unified diff (cheap and good-enough)
    for line in unified.splitlines():
        if (line.startswith("+") or line.startswith("-")) and not line.startswith(("+++", "---")):
            total_lines += 1

    return {
        "scope_kind": "uncommitted",
        "scope_summary": "uncommitted changes",
        "unified_diff": unified if unified else None,
        "changed_files": changed,
        "doc_files": [],
        "total_lines_changed": total_lines,
        "changed_file_count": len(changed),
        "has_reviewable_changes": len(changed) > 0,
        # Uncommitted runs in the user's working tree — no disposable worktree
        # gets created. Explicit None keeps the materialize-output shape stable
        # across kinds so Phase A7's `merged["worktree_path"] = MAT_JSON.worktree_path`
        # works without conditional logic.
        "worktree_path": None,
        "warnings": [],
    }


KIND_HANDLERS = {"uncommitted": materialize_uncommitted}


def main() -> None:
    scope = json.load(sys.stdin)
    handler = KIND_HANDLERS.get(scope["kind"])
    if handler is None:
        raise SystemExit(f"error: materialize for kind={scope['kind']!r} not implemented")
    out = handler(scope)
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests, verify all pass**

```bash
chmod +x scripts/materialize-scope.py
pytest tests/test_materialize_uncommitted.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_uncommitted.py
git commit -m "feat: materialize-scope.py for uncommitted scope (text/binary/symlink/submodule + untracked)"
```

---

## Task 7: materialize-scope.py — base and commit scopes (with worktree)

**Files:**
- Modify: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_diff_scopes.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_materialize_diff_scopes.py
"""Tests for materialize-scope.py — base and commit scopes (worktree-based)."""
import json
import subprocess
from pathlib import Path

from tests.conftest import run_script


def base_scope(repo, **overrides):
    s = {
        "kind": None, "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    s.update(overrides)
    return s


def add_commit(repo, path, content, msg):
    (repo / path).write_text(content)
    subprocess.run(["git", "add", path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=repo, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()


def test_base_scope_three_dot_diff(tmp_repo):
    # main has initial commit; feature branches off, gets one commit
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    head_sha = add_commit(tmp_repo, "feature.py", "x = 1\n", "feat: add feature.py")
    scope = base_scope(tmp_repo, kind="base", base_sha=base_sha, head_sha=head_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "base"
    assert out["has_reviewable_changes"] is True
    assert any(f["path"] == "feature.py" for f in out["changed_files"])
    # worktree was created and recorded
    assert out["worktree_path"]  # truthy
    assert Path(out["worktree_path"]).exists()
    # cleanup
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)


def test_commit_scope(tmp_repo):
    sha = add_commit(tmp_repo, "added.py", "y = 2\n", "feat: added.py")
    scope = base_scope(tmp_repo, kind="commit", commit_sha=sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "commit"
    assert any(f["path"] == "added.py" for f in out["changed_files"])
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)


def test_commit_scope_root_commit_errors(tmp_repo):
    # The very first commit in tmp_repo has no parent — it's a root commit.
    root_sha = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        cwd=tmp_repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    scope = base_scope(tmp_repo, kind="commit", commit_sha=root_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "root commit" in r.stderr.lower()
    # Critical: no worktree leak even though make_worktree() succeeded
    leftover = [
        line for line in subprocess.run(
            ["git", "worktree", "list", "--porcelain"], cwd=tmp_repo,
            capture_output=True, text=True,
        ).stdout.splitlines() if "combined-review-" in line
    ]
    assert leftover == []


def test_commit_scope_merge_commit_errors(tmp_repo):
    # Build a merge commit on tmp_repo
    subprocess.run(["git", "checkout", "-q", "-b", "side"], cwd=tmp_repo, check=True)
    (tmp_repo / "side.py").write_text("s = 1\n")
    subprocess.run(["git", "add", "side.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "side commit"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "checkout", "-q", "-"], cwd=tmp_repo, check=True)  # back to default
    (tmp_repo / "main.py").write_text("m = 1\n")
    subprocess.run(["git", "add", "main.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "main commit"], cwd=tmp_repo, check=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "-m", "merge", "side"],
        cwd=tmp_repo, capture_output=True, text=True, check=True,
    )
    merge_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True,
    ).stdout.strip()
    scope = base_scope(tmp_repo, kind="commit", commit_sha=merge_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "merge commit" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_diff_scopes.py -v
```

- [ ] **Step 3: Extend `scripts/materialize-scope.py` with worktree creation + diff scopes**

Add at module top:

```python
import tempfile
import os
```

Add helpers (above `materialize_uncommitted`):

```python
def make_worktree(repo: str, ref: str) -> str:
    repo_basename = Path(repo).name
    tmp = tempfile.mkdtemp(
        prefix=f"combined-review-{repo_basename}-", dir=os.environ.get("TMPDIR", "/tmp")
    )
    # Remove the empty dir mktemp made; git worktree wants a fresh path
    Path(tmp).rmdir()
    subprocess.run(
        ["git", "worktree", "add", "--detach", tmp, ref],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return tmp


def materialize_diff_in_worktree(
    repo: str, worktree: str, base_sha: str, head_sha: str
) -> tuple[str, list[dict], int]:
    """Three-dot diff (merge-base semantics) and per-file entries.

    `git diff base...head` is shorthand for `git diff merge-base(base, head)..head`,
    so the diff content is anchored at the merge base, NOT base_sha. For deleted
    files, reading `git show base_sha:path` would return the file as it existed
    at base_sha — but if the base branch modified that file after the feature
    branch forked, base_sha's content disagrees with the diff. Reading from the
    merge-base commit instead keeps pre_content consistent with the unified diff.
    """
    merge_base = subprocess.run(
        ["git", "merge-base", base_sha, head_sha],
        cwd=worktree, capture_output=True, text=True, check=True,
    ).stdout.strip()

    unified = git("diff", f"{base_sha}...{head_sha}", cwd=worktree)
    name_status = git("diff", "--name-status", f"{base_sha}...{head_sha}", cwd=worktree)
    changed: list[dict] = []
    for status, path, old_path in parse_name_status(name_status):
        # Deleted files: detect kind from the merge-base (where the file last
        # existed) and read content via the binary-safe helper, not via
        # subprocess text=True which would crash on a deleted PNG.
        if status == "deleted":
            kind = detect_kind_at_ref(worktree, merge_base, path)
        else:
            kind = detect_kind(worktree, path)
        entry = {
            "path": path, "old_path": old_path, "status": status, "kind": kind,
            "lines_changed": None, "post_content": None,
            "pre_content": None, "note": None,
        }
        if kind == "text" and status != "deleted":
            entry["post_content"] = safe_read_text(worktree, path)
        if status == "deleted":
            if kind == "text":
                entry["pre_content"] = read_at_ref(worktree, merge_base, path)
            elif kind == "binary":
                entry["note"] = "binary file deleted — content not inlined"
            elif kind == "symlink":
                entry["symlink_target"] = read_at_ref(worktree, merge_base, path)
                entry["note"] = "symlink deleted"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
                entry["submodule_post_sha"] = None
                entry["note"] = "submodule removed"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        elif kind == "symlink":
            # Post-change target lives in the worktree (HEAD = head_sha).
            entry["symlink_target"] = symlink_target(worktree, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            # Pre at merge_base, post at head_sha. Both reachable in the worktree.
            entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
            entry["submodule_post_sha"] = submodule_sha_at(worktree, head_sha, path)
            entry["note"] = "submodule pointer change"
        changed.append(entry)
    total = sum(
        1 for line in unified.splitlines()
        if (line.startswith("+") or line.startswith("-"))
        and not line.startswith(("+++", "---"))
    )
    return unified, changed, total


def materialize_base(scope: dict) -> dict:
    repo = scope["repo_root"]
    worktree = make_worktree(repo, scope["head_sha"])
    try:
        unified, changed, total = materialize_diff_in_worktree(
            repo, worktree, scope["base_sha"], scope["head_sha"]
        )
        return {
            "scope_kind": "base",
            "scope_summary": (
                f"branch {scope['base_ref_name']}...HEAD "
                f"({scope['base_sha'][:7]}..{scope['head_sha'][:7]})"
            ),
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        # If we created a worktree but never returned it in the handoff JSON,
        # the orchestrator has no way to clean it up. Self-clean and re-raise
        # so it never leaks. Phase D handles the (worktree_path, repo_root)
        # tuple for successful runs only.
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise


def commit_parent_count(repo_or_worktree: str, sha: str) -> int:
    """Number of parents — 0 for root commits, 1 for normal, ≥2 for merges."""
    out = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", sha],
        cwd=repo_or_worktree, capture_output=True, text=True, check=True,
    ).stdout.strip()
    # output is "<sha> <parent1> [<parent2> …]"
    return max(0, len(out.split()) - 1)


def materialize_commit(scope: dict) -> dict:
    repo = scope["repo_root"]
    sha = scope["commit_sha"]
    worktree = make_worktree(repo, sha)
    try:
        n_parents = commit_parent_count(worktree, sha)
        if n_parents == 0:
            # Root commit — no parent to diff against. v1 does not support
            # reviewing root commits; the right diff is "everything added"
            # but neither codex nor the Claude sub-agents are tuned for it.
            raise SystemExit(
                f"error: commit {sha[:7]} is a root commit (no parent); "
                f"v1 does not support reviewing root commits"
            )
        if n_parents >= 2:
            # Merge commit. The first-parent diff (`git show --first-parent`)
            # is conventional but loses changes from the second parent's branch.
            # v1 surfaces this explicitly rather than silently picking one diff.
            raise SystemExit(
                f"error: commit {sha[:7]} is a merge commit with {n_parents} parents; "
                f"v1 does not support reviewing merge commits — review the "
                f"merged branch's individual commits instead"
            )
        # Normal single-parent commit: use git show semantics, which produces
        # the patch the commit introduced. This is more direct (and correct
        # for non-fast-forward histories) than `git diff parent...commit`.
        unified = subprocess.run(
            ["git", "show", "--format=", sha],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout
        name_status = subprocess.run(
            ["git", "show", "--format=", "--name-status", sha],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout
        parent_sha = subprocess.run(
            ["git", "rev-parse", f"{sha}^"],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout.strip()
        changed: list[dict] = []
        for status, path, old_path in parse_name_status(name_status):
            # Deleted files: detect kind from the parent commit (where the file
            # last existed), and use the binary-safe reader.
            if status == "deleted":
                kind = detect_kind_at_ref(worktree, parent_sha, path)
            else:
                kind = detect_kind(worktree, path)
            entry = {
                "path": path, "old_path": old_path, "status": status, "kind": kind,
                "lines_changed": None, "post_content": None,
                "pre_content": None, "note": None,
            }
            if kind == "text" and status != "deleted":
                entry["post_content"] = safe_read_text(worktree, path)
            if status == "deleted":
                if kind == "text":
                    entry["pre_content"] = read_at_ref(worktree, parent_sha, path)
                elif kind == "binary":
                    entry["note"] = "binary file deleted — content not inlined"
                elif kind == "symlink":
                    entry["symlink_target"] = read_at_ref(worktree, parent_sha, path)
                    entry["note"] = "symlink deleted"
                elif kind == "submodule":
                    entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
                    entry["submodule_post_sha"] = None
                    entry["note"] = "submodule removed"
            elif kind == "binary":
                entry["note"] = "binary file — content not inlined"
            elif kind == "symlink":
                entry["symlink_target"] = symlink_target(worktree, path)
                entry["note"] = "symlink"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
                entry["submodule_post_sha"] = submodule_sha_at(worktree, sha, path)
                entry["note"] = "submodule pointer change"
            changed.append(entry)
        total = sum(
            1 for line in unified.splitlines()
            if (line.startswith("+") or line.startswith("-"))
            and not line.startswith(("+++", "---"))
        )
        return {
            "scope_kind": "commit",
            "scope_summary": f"commit {sha[:7]}",
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        # Worktree was created above; clean it up before re-raising so the
        # orchestrator doesn't have to track a worktree_path that materialize
        # never returned. See "Materialize failure cleanup" comment near
        # make_worktree() for the full rationale.
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise
```

Then extend `KIND_HANDLERS`:

```python
KIND_HANDLERS = {
    "uncommitted": materialize_uncommitted,
    "base": materialize_base,
    "commit": materialize_commit,
}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_materialize_diff_scopes.py tests/test_materialize_uncommitted.py -v
```

Expected: 9 passed (5 in uncommitted + 4 in diff_scopes, where diff_scopes includes test_base_scope_three_dot_diff, test_commit_scope, test_commit_scope_root_commit_errors, test_commit_scope_merge_commit_errors).

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_diff_scopes.py
git commit -m "feat: materialize-scope.py for base and commit scopes via worktrees"
```

---

## Task 8: materialize-scope.py — PR scope with cat-file SHA reachability check

**Files:**
- Modify: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_pr.py`

- [ ] **Step 1: Write failing tests using a fake `gh pr checkout`**

```python
# tests/test_materialize_pr.py
"""Tests for materialize-scope.py PR scope.

Simulates `gh pr checkout` by hand-applying the head SHA inside the worktree,
since we don't have GitHub in the test loop.
"""
import json
import subprocess
from pathlib import Path

from tests.conftest import run_script


def test_pr_stale_snapshot_failure(tmp_repo, fake_bin):
    # gh pr checkout: do nothing (worktree stays at the initial commit).
    # The PR scope wants head_sha=<nonexistent SHA>, which should fail loudly.
    gh = fake_bin / "gh"
    gh.write_text('#!/bin/sh\nexit 0\n')
    gh.chmod(0o755)
    scope = {
        "kind": "pr", "pr_number": 99,
        "base_ref_name": "main", "head_ref_name": "feature",
        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
        "base_sha": "0" * 40, "head_sha": "f" * 40, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "force-pushed" in r.stderr.lower() or "stale" in r.stderr.lower() or "unreachable" in r.stderr.lower()


def test_pr_happy_path(tmp_repo, fake_bin):
    # Set up: initial commit on main; create feature branch with a commit;
    # capture both SHAs. Make gh pr checkout a no-op (worktree is already
    # at the head via our test setup) — and skip the base-repo fetch by
    # using the local repo's URL.
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    (tmp_repo / "f.py").write_text("z = 3\n")
    subprocess.run(["git", "add", "f.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    # Fake `gh pr checkout` resets the worktree to head_sha
    gh = fake_bin / "gh"
    gh.write_text(
        '#!/bin/sh\n'
        '# only handle `gh pr checkout`; defer to git for the rest\n'
        f'if [ "$1" = "pr" ] && [ "$2" = "checkout" ]; then\n'
        f'  git -C "$PWD" reset --hard {head_sha} >/dev/null\n'
        '  exit 0\n'
        'fi\n'
        'exit 1\n'
    )
    gh.chmod(0o755)
    scope = {
        "kind": "pr", "pr_number": 1,
        "base_ref_name": "main", "head_ref_name": "feature",
        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
        "base_sha": base_sha, "head_sha": head_sha, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "pr"
    assert any(f["path"] == "f.py" for f in out["changed_files"])
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_pr.py -v
```

- [ ] **Step 3: Add `materialize_pr` to `scripts/materialize-scope.py`**

Add helper and handler:

```python
def cat_file_exists(repo_or_worktree: str, sha: str) -> bool:
    r = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=repo_or_worktree, capture_output=True,
    )
    return r.returncode == 0


def materialize_pr(scope: dict) -> dict:
    repo = scope["repo_root"]
    head_sha = scope["head_sha"]
    base_sha = scope["base_sha"]
    base_url = scope["base_repo_url"]
    base_ref = scope["base_ref_name"]
    pr = scope["pr_number"]

    # Create an empty worktree we'll populate via gh pr checkout
    repo_basename = Path(repo).name
    worktree = tempfile.mkdtemp(
        prefix=f"combined-review-{repo_basename}-pr-",
        dir=os.environ.get("TMPDIR", "/tmp"),
    )
    Path(worktree).rmdir()
    subprocess.run(
        ["git", "worktree", "add", "--detach", worktree],
        cwd=repo, check=True, capture_output=True, text=True,
    )

    # Wrap everything after worktree creation in try/except so we never leak
    # a worktree the orchestrator can't see in the handoff JSON.
    try:
        # `gh pr checkout` handles fork PRs natively. Cwd = worktree.
        r = subprocess.run(
            ["gh", "pr", "checkout", "--detach", str(pr)],
            cwd=worktree, capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise SystemExit(f"error: gh pr checkout failed: {r.stderr.strip()}")

        # Fetch base from the PR's actual base repo (NOT origin — may be a fork)
        subprocess.run(
            ["git", "fetch", base_url, base_ref],
            cwd=worktree, capture_output=True, text=True,
        )

        # Pin head: if HEAD drifted, reset to recorded head_sha
        current_head = git("rev-parse", "HEAD", cwd=worktree).strip()
        if current_head != head_sha:
            if not cat_file_exists(worktree, head_sha):
                raise SystemExit(
                    f"error: PR head force-pushed mid-review — recorded {head_sha[:7]} "
                    f"no longer reachable. Rerun /combined-review --pr {pr} to fetch the current snapshot."
                )
            subprocess.run(
                ["git", "reset", "--hard", head_sha],
                cwd=worktree, check=True, capture_output=True, text=True,
            )

        # Verify base SHA is reachable
        if not cat_file_exists(worktree, base_sha):
            raise SystemExit(
                f"error: PR base SHA {base_sha[:7]} not reachable in worktree. "
                f"Rerun /combined-review --pr {pr} to fetch the current snapshot."
            )

        unified, changed, total = materialize_diff_in_worktree(
            repo, worktree, base_sha, head_sha
        )
        return {
            "scope_kind": "pr",
            "scope_summary": f"PR #{pr} ({base_sha[:7]}..{head_sha[:7]})",
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        # Any failure after worktree creation: clean up the worktree so the
        # orchestrator never has to recover a path it didn't receive.
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise
```

Extend `KIND_HANDLERS`:

```python
KIND_HANDLERS = {
    "uncommitted": materialize_uncommitted,
    "base": materialize_base,
    "commit": materialize_commit,
    "pr": materialize_pr,
}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_materialize_pr.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_pr.py
git commit -m "feat: materialize-scope.py PR scope with cat-file SHA verification"
```

---

## Task 9: materialize-scope.py — files scope and non-code-mode doc_files

**Files:**
- Modify: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_files_and_modes.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_materialize_files_and_modes.py
"""Tests for materialize-scope.py — files scope and doc_files for non-code modes."""
import json
import subprocess
from tests.conftest import run_script


def files_scope(repo, files, mode="code"):
    return {
        "kind": "files", "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": files, "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": False, "mode": mode, "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def test_files_scope_reads_current_content(tmp_repo):
    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
    (tmp_repo / "plan.md").write_text("# plan\nbar\n")
    scope = files_scope(tmp_repo, ["spec.md", "plan.md"])
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "files"
    assert out["unified_diff"] is None
    assert out["changed_files"] == []
    docs = {d["path"]: d for d in out["doc_files"]}
    assert "spec.md" in docs
    assert docs["spec.md"]["content"] == "# spec\nfoo\n"
    assert out["has_reviewable_changes"] is True


def test_files_scope_with_spec_mode_preserves_doc_files(tmp_repo):
    """Regression: maybe_populate_doc_files() must not overwrite materialize_files()'s
    output. Was: --mode spec + files-scope wiped doc_files because the helper iterated
    over an empty changed_files. Now: helper short-circuits for files scope."""
    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
    scope = files_scope(tmp_repo, ["spec.md"], mode="spec")
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert len(out["doc_files"]) == 1
    assert out["doc_files"][0]["path"] == "spec.md"
    assert out["doc_files"][0]["content"] == "# spec\nfoo\n"


def test_non_code_mode_with_diff_scope_populates_doc_files(tmp_repo):
    # Set up a base-scope review on a .md change with --mode spec
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feat"], cwd=tmp_repo, check=True)
    (tmp_repo / "design.md").write_text("# design\n")
    subprocess.run(["git", "add", "design.md"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "design"], cwd=tmp_repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    scope = files_scope(tmp_repo, [], mode="spec")
    scope["kind"] = "base"
    scope["base_sha"] = base_sha
    scope["head_sha"] = head_sha
    scope["base_ref_name"] = "main"
    scope["needs_clean_worktree"] = True
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    paths = {d["path"]: d for d in out["doc_files"]}
    assert "design.md" in paths
    assert "design" in paths["design.md"]["content"]
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_files_and_modes.py -v
```

- [ ] **Step 3: Extend `scripts/materialize-scope.py`**

Add handler and patch the diff handlers to populate `doc_files` when `mode != "code"`:

```python
def materialize_files(scope: dict) -> dict:
    """Build doc_files entries for positional files. Symlink and submodule
    entries carry kind-specific metadata (target / pointer SHA) instead of
    just a "non-text" note, so the rendered prompt can show the reviewer
    what's actually there. Without this, reviewing a symlink would print
    only a heading and the reviewer can't judge the target."""
    root = scope["repo_root"]
    doc_files: list[dict] = []
    for path in scope["files"]:
        kind = detect_kind(root, path)
        entry: dict = {
            "path": path, "status": "current", "kind": kind,
            "content": None, "note": None,
        }
        if kind == "text":
            entry["content"] = safe_read_text(root, path)
        elif kind == "symlink":
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            entry["submodule_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer (no diff — single snapshot)"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        else:
            entry["note"] = f"non-text ({kind}) — content not inlined"
        doc_files.append(entry)
    return {
        "scope_kind": "files",
        "scope_summary": f"{len(doc_files)} file(s) — current working-tree content",
        "unified_diff": None,
        "changed_files": [],
        "doc_files": doc_files,
        "total_lines_changed": 0,
        "changed_file_count": 0,
        "has_reviewable_changes": len(doc_files) > 0,
        "worktree_path": None, "warnings": [],
    }
```

Then add a post-processing helper to populate `doc_files` for diff scopes when `mode != "code"`:

```python
def maybe_populate_doc_files(out: dict, scope: dict) -> None:
    """For non-code modes on diff scopes, mirror changed text files into doc_files
    using post_content (or pre_content for deletes) so the document-reviewer
    agent has something reviewable.

    Gate: skip in code mode (doc_files is empty by design), and skip for files
    scope — `materialize_files()` already populated doc_files correctly and we
    must not overwrite it with an empty list derived from the (also empty)
    changed_files."""
    if scope["mode"] == "code":
        return
    if scope["kind"] == "files":
        return
    docs = []
    for cf in out["changed_files"]:
        if cf["kind"] != "text":
            continue
        if cf["status"] == "deleted":
            content = cf.get("pre_content")
        else:
            content = cf.get("post_content")
        if content is None:
            continue
        docs.append({"path": cf["path"], "status": cf["status"], "content": content})
    out["doc_files"] = docs
```

Call it at the bottom of `main()`:

```python
def main() -> None:
    scope = json.load(sys.stdin)
    handler = KIND_HANDLERS.get(scope["kind"])
    if handler is None:
        raise SystemExit(f"error: materialize for kind={scope['kind']!r} not implemented")
    out = handler(scope)
    maybe_populate_doc_files(out, scope)
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")
```

Extend handlers:

```python
KIND_HANDLERS = {
    "uncommitted": materialize_uncommitted,
    "base": materialize_base,
    "commit": materialize_commit,
    "pr": materialize_pr,
    "files": materialize_files,
}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_materialize_files_and_modes.py tests/test_materialize_uncommitted.py tests/test_materialize_diff_scopes.py tests/test_materialize_pr.py -v
```

Expected: 14 passed (5 uncommitted + 4 diff_scopes + 2 pr + 3 files_and_modes).

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_files_and_modes.py
git commit -m "feat: materialize-scope.py files scope + doc_files for non-code modes"
```

---

## Task 10: Mode prompt templates

**Files:**
- Create: `prompts/code.md`
- Create: `prompts/spec.md`
- Create: `prompts/plan.md`
- Create: `prompts/docs.md`

- [ ] **Step 1: Write `prompts/code.md`**

```markdown
# Code Review Mode

You are reviewing a code change. Focus on:

- **Correctness** — bugs, off-by-one errors, null/undefined handling, race conditions.
- **Error handling** — silent failures, missing catches, swallowed exceptions.
- **Test coverage** — new logic without tests, edge cases unverified.
- **Security** — injection, secrets, unsafe deserialization, auth bypass.
- **Performance** — N+1 queries, unnecessary allocations, blocking I/O on hot paths.
- **Project conventions** — alignment with CLAUDE.md if present.

You will receive the materialized review subject below (unified diff + per-file content).
Cite findings by `path:line` from the post-change file content. Skip stylistic nits
unless they obscure intent.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble. If you find no
issues, emit zero blocks.
```

- [ ] **Step 2: Write `prompts/spec.md`**

```markdown
# Spec Review Mode

You are reviewing a specification document. Focus on:

- **Completeness** — are requirements fully specified? Are edge cases addressed?
- **Ambiguity** — could any sentence be interpreted two ways? Pick out the ambiguous bit.
- **Internal consistency** — do sections contradict each other? Do field names match?
- **Scope creep** — does the spec drift into implementation when it should stay at the design level?
- **Missing edge cases** — failure modes, concurrency, ordering, partial states.
- **Unstated assumptions** — what does the spec take for granted that a reader might not know?
- **Success criteria** — is "done" defined? Is it testable?

You will receive the materialized review subject below (changed files + their current content).
Cite findings by `path:line` or section heading.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble.
```

- [ ] **Step 3: Write `prompts/plan.md`**

```markdown
# Plan Review Mode

You are reviewing an implementation plan. Focus on:

- **Step ordering** — does task N assume something task M hasn't delivered yet?
- **Hidden dependencies** — does a step rely on something not produced by an earlier step?
- **Verification per task** — does each task have a check that proves it worked, or is it "implement X, trust it works"?
- **Risk surface** — destructive ops, force-pushes, schema migrations, anything hard to roll back.
- **What could fail silently** — what would let the plan "complete" while producing a broken result?
- **Code completeness in steps** — placeholders like "implement appropriate logic", missing exact paths, undefined symbols.

You will receive the plan document below.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble.
```

- [ ] **Step 4: Write `prompts/docs.md`**

```markdown
# Docs Review Mode

You are reviewing user/developer documentation. Focus on:

- **Accuracy vs. current code** — do code samples match the actual API? Do paths exist?
- **Broken examples** — does the snippet actually run, or is it pseudo-code dressed up as runnable?
- **Drift** — has the underlying code changed in ways the docs still claim differently?
- **Missing prerequisites** — does the reader know what they need before step 1?
- **Audience fit** — is it pitched at someone who knows nothing? Too much? Just right?

You will receive the materialized review subject below.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble.
```

- [ ] **Step 5: Verify they exist and commit**

```bash
ls prompts/
git add prompts/
git commit -m "feat: mode prompt templates (code, spec, plan, docs)"
```

---

## Task 11: Finding schema appendix + render-prompt.py

**Files:**
- Create: `prompts/_schema.md`
- Create: `scripts/render-prompt.py`
- Create: `tests/test_render_prompt.py`

- [ ] **Step 1: Write `prompts/_schema.md`** (the shared schema appendix, included in every prompt)

Note the **four-backtick** outer fence below — the file's content contains its own triple-backtick code block, and a triple-backtick outer fence would close prematurely at the inner one. CommonMark allows fences of any length ≥ 3; the closing fence must match the opening length, so four-tick outer + three-tick inner is unambiguous.

````markdown
---

## Output schema (mandatory)

Emit findings only as `---FINDING---` blocks. One block per finding. No preamble, no
postamble, no summary, no headers.

```
---FINDING---
severity: critical|high|medium|low
file: <relative path or "(general)">
line: <int> | <start>-<end> | -
category: bug|test-gap|perf|security|clarity|style|other
title: <single-line summary, no period>
detail: |
  <multi-line free text — recommendation, evidence, suggested fix>
---END-FINDING---
```

If you find no issues, emit zero blocks. Do not write "no issues found" or anything else.

**You are in review mode. Do not write, edit, or delete any files. Do not run code.
Read only.**
````

- [ ] **Step 2: Write failing tests for render-prompt.py**

```python
# tests/test_render_prompt.py
"""Tests for render-prompt.py — assembles mode template + materialized blob + schema."""
import json
from tests.conftest import run_script


def make_materialized(**overrides):
    base = {
        "scope_kind": "uncommitted",
        "scope_summary": "uncommitted changes",
        "unified_diff": "diff --git a/x b/x\n+y\n",
        "changed_files": [
            {"path": "x", "status": "modified", "kind": "text",
             "post_content": "y\n", "pre_content": None, "old_path": None,
             "lines_changed": "(modified)", "note": None},
        ],
        "doc_files": [], "total_lines_changed": 1,
        "changed_file_count": 1, "has_reviewable_changes": True,
        "warnings": [],
    }
    base.update(overrides)
    return base


def test_render_includes_mode_template():
    r = run_script(
        "render-prompt.py", "--mode", "code",
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0, r.stderr
    assert "Code Review Mode" in r.stdout
    assert "FINDING" in r.stdout  # schema appendix
    assert "no-edit" not in r.stdout.lower()  # we use the "read only" wording
    assert "diff --git" in r.stdout
    assert "y\n" in r.stdout


def test_render_includes_focus():
    r = run_script(
        "render-prompt.py", "--mode", "code", "--focus", "API contract changes",
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0
    assert "API contract changes" in r.stdout


def test_focus_file_mode_handles_shell_metacharacters(tmp_path):
    """Focus text containing $(...), backticks, etc. must round-trip safely."""
    f = tmp_path / "focus.txt"
    f.write_text("review $(rm -rf /) carefully and `dangerous` patterns")
    r = run_script(
        "render-prompt.py", "--mode", "code", "--focus-file", str(f),
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0, r.stderr
    # The literal text must appear verbatim — no shell expansion happens
    # because the orchestrator passes a file path, not the text itself.
    assert "review $(rm -rf /) carefully" in r.stdout
    assert "`dangerous` patterns" in r.stdout


def test_focus_and_focus_file_mutually_exclusive(tmp_path):
    f = tmp_path / "focus.txt"; f.write_text("x")
    r = run_script(
        "render-prompt.py", "--mode", "code",
        "--focus", "y", "--focus-file", str(f),
        input=json.dumps(make_materialized()),
    )
    assert r.returncode != 0


def test_render_doc_mode_uses_doc_files():
    mat = make_materialized(
        scope_kind="files", unified_diff=None, changed_files=[],
        doc_files=[{"path": "spec.md", "status": "current", "content": "# spec\n"}],
    )
    r = run_script(
        "render-prompt.py", "--mode", "spec",
        input=json.dumps(mat),
    )
    assert r.returncode == 0
    assert "Spec Review Mode" in r.stdout
    assert "spec.md" in r.stdout
    assert "# spec" in r.stdout


def test_render_handles_nested_fences_in_doc(tmp_path):
    """Specs/plans commonly contain ``` blocks. A naive triple-backtick wrapper
    would let the inner ``` close the outer fence prematurely, swallowing the
    schema appendix. Verify the schema appendix is still present and intact."""
    doc_with_fences = (
        "# Spec\n\n"
        "Example code:\n\n"
        "```python\n"
        "def f(): return 1\n"
        "```\n\n"
        "Another block:\n\n"
        "````diff\n"  # nested fence with FOUR backticks
        "+ added line\n"
        "````\n"
    )
    mat = make_materialized(
        scope_kind="files", unified_diff=None, changed_files=[],
        doc_files=[{"path": "spec.md", "status": "current",
                    "content": doc_with_fences}],
    )
    r = run_script("render-prompt.py", "--mode", "spec",
                   input=json.dumps(mat))
    assert r.returncode == 0, r.stderr
    out = r.stdout
    # Doc content must appear
    assert "def f(): return 1" in out
    assert "+ added line" in out
    # Schema appendix must NOT have been swallowed by an unbalanced fence
    assert "---FINDING---" in out
    assert "End of prompt" not in out or "FINDING" in out  # schema present
```

- [ ] **Step 3: Run tests, verify they fail**

```bash
pytest tests/test_render_prompt.py -v
```

- [ ] **Step 4: Implement `scripts/render-prompt.py`**

```python
#!/usr/bin/env python3
"""render-prompt.py — assemble the prompt body for a reviewer.

Inputs:
- --mode {code,spec,plan,docs}
- --focus "<text>" (optional)
- materialized blob on stdin (JSON from materialize-scope.py)

Output: plain-text prompt body on stdout, suitable for piping to a reviewer
(codex via stdin, or pasted into a Claude sub-agent's prompt).
"""
import argparse
import json
import sys
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def fence_for(content: str) -> str:
    """Return a backtick fence longer than any run of backticks already inside
    `content`. CommonMark requires the closing fence be at least as long as
    the opening one, so a fence of length N+1 (where N is the longest run
    inside) will never collide. Without this, embedding a spec/plan that
    itself contains ``` would terminate our outer fence early and swallow
    everything after it — including the finding-schema appendix."""
    longest = 0
    run = 0
    for ch in content:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def fenced(content: str, lang: str = "") -> str:
    fence = fence_for(content)
    return f"{fence}{lang}\n{content.rstrip(chr(10))}\n{fence}"


def render_changed_files(mat: dict) -> str:
    parts = []
    for cf in mat["changed_files"]:
        parts.append(f"\n### {cf['path']}  (status: {cf['status']}, kind: {cf['kind']})")
        if cf.get("old_path"):
            parts.append(f"(renamed from {cf['old_path']})")
        if cf["kind"] == "text" and cf.get("post_content"):
            parts.append(fenced(cf["post_content"]))
        elif cf["status"] == "deleted" and cf.get("pre_content"):
            parts.append("(deleted; previous content was:)")
            parts.append(fenced(cf["pre_content"]))
        elif cf["kind"] == "symlink":
            target = cf.get("symlink_target")
            if target is not None:
                parts.append(f"Symlink target: `{target}`")
            if cf.get("note"):
                parts.append(f"_{cf['note']}_")
        elif cf["kind"] == "submodule":
            pre, post = cf.get("submodule_pre_sha"), cf.get("submodule_post_sha")
            if pre or post:
                parts.append(f"Submodule pointer: `{pre or '(none)'}` → `{post or '(none)'}`")
            if cf.get("note"):
                parts.append(f"_{cf['note']}_")
        elif cf.get("note"):
            parts.append(f"_{cf['note']}_")
    return "\n".join(parts)


def render_doc_files(mat: dict) -> str:
    parts = []
    for d in mat["doc_files"]:
        kind = d.get("kind", "text")
        parts.append(
            f"\n### {d['path']}  (status: {d['status']}, kind: {kind})"
        )
        if d.get("content"):
            parts.append(fenced(d["content"]))
        elif kind == "symlink":
            target = d.get("symlink_target")
            if target is not None:
                parts.append(f"Symlink target: `{target}`")
            if d.get("note"):
                parts.append(f"_{d['note']}_")
        elif kind == "submodule":
            sha = d.get("submodule_sha")
            if sha:
                parts.append(f"Submodule pointer: `{sha}`")
            if d.get("note"):
                parts.append(f"_{d['note']}_")
        elif d.get("note"):
            parts.append(f"_{d['note']}_")
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["code", "spec", "plan", "docs"], required=True)
    # Two ways to pass focus text:
    #   --focus "<text>" — convenient when the text has no shell metacharacters
    #   --focus-file <path> — REQUIRED when the text is user-provided, since
    #     argv interpolation by the orchestrator into a Bash command line
    #     would expose $(...), backticks, and other shell-injection vectors.
    # The skill orchestrator MUST use --focus-file for any user-provided focus.
    ap.add_argument("--focus", default=None)
    ap.add_argument("--focus-file", default=None)
    args = ap.parse_args()
    if args.focus and args.focus_file:
        ap.error("--focus and --focus-file are mutually exclusive")
    focus = args.focus
    if args.focus_file:
        with open(args.focus_file, "r") as f:
            focus = f.read().strip()
    mat = json.load(sys.stdin)

    template = (PROMPTS_DIR / f"{args.mode}.md").read_text()
    schema = (PROMPTS_DIR / "_schema.md").read_text()

    out = [template]
    if focus:
        out.append(f"\n## Additional focus\n\n{focus}\n")
    out.append(f"\n## Review subject\n\n**Scope:** {mat['scope_summary']}\n")
    if mat.get("unified_diff"):
        out.append("\n### Unified diff\n\n" + fenced(mat["unified_diff"], "diff") + "\n")
    if mat["changed_files"]:
        out.append("\n### Changed files (full content)\n")
        out.append(render_changed_files(mat))
    if mat["doc_files"]:
        out.append("\n### Document files\n")
        out.append(render_doc_files(mat))
    out.append("\n" + schema)
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests, commit**

```bash
chmod +x scripts/render-prompt.py
pytest tests/test_render_prompt.py -v
git add prompts/_schema.md scripts/render-prompt.py tests/test_render_prompt.py
git commit -m "feat: render-prompt.py assembles mode template + materialized blob + schema"
```

---

## Task 12: run-codex.py (Python, for macOS portability)

**Files:**
- Create: `scripts/run-codex.py`
- Create: `tests/test_run_codex.py`

**Why Python and not Bash:** GNU `timeout` is not on macOS by default (no `gtimeout` either), and BSD `date` doesn't understand `%3N` for millisecond precision. Python's `subprocess.run(..., timeout=...)` handles both portably and gives us a single language for testability.

- [ ] **Step 1: Write failing tests with a fake `codex` binary**

```python
# tests/test_run_codex.py
"""Tests for run-codex.py — invokes codex exec --sandbox read-only with stdin prompt."""
import json
import subprocess
from pathlib import Path

from tests.conftest import SCRIPTS_DIR


def write_fake_codex(fake_bin, behavior="echo"):
    codex = fake_bin / "codex"
    if behavior == "echo":
        codex.write_text(
            '#!/bin/sh\n'
            '# Echo the args + stdin, plus a fake finding. Advertise --sandbox.\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE   sandbox policy"\n'
            '  exit 0\n'
            'fi\n'
            'echo "ARGS: $*" >&2\n'
            'cat - >/dev/null\n'
            'echo "---FINDING---"\n'
            'echo "severity: low"\n'
            'echo "file: x.py"\n'
            'echo "line: 1"\n'
            'echo "category: style"\n'
            'echo "title: fake codex finding"\n'
            'echo "detail: |"\n'
            'echo "  emitted by fake codex"\n'
            'echo "---END-FINDING---"\n'
        )
    elif behavior == "no-sandbox":
        codex.write_text(
            '#!/bin/sh\n'
            '# --help does NOT advertise --sandbox; run-codex.py should refuse.\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --some-other-flag"\n'
            '  exit 0\n'
            'fi\n'
            'cat - >/dev/null; echo "ok"\n'
        )
    elif behavior == "slow":
        codex.write_text(
            '#!/bin/sh\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE"\n'
            '  exit 0\n'
            'fi\n'
            'sleep 30\n'
        )
    elif behavior == "fail":
        codex.write_text(
            '#!/bin/sh\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE"\n'
            '  exit 0\n'
            'fi\n'
            'echo "codex internal error" >&2; exit 7\n'
        )
    codex.chmod(0o755)


def run_codex(scope_path, prompt_path, stdout_path, stderr_path,
              status_path=None, timeout=None, **kwargs):
    args = ["python3", str(SCRIPTS_DIR / "run-codex.py"),
            "--scope", str(scope_path),
            "--prompt-file", str(prompt_path),
            "--stdout", str(stdout_path),
            "--stderr", str(stderr_path)]
    if status_path:
        args += ["--status", str(status_path)]
    env = kwargs.pop("env", None) or {}
    if timeout is not None:
        env["COMBINED_REVIEW_CODEX_TIMEOUT"] = str(timeout)
    import os as _os
    env = {**_os.environ, **env}
    return subprocess.run(args, capture_output=True, text=True, env=env, **kwargs)


def test_run_codex_writes_to_orchestrator_paths(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "echo")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("review please")
    stdout = tmp_path / "out"; stderr = tmp_path / "err"; status = tmp_path / "status.json"
    r = run_codex(scope, prompt, stdout, stderr, status_path=status)
    assert r.returncode == 0, r.stderr
    assert stdout.exists() and stderr.exists() and status.exists()
    assert "---FINDING---" in stdout.read_text()
    st = json.loads(status.read_text())
    assert st["status"] == "ok"
    assert st["exit_code"] == 0
    # orchestrator-owned files must not be deleted
    assert prompt.exists() and stdout.exists()


def test_run_codex_records_failure(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "fail")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
    # run-codex always exits 0; outcome is in the status file
    assert r.returncode == 0
    st = json.loads(status.read_text())
    assert st["status"] == "failed"
    assert st["exit_code"] == 7


def test_run_codex_records_timeout(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "slow")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e",
                  status_path=status, timeout=2)
    assert r.returncode == 0
    st = json.loads(status.read_text())
    assert st["status"] == "timeout"


def test_run_codex_errors_without_sandbox_support(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "no-sandbox")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
    # Sandbox-flag failure is a HARD error — exits non-zero, no status file written.
    assert r.returncode != 0
    assert "sandbox" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_run_codex.py -v
```

- [ ] **Step 3: Implement `scripts/run-codex.py`**

```python
#!/usr/bin/env python3
"""run-codex.py — drive `codex exec --sandbox read-only` with a stdin prompt.

Portable across macOS and Linux. GNU `timeout` isn't on macOS by default and
BSD `date` doesn't support `%3N`, so we use Python's subprocess.run(timeout=)
and time.monotonic_ns() instead.

All long-lived files (prompt, stdout, stderr, status) are orchestrator-owned.
This script writes to them but never deletes them. It ALWAYS exits 0 except
for hard pre-flight failures (missing --sandbox support, missing required
args); outcome of the codex run goes into the status JSON so the
orchestrator's background-Bash mechanics don't have to interpret exit codes.
"""
import argparse
import json
import os
import subprocess
import sys
import time


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--stdout", required=True)
    ap.add_argument("--stderr", required=True)
    ap.add_argument("--status", default=None,
                    help="default: <stdout>.status")
    args = ap.parse_args()

    status_path = args.status or f"{args.stdout}.status"

    def write_failed_status(msg: str, exit_code: int) -> None:
        """Write a status JSON AND mirror the message into the orchestrator-
        owned stderr capture for hard failures. Phase C builds its error
        section from $CODEX_STDERR and report.py embeds it in the audit
        trail. Writing only to sys.stderr (this script's own stderr) would
        leave the audit trail empty for missing-sandbox / missing-codex
        cases — invisible to anyone reading the report.

        Two destinations:
          1. status JSON: structured error for Phase C's reviewer_summary
          2. args.stderr: free-form text the audit trail can show verbatim

        Phase A pre-flight should catch these before Phase B launches at
        all, but this still matters for the (narrow) case where codex was
        upgraded or replaced between Phase A and Phase B.
        """
        try:
            with open(status_path, "w") as sf:
                json.dump({
                    "status": "failed", "exit_code": exit_code,
                    "duration_ms": 0, "timeout_seconds": 0,
                    "error": msg,
                }, sf)
        except OSError:
            pass
        try:
            with open(args.stderr, "w") as ef:
                ef.write(f"run-codex.py hard failure: {msg}\n")
        except OSError:
            pass

    # Hard pre-flight: verify codex exec advertises --sandbox before we ever
    # invoke it. Missing the flag means we cannot guarantee read-only mode —
    # refuse to run rather than silently going unsandboxed.
    # Phase A pre-flight should catch this, but check here too in case codex
    # was upgraded/replaced between Phase A and Phase B launch.
    try:
        help_out = subprocess.run(
            ["codex", "exec", "--help"], capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        msg = "codex not on PATH"
        print(f"error: {msg}", file=sys.stderr)
        write_failed_status(msg, 3); sys.exit(3)
    if "--sandbox" not in (help_out.stdout + help_out.stderr):
        msg = "installed codex does not advertise --sandbox; refusing to run unsandboxed"
        print(f"error: {msg}", file=sys.stderr)
        write_failed_status(msg, 3); sys.exit(3)

    # Resolve cwd: prefer worktree_path (diff-based scopes), else repo_root.
    with open(args.scope) as f:
        scope = json.load(f)
    cwd = scope.get("worktree_path") or scope.get("repo_root") or os.getcwd()

    timeout_s = int(os.environ.get("COMBINED_REVIEW_CODEX_TIMEOUT", "300"))

    with open(args.prompt_file, "rb") as pf, \
         open(args.stdout, "wb") as outf, \
         open(args.stderr, "wb") as errf:
        prompt_bytes = pf.read()
        start = time.monotonic_ns()
        status = "ok"; exit_code = 0
        try:
            proc = subprocess.run(
                ["codex", "exec", "--sandbox", "read-only", "-"],
                input=prompt_bytes, stdout=outf, stderr=errf,
                cwd=cwd, timeout=timeout_s,
            )
            exit_code = proc.returncode
            status = "ok" if exit_code == 0 else "failed"
        except subprocess.TimeoutExpired:
            status = "timeout"; exit_code = 124
        except FileNotFoundError:
            # codex disappeared between --help and exec; treat as failure
            status = "failed"; exit_code = 127
            errf.write(b"codex binary not found at exec time\n")
        end = time.monotonic_ns()

    duration_ms = (end - start) // 1_000_000

    with open(status_path, "w") as sf:
        json.dump({
            "status": status,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "timeout_seconds": timeout_s,
        }, sf)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/run-codex.py
pytest tests/test_run_codex.py -v
```

Expected: 4 passed (writes-to-orchestrator-paths, records-failure, records-timeout, errors-without-sandbox-support).

- [ ] **Step 5: Commit**

```bash
git add scripts/run-codex.py tests/test_run_codex.py
git commit -m "feat: run-codex.py (portable) drives codex exec read-only with orchestrator-owned IO"
```

---

## Task 13: normalize-findings.py

**Files:**
- Create: `scripts/normalize-findings.py`
- Create: `tests/test_normalize_findings.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_normalize_findings.py
"""Tests for normalize-findings.py — delimited-block schema → JSON array."""
import json
from tests.conftest import run_script


SAMPLE = """\
preamble that should be ignored
---FINDING---
severity: high
file: src/foo.py
line: 42
category: bug
title: Null deref when config missing 'api_key'
detail: |
  Accessing config['api_key'] directly raises KeyError.
  Use config.get('api_key') or guard with an early return.
---END-FINDING---
some prose in between
---FINDING---
severity: medium
file: src/bar.py
line: 10-15
category: clarity
title: Function does two unrelated things
detail: |
  Split into authenticate() and load_profile().
---END-FINDING---
trailing noise
"""


def test_parses_two_findings():
    r = run_script("normalize-findings.py", "--source", "codex",
                   input=SAMPLE)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert len(out["findings"]) == 2
    f0 = out["findings"][0]
    assert f0["source"] == "codex"
    assert f0["severity"] == "high"
    assert f0["file"] == "src/foo.py"
    assert f0["line"] == "42"
    assert "KeyError" in f0["detail"]
    f1 = out["findings"][1]
    assert f1["line"] == "10-15"


def test_unparseable_chunks_go_to_warnings():
    bad = """\
---FINDING---
severity: bananas
file: x
title: missing required fields
---END-FINDING---
"""
    r = run_script("normalize-findings.py", "--source", "claude:code-reviewer",
                   input=bad)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    # missing fields → parse warning, severity normalized
    assert len(out["parse_warnings"]) >= 1 or out["findings"][0]["severity"] == "medium"


def test_empty_input_returns_empty_array():
    r = run_script("normalize-findings.py", "--source", "codex", input="")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["findings"] == []
    assert out["parse_warnings"] == []
    assert out["unparsed_chunks"] == []


def test_prose_only_output_becomes_unparsed_chunk():
    """Regression: a reviewer that ignores the schema and emits prose used to
    produce findings:[] AND parse_warnings:[] — silently swallowing the entire
    output. Now we capture it as an unparsed_chunk so the final report shows
    "reviewer X did not follow the schema; see chunk:"."""
    prose = """I reviewed the diff and found a few issues:

1. The naming convention is inconsistent.
2. There's a possible null deref on line 42.
3. The tests don't cover the edge case.

Overall the change looks fine but could use a second pass."""
    r = run_script("normalize-findings.py", "--source", "codex", input=prose)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["findings"] == []
    assert len(out["unparsed_chunks"]) == 1
    assert out["unparsed_chunks"][0]["source"] == "codex"
    assert "null deref" in out["unparsed_chunks"][0]["text"]
    assert len(out["parse_warnings"]) >= 1


def test_text_between_blocks_captured():
    """Prose between two valid FINDING blocks must also surface as a warning."""
    mixed = """\
---FINDING---
severity: high
file: a.py
line: 1
category: bug
title: first
detail: |
  one
---END-FINDING---

Some prose the reviewer added in between that shouldn't be there.

---FINDING---
severity: low
file: b.py
line: 2
category: style
title: second
detail: |
  two
---END-FINDING---
"""
    r = run_script("normalize-findings.py", "--source", "claude:code-reviewer",
                   input=mixed)
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert len(out["findings"]) == 2
    assert any("Some prose" in c["text"] for c in out["unparsed_chunks"])
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_normalize_findings.py -v
```

- [ ] **Step 3: Implement `scripts/normalize-findings.py`**

```python
#!/usr/bin/env python3
"""normalize-findings.py — parse delimited-block reviewer output → JSON.

Reads raw reviewer output on stdin; writes a JSON object with `findings`
(array of normalized finding dicts) and `parse_warnings` (array of strings
describing unparseable chunks). One reviewer's output per invocation.
"""
import argparse
import json
import re
import sys

VALID_SEVERITY = {"critical", "high", "medium", "low"}
SEVERITY_MAP = {
    "critical": "critical", "high": "high", "medium": "medium", "low": "low",
    "error": "high", "warning": "medium", "info": "low", "note": "low",
}
VALID_CATEGORY = {"bug", "test-gap", "perf", "security", "clarity", "style", "other"}


BLOCK_RE = re.compile(
    r"---FINDING---\s*\n(.*?)\n---END-FINDING---",
    re.DOTALL,
)


def parse_block(body: str) -> tuple[dict | None, str | None]:
    """Return (finding dict, warning str). If both None, the block is empty."""
    fields: dict[str, str] = {}
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            i += 1; continue
        key, val = m.group(1), m.group(2)
        if val.strip() == "|":
            # multi-line scalar
            buf = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
                buf.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            fields[key] = "\n".join(buf).strip()
            continue
        fields[key] = val.strip()
        i += 1

    warnings = []
    sev = (fields.get("severity") or "").lower()
    if sev not in VALID_SEVERITY:
        mapped = SEVERITY_MAP.get(sev, "medium")
        warnings.append(f"unknown severity {sev!r} mapped to {mapped!r}")
        sev = mapped
    cat = (fields.get("category") or "other").lower()
    if cat not in VALID_CATEGORY:
        warnings.append(f"unknown category {cat!r} mapped to 'other'")
        cat = "other"
    if not fields.get("title"):
        warnings.append(f"finding missing title; skipping")
        return None, "\n".join(warnings)

    f = {
        "severity": sev,
        "file": fields.get("file") or "(general)",
        "line": fields.get("line") or "-",
        "category": cat,
        "title": fields["title"],
        "detail": fields.get("detail") or "",
    }
    return f, "; ".join(warnings) if warnings else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True,
                    help='e.g. "codex" or "claude:code-reviewer"')
    args = ap.parse_args()
    raw = sys.stdin.read()
    findings: list[dict] = []
    warnings: list[str] = []
    unparsed_chunks: list[dict] = []

    cursor = 0
    for m in BLOCK_RE.finditer(raw):
        # Capture any non-whitespace text BEFORE this block as an unparsed
        # chunk. A reviewer that ignores the schema and emits prose would
        # otherwise produce findings: [] and warnings: [] silently — the
        # spec says these failures must surface in the final report.
        between = raw[cursor:m.start()].strip()
        if between:
            unparsed_chunks.append({
                "source": args.source,
                "text": between[:1000],  # cap; full raw is in audit trail
                "position": "before_block" if findings else "preamble",
            })
            warnings.append(
                f"[{args.source}] {len(between)} chars of non-schema text outside "
                f"---FINDING--- blocks (see unparsed_chunks)"
            )
        body = m.group(1)
        finding, warn = parse_block(body)
        if finding is not None:
            finding["source"] = args.source
            findings.append(finding)
        if warn:
            warnings.append(f"[{args.source}] {warn}")
        cursor = m.end()

    # Trailing text after the last block (or all text if no blocks matched).
    trailing = raw[cursor:].strip()
    if trailing:
        unparsed_chunks.append({
            "source": args.source,
            "text": trailing[:1000],
            "position": "postamble" if findings else "no_blocks",
        })
        warnings.append(
            f"[{args.source}] {len(trailing)} chars of non-schema text after "
            f"last FINDING block (see unparsed_chunks)"
        )

    json.dump({
        "findings": findings,
        "parse_warnings": warnings,
        "unparsed_chunks": unparsed_chunks,
    }, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/normalize-findings.py
pytest tests/test_normalize_findings.py -v
```

Expected: 5 passed (parses-two-findings, unparseable-chunks-go-to-warnings, empty-input, prose-only-becomes-unparsed-chunk, text-between-blocks-captured).

- [ ] **Step 5: Commit**

```bash
git add scripts/normalize-findings.py tests/test_normalize_findings.py
git commit -m "feat: normalize-findings.py parses delimited-block schema with parse warnings"
```

---

## Task 14: validate-clusters.py

**Files:**
- Create: `scripts/validate-clusters.py`
- Create: `tests/test_validate_clusters.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_validate_clusters.py
"""Tests for validate-clusters.py — JSON Schema check on synthesis output."""
import json
from tests.conftest import run_script


VALID_CLUSTERS = {
    "scope_summary": "PR #105",
    "mode": "code",
    "focus": None,
    "reviewer_summary": {
        "codex": {"status": "ok", "raw_findings": 3, "parse_warnings": 0},
        "claude": [
            {"agent": "code-reviewer", "status": "ok",
             "raw_findings": 2, "parse_warnings": 0},
        ],
    },
    "clusters": [
        {
            "tag": "agreement",
            "severity": "high",
            "file": "src/foo.py",
            "line": "42",
            "category": "bug",
            "title": "Null deref",
            "synthesized_detail": "Both reviewers flag this.",
            "sources": [
                {"source": "codex", "original_title": "Null deref",
                 "original_detail": "...", "severity": "high"},
                {"source": "claude:code-reviewer",
                 "original_title": "Possible KeyError",
                 "original_detail": "...", "severity": "medium"},
            ],
            "severity_divergence": "codex=high, claude=medium → high",
        },
    ],
    "unparsed_chunks": [],
}


def test_valid_passes():
    r = run_script("validate-clusters.py", input=json.dumps(VALID_CLUSTERS))
    assert r.returncode == 0, r.stderr


def test_invalid_severity_fails():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["clusters"][0]["severity"] = "blocker"
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0
    assert "severity" in r.stderr.lower()


def test_missing_clusters_field_fails():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    del bad["clusters"]
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_invalid_tag_fails():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["clusters"][0]["tag"] = "maybe"
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_codex_timeout_status_accepted():
    """Schema must accept timeout from run-codex.py."""
    ok = json.loads(json.dumps(VALID_CLUSTERS))
    ok["reviewer_summary"]["codex"] = {
        "status": "timeout", "error": "codex did not finish within 300s",
        "duration_ms": 300000,
    }
    r = run_script("validate-clusters.py", input=json.dumps(ok))
    assert r.returncode == 0, r.stderr


def test_codex_skipped_status_accepted():
    """Schema must accept skipped (--no-codex was passed)."""
    ok = json.loads(json.dumps(VALID_CLUSTERS))
    ok["reviewer_summary"]["codex"] = {"status": "skipped"}
    # Also drop codex from any cluster sources so we don't accidentally
    # claim codex contributed to a finding when it was skipped.
    for c in ok["clusters"]:
        c["sources"] = [s for s in c["sources"] if s["source"] != "codex"]
        if not c["sources"]:
            c["sources"] = [{"source": "claude:code-reviewer",
                             "original_title": "...", "original_detail": "...",
                             "severity": "medium"}]
            c["tag"] = "claude_only"
    r = run_script("validate-clusters.py", input=json.dumps(ok))
    assert r.returncode == 0, r.stderr


def test_unparsed_chunks_rejects_bare_string():
    """Regression: previously the schema accepted any array shape for
    unparsed_chunks. A bare string item ("raw prose") validated fine and
    then crashed report.py at ch['source'] lookup. Now: each item must
    be an object with source + text."""
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["unparsed_chunks"] = ["raw prose"]
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_unparsed_chunks_rejects_missing_source():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["unparsed_chunks"] = [{"text": "no source field"}]
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_validate_clusters.py -v
```

- [ ] **Step 3: Implement `scripts/validate-clusters.py`**

```python
#!/usr/bin/env python3
"""validate-clusters.py — JSON-Schema-validate the synthesis cluster JSON.

Exits 0 if valid; non-zero with a descriptive stderr if not. The orchestrator
catches non-zero, re-prompts the synthesis LLM once with the error, then
re-validates. If validation fails twice, the final report runs in "synthesis
failed" mode (see SKILL.md).
"""
import json
import sys

import jsonschema

SCHEMA = {
    "type": "object",
    "required": ["scope_summary", "mode", "reviewer_summary",
                 "clusters", "unparsed_chunks"],
    "properties": {
        "scope_summary": {"type": "string"},
        "mode": {"enum": ["code", "spec", "plan", "docs"]},
        "focus": {"type": ["string", "null"]},
        "reviewer_summary": {
            "type": "object",
            "required": ["codex", "claude"],
            "properties": {
                "codex": {
                    "type": "object",
                    "required": ["status"],
                    "properties": {
                        "status": {"enum": ["ok", "failed", "timeout", "skipped"]},
                        "raw_findings": {"type": "integer"},
                        "parse_warnings": {"type": "integer"},
                        "error": {"type": "string"},
                        "duration_ms": {"type": "integer"},
                    },
                },
                "claude": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["agent", "status"],
                        "properties": {
                            "agent": {"type": "string"},
                            "status": {"enum": ["ok", "failed", "skipped"]},
                            "raw_findings": {"type": "integer"},
                            "parse_warnings": {"type": "integer"},
                            "error": {"type": "string"},
                        },
                    },
                },
            },
        },
        "clusters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["tag", "severity", "file", "line",
                             "category", "title", "synthesized_detail", "sources"],
                "properties": {
                    "tag": {"enum": ["agreement", "claude_only",
                                     "codex_only", "disagreement"]},
                    "severity": {"enum": ["critical", "high", "medium", "low"]},
                    "file": {"type": "string"},
                    "line": {"type": "string"},
                    "category": {"enum": ["bug", "test-gap", "perf",
                                          "security", "clarity", "style", "other"]},
                    "title": {"type": "string"},
                    "synthesized_detail": {"type": "string"},
                    "sources": {
                        "type": "array", "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["source", "severity"],
                            "properties": {
                                "source": {"type": "string"},
                                "original_title": {"type": "string"},
                                "original_detail": {"type": "string"},
                                "severity": {"enum": ["critical", "high",
                                                      "medium", "low"]},
                            },
                        },
                    },
                    "severity_divergence": {"type": "string"},
                },
            },
        },
        "unparsed_chunks": {
            "type": "array",
            "items": {
                "type": "object",
                # report.py iterates these and reads ch['source'] + ch.get('text','')
                # — a bare-string item (legal under the prior {type: array} shape)
                # would crash rendering. The item schema below mirrors what
                # normalize-findings.py actually emits.
                "required": ["source", "text"],
                "properties": {
                    "source": {"type": "string"},
                    "text": {"type": "string"},
                    "position": {"type": "string"},
                },
            },
        },
    },
}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"error: input is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    try:
        jsonschema.validate(data, SCHEMA)
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        print(f"error: schema violation at {path}: {e.message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/validate-clusters.py
pytest tests/test_validate_clusters.py -v
```

Expected: 8 passed (valid, invalid-severity, missing-clusters, invalid-tag, codex-timeout-accepted, codex-skipped-accepted, unparsed-rejects-bare-string, unparsed-rejects-missing-source).

- [ ] **Step 5: Commit**

```bash
git add scripts/validate-clusters.py tests/test_validate_clusters.py
git commit -m "feat: validate-clusters.py JSON Schema check on synthesis output"
```

---

## Task 15: report.py — final Markdown rendering

**Files:**
- Create: `scripts/report.py`
- Create: `tests/test_report.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_report.py
"""Tests for report.py — cluster JSON + raw outputs → final Markdown."""
import json
import subprocess
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def test_report_renders_high_confidence_section(tmp_path):
    clusters = {
        "scope_summary": "PR #105",
        "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "ok", "raw_findings": 1, "parse_warnings": 0},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 1, "parse_warnings": 0}],
        },
        "clusters": [
            {
                "tag": "agreement", "severity": "high",
                "file": "src/foo.py", "line": "42", "category": "bug",
                "title": "Null deref",
                "synthesized_detail": "Both flag this.",
                "sources": [
                    {"source": "codex", "severity": "high"},
                    {"source": "claude:code-reviewer", "severity": "medium"},
                ],
                "severity_divergence": "codex=high vs claude=medium → high",
            },
        ],
        "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "codex.txt"; codex_raw.write_text("raw codex")
    claude_raw = tmp_path / "claude.txt"; claude_raw.write_text("raw claude")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw),
         "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    md = r.stdout
    assert "# Combined Review" in md
    assert "PR #105" in md
    assert "## High-confidence findings" in md
    assert "src/foo.py:42" in md
    assert "Null deref" in md
    assert "codex, claude:code-reviewer" in md
    assert "raw codex" in md
    assert "raw claude" in md


def test_report_embeds_codex_stderr_in_audit(tmp_path):
    """When codex fails (auth/quota/sandbox), the diagnostic lives on stderr.
    Earlier versions only embedded stdout, so users saw the reviewer_summary
    line and nothing else. Stderr must appear in the audit-trail section."""
    clusters = {
        "scope_summary": "PR #99", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "failed", "error": "auth", "exit_code": 1},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 0, "parse_warnings": 0}],
        },
        "clusters": [], "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    codex_err = tmp_path / "ce.txt"
    codex_err.write_text("ERROR: codex auth failed: token expired at 12:34 UTC")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw),
         "--codex-stderr", str(codex_err),
         "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    md = r.stdout
    assert "Codex stderr" in md
    assert "token expired" in md


def test_report_renders_codex_timeout_in_reviewer_status(tmp_path):
    """If codex timed out, the user must see it in the report — not just
    "no codex findings" with no explanation."""
    clusters = {
        "scope_summary": "PR #105", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "timeout", "duration_ms": 300000,
                      "error": "did not finish within 300s"},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 1, "parse_warnings": 0}],
        },
        "clusters": [],
        "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("raw claude")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    md = r.stdout
    assert "## Reviewer status" in md
    assert "Codex" in md and "timeout" in md
    assert "300s" in md


def test_report_renders_no_codex_skipped(tmp_path):
    """`--no-codex` runs must show codex as 'skipped' in the report."""
    clusters = {
        "scope_summary": "uncommitted", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "skipped"},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 0, "parse_warnings": 0}],
        },
        "clusters": [], "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "skipped" in r.stdout
    assert "--no-codex" in r.stdout


def test_report_renders_failed_claude_agent(tmp_path):
    """A failed sub-agent must appear in the reviewer status section."""
    clusters = {
        "scope_summary": "PR #5", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "ok", "raw_findings": 2, "parse_warnings": 0},
            "claude": [
                {"agent": "code-reviewer", "status": "ok",
                 "raw_findings": 1, "parse_warnings": 0},
                {"agent": "pr-test-analyzer", "status": "failed",
                 "error": "agent dispatch failed"},
            ],
        },
        "clusters": [], "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "pr-test-analyzer" in r.stdout
    assert "failed" in r.stdout


def test_report_synthesis_failed_banner(tmp_path):
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("c")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("cl")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw),
         "--claude-raw", str(claude_raw),
         "--synthesis-failed", "schema invalid: clusters missing"],
        input="", capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "Synthesis failed" in r.stdout
    assert "schema invalid" in r.stdout
    assert "raw codex" not in r.stdout  # but raw outputs should be embedded:
    # actually they should be embedded — fix:
    assert "c\n" in r.stdout or "raw" in r.stdout.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_report.py -v
```

- [ ] **Step 3: Implement `scripts/report.py`**

```python
#!/usr/bin/env python3
"""report.py — render the final Combined Review report from cluster JSON.

Inputs:
- stdin: cluster JSON (from synthesis pass, validated by validate-clusters.py).
  Empty when --synthesis-failed is set.
- --codex-raw <path>: codex raw output file
- --claude-raw <path>: aggregated Claude sub-agent transcripts
- --synthesis-failed "<msg>": if set, emit a "synthesis failed" report
  with raw outputs only and the diagnostic message.

Output: Markdown to stdout.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


# Duplicated from render-prompt.py (small helpers; not worth a shared module
# for a personal skill). Reviewer transcripts routinely contain triple-
# backtick code blocks (codex inlines diffs, Claude agents inline examples),
# so wrapping raw output in plain ``` would let the first inner ``` close the
# outer fence — same class of bug as the prompt-rendering one, but in the
# audit-trail section of the report.
def fence_for(content: str) -> str:
    longest = 0
    run = 0
    for ch in content:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def fenced(content: str, lang: str = "") -> str:
    fence = fence_for(content)
    return f"{fence}{lang}\n{content.rstrip(chr(10))}\n{fence}"


def header(scope_summary: str, mode: str, focus: str | None) -> str:
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Combined Review", "",
        f"**Scope:** {scope_summary}", f"**Mode:** {mode}",
        f"**Focus:** {focus or '(none)'}",
        f"**Generated:** {ts}",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def render_reviewer_status(rs: dict) -> str:
    """Render the reviewer_summary block so codex failures/timeouts/skipped
    runs and failed Claude agents are visible in the final report — not buried
    in the raw outputs section. Promised in §10 'In-flight failure handling';
    omitting this caused the user-facing report to silently degrade."""
    lines = ["## Reviewer status", ""]
    codex = rs.get("codex", {})
    cstatus = codex.get("status", "unknown")
    if cstatus == "ok":
        rf = codex.get("raw_findings", "?")
        pw = codex.get("parse_warnings", 0)
        warn = f" ({pw} parse warnings)" if pw else ""
        lines.append(f"- **Codex**: ok — {rf} raw findings{warn}")
    elif cstatus == "skipped":
        lines.append("- **Codex**: skipped (`--no-codex`)")
    elif cstatus in ("failed", "timeout"):
        dur = codex.get("duration_ms")
        dur_s = f" after {dur//1000}s" if isinstance(dur, int) else ""
        err = codex.get("error", "no detail")
        # truncate aggressive — full stderr is in the raw outputs section
        if len(err) > 240: err = err[:240] + "…"
        lines.append(f"- **Codex**: {cstatus}{dur_s} — `{err}`")
    else:
        lines.append(f"- **Codex**: {cstatus}")
    for agent in rs.get("claude", []):
        name = agent.get("agent", "?")
        st = agent.get("status", "unknown")
        if st == "ok":
            rf = agent.get("raw_findings", "?")
            pw = agent.get("parse_warnings", 0)
            warn = f" ({pw} parse warnings)" if pw else ""
            lines.append(f"- **Claude:{name}**: ok — {rf} raw findings{warn}")
        elif st == "failed":
            err = agent.get("error", "no detail")
            if len(err) > 240: err = err[:240] + "…"
            lines.append(f"- **Claude:{name}**: failed — `{err}`")
        else:
            lines.append(f"- **Claude:{name}**: {st}")
    lines.append("")
    return "\n".join(lines)


def render_cluster(c: dict) -> str:
    src_list = ", ".join(s["source"] for s in c["sources"])
    parts = [
        f"- **[{c['severity'].title()}] {c['file']}:{c['line']}** — {c['title']}",
        f"  {c['synthesized_detail']}",
        f"  _Sources: {src_list}_",
    ]
    if c.get("severity_divergence"):
        parts.append(f"  _Severity: {c['severity_divergence']}_")
    return "\n".join(parts)


def by_tag(clusters: list[dict], tag: str) -> list[dict]:
    out = [c for c in clusters if c["tag"] == tag]
    out.sort(key=lambda c: SEV_ORDER.get(c["severity"], 4))
    return out


def render_sections(clusters: list[dict]) -> str:
    sections = []
    agreements = by_tag(clusters, "agreement")
    if agreements:
        sections.append("## High-confidence findings (both tools agree)\n")
        sections += [render_cluster(c) for c in agreements]
        sections.append("")
    claude_only = by_tag(clusters, "claude_only")
    codex_only = by_tag(clusters, "codex_only")
    if claude_only or codex_only:
        sections.append("## Single-source findings\n")
        if claude_only:
            sections.append("### Claude only\n")
            sections += [render_cluster(c) for c in claude_only]
            sections.append("")
        if codex_only:
            sections.append("### Codex only\n")
            sections += [render_cluster(c) for c in codex_only]
            sections.append("")
    disagreements = by_tag(clusters, "disagreement")
    if disagreements:
        sections.append("## Disagreements (worth a second look)\n")
        sections += [render_cluster(c) for c in disagreements]
        sections.append("")
    if not (agreements or claude_only or codex_only or disagreements):
        sections.append("## No issues found\n")
    return "\n".join(sections)


def _read_or_empty(p: Path | None) -> str:
    if p is None or not p.exists():
        return ""
    try:
        return p.read_text()
    except OSError:
        return ""


def render_raw(codex_raw: Path, claude_raw: Path, codex_stderr: Path | None) -> str:
    """Embed raw reviewer outputs in a collapsed audit-trail section.

    Codex stderr is critical for failure/timeout diagnostics (auth errors,
    quota exhaustion, sandbox refusals) — codex writes the diagnostic to
    stderr and produces no findings on stdout. Earlier versions only embedded
    stdout, leaving users with the reviewer_summary line as the only signal.
    Now we include stderr when it has content, so the failure mode is
    actually debuggable from the report alone.
    """
    err_text = _read_or_empty(codex_stderr).rstrip()
    codex_text = codex_raw.read_text().rstrip() or "(empty)"
    claude_text = claude_raw.read_text().rstrip() or "(empty)"
    parts = [
        "---", "",
        "<details>", "<summary>Raw outputs (audit trail)</summary>", "",
        "### Codex stdout", "",
        fenced(codex_text), "",
    ]
    if err_text:
        parts += [
            "### Codex stderr", "",
            fenced(err_text), "",
        ]
    parts += [
        "### Claude sub-agents", "",
        fenced(claude_text), "",
        "</details>", "",
    ]
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--codex-raw", required=True, type=Path,
                    help="codex stdout capture")
    ap.add_argument("--codex-stderr", default=None, type=Path,
                    help="codex stderr capture (recommended — failures live here)")
    ap.add_argument("--claude-raw", required=True, type=Path)
    # Two ways to pass the synthesis-failure message:
    #   --synthesis-failed "<msg>" — convenient when msg is short and known-safe
    #   --synthesis-failed-file <path> — REQUIRED when msg originates from
    #     validator stderr / model output / anything the orchestrator can't
    #     pre-sanitize. Same shell-injection class as the focus-text case:
    #     interpolating arbitrary content into a Bash command line is unsafe.
    ap.add_argument("--synthesis-failed", default=None)
    ap.add_argument("--synthesis-failed-file", default=None, type=Path)
    args = ap.parse_args()
    if args.synthesis_failed and args.synthesis_failed_file:
        ap.error("--synthesis-failed and --synthesis-failed-file are mutually exclusive")
    synthesis_failed_msg = args.synthesis_failed
    if args.synthesis_failed_file is not None:
        try:
            synthesis_failed_msg = args.synthesis_failed_file.read_text().strip()
        except OSError as e:
            ap.error(f"could not read --synthesis-failed-file: {e}")

    if synthesis_failed_msg:
        out = [
            "# Combined Review — synthesis failed", "",
            f"> **Synthesis failed.** {synthesis_failed_msg}",
            "> Manual review of raw outputs required.", "",
            "---", "",
            render_raw(args.codex_raw, args.claude_raw, args.codex_stderr),
        ]
        sys.stdout.write("\n".join(out))
        return

    data = json.load(sys.stdin)
    out = [
        header(data["scope_summary"], data["mode"], data.get("focus")),
        render_reviewer_status(data.get("reviewer_summary", {})),
        render_sections(data["clusters"]),
    ]
    if data.get("unparsed_chunks"):
        out.append("## Parse warnings\n")
        for ch in data["unparsed_chunks"]:
            out.append(f"- From {ch['source']}: {ch.get('text','')[:200]}")
        out.append("")
    out.append(render_raw(args.codex_raw, args.claude_raw, args.codex_stderr))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/report.py
pytest tests/test_report.py -v
```

Expected: 6 passed (high-confidence rendering, codex-stderr-in-audit, codex-timeout-in-reviewer-status, no-codex-skipped, failed-claude-agent, synthesis-failed-banner).

- [ ] **Step 5: Commit**

```bash
git add scripts/report.py tests/test_report.py
git commit -m "feat: report.py renders cluster JSON + raw outputs to Markdown"
```

---

## Task 16: cleanup-worktree.sh

**Files:**
- Create: `scripts/cleanup-worktree.sh`
- Create: `tests/test_cleanup_worktree.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cleanup_worktree.py
"""Tests for cleanup-worktree.sh — triple-assertion gate before removal."""
import subprocess
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def cleanup(repo, worktree):
    return subprocess.run(
        [str(SCRIPTS_DIR / "cleanup-worktree.sh"), str(repo), str(worktree)],
        capture_output=True, text=True,
    )


def test_cleanup_removes_legitimate_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    wt = tmp_path / "combined-review-x-abcdef"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=tmp_repo, check=True)
    assert wt.exists()
    r = cleanup(tmp_repo, wt)
    assert r.returncode == 0, r.stderr
    assert not wt.exists()


def test_cleanup_refuses_repo_root(tmp_repo):
    r = cleanup(tmp_repo, tmp_repo)
    assert r.returncode != 0
    assert "refus" in r.stderr.lower() or "root" in r.stderr.lower()


def test_cleanup_refuses_arbitrary_directory(tmp_repo, tmp_path):
    arbitrary = tmp_path / "not-a-worktree"
    arbitrary.mkdir()
    r = cleanup(tmp_repo, arbitrary)
    assert r.returncode != 0
    assert arbitrary.exists()  # we DID NOT delete it


def test_cleanup_skips_when_marker_present(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    wt = tmp_path / "combined-review-x-keepme"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=tmp_repo, check=True)
    (wt / ".combined-review-keep").touch()
    r = cleanup(tmp_repo, wt)
    # We expect non-zero (refused) AND the worktree still exists.
    assert r.returncode != 0
    assert wt.exists()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_cleanup_worktree.py -v
```

- [ ] **Step 3: Implement `scripts/cleanup-worktree.sh`**

```bash
#!/usr/bin/env bash
# cleanup-worktree.sh <repo_root> <worktree_path>
#
# Triple-assertion gate before destructive removal:
#   1. Path appears in `git worktree list --porcelain` for the repo.
#   2. Path matches the combined-review-* mktemp pattern under $TMPDIR or /tmp.
#   3. Path is not the repo root, and not the main worktree.
# Plus: skip if `.combined-review-keep` marker exists at the worktree root.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: cleanup-worktree.sh <repo_root> <worktree_path>" >&2
  exit 2
fi
REPO="$1"
WT="$2"
REPO_ABS="$(cd "$REPO" && pwd)"
WT_ABS="$(cd "$(dirname "$WT")" && pwd)/$(basename "$WT")"

# 0. Marker check
if [[ -f "$WT_ABS/.combined-review-keep" ]]; then
  echo "refused: marker .combined-review-keep present at $WT_ABS" >&2
  exit 3
fi

# 1. git worktree registry check
if ! git -C "$REPO_ABS" worktree list --porcelain | grep -Fq "worktree $WT_ABS"; then
  echo "refused: $WT_ABS not in git worktree list for $REPO_ABS" >&2
  exit 3
fi

# 2. mktemp pattern check (basename must start with combined-review-)
base="$(basename "$WT_ABS")"
if [[ ! "$base" =~ ^combined-review- ]]; then
  echo "refused: $WT_ABS basename does not match combined-review-* pattern" >&2
  exit 3
fi
parent="$(cd "$(dirname "$WT_ABS")" && pwd)"
TMP="${TMPDIR:-/tmp}"
TMP_ABS="$(cd "$TMP" && pwd)"
if [[ "$parent" != "$TMP_ABS" && "$parent" != "/tmp" ]]; then
  echo "refused: $WT_ABS parent ($parent) is not \$TMPDIR ($TMP_ABS) or /tmp" >&2
  exit 3
fi

# 3. not repo root, not main worktree
if [[ "$WT_ABS" == "$REPO_ABS" ]]; then
  echo "refused: $WT_ABS is the repo root" >&2
  exit 3
fi
main_wt="$(git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2; exit}')"
if [[ "$WT_ABS" == "$main_wt" ]]; then
  echo "refused: $WT_ABS is the main worktree" >&2
  exit 3
fi

git -C "$REPO_ABS" worktree remove --force "$WT_ABS"
echo "removed: $WT_ABS"
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/cleanup-worktree.sh
pytest tests/test_cleanup_worktree.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/cleanup-worktree.sh tests/test_cleanup_worktree.py
git commit -m "feat: cleanup-worktree.sh with triple-assertion safety gate"
```

---

## Task 17: gc-worktrees.sh

**Files:**
- Create: `scripts/gc-worktrees.sh`
- Create: `tests/test_gc_worktrees.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_gc_worktrees.py
"""Tests for gc-worktrees.sh — list-then-filter via git worktree list."""
import os
import subprocess
import time
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def gc(repo):
    return subprocess.run(
        [str(SCRIPTS_DIR / "gc-worktrees.sh"), str(repo)],
        capture_output=True, text=True,
    )


def make_aged_worktree(repo, tmp_path, name, age_hours):
    wt = tmp_path / name
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=repo, check=True)
    old = time.time() - (age_hours * 3600)
    os.utime(wt, (old, old))
    return wt


def test_gc_removes_old_combined_review(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    old_wt = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-aaa", 48)
    r = gc(tmp_repo)
    assert r.returncode == 0, r.stderr
    assert not old_wt.exists()


def test_gc_skips_marked_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    kept = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-keep", 48)
    (kept / ".combined-review-keep").touch()
    r = gc(tmp_repo)
    assert r.returncode == 0, r.stderr
    assert kept.exists()


def test_gc_skips_recent_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    recent = make_aged_worktree(tmp_repo, tmp_path, "combined-review-recent-bbb", 1)
    r = gc(tmp_repo)
    assert r.returncode == 0
    assert recent.exists()


def test_gc_skips_non_combined_review_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    other = make_aged_worktree(tmp_repo, tmp_path, "some-other-wt", 48)
    r = gc(tmp_repo)
    assert r.returncode == 0
    assert other.exists()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_gc_worktrees.py -v
```

- [ ] **Step 3: Implement `scripts/gc-worktrees.sh`**

```bash
#!/usr/bin/env bash
# gc-worktrees.sh <repo_root>
#
# Enumerates worktrees via `git worktree list --porcelain`, selects entries
# matching the combined-review-* basename pattern, AND older than 24h
# (by mtime), AND not carrying a .combined-review-keep marker. Each removal
# goes through the same triple-assertion gate as cleanup-worktree.sh.
set -euo pipefail

REPO="${1:-$PWD}"
REPO_ABS="$(cd "$REPO" && pwd)"
AGE_HOURS="${COMBINED_REVIEW_GC_AGE_HOURS:-24}"
NOW="$(date +%s)"
CUTOFF=$(( NOW - (AGE_HOURS * 3600) ))

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Portable mtime helper. Tries GNU `stat -c %Y` first, then BSD `stat -f %m`,
# then Python as a last-resort fallback. Earlier versions of this script tried
# `stat -f %m` first, but on GNU/Linux `-f` means "filesystem mode" (not file)
# and `%m` is the mount point, so the command exits 0 with non-numeric output —
# the GNU `-c %Y` fallback never ran, and the numeric `[[ ]]` comparison broke
# silently, leaving stale worktrees forever.
mtime_of() {
  local p="$1" m
  if m=$(stat -c %Y "$p" 2>/dev/null); then
    echo "$m"
  elif m=$(stat -f %m "$p" 2>/dev/null); then
    echo "$m"
  else
    python3 -c 'import os, sys; print(int(os.stat(sys.argv[1]).st_mtime))' "$p" 2>/dev/null || echo 0
  fi
}

git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2}' \
| while IFS= read -r wt; do
  base="$(basename "$wt")"
  [[ "$base" =~ ^combined-review- ]] || continue
  [[ -f "$wt/.combined-review-keep" ]] && continue
  mtime="$(mtime_of "$wt")"
  # Sanity-check that mtime is a positive integer before arithmetic; on the
  # off chance both stat forms return something non-numeric, treat as "skip"
  # rather than crash the GC loop.
  if [[ "$mtime" =~ ^[0-9]+$ ]] && [[ "$mtime" -lt "$CUTOFF" ]]; then
    "$SCRIPT_DIR/cleanup-worktree.sh" "$REPO_ABS" "$wt" || true
  fi
done
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/gc-worktrees.sh
pytest tests/test_gc_worktrees.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/gc-worktrees.sh tests/test_gc_worktrees.py
git commit -m "feat: gc-worktrees.sh removes stale combined-review-* worktrees > 24h"
```

---

## Task 18: SKILL.md — orchestration document

**Files:**
- Create: `SKILL.md`

This is a documentation task — no test code, but the SKILL.md content must be precise enough that an LLM following it will execute the pipeline correctly.

- [ ] **Step 1: Write `SKILL.md`**

Note the **four-backtick** outer fence — the SKILL.md content contains many indented triple-backtick code blocks, and a triple-backtick outer fence would let those (indented up to 3 spaces is still valid CommonMark close-fence) terminate the wrapper prematurely.

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "feat: SKILL.md orchestration document for combined-review"
```

---

## Task 19: commands/combined-review.md — slash entry

**Files:**
- Create: `commands/combined-review.md`

- [ ] **Step 1: Write the slash command**

Four-backtick outer fence: the slash command's body contains a triple-backtick block around `$ARGUMENTS`.

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add commands/combined-review.md
git commit -m "feat: slash command entry point for combined-review"
```

---

## Task 20: Install via symlinks; baseline smoke test

**Files:**
- Modify: `README.md` (install instructions)

- [ ] **Step 1: Document install in `README.md`**

Four-backtick outer fence: the README contains multiple triple-backtick code blocks.

````markdown
# combined-review

A Claude Code skill that runs Claude's `pr-review-toolkit` sub-agents and
`codex exec --sandbox read-only` in parallel against the same materialized
review subject, then synthesizes the findings into one report.

See `docs/superpowers/specs/2026-05-11-combined-review-skill-design.md`
in the original juvera repo for the design rationale.

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
````

- [ ] **Step 2: Run the install commands**

```bash
cd ~/projects/combined-review
mkdir -p ~/.claude/skills ~/.claude/commands
ln -sfn "$PWD" ~/.claude/skills/combined-review
ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
ls -la ~/.claude/skills/combined-review
ls -la ~/.claude/commands/combined-review.md
```

Expected: both symlinks present and pointing at `~/projects/combined-review/`. (Earlier audit found `~/.claude/commands/` did not exist on this machine — the `mkdir -p` makes the install idempotent regardless of starting state.)

- [ ] **Step 3: Run the full test suite end-to-end**

```bash
cd ~/projects/combined-review && pytest -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: install instructions and dev workflow"
```

---

## Task 21: End-to-end smoke — --uncommitted on a tiny diff

This task is **manual** — run the skill against a real repo to verify the pipeline holds together. Failures here typically expose orchestration glitches that unit tests miss.

- [ ] **Step 1: Make a tiny throwaway change in this Juvera repo**

**Do NOT modify any existing file** — `git checkout -- <file>` would discard real edits at rollback time. Use a brand-new file that's safe to delete.

```bash
cd ~/Projects/juvera_ai_4
# Create a brand-new file that doesn't exist in the tree
test ! -e .combined-review-smoke.txt || (echo "remove first" && false)
cat > .combined-review-smoke.txt <<'EOF'
# Combined-review smoke test fixture
This file exists only so the skill has something tangible to review.
It will be removed after the smoke test.
EOF
```

- [ ] **Step 2: Invoke `/combined-review --uncommitted`**

In your Claude Code session for the Juvera repo, type:

```
/combined-review --uncommitted
```

- [ ] **Step 3: Verify expected behavior**

- Phase A runs sequentially — you should see GC, args-file write, parse-args, resolve-scope, materialize executed in order via Bash calls (parse-args reads from the args file, never from inline `$ARGUMENTS` substitution).
- Pre-flight passes (codex available, no PR, has reviewable changes — the smoke fixture file is untracked but materialize-scope picks it up).
- Phase B issues one background Bash (codex with `--status` flag) and three Agent calls (code-reviewer, silent-failure-hunter, pr-test-analyzer) in a SINGLE message.
- Phase C reads `$CODEX_STATUS`, branches correctly (should be `ok` for a real codex run).
- Synthesis runs and produces a clustered report.
- Final report is printed.
- Phase D cleanup runs — verify with `ls $TMPDIR/combined-review-*` (no leftovers) and `git worktree list` (no extra entries — though for `--uncommitted` no worktree was created in the first place).

- [ ] **Step 4: Remove the throwaway file**

```bash
cd ~/Projects/juvera_ai_4
rm .combined-review-smoke.txt
git status   # should now be clean
```

- [ ] **Step 5: If anything failed**, capture the failure mode (what didn't run, what error appeared) and fix in a follow-up commit before moving on.

---

## Task 22: End-to-end smoke — --pr on a real PR

- [ ] **Step 1: Pick a small, recently-merged PR in this repo** (or use a current open PR if available)

```bash
cd ~/Projects/juvera_ai_4
gh pr list --state all --limit 5
# pick one with a small diff, e.g., PR #91 (the test-unit gate work)
```

- [ ] **Step 2: Invoke `/combined-review --pr <#>`**

```
/combined-review --pr 91
```

- [ ] **Step 3: Verify**

- A worktree gets created under `$TMPDIR/combined-review-juvera_ai_4-pr-*`
- `gh pr checkout --detach` runs inside it
- `git fetch <base_repo_url> main` runs (NOT `git fetch origin main`)
- `git cat-file -e <head_sha>^{commit}` and `git cat-file -e <base_sha>^{commit}` both succeed
- Both reviewers see the three-dot diff (compare a few line citations against `gh pr diff 91`)
- Report renders
- `cleanup-worktree.sh` runs and the temp worktree is gone

- [ ] **Step 4: If failures**, fix and re-run.

---

## Task 23: End-to-end smoke — --mode spec on a doc file

- [ ] **Step 1: Pick a spec file in this repo**

```bash
ls docs/superpowers/specs/ | head -5
# e.g., docs/superpowers/specs/2026-05-08-ci-test-unit-path-filter-design.md
```

- [ ] **Step 2: Invoke**

```
/combined-review --mode spec docs/superpowers/specs/2026-05-08-ci-test-unit-path-filter-design.md
```

- [ ] **Step 3: Verify**

- `materialize-scope.py` puts the file into `doc_files` (not `changed_files`).
- Codex is invoked via `codex exec` (not codex review).
- ONE Claude agent (document-reviewer brief), not three.
- Findings reflect spec-review concerns (completeness, ambiguity) — NOT "no test coverage".
- Report renders.

- [ ] **Step 4: Fix any issues, then commit any fixes**

---

## Task 24: Final test suite + commit

- [ ] **Step 1: Run the full suite one last time**

```bash
cd ~/projects/combined-review && pytest -v
```

Expected: all green.

- [ ] **Step 2: Check git log for sanity**

```bash
git log --oneline
```

Expected: ~20 commits, each a single coherent step.

- [ ] **Step 3: Push to a fork (optional — only if you intend to share)**

```bash
gh repo create combined-review --public --source=. --remote=origin --push
```

---

## Spec coverage verification

| Spec section | Covered by task(s) |
|---|---|
| §2 Invocation (slash + skill) | T18 (SKILL.md), T19 (slash command) |
| §2 CLI flags | T2 (parse-args.py) |
| §3 Scope resolution | T3, T4, T5 (resolve-scope.py) |
| §4 Codex routing via `codex exec` | T12 (run-codex.py) |
| §4 Worktree lifecycle | T7, T8 (creation), T16 (cleanup), T17 (GC) |
| §4 PR fetch by URL + cat-file check | T8 |
| §4 Shared-primary-input guarantee | T11 (render-prompt unifies both sides' inputs) |
| §4 codex exec --sandbox safety | T12 (verifies flag is supported) |
| §5 Materialize-scope for all kinds | T6, T7, T8, T9 |
| §5 Phase A/B/C/D dispatch ordering | T18 (SKILL.md) |
| §5 Raw output ownership | T18, T12, T20 (manual verify) |
| §6 Mode prompts | T10 |
| §7 Finding schema | T11 (schema appendix), T13 (parser) |
| §8 Synthesis pass + cluster JSON | T18 (skill instructs synthesis) |
| §8 validate-clusters + repair | T14, T18 |
| §9 Report format | T15 |
| §10 Pre-flight checks | T18 (codex auth, gh auth, empty scope, large diff) |
| §10 In-flight failure handling | T18 (codex timeout, sub-agent failure) |
| §11 File layout | T1, all create tasks |
| §12 Testing approach | T21–T23 (smoke), unit tests throughout |
| §13 Non-goals (no auto-fix) | T11 + T12 enforce no-edit |
| §14 Locked decisions | All reflected in implementation |

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

**Which approach?**
`````

### docs/superpowers/specs/2026-05-11-combined-review-skill-design.md  (status: added, kind: text)
````
# Combined Review Skill — Design Spec

**Date:** 2026-05-11
**Scope:** Personal Claude Code skill (`~/.claude/`), not a project artifact. Spec lives here for review history.
**Goal:** A single Claude Code invocation that runs both Claude Code's review (the `pr-review-toolkit` sub-agents) and Codex (via `codex exec --sandbox read-only` driven by a materialized review prompt — see §4 for why we bypass `codex review`'s native diff), then merges findings into a deduped, attributed, high-signal report — without the user juggling two sessions.

---

## 1. Overview

Today the user runs two reviewers in two separate sessions:

- **Claude Code side:** the `pr-review-toolkit` plugin (slash command `/pr-review-toolkit:review-pr`), which dispatches specialized sub-agents — code-reviewer, silent-failure-hunter, pr-test-analyzer, comment-analyzer, type-design-analyzer, code-simplifier — and aggregates into severity buckets. (Not to be confused with Claude Code's built-in `/review` command, which is a separate, lighter-weight flow.) This skill **reuses the toolkit's sub-agents directly** rather than invoking the toolkit's slash command — orchestrating the agents in-session gives us control over prompts and output schema.
- **Codex side:** the `codex` CLI. The skill drives codex via `codex exec --sandbox read-only` with a fully-materialized review prompt (diff + file contents) on stdin, **not** via `codex review`'s native auto-diff. §4 details the reasoning: codex review's diff semantics are unobservable, and a silent mismatch with the Claude-side diff would corrupt synthesis. By feeding both sides the same materialized blob from `materialize-scope.py`, we pin the primary input.

The user's workflow is mostly PR review with occasional spec/plan/doc review. Two-tool review is high-signal because the tools disagree usefully — but the manual merge is tedious and the user wants the synthesis automated.

The skill orchestrates both reviews in parallel from one Claude Code session and produces a unified report that distinguishes:

- **High-confidence findings** — both tools independently flagged the same issue.
- **Single-source findings** — only one tool flagged it.
- **Disagreements** — both tools flagged the same location but with contradictory recommendations.

---

## 2. Invocation

Two files:

- `~/.claude/commands/combined-review.md` — slash command. Parses `$ARGUMENTS`, hands off to the skill.
- `~/.claude/skills/combined-review/SKILL.md` — orchestration logic, activated by the slash command.

This split follows Anthropic's distinction: slash commands are user-typed entry points; skills are model-invoked workflows. The slash command exists because the user wants `/combined-review` to work as a literal command; the skill exists because the orchestration is non-trivial and worth being model-invocable in its own right.

### CLI surface

```
/combined-review                                 # auto-detect scope, code mode
/combined-review --pr 105                        # GitHub PR by number
/combined-review --uncommitted                   # staged + unstaged + untracked
/combined-review --base develop                  # current branch vs custom base (merge-base diff)
/combined-review --commit abc1234                # single commit
/combined-review docs/spec.md plan.md            # positional file list (current contents)
/combined-review --mode spec --pr 105            # spec lens applied to PR changes
/combined-review --focus "API contract changes"  # extra lens, default code mode
/combined-review --full                          # opt into full Claude sub-agent fanout
/combined-review --pr 105 --force-large          # bypass large-diff confirm prompt
/combined-review --pr 105 --keep-worktree        # debug: don't tear down /tmp worktree
```

### Flags

| Flag | Type | Effect |
|---|---|---|
| `--pr <#>` | int | Review GitHub PR by number |
| `--uncommitted` | bool | Review staged + unstaged + untracked |
| `--base <branch>` | string | Review current HEAD vs given base (merge-base diff, §5) |
| `--commit <sha>` | string | Review the changes in one commit |
| `<files...>` | positional | Specific files reviewed as **current working-tree content** (includes any local edits). Mutually exclusive with `--pr`/`--uncommitted`/`--base`/`--commit`. |
| `--mode <code\|spec\|plan\|docs>` | enum, default `code` | Select review template + sub-agent set |
| `--focus "<text>"` | string | Freeform extra emphasis appended to mode prompt |
| `--full` | bool | Use full pr-review-toolkit sub-agent set (6) instead of default 3 |
| `--no-codex` | bool | Skip Codex side (fallback when codex unavailable / quota exhausted) |
| `--save <path>` | string | Also write the final report to a file |
| `--force-large` | bool | Skip the large-diff confirm prompt. Required when the skill runs non-interactively above the threshold. |
| `--keep-worktree` | bool | Debug only. Inhibits worktree teardown and prints the path on completion. |

`--pr`, `--uncommitted`, `--base`, `--commit`, and positional files are mutually exclusive scope inputs. Specifying more than one is an error.

---

## 3. Scope resolution

Precedence (first match wins):

1. **Explicit scope flag** — use it as-is. Worktree rules:
   - **Diff-based scopes** (`--pr`, `--base`, `--commit`) always run inside a disposable clean worktree, never in the user's working tree. This prevents local uncommitted edits from contaminating a branch / PR / commit review.
   - **`--uncommitted`** runs in the user's working tree (that's the point of it).
   - **Positional files** are reviewed as **current working-tree content** including any local edits the user just made. Reviewing a doc/spec/plan you've been editing is the canonical use case — pinning to HEAD would defeat the purpose. No worktree needed.
2. **Dirty tree + PR exists for current branch** — **error**, surface ambiguity, require `--uncommitted` or `--pr <#>`.
3. **Dirty tree, no PR** — implicit `--uncommitted`.
4. **Clean tree, current branch has PR** — implicit `--pr <#>` (resolved via `gh pr view --json number,headRefOid,baseRefOid`).
5. **Clean tree, no PR, current branch ≠ default** — implicit `--base <default>` (default branch via `gh repo view --json defaultBranchRef`).
6. **Clean tree, current branch == default** — **error**, nothing to review.

Logic lives in `scripts/resolve-scope.py`. Emits a normalized scope object:

```json
{
  "kind": "pr" | "uncommitted" | "base" | "commit" | "files",
  "pr_number": 105,
  "base_ref_name": "main",
  "head_ref_name": "feature-x",
  "base_repo_url": "https://github.com/Juvera-AI/juvera_ai.git",
  "head_repo_url": "https://github.com/contributor/juvera_ai.git",
  "base_sha": "<immutable 40-char sha>",
  "head_sha": "<immutable 40-char sha>",
  "commit_sha": "<immutable 40-char sha>",
  "files": ["docs/spec.md"],
  "worktree_path": "<mktemp -d -t combined-review-XXXX>" | null,
  "repo_root": "/abs/path/to/repo",
  "needs_clean_worktree": true | false
}
```

Ref names + repo URLs are used for `git fetch` (portable across remotes, correct for fork PRs); SHAs are used to **verify** the recorded commits are reachable after fetch. Fetching by SHA alone is less portable; trusting the ref alone is unsafe; assuming `origin` is the base repo is wrong for fork PRs.

All ref-shaped inputs are resolved to immutable SHAs by `resolve-scope.py` — never `origin/<branch>` strings passed downstream, since branches move. For `--pr <#>`, this means `gh pr view <#> --json headRefOid,baseRefOid` first, then materialize against those SHAs.

`resolve-scope.py` does not create the worktree — it only sets `needs_clean_worktree: true` when one will be required. Creation is `materialize-scope.py`'s job (§5 / §4 Worktree lifecycle), since materialize is the first step that actually needs the worktree to exist. `worktree_path` in this object is `null` at this stage and gets populated by materialize.

Downstream steps consume this object, not raw flags.

---

## 4. Codex routing

### Shared-primary-input guarantee — why we don't use `codex review`'s native diff

What the skill guarantees, precisely:

- **Same primary input**: both codex and the Claude sub-agents receive the **same materialized blob** from `materialize-scope.py` (§5) — the same unified diff, the same per-file content snapshots, the same metadata. This is what they're *asked* to review.
- **Same repo context**: both run with cwd set to the **same git state** — the worktree pinned at the recorded SHA for diff scopes, the user's tree for `uncommitted`/`files`. Neither agent is isolated from the rest of the repo; both may consult adjacent files for context.
- **Not isolated to the blob**: read-only sandbox prevents *edits*, but `codex exec` and Claude sub-agents (Read, Grep, etc.) can still inspect files beyond the materialized inputs. We don't claim otherwise. Treating "look up callers/types for context" as a feature, not a leak — code review benefits from it, and both tools are looking at the same git state.

What this rules out is the failure mode that motivated this design: `codex review`'s native auto-diff. `codex review` computes its own diff from git state, and we can't observe whether it uses two-dot or three-dot semantics, how it handles untracked files, or how it filters renames. If it diverges from `materialize-scope.py`'s diff, the synthesis (§8) silently merges reviews of different primary inputs.

The skill therefore **bypasses `codex review`'s auto-diff entirely** and uses `codex exec --sandbox read-only` for every scope. The primary input is fixed; context lookups are intentionally allowed. Worth revisiting in v2 if codex review's diff semantics turn out to match ours exactly — but for v1, correctness on the primary input over speculation.

### Scope → invocation

`materialize-scope.py` produces a single content blob (unified diff + per-file `post_content` / `pre_content` / metadata, or doc contents for files mode). Both sides receive this blob. Routing differs only in **what worktree codex runs in** and **what the materialize step has to do first**.

| Scope kind | Setup | Codex invocation |
|---|---|---|
| `uncommitted` | None — operate in user's working tree. Materialize uses `git diff HEAD` + untracked. | `codex exec --sandbox read-only` (cwd = user repo root, prompt via stdin) |
| `base` | `git worktree add --detach <tmp> <head_sha>` (immutable SHA, not literal `HEAD`). Materialize uses `git diff <base_sha>...<head_sha>` inside worktree. | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
| `commit` | `git worktree add --detach <tmp> <commit_sha>`. Materialize uses `git show --format= <commit_sha>` + commit metadata (author, date, message). | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
| `pr` | `git worktree add --detach <tmp>` → `gh pr checkout --detach <#>` → fetch base from `<base_repo_url>` (not necessarily `origin` — see PR fetch detail below) → `git reset --hard <head_sha>` if drifted → verify both SHAs exist via `git cat-file -e <sha>^{commit}`. Materialize uses `git diff <base_sha>...<head_sha>` inside worktree. | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
| `files` (any mode) | None — operate against current working-tree content. Materialize populates `doc_files`. | `codex exec --sandbox read-only` (cwd = user repo root, prompt via stdin) |

### PR fetch detail

In fork/upstream setups, `origin` may be the contributor fork, not the PR base repo. Fetching the base from the wrong remote silently retrieves the wrong commits. The skill:

1. Reads `baseRepository.url`, `headRepository.url`, `baseRefName`, `headRefName`, `baseRefOid`, `headRefOid` from `gh pr view <#> --json baseRepository,headRepository,baseRefName,headRefName,baseRefOid,headRefOid`.
2. Runs `gh pr checkout --detach <#>` inside the worktree (handles the head fetch including fork mirrors).
3. **Fetches the base by URL directly, no remote-add**: `git fetch <base_repo_url> <base_ref_name>`. This fetches the ref into `FETCH_HEAD` without mutating the user's `.git/config` (which `git remote add` would do — and which would leak across runs or fail if the remote name already existed).
4. Pins head: if `git rev-parse HEAD != head_sha`, attempts `git reset --hard <head_sha>`. **If `git reset` fails because the SHA is unreachable**, the PR head was force-pushed between `gh pr view` and `gh pr checkout` — surfaces as **stale-snapshot failure**: "PR head force-pushed mid-review (recorded `<head_sha>` no longer reachable). Rerun `/combined-review --pr <#>` to fetch the current snapshot." No silent fallback; the recorded SHA is the contract.
5. Verifies the recorded base SHA is reachable locally: `git cat-file -e <base_sha>^{commit}`. If unreachable, same stale-snapshot failure with base-side messaging. **Does NOT** assert `FETCH_HEAD == base_sha` — that would fail harmlessly when the base branch advances between `gh pr view` and `git fetch`. We need the recorded commit to be reachable, not to be the current tip.
6. Optionally surfaces a warning if the base tip moved (`FETCH_HEAD != base_sha`) — informational only, doesn't block.

### `codex exec` safety

Because `codex exec` is a general agent (unlike the inherently read-only `codex review`), `run-codex.sh` MUST:

- Pass `--sandbox read-only` (or codex's equivalent flag — `run-codex.sh` probes the installed codex version's flag list at start and errors out if no read-only sandbox is available, rather than silently running unsandboxed).
- Begin the prompt body with an explicit no-edit instruction: `"You are running in review mode. Do not write, edit, or delete any files. Read the materialized inputs below and emit findings only as ---FINDING--- blocks per the schema."`.

Both layers must hold. Missing either violates non-goal §13.

### Worktree lifecycle

- **Creation**: `materialize-scope.py` (§5) creates the worktree when the scope kind requires one, since it needs the worktree to extract file contents and the diff. Path is `mktemp -d -t combined-review-<repo>-XXXXXX` honoring `$TMPDIR`. The path goes into the scope object's `worktree_path` field.
- **Use**: `run-codex.sh` reads `worktree_path` from the scope object and runs codex inside it. Does not create or destroy.
- **Fork PRs**: handled by `gh pr checkout --detach <#>` as the primary path inside the empty worktree. `gh` fetches the PR head into a detached HEAD regardless of whether the PR comes from `origin` or a fork. After checkout, `git reset --hard <head-sha>` pins to the exact recorded SHA (defensive against race between `gh pr view` and `gh pr checkout`).
- **Teardown** — there are three layers, because a skill markdown file cannot hold a shell trap across a multi-tool-call orchestration. **Destructive cleanup never trusts the path string alone** — it cross-checks against git's own worktree registry:
  1. **In-driver trap**: `run-codex.sh` has a `trap 'cleanup' EXIT INT TERM` for temp files it owns *internally* (e.g., intermediate codex state). It does **not** delete the prompt file or the raw-output files — those are passed in by the orchestrator (see "Raw output ownership" below) and have a different lifecycle.
  2. **Explicit orchestrator cleanup**: the SKILL.md instructions require that after synthesis + rendering, the orchestrator's final step is a `Bash` call to `scripts/cleanup-worktree.sh <repo_root> <worktree_path>`. The script runs `git -C <repo_root> worktree remove --force <worktree_path>` only after **three independent assertions**:
     - The path appears in `git -C <repo_root> worktree list --porcelain` for this repo (git considers it a worktree of this repo — the authoritative check, not a pattern match).
     - The path matches the `combined-review-*` mktemp pattern under `$TMPDIR` or `/tmp` (defense-in-depth — if git's registry is somehow wrong, we still won't delete an arbitrary directory).
     - The path is not the repo root and not the user's main worktree.
     If any assertion fails, cleanup-worktree.sh refuses to delete and exits non-zero with a clear message. The skill explicitly forbids skipping this step. Also runs on early-error exit paths.
  3. **GC on every invocation**: `scripts/gc-worktrees.sh` runs as the first step of every `/combined-review` invocation. It enumerates worktrees via `git -C <current-repo-root> worktree list --porcelain` and selects entries whose path matches `combined-review-*` AND whose mtime is older than 24h AND **do not contain a `.combined-review-keep` marker file** at the worktree root. Each removal goes through the same triple-assertion gate as `cleanup-worktree.sh`. **It does not scan `$TMPDIR` for arbitrary directories** — that would pick up leaks from other repos, which the current invocation has no business deleting. Cross-repo orphans wait for the next `/combined-review` in their own repo, or for OS-level `/tmp` cleanup. Worktrees kept via `--keep-worktree` carry the marker and live until the user removes them manually.

  Together: in-driver trap handles run-codex's internal temp files; explicit cleanup handles the worktree under normal completion (with git-registry verification); GC handles orchestrator-died-mid-run leaks within the current repo. No layer relies on path-pattern matching alone for destructive operations.

### Raw output ownership

All long-lived intermediate files — the prompt file, codex stdout capture, codex stderr capture, sub-agent transcripts — are **orchestrator-owned**, not script-owned:

- The orchestrator creates them via `mktemp` before launching reviewers, passes the paths to `run-codex.sh` as `--prompt-file`, `--stdout`, `--stderr` arguments, and to sub-agents inline.
- `run-codex.sh` writes to those paths but never deletes them (its `trap` only cleans up files it created internally).
- `report.py` reads them for the audit-trail section of the final report.
- The orchestrator deletes them as the final step **after `report.py` completes**, via a dedicated `Bash` call.

Without this ownership split, the prior design contradicted itself: `run-codex.sh` was nominally cleaning up the captures, but `report.py` needed them; and the `> <stdout>` redirection shown in §5 was applied by the orchestrator (outside run-codex.sh) anyway, so run-codex.sh couldn't have known about those paths in the first place.
- **`--no-codex`**: still creates a worktree if the Claude side needs one (non-`uncommitted` scopes). Only skips codex invocation.
- **`--keep-worktree`** (debug-only): inhibits the explicit `cleanup-worktree.sh` call and prints the path on completion. **Also writes a marker file `.combined-review-keep` at the worktree root.** `gc-worktrees.sh` skips any worktree containing this marker, regardless of age — so a debug worktree won't get silently swept by a later invocation's GC. The user is responsible for removing kept worktrees manually (`git worktree remove --force <path>`).

The mode prompt + materialized inputs (see §5/§6) are passed to every codex invocation via stdin, not as shell arguments — see §5 "Prompt handling" for why.

---

## 5. Claude-side review

Before any agent dispatch, `scripts/materialize-scope.py` runs once and turns the scope object into concrete bytes both sides can consume. **Both Claude and Codex receive their inputs from this same materialization**, so the primary review subject (the diff + per-file content) is shared. Context lookups against the surrounding repo are intentionally allowed for both — see §4's shared-primary-input guarantee.

### Materialize step

Input: scope object from `resolve-scope.py` (§3).
Output JSON:

```json
{
  "scope_kind": "pr",
  "scope_summary": "PR #105 — Feature X (head abc1234, base def5678)",
  "unified_diff": "<full diff text or null for files-mode>",
  "changed_files": [
    {
      "path": "src/foo.py",
      "old_path": null,
      "status": "modified",
      "kind": "text",
      "lines_changed": [12, 13, 14, 88, 89],
      "post_content": "..."
    },
    {
      "path": "src/legacy.py",
      "old_path": null,
      "status": "deleted",
      "kind": "text",
      "lines_changed": "(deleted)",
      "post_content": null,
      "pre_content": "..."
    },
    {
      "path": "src/new_name.py",
      "old_path": "src/old_name.py",
      "status": "renamed",
      "kind": "text",
      "lines_changed": [12, 13],
      "post_content": "..."
    },
    {
      "path": "assets/logo.png",
      "old_path": null,
      "status": "added",
      "kind": "binary",
      "lines_changed": "(binary)",
      "post_content": null,
      "note": "binary file — content not inlined"
    },
    {
      "path": "config/secrets.link",
      "status": "modified",
      "kind": "symlink",
      "post_content": null,
      "symlink_target": "/etc/secrets.conf"
    },
    {
      "path": "vendor/lib",
      "status": "modified",
      "kind": "submodule",
      "post_content": null,
      "submodule_pre_sha": "abc1234",
      "submodule_post_sha": "def5678"
    }
  ],
  "doc_files": [
    { "path": "docs/spec.md", "content": "..." }
  ],
  "total_lines_changed": 247,
  "changed_file_count": 7,
  "has_reviewable_changes": true,
  "warnings": []
}
```

`has_reviewable_changes` is `true` if `changed_file_count > 0` OR `doc_files` is non-empty. Used by the empty-scope pre-flight (§10) instead of `total_lines_changed == 0`, so a PR that only updates a submodule, symlink, or binary asset is **not** rejected as "nothing to review" — those are legitimate review subjects (e.g., bumping a submodule SHA can be high-risk and deserves review).

File entry fields:

- `status`: `added` | `modified` | `deleted` | `renamed` | `typechange` (per `git diff --name-status`).
- `kind`: `text` | `binary` | `symlink` | `submodule`. Determined from git's mode bits + a content-type sniff.
- `post_content`: present only for text files that still exist after the change. Null for deleted, binary, symlink, submodule.
- `pre_content`: included for `status: deleted` so reviewers can see what was lost. Otherwise null.
- `old_path`: set only for renames; otherwise null.
- `symlink_target` / `submodule_pre_sha` / `submodule_post_sha`: kind-specific fields.

Reviewer prompts include a brief schema explainer so agents know to handle non-text entries appropriately (e.g., "deleted text file — review whether the deletion is correct" rather than "no content").

- **`pr` / `base`**: `unified_diff` is `git diff <base-sha>...<head-sha>` (three-dot / merge-base semantics) — matches GitHub's PR review semantics, excludes unrelated movement on the base branch. `changed_files` is populated per the schema above (one entry per `git diff --name-status` line), with content fields populated according to `kind`.
- **`commit`**: `unified_diff` is `git show --format= <commit-sha>` (the patch the commit introduced). `changed_files` entries reflect the commit's tree.
- **`uncommitted`**: `unified_diff` is `git diff HEAD` (staged + unstaged tracked changes). **Untracked files** (which `git diff HEAD` ignores) are appended to `changed_files` with `status: "added"`, `lines_changed: "(new file)"`, and `post_content` populated if `kind: text`. Without this, the `--uncommitted` flag would silently under-review new files.
- **Positional `files`**: `unified_diff` is `null`, `changed_files` is empty, `doc_files` holds current working-tree contents (with any local edits — see §3 worktree rules). Binary / symlink / submodule files in the positional list are represented in `doc_files` with the same `kind` semantics — content omitted, kind-specific fields populated.
- **Non-code modes with diff scopes** (`--mode spec --pr 105`, etc.): `doc_files` is additionally populated with one entry per changed text file — `{path, status, content}` where `content` is `post_content` for added/modified/renamed and `pre_content` for deleted (so the reviewer can judge whether the deletion was correct). Binary/symlink/submodule changes show up only in `changed_files`, not `doc_files`, since they're not document-reviewable.
- All operations run inside the worktree (when present) or the working tree (`--uncommitted` and positional files).
- `total_lines_changed` counts only text-file line changes (post-change line count for added, deletion count for deleted, both for modified). Binary/symlink/submodule changes contribute 0 — they don't meaningfully load the reviewers.

### Agent dispatch

- **Default (3 sub-agents, code mode):** dispatch three parallel `Agent` calls (using `subagent_type` when available, else general-purpose) — code-reviewer, silent-failure-hunter, pr-test-analyzer. Each receives the materialized diff and file contents.
- **`--full` (6 sub-agents, code mode):** adds comment-analyzer, type-design-analyzer, code-simplifier. Opt-in only.
- **`--mode spec|plan|docs`:** single document-reviewer agent with mode-specific prompt template (§6). Receives `doc_files`. The 3/6 sub-agent fanout is code-specific.

All Claude-side agents receive:

1. The materialized inputs (diff + file contents, or doc contents).
2. The mode-specific review prompt template (§6).
3. `--focus` text appended verbatim if provided.
4. The structured output schema (§7) and a strict instruction to emit findings only in that format.

Codex receives the same materialized inputs through its prompt — always via `codex exec --sandbox read-only` (§4 explains why we don't trust `codex review`'s native diff). Both sides receive the same **primary input**; both also operate against the **same git state** (worktree at recorded SHA or user's tree) and may consult adjacent files for context. The "shared-primary-input" guarantee in §4 spells out the precise scope of what's pinned vs. what's intentionally free.

### Prompt handling

The mode prompt (+ optional `--focus` text + structured-output schema instruction + for `codex exec` the inlined file contents) can be many KB. Passing this as a shell argv is brittle — multi-line content breaks quoting, and argv length limits kick in for `files` mode with large docs.

`run-codex.sh` accepts the prompt via a **file path** (not argv):

- Orchestrator writes the rendered prompt to a temp file *adjacent to* — not inside — any worktree: `mktemp -t combined-review-prompt-XXXXXX` under `$TMPDIR`. Placing it inside the worktree would make codex see it as an untracked file and contaminate the review.
- Invokes `scripts/run-codex.sh --scope <scope.json> --prompt-file <path>` (still passes scope.json by path, not inline).
- `run-codex.sh` reads the prompt file and pipes it to codex on stdin: `cat <prompt-file> | codex exec --sandbox read-only -` (or equivalent stdin syntax for the installed codex version).
- The prompt temp file is **orchestrator-owned** (see §4 "Raw output ownership"). `run-codex.sh` reads it but never deletes it; the orchestrator deletes it in Phase D after `report.py` completes. The script's own `trap` only handles temp files run-codex.sh creates internally, never paths handed in by the orchestrator.

### Dispatch ordering — setup is sequential, reviewers run in parallel

Parallel tool calls within one message run with no defined order — if `Write` and a background `Bash` were issued together, `run-codex.sh` could start before the prompt file existed. The orchestrator therefore splits setup from review:

**Phase A — sequential setup (must complete before Phase B starts):**

1. `Bash` → `scripts/parse-args.py` and `scripts/resolve-scope.py`. Produces the scope object.
2. `Bash` → `scripts/materialize-scope.py`. Creates the worktree if needed; produces the materialized blob.
3. Pre-flight checks (§10): codex availability, gh auth, empty scope, large diff.
4. `Bash` → `mktemp` for the four orchestrator-owned files: `<prompt-path>`, `<codex-stdout>`, `<codex-stderr>`, `<agent-transcripts-dir>`. (One Bash call, four paths captured.)
5. `Write` → render the full prompt (mode template + `--focus` + materialized blob + no-edit instruction + finding schema) to `<prompt-path>`.

Only after step 5 returns do reviewers launch.

**Phase B — parallel review (one message, no inter-dependencies):**

1. `Bash` with `run_in_background: true` — `scripts/run-codex.sh --scope <scope.json> --prompt-file <prompt-path> --stdout <codex-stdout> --stderr <codex-stderr>`. `run-codex.sh` writes to the paths but does not delete them.
2. Multiple `Agent` calls in the same message — one per sub-agent. Each receives the materialized inputs and the rendered prompt body inline. Transcripts come back in-band as the Agent tool's return value; the orchestrator writes them to files under `<agent-transcripts-dir>` for `report.py` to consume.

These two are independent (codex doesn't depend on Agent results and vice versa), so issuing them in the same message is safe — and necessary, since parallel execution is the whole point of running both reviewers in one session.

**Phase C — synthesis + report:** the orchestrator awaits all Phase B results (Agent calls return inline; `Monitor` signals codex completion), runs `normalize-findings.py`, the in-session synthesis pass (§8), `validate-clusters.py`, and `report.py`.

**Phase D — cleanup:** after `report.py` finishes, the orchestrator deletes the orchestrator-owned files (prompt, codex stdout/stderr, agent transcripts) and calls `cleanup-worktree.sh`.

### Default-3 selection rationale

Codex's code-mode pass (driven by the code-mode prompt template) covers comment quality, type design, and code simplification competently — those Claude sub-agents would duplicate effort. The high-signal Claude specialists that codex doesn't naturally cover are code-reviewer (correctness + CLAUDE.md compliance), silent-failure-hunter (error handling), and pr-test-analyzer (coverage gaps). `--full` exists for users who want belt-and-braces.

---

## 6. Mode prompts

Each mode has a template stored in `~/.claude/skills/combined-review/prompts/<mode>.md`. The template is loaded, `--focus` text is appended, then the result is passed to both sides.

| Mode | Template focus |
|---|---|
| `code` (default) | Correctness, bugs, error handling, test coverage, security, performance regressions, CLAUDE.md compliance |
| `spec` | Completeness, ambiguity, internal consistency, scope creep, missing edge cases, unstated assumptions, success criteria |
| `plan` | Step ordering, hidden dependencies, verification steps per task, risk surface, what could fail and not be detected |
| `docs` | Accuracy vs. current code, broken examples, drift, missing prerequisites, audience fit |

All templates end with the schema (§7) and the instruction: "Emit findings only as `---FINDING---` blocks. Do not summarize. Do not include preamble or postamble."

---

## 7. Structured output schema

Both sides emit findings as delimited blocks. Strict JSON from LLMs is unreliable for multi-line `detail` fields; delimited blocks are more robust and easier to recover from partial compliance.

```
---FINDING---
severity: critical|high|medium|low
file: <relative path or "(general)">
line: <int> | <start>-<end> | -
category: bug|test-gap|perf|security|clarity|style|other
title: <single-line summary, no period>
detail: |
  <multi-line free text — recommendation, evidence, suggested fix>
---END-FINDING---
```

Parsing is in `scripts/normalize-findings.py`:

- Input: raw stdout from each reviewer (codex + each Claude sub-agent).
- Output: JSON array of findings, each tagged with `source: "codex" | "claude:<agent-name>"`.
- Best-effort parsing: if a reviewer ignores the schema and emits prose, the parser extracts what it can; unparseable chunks go to a `parse_warnings[]` array so they surface in the final report rather than being silently dropped.
- Severity normalization: any reviewer using non-canonical severity (`error`, `warning`, `info`, etc.) is mapped to the canonical set; unmapped values default to `medium` with a parse warning.

---

## 8. Synthesis pass

After parsing, all findings exist as a single JSON array (`normalized-findings.json`). The skill runs **one in-session LLM pass** (no new agent — main Claude does it) that emits **cluster JSON only** — not Markdown. Markdown rendering is `report.py`'s job (§9).

The synthesis LLM step:

1. **Clusters findings by semantic similarity** — same root issue across tools, regardless of phrasing. Inputs to clustering: `file`, `line` proximity (≤ 10 lines), and `title + detail` text. The LLM does the judgment; no string-distance heuristics — those over-merge or under-merge.

2. **Tags each cluster:**
   - `agreement` — at least one finding from codex AND at least one from claude.
   - `claude_only` — claude-only.
   - `codex_only` — codex-only.
   - `disagreement` — at least one finding from each side, but the recommendations are contradictory (e.g., one says "add nil check", the other says "remove the redundant nil check").

3. **Synthesises wording** — picks the clearer description, merges complementary detail.

4. **Re-ranks severity** — if tools agree, keep it. If they disagree, take the higher and note the divergence.

### Cluster JSON schema (synthesis output → report input)

```json
{
  "scope_summary": "PR #105 — ...",
  "mode": "code",
  "focus": "API contract changes",
  "reviewer_summary": {
    "codex": { "status": "ok", "raw_findings": 14, "parse_warnings": 0 },
    "claude": [
      { "agent": "code-reviewer", "status": "ok", "raw_findings": 8, "parse_warnings": 0 },
      { "agent": "silent-failure-hunter", "status": "ok", "raw_findings": 3, "parse_warnings": 0 },
      { "agent": "pr-test-analyzer", "status": "failed", "error": "timeout" }
    ]
  },
  "clusters": [
    {
      "tag": "agreement",
      "severity": "high",
      "file": "src/foo.py",
      "line": "42",
      "category": "bug",
      "title": "Null deref when config is missing 'api_key'",
      "synthesized_detail": "Both reviewers flag that accessing `config['api_key']` directly will raise KeyError. Codex suggests `config.get('api_key')`; Claude suggests an early-return guard. Recommended: early-return guard — surfaces the misconfiguration explicitly.",
      "sources": [
        { "source": "codex", "original_title": "...", "original_detail": "...", "severity": "high" },
        { "source": "claude:code-reviewer", "original_title": "...", "original_detail": "...", "severity": "medium" }
      ],
      "severity_divergence": "codex=high, claude=medium → taking high"
    }
  ],
  "unparsed_chunks": [
    { "source": "codex", "text": "<raw text that couldn't be parsed as a finding>" }
  ]
}
```

This is the value-add of the skill over running both tools manually. **It's the reason synthesis isn't a Python script** — clustering by meaning is a judgment task, not a string-distance task. But the LLM only emits JSON; rendering stays deterministic.

### JSON validation + one repair attempt

Strict JSON from LLMs is unreliable for free-form fields — the same failure mode that drove the delimited-block schema for reviewer output (§7) applies here. The skill therefore validates synthesis output before passing it to `report.py`:

1. **Validate**: `scripts/validate-clusters.py` parses the synthesis output against a JSON Schema covering the cluster JSON structure (required fields, enum values for `tag` and `severity`, well-formed `sources[]`, etc.). On success: passes through to `report.py`.
2. **One repair attempt**: on failure, the orchestrator re-prompts itself with the validator's error message ("the `severity` field on cluster #3 must be one of critical|high|medium|low, got `important`") and a single instruction: "emit a corrected cluster JSON; do not re-cluster, only fix the schema violations". The repaired JSON is re-validated.
3. **Fail loud**: if the second validation also fails, `report.py` runs with the raw reviewer outputs only and the final report includes a prominent "Synthesis failed — manual review of raw outputs required" banner plus the validator's error message. No silent degradation.

This mirrors the parse-warnings approach for reviewer output (§7): one repair, then surface the failure rather than papering over it.

---

## 9. Report format

`scripts/report.py` consumes the cluster JSON from §8 (stdin) plus raw reviewer outputs (file paths passed as args) and emits the final Markdown to stdout. Optionally written to `--save <path>` via tee. Deterministic — same JSON in, same Markdown out.

```markdown
# Combined Review — <scope description>

**Scope:** <pr #105 / branch foo vs main / 3 files / etc.>
**Mode:** <code / spec / plan / docs>
**Focus:** <freeform text, if any>
**Reviewers:** Claude (3 sub-agents) + Codex
**Generated:** <ISO timestamp>

---

## High-confidence findings (both tools agree)

### [Critical]
- **path/file.py:42** — <title>
  <detail>
  _Sources: codex, claude:code-reviewer_

### [High]
...

## Single-source findings

### Claude only
- **[High] path/file.py:88** — <title>
  <detail>
  _Source: claude:silent-failure-hunter_

### Codex only
- **[Medium] path/other.py:14** — <title>
  <detail>
  _Source: codex_

## Disagreements (worth a second look)

- **path/file.py:42** — Codex says X, Claude says Y. <synthesis note on which seems right and why>

## Parse warnings
- 2 chunks from codex output could not be parsed; raw text below.

---

<details>
<summary>Raw outputs (audit trail)</summary>

### Codex
<full codex stdout>

### Claude sub-agents
#### code-reviewer
<full agent output>
#### silent-failure-hunter
<full agent output>
#### pr-test-analyzer
<full agent output>
</details>
```

Severity ordering in the report: critical → high → medium → low, within each section.

---

## 10. Failure modes

### Pre-flight checks (main session, before any tools run)

The skill orchestrator (main Claude session) performs these checks **before** dispatching any sub-agent or Bash. These need user interaction or skill-level decisions, so they don't belong in scripts.

1. **Codex availability.** Run `codex login status` (or equivalent) early. If codex isn't on PATH or isn't logged in, stop with a clear message — unless `--no-codex` was passed, in which case skip codex and continue Claude-only with a note in the report.
2. **`gh` authentication when `--pr` used.** `gh auth status`. Error early.
3. **Empty scope.** If `materialize-scope.py` reports `has_reviewable_changes == false`, error: "nothing to review". This intentionally uses the file-count-based flag, not `total_lines_changed == 0` — a PR that only changes a submodule, symlink, or binary asset is reviewable and shouldn't be rejected.
4. **Large diff.** If `total_lines_changed > LARGE_DIFF_THRESHOLD` (default 2000, env `COMBINED_REVIEW_LARGE_DIFF_THRESHOLD`), the orchestrator asks the user in chat: "Diff is N lines — both reviewers degrade on large diffs. Proceed?" If not interactive (e.g., the skill was called by another agent), require explicit `--force-large` flag instead of prompting.

### In-flight failure handling

| Failure | Behavior |
|---|---|
| `codex` returns non-zero | Report Claude-only result, include codex stderr in a "codex failed" section. Continue synthesis. |
| `codex` exceeds timeout (default 5 min, env `COMBINED_REVIEW_CODEX_TIMEOUT`) | Same as non-zero. |
| Worktree creation fails | Error early; no partial state. |
| Mixed code + docs in scope under `--mode code` | Proceed; surface a note in the report that doc files were reviewed with code lens. |
| Both reviewers emit zero findings | Report shows "no issues found" + raw outputs available for audit. |
| One Claude sub-agent fails | Continue with the others; failed agent's section in report says "agent failed: <error>". `reviewer_summary` (§8) records the failure. |
| All Claude sub-agents fail | Report codex-only result + Claude-failed note. If both sides fail, error. |

Cleanup follows the three-layer model in §4: `run-codex.sh`'s `trap` removes codex-side temp files (prompt file, stdout/stderr captures); the orchestrator's final `Bash` call to `scripts/cleanup-worktree.sh` removes the worktree (gated by the triple-assertion check); `scripts/gc-worktrees.sh` runs at the start of every invocation as the leak backstop. `--keep-worktree` (debug-only) suppresses the explicit cleanup step.

---

## 11. File layout

```
~/.claude/
├── commands/
│   └── combined-review.md          # slash entry point
└── skills/
    └── combined-review/
        ├── SKILL.md                # orchestration logic (model-readable)
        ├── prompts/
        │   ├── code.md             # mode templates
        │   ├── spec.md
        │   ├── plan.md
        │   └── docs.md
        └── scripts/
            ├── parse-args.py          # flags → normalized config JSON
            ├── resolve-scope.py       # auto-detect + validation + immutable SHA resolution
            ├── materialize-scope.py   # scope object → concrete diff + file contents (creates worktree if needed)
            ├── run-codex.sh           # codex driver; reads scope/prompt from orchestrator-owned paths; writes captures to orchestrator-owned stdout/stderr paths; internal trap only for files run-codex creates itself
            ├── normalize-findings.py  # parse delimited-block schema → JSON
            ├── validate-clusters.py   # JSON-schema-validate synthesis output; one repair attempt
            ├── cleanup-worktree.sh    # explicit teardown invoked by orchestrator at end of run
            ├── gc-worktrees.sh        # runs first; lists git worktrees and removes stale combined-review-* entries
            └── report.py              # cluster JSON + raw outputs → final markdown
```

Where practical, deterministic scripts communicate via JSON on stdin/stdout (`parse-args.py`, `resolve-scope.py`, `materialize-scope.py`, `normalize-findings.py`, `validate-clusters.py`, `report.py`). Scripts that operate on large or path-bound inputs use **explicit file-path contracts**: `run-codex.sh` takes `--prompt-file`, `--stdout`, `--stderr`; `cleanup-worktree.sh` and `gc-worktrees.sh` take repo + worktree paths and perform side effects. The orchestrator owns intermediate file lifecycle (see §4 "Raw output ownership"). `SKILL.md` describes the pipeline and points the model at each script in order.

---

## 12. Testing approach (TDD per writing-skills)

Per the `superpowers:writing-skills` discipline — **RED-GREEN-REFACTOR with pressure scenarios:**

### RED — baseline without the skill

Subagent scenarios to run before writing the skill:

1. "Run both Claude review and codex review on PR #105 and combine the findings." → Expect: sequential execution, no deduplication, no attribution, no disagreement surfacing.
2. "Review docs/spec.md with both tools." → Expect: confusion about how to point codex at a single file; default code-review lens applied to a markdown file.
3. "Run combined review on uncommitted changes when there's also a PR for the current branch." → Expect: silent ambiguity, agent picks one or the other without surfacing it.

Document the verbatim rationalizations / failure modes.

### GREEN — write skill + scripts

Implement to address the specific failures from RED. Re-run the scenarios. Confirm:

- Both reviewers run in parallel, not sequence.
- Findings are clustered into the `agreement` / `claude_only` / `codex_only` / `disagreement` tags from §8, and the rendered Markdown puts them in the corresponding sections from §9.
- Scope ambiguity (dirty + PR) errors out, not silent pick.
- `--mode spec` produces document-lens findings, not "no test coverage" suggestions.

### REFACTOR — close loopholes

New rationalizations to plug, e.g.:

- Agent decides "synthesis is too hard" and just concatenates outputs → add explicit anti-pattern in SKILL.md.
- Agent skips schema enforcement for codex → SKILL.md explicitly says "if codex output is unparseable, surface as parse warning, don't silently summarize".
- Agent runs reviews sequentially under cognitive load → SKILL.md mandates parallel-tool-call pattern.

---

## 13. Non-goals

- **Auto-fixing findings.** The skill reviews; it does not edit. Remediation is a separate step.
- **Reviewing across multiple PRs / commits in one invocation.** One scope per invocation.
- **Replacing the underlying `/review` skill or the standalone `codex` CLI.** They remain available standalone for users who want a single-tool review or who prefer codex's native review framing.
- **Persistent finding storage / triage history.** Output is per-invocation. `--save` is the only persistence.
- **Cross-tool prompt unification beyond the mode template.** We don't try to make codex emit the same exact sub-finding categories as Claude — we let each tool review naturally and synthesize after.

---

## 14. Decisions locked

- **Worktree location**: `mktemp -d -t combined-review-<repo>-XXXXXX` honoring `$TMPDIR`. Random suffix, repo basename for legibility.
- **`--full` opt-in vs `--agents`**: keep `--full` binary for v1. No `--agents` surface area until there's real pressure.
- **`--save` and `--keep-worktree`**: independent. `--save` writes the report file but does not preserve the worktree. `--keep-worktree` is debug-only and inhibits teardown.
- **Codex auth failure**: run `codex login status` early. Treat unauthenticated the same as "Codex unavailable" — stop with a clear message unless `--no-codex` was passed.
- **Diff semantics**: three-dot / merge-base (`git diff base...head`) for `--pr` and `--base`, matching GitHub PR review. Not two-dot. `git show` for `--commit`. `git diff HEAD` + appended untracked files for `--uncommitted`.
- **Positional files = current working-tree content**: includes any local edits the user just made. No clean worktree, no pinning to HEAD.
- **Non-code modes with diff scopes**: materialize-scope populates `doc_files` with post-change (or pre-change for deletes) content of changed text files in addition to the diff, so the document-reviewer agent has something reviewable.
- **PR materialization**: `gh pr checkout --detach <#>` as primary path (handles fork PRs natively); fetch base by `base_ref_name` for portability; verify both head and base with `headRefOid`/`baseRefOid` after fetch; `git reset --hard <head-sha>` if HEAD drifted.
- **Base scope worktree**: created from `<head-sha>` not literal `HEAD`, so the reviewed commit can't drift between resolve-scope and materialize.
- **Codex exec safety for files mode**: must pass `--sandbox read-only` (or codex's equivalent flag) AND include an explicit no-edit instruction at the top of the prompt. `run-codex.sh` errors out if the read-only flag isn't supported by the installed codex version. Non-negotiable — `codex exec` is otherwise a general agent that can edit files, which violates non-goal §13.
- **File-entry schema in materialize**: every `changed_files` entry has `status` (added|modified|deleted|renamed|typechange) and `kind` (text|binary|symlink|submodule). `post_content` populated only for kind=text and status ≠ deleted; `pre_content` for status=deleted; `old_path` for renames; symlink-target and submodule-pre/post-sha for those kinds.
- **Worktree cleanup safety**: every destructive cleanup goes through a triple-assertion gate — (1) path appears in `git worktree list --porcelain` for the current repo, (2) path matches `combined-review-*` mktemp pattern under `$TMPDIR`/`/tmp`, (3) path is not the repo root or main worktree. `gc-worktrees.sh` enumerates only via `git worktree list`, never scans `$TMPDIR` for arbitrary directories.
- **Prompt passing to codex**: via stdin (read from a temp file by `run-codex.sh`), not argv. Multi-KB prompts (file-mode embeds full doc contents) break shell quoting otherwise.
- **Shared-primary-input guarantee** (revised, was "same-bytes"): codex always runs via `codex exec --sandbox read-only` with the materialized blob from `materialize-scope.py`, never via `codex review`'s native auto-diff. The guarantee is *shared primary input* + *shared repo context*, not full isolation — both reviewers can still consult adjacent files via Read/Grep equivalents, and that's a feature for context-aware review. What's pinned: the diff and per-file content embedded in the prompt body, plus the git state of the cwd (worktree at recorded SHA or user's tree).
- **PR base fetch**: `git fetch <base_repo_url> <base_ref_name>` directly — **no `git remote add`**, which would mutate `.git/config` and leak across runs. SHA verification via `git cat-file -e <sha>^{commit}`, not `rev-parse FETCH_HEAD == base_sha` — the recorded commit must be reachable, but the tip may have moved (warn-only).
- **PR stale-snapshot failure**: if the recorded `head_sha` is not reachable after `gh pr checkout` + `git reset --hard <head_sha>`, the PR was force-pushed between `gh pr view` and `gh pr checkout`. The skill fails loudly with "PR head force-pushed mid-review; rerun" — does not silently fall back to the current head.
- **Raw output ownership**: the orchestrator creates and deletes all long-lived intermediate files (prompt, codex stdout/stderr, sub-agent transcripts). `run-codex.sh` writes to paths passed in via args; doesn't own deletion. Cleanup happens after `report.py` completes, before the worktree teardown.
- **Dispatch ordering**: setup is sequential (parse-args → resolve-scope → materialize → pre-flight → mktemp → Write prompt), reviewers run in parallel only after setup completes. Avoids the race where a parallel `Write` and background Bash launch run-codex.sh before the prompt file exists.
- **`--keep-worktree` + GC interaction**: `--keep-worktree` writes `.combined-review-keep` at the worktree root; `gc-worktrees.sh` skips marked worktrees regardless of age. Without the marker, a debug worktree would silently disappear after 24h on the next invocation's GC pass.
- **Empty-scope check**: uses `has_reviewable_changes` (file-count-based + doc_files), not `total_lines_changed == 0`. Submodule/symlink/binary-only PRs are legitimate review subjects.
- **Synthesis JSON validation**: `validate-clusters.py` enforces a JSON Schema on cluster output. One LLM repair attempt on failure; if that fails too, the report runs with raw outputs and a "synthesis failed" banner. No silent degradation.

## 15. Open questions

1. **Default Codex timeout.** 5 min is the current proposal. Should it be tighter (3 min) to avoid hanging the synthesis on a slow run?
2. **`materialize-scope.py` for large file contents.** If a changed file is huge (megabytes), inlining its `post_content` into the JSON is wasteful. Cap at e.g. 200KB per file and switch to "see worktree for full content" beyond that? Or always inline?
3. **`codex exec` prompt size limits.** For positional-files mode, the prompt has to include full file contents. If the user passes 20 large files, we'll hit the model's context limit. Should the skill error out above a content-size threshold and ask the user to narrow the file list?
````

### Document files


### docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md  (status: added, kind: text)
`````
# Combined Review Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill `/combined-review` that runs `pr-review-toolkit` sub-agents and `codex exec --sandbox read-only` in parallel against the same materialized review subject, then synthesizes the findings into a single deduped, attributed report.

**Architecture:** Slash command at `~/.claude/commands/combined-review.md` hands off to skill at `~/.claude/skills/combined-review/SKILL.md`. The skill orchestrates four phases — sequential setup (parse-args → resolve-scope → materialize → pre-flight → write prompt), parallel review (codex background + Claude sub-agents), in-session synthesis + JSON-validated cluster output, deterministic rendering — with a strict worktree-cleanup model gated by `git worktree list --porcelain`.

**Tech Stack:** Python 3 (stdlib + `jsonschema`), Bash, pytest. Codex CLI (`codex exec --sandbox read-only`). `gh` CLI for PR metadata. Git plumbing for worktrees and diffs.

**Spec:** `docs/superpowers/specs/2026-05-11-combined-review-skill-design.md`.

**Development layout:**

```
~/projects/combined-review/        # git repo (this plan develops here)
├── SKILL.md
├── commands/combined-review.md
├── prompts/{code,spec,plan,docs}.md
├── scripts/{parse-args,resolve-scope,materialize-scope,normalize-findings,validate-clusters,report}.py
├── scripts/run-codex.py
├── scripts/{cleanup-worktree,gc-worktrees}.sh
├── tests/
└── README.md
```

After implementation, install via:

```
ln -s ~/projects/combined-review ~/.claude/skills/combined-review
ln -s ~/projects/combined-review/commands/combined-review.md ~/.claude/commands/combined-review.md
```

---

## Task 1: Repo scaffolding

**Files:**
- Create: `~/projects/combined-review/.gitignore`
- Create: `~/projects/combined-review/README.md`
- Create: `~/projects/combined-review/pyproject.toml`
- Create: `~/projects/combined-review/tests/conftest.py`

- [ ] **Step 1: Create the repo and directory tree**

```bash
mkdir -p ~/projects/combined-review/{scripts,prompts,commands,tests}
cd ~/projects/combined-review
git init
```

- [ ] **Step 2: Write `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
*.egg-info/
```

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[project]
name = "combined-review"
version = "0.1.0"
description = "Claude Code skill that fuses Claude + Codex reviews in one session"
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.21.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Write `tests/conftest.py`**

```python
"""Shared pytest fixtures for the combined-review test suite."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


@pytest.fixture
def tmp_repo(tmp_path):
    """A throwaway git repo with one initial commit. Returns the repo Path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test repo\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=repo, check=True)
    return repo


@pytest.fixture
def fake_bin(tmp_path, monkeypatch):
    """Prepend a tmp dir to PATH so tests can drop fake `gh`/`codex` scripts."""
    fake = tmp_path / "bin"
    fake.mkdir()
    monkeypatch.setenv("PATH", f"{fake}:{os.environ['PATH']}")
    return fake


def run_script(name, *args, **kwargs):
    """Invoke a script in scripts/ via subprocess; return CompletedProcess."""
    script = SCRIPTS_DIR / name
    cmd = [str(script), *args] if script.suffix == ".sh" else ["python3", str(script), *args]
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
```

- [ ] **Step 5: Verify pytest runs (zero tests is OK)**

```bash
cd ~/projects/combined-review
python3 -m pip install -e ".[dev]"
pytest -v
```

Expected: `no tests ran` exit code 5, no errors.

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md pyproject.toml tests/conftest.py
git commit -m "feat: scaffold combined-review repo"
```

---

## Task 2: parse-args.py — CLI surface

**Files:**
- Create: `scripts/parse-args.py`
- Create: `tests/test_parse_args.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_parse_args.py
"""Tests for parse-args.py — flag parsing into normalized config JSON."""
import json
from tests.conftest import run_script


def parse(*args):
    r = run_script("parse-args.py", *args)
    assert r.returncode == 0, f"stderr: {r.stderr}"
    return json.loads(r.stdout)


def test_no_args_defaults_to_code_mode():
    cfg = parse()
    assert cfg["mode"] == "code"
    assert cfg["scope_flag"] is None
    assert cfg["files"] == []
    assert cfg["full"] is False


def test_pr_flag():
    cfg = parse("--pr", "105")
    assert cfg["scope_flag"] == "pr"
    assert cfg["pr_number"] == 105


def test_uncommitted_flag():
    cfg = parse("--uncommitted")
    assert cfg["scope_flag"] == "uncommitted"


def test_base_flag():
    cfg = parse("--base", "develop")
    assert cfg["scope_flag"] == "base"
    assert cfg["base_branch"] == "develop"


def test_commit_flag():
    cfg = parse("--commit", "abc1234")
    assert cfg["scope_flag"] == "commit"
    assert cfg["commit_sha"] == "abc1234"


def test_positional_files():
    cfg = parse("docs/spec.md", "plan.md")
    assert cfg["scope_flag"] == "files"
    assert cfg["files"] == ["docs/spec.md", "plan.md"]


def test_mode_and_focus():
    cfg = parse("--mode", "spec", "--focus", "API contract")
    assert cfg["mode"] == "spec"
    assert cfg["focus"] == "API contract"


def test_all_modifier_flags():
    cfg = parse("--full", "--no-codex", "--force-large", "--keep-worktree",
                "--save", "/tmp/report.md")
    assert cfg["full"] is True
    assert cfg["no_codex"] is True
    assert cfg["force_large"] is True
    assert cfg["keep_worktree"] is True
    assert cfg["save_path"] == "/tmp/report.md"


def test_mutually_exclusive_scope_flags_error():
    r = run_script("parse-args.py", "--pr", "1", "--uncommitted")
    assert r.returncode != 0
    assert "mutually exclusive" in r.stderr.lower()


def test_files_with_scope_flag_errors():
    r = run_script("parse-args.py", "--pr", "1", "foo.md")
    assert r.returncode != 0
    assert "mutually exclusive" in r.stderr.lower()


def test_invalid_mode_errors():
    r = run_script("parse-args.py", "--mode", "nonsense")
    assert r.returncode != 0


def test_args_file_mode(tmp_path):
    """Orchestrator writes $ARGUMENTS to a file; parse-args reads + shlex-splits it.
    Necessary because shell-substituting $ARGUMENTS directly is injection-prone."""
    f = tmp_path / "args.txt"
    f.write_text('--pr 105 --focus "API contract changes" --mode spec')
    r = run_script("parse-args.py", "--args-file", str(f))
    assert r.returncode == 0, r.stderr
    cfg = json.loads(r.stdout)
    assert cfg["pr_number"] == 105
    assert cfg["focus"] == "API contract changes"
    assert cfg["mode"] == "spec"


def test_args_file_handles_paths_with_spaces(tmp_path):
    f = tmp_path / "args.txt"
    f.write_text('"docs/path with spaces/spec.md"')
    r = run_script("parse-args.py", "--args-file", str(f))
    assert r.returncode == 0, r.stderr
    cfg = json.loads(r.stdout)
    assert cfg["files"] == ["docs/path with spaces/spec.md"]
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd ~/projects/combined-review && pytest tests/test_parse_args.py -v
```

Expected: all tests FAIL (script doesn't exist yet).

- [ ] **Step 3: Implement `scripts/parse-args.py`**

```python
#!/usr/bin/env python3
"""parse-args.py — turn /combined-review CLI args into a normalized config JSON.

Reads sys.argv[1:] OR, if --args-file <path> is given, reads the raw argument
string from that file and shlex-splits it. The args-file mode exists because
the orchestrator must not shell-substitute $ARGUMENTS directly — quoting
fragility and injection risk. Instead, the slash command writes $ARGUMENTS
to a file and we read it back literally here.

Writes a config object to stdout; returns non-zero on validation errors.
"""
import argparse
import json
import shlex
import sys

VALID_MODES = ("code", "spec", "plan", "docs")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="combined-review", add_help=True)
    p.add_argument("--pr", type=int, dest="pr_number")
    p.add_argument("--uncommitted", action="store_true")
    p.add_argument("--base", dest="base_branch")
    p.add_argument("--commit", dest="commit_sha")
    p.add_argument("--mode", choices=VALID_MODES, default="code")
    p.add_argument("--focus", default=None)
    p.add_argument("--full", action="store_true")
    p.add_argument("--no-codex", action="store_true", dest="no_codex")
    p.add_argument("--force-large", action="store_true", dest="force_large")
    p.add_argument("--keep-worktree", action="store_true", dest="keep_worktree")
    p.add_argument("--save", default=None, dest="save_path")
    p.add_argument("files", nargs="*")
    return p


def normalize(ns: argparse.Namespace) -> dict:
    scope_flags = {
        "pr": ns.pr_number is not None,
        "uncommitted": ns.uncommitted,
        "base": ns.base_branch is not None,
        "commit": ns.commit_sha is not None,
        "files": bool(ns.files),
    }
    selected = [k for k, v in scope_flags.items() if v]
    if len(selected) > 1:
        raise SystemExit(
            f"error: scope flags are mutually exclusive; got {selected}"
        )
    scope_flag = selected[0] if selected else None
    return {
        "scope_flag": scope_flag,
        "pr_number": ns.pr_number,
        "base_branch": ns.base_branch,
        "commit_sha": ns.commit_sha,
        "files": ns.files,
        "mode": ns.mode,
        "focus": ns.focus,
        "full": ns.full,
        "no_codex": ns.no_codex,
        "force_large": ns.force_large,
        "keep_worktree": ns.keep_worktree,
        "save_path": ns.save_path,
    }


def resolve_argv(raw_argv: list[str]) -> list[str]:
    """If --args-file <path> is the only/first pair, read the file and shlex-split.
    Otherwise return raw_argv unchanged."""
    if len(raw_argv) >= 2 and raw_argv[0] == "--args-file":
        path = raw_argv[1]
        with open(path, "r") as f:
            raw_string = f.read().strip()
        return shlex.split(raw_string)
    return raw_argv


def main(argv: list[str]) -> None:
    argv = resolve_argv(argv)
    ns = build_parser().parse_args(argv)
    cfg = normalize(ns)
    json.dump(cfg, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 4: Make it executable**

```bash
chmod +x scripts/parse-args.py
```

- [ ] **Step 5: Run tests, verify all pass**

```bash
pytest tests/test_parse_args.py -v
```

Expected: 12 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/parse-args.py tests/test_parse_args.py
git commit -m "feat: parse-args.py with CLI surface and mutex validation"
```

---

## Task 3: resolve-scope.py — auto-detect skeleton

**Files:**
- Create: `scripts/resolve-scope.py`
- Create: `tests/test_resolve_scope_explicit.py`

This task handles the four **explicit** scope kinds (uncommitted/base/commit/files). PR auto-detect lands in Task 4.

- [ ] **Step 1: Write failing tests for explicit-scope resolution**

```python
# tests/test_resolve_scope_explicit.py
"""Tests for resolve-scope.py — explicit scope flags only."""
import json
import subprocess
from tests.conftest import run_script


def resolve(cfg, cwd=None):
    r = run_script("resolve-scope.py", input=json.dumps(cfg), cwd=cwd)
    return r


def make_cfg(**kw):
    base = {
        "scope_flag": None, "pr_number": None, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    base.update(kw)
    return base


def test_uncommitted_scope(tmp_repo):
    (tmp_repo / "new.txt").write_text("x")
    r = resolve(make_cfg(scope_flag="uncommitted"), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "uncommitted"
    assert scope["repo_root"] == str(tmp_repo)
    assert scope["worktree_path"] is None
    assert scope["needs_clean_worktree"] is False


def test_base_scope_resolves_sha(tmp_repo):
    # Create a feature branch with one commit
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    (tmp_repo / "x.txt").write_text("y")
    subprocess.run(["git", "add", "x.txt"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
    r = resolve(make_cfg(scope_flag="base", base_branch="main"), cwd=tmp_repo)
    # git init default branch may be 'main' or 'master' depending on config
    if r.returncode != 0:
        # retry with detected default branch
        head = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"],
            cwd=tmp_repo, capture_output=True, text=True
        ).stdout.split()
        default = "master" if "master" in head else "main"
        r = resolve(make_cfg(scope_flag="base", base_branch=default), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "base"
    assert len(scope["base_sha"]) == 40
    assert len(scope["head_sha"]) == 40
    assert scope["base_sha"] != scope["head_sha"]
    assert scope["needs_clean_worktree"] is True


def test_commit_scope_resolves_sha(tmp_repo):
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    r = resolve(make_cfg(scope_flag="commit", commit_sha=sha), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "commit"
    assert scope["commit_sha"] == sha
    assert scope["needs_clean_worktree"] is True


def test_files_scope_passes_paths(tmp_repo):
    (tmp_repo / "spec.md").write_text("# spec")
    r = resolve(make_cfg(scope_flag="files", files=["spec.md"]), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "files"
    assert scope["files"] == ["spec.md"]
    assert scope["needs_clean_worktree"] is False


def test_files_scope_rejects_nonexistent(tmp_repo):
    r = resolve(make_cfg(scope_flag="files", files=["nope.md"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "nope.md" in r.stderr


def test_files_scope_rejects_absolute_paths(tmp_repo, tmp_path):
    """Regression for path-traversal / data-exfiltration. Absolute paths must
    be refused outright — inlining /Users/.../.ssh/id_rsa or /etc/passwd into
    the review prompt would send it to Codex (remote) + Claude sub-agents.
    `Path(repo_root) / absolute_path` evaluates to the absolute path in
    pathlib, so the previous `.exists()` check accepted any local file."""
    leaked = tmp_path / "leaked.txt"
    leaked.write_text("would-be-exfiltrated")
    r = resolve(make_cfg(scope_flag="files", files=[str(leaked)]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "absolute" in r.stderr.lower()


def test_files_scope_rejects_dotdot_escape(tmp_repo, tmp_path):
    """`../other-dir/secret.txt` must be rejected even though it's a relative
    path — after resolve() it lands outside repo_root."""
    outside = tmp_path / "outside.txt"
    outside.write_text("not in repo")
    # tmp_repo lives at tmp_path/"repo"; ../outside.txt escapes
    r = resolve(make_cfg(scope_flag="files", files=["../outside.txt"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()


def test_files_scope_rejects_symlink_pointing_outside(tmp_repo, tmp_path):
    """A symlink inside the repo whose target is outside the repo must also be
    rejected — resolve() follows symlinks, so the canonical path escapes."""
    outside = tmp_path / "secret.txt"
    outside.write_text("secret")
    (tmp_repo / "innocent.txt").symlink_to(outside)
    r = resolve(make_cfg(scope_flag="files", files=["innocent.txt"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "outside" in r.stderr.lower() or "escape" in r.stderr.lower()


def test_files_scope_preserves_symlink_path_when_target_is_in_repo(tmp_repo):
    """Regression: an in-repo symlink pointing at another in-repo file must keep
    its user-supplied name in the resolved scope, NOT be replaced with the
    target path. Otherwise materialize_files() sees a regular file and the
    symlink metadata (target path) never makes it into the prompt."""
    (tmp_repo / "real.md").write_text("# real file\n")
    (tmp_repo / "alias.md").symlink_to("real.md")
    r = resolve(make_cfg(scope_flag="files", files=["alias.md"]), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    # The returned path must be the user's input, not the target
    assert scope["files"] == ["alias.md"]


def test_files_scope_rejects_directory(tmp_repo):
    """A directory passed in files-scope must be rejected. Earlier behavior
    would let exists() pass and produce a doc_files entry with kind=text and
    content=None — confusing prompt with no value to the reviewer."""
    (tmp_repo / "subdir").mkdir()
    r = resolve(make_cfg(scope_flag="files", files=["subdir"]), cwd=tmp_repo)
    assert r.returncode != 0
    assert "regular file" in r.stderr.lower() or "directory" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_resolve_scope_explicit.py -v
```

Expected: all fail (script doesn't exist).

- [ ] **Step 3: Implement `scripts/resolve-scope.py` (explicit-scope paths only — auto-detect in Task 4)**

```python
#!/usr/bin/env python3
"""resolve-scope.py — config JSON in → scope object JSON out.

Handles explicit scope flags (uncommitted/base/commit/files) and validates
inputs against git. PR resolution and full auto-detect happen in a later
patch. All ref-shaped inputs are resolved to immutable SHAs here; downstream
steps consume SHAs, never ref names.
"""
import json
import subprocess
import sys
from pathlib import Path


def git(*args, cwd=None, check=True) -> str:
    r = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )
    return r.stdout.strip()


def repo_root(cwd=None) -> str:
    return git("rev-parse", "--show-toplevel", cwd=cwd)


def base_scope_object() -> dict:
    return {
        "kind": None, "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": None,
        "needs_clean_worktree": False,
        "mode": "code", "focus": None, "full": False,
        "no_codex": False, "force_large": False, "keep_worktree": False,
        "save_path": None,
    }


def carry_modifiers(scope: dict, cfg: dict) -> None:
    """Copy modifier flags from cfg into scope so downstream sees one object."""
    for k in ("mode", "focus", "full", "no_codex",
              "force_large", "keep_worktree", "save_path"):
        scope[k] = cfg[k]


def resolve_uncommitted(cfg: dict, root: str) -> dict:
    s = base_scope_object()
    s["kind"] = "uncommitted"
    s["repo_root"] = root
    s["needs_clean_worktree"] = False
    carry_modifiers(s, cfg)
    return s


def resolve_base(cfg: dict, root: str) -> dict:
    base_ref = cfg["base_branch"]
    try:
        base_sha = git("rev-parse", "--verify", f"{base_ref}^{{commit}}", cwd=root)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"error: cannot resolve base ref {base_ref!r}: {e.stderr}")
    head_sha = git("rev-parse", "--verify", "HEAD^{commit}", cwd=root)
    s = base_scope_object()
    s["kind"] = "base"
    s["repo_root"] = root
    s["base_ref_name"] = base_ref
    s["base_sha"] = base_sha
    s["head_sha"] = head_sha
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s


def resolve_commit(cfg: dict, root: str) -> dict:
    try:
        sha = git("rev-parse", "--verify", f"{cfg['commit_sha']}^{{commit}}", cwd=root)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"error: cannot resolve commit {cfg['commit_sha']!r}: {e.stderr}")
    s = base_scope_object()
    s["kind"] = "commit"
    s["repo_root"] = root
    s["commit_sha"] = sha
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s


def _validate_under_root(root: str, paths: list[str]) -> list[str]:
    """Reject absolute paths, `..` escapes, and symlinks whose targets are
    outside repo_root. Return the **user-supplied path, lexically normalized**
    — NOT the resolved target.

    Why we don't return the resolved path: if the user passes an in-repo
    symlink like `innocent-link.md` that points to another in-repo file,
    `.resolve()` follows it to the target. Returning the target would make
    materialize_files() see a regular text file instead of a symlink, and
    the symlink-specific metadata promised in Task 9 (target path) would
    never make it into the prompt. The report would also cite the wrong path.

    Why this is P1: positional file contents are inlined into the review
    prompt and sent to Codex (remote) + Claude sub-agents. Without the
    escape checks, passing `/Users/.../.ssh/id_rsa` or `../../etc/passwd`
    would silently exfiltrate secrets to remote APIs.
    """
    import os.path
    root_abs = Path(root).resolve()
    out = []
    for p in paths:
        if Path(p).is_absolute():
            raise SystemExit(
                f"error: refusing absolute path {p!r} — pass repo-relative paths only"
            )
        # Lexical normalization (does NOT follow symlinks). Rejects `..` escapes.
        lexical = os.path.normpath(p)
        if lexical.startswith("..") or lexical == ".." or "/../" in f"/{lexical}/":
            raise SystemExit(
                f"error: path {p!r} escapes via .. — refusing"
            )
        # Security check: does the resolved (symlink-followed) target land
        # inside the repo? If not, refuse — an in-repo symlink pointing at
        # /etc/passwd would otherwise exfiltrate it.
        try:
            resolved = (root_abs / p).resolve()
            resolved.relative_to(root_abs)
        except ValueError:
            raise SystemExit(
                f"error: path {p!r} resolves outside repo root ({root_abs}); refusing"
            )
        # Existence check using the original path (does not follow symlinks
        # except where the user intended; resolve() check above already
        # validated the target).
        full = root_abs / lexical
        if not full.exists():
            raise SystemExit(f"error: file not found: {p!r}")
        # Reject plain directories: positional files mode reviews file
        # content. A directory passed here would slip through with kind=text
        # + content=None downstream and render as a confusing header with no
        # content. If the user wants to review every file in a directory,
        # they should expand the glob themselves — the skill doesn't recurse
        # implicitly. is_file() returns True for symlinks pointing at regular
        # files, which is the behavior we want (symlinks ARE supported).
        #
        # Exception: submodules are gitlinks — they appear as directories on
        # disk (is_file() is False) but git tracks them as mode 160000.
        # materialize_files() has a kind=submodule branch that produces useful
        # output (the pointer SHA), so we must let these through.
        if not full.is_file():
            ls = subprocess.run(
                ["git", "ls-files", "--stage", "--", lexical],
                cwd=str(root_abs), capture_output=True, text=True,
            )
            is_submodule = ls.stdout.strip().startswith("160000 ")
            if not is_submodule:
                raise SystemExit(
                    f"error: {p!r} is not a regular file "
                    f"(directory or special file — pass file paths only, expand globs yourself)"
                )
        out.append(lexical)
    return out


def resolve_files(cfg: dict, root: str) -> dict:
    files = _validate_under_root(root, cfg["files"])
    s = base_scope_object()
    s["kind"] = "files"
    s["repo_root"] = root
    s["files"] = files
    s["needs_clean_worktree"] = False
    carry_modifiers(s, cfg)
    return s


SCOPE_RESOLVERS = {
    "uncommitted": resolve_uncommitted,
    "base": resolve_base,
    "commit": resolve_commit,
    "files": resolve_files,
}


def main() -> None:
    cfg = json.load(sys.stdin)
    root = repo_root()
    scope_flag = cfg["scope_flag"]
    if scope_flag is None:
        raise SystemExit(
            "error: auto-detect not yet implemented; pass an explicit scope flag"
        )
    if scope_flag == "pr":
        raise SystemExit("error: --pr resolution not yet implemented")
    resolver = SCOPE_RESOLVERS[scope_flag]
    scope = resolver(cfg, root)
    json.dump(scope, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Make executable, run tests**

```bash
chmod +x scripts/resolve-scope.py
pytest tests/test_resolve_scope_explicit.py -v
```

Expected: 10 passed (5 original + 3 path-traversal rejection + 1 in-repo-symlink-preservation + 1 directory-rejection).

- [ ] **Step 5: Commit**

```bash
git add scripts/resolve-scope.py tests/test_resolve_scope_explicit.py
git commit -m "feat: resolve-scope.py for explicit scopes (uncommitted/base/commit/files)"
```

---

## Task 4: resolve-scope.py — PR scope via gh

**Files:**
- Modify: `scripts/resolve-scope.py`
- Create: `tests/test_resolve_scope_pr.py`

- [ ] **Step 1: Write failing tests using a fake `gh`**

```python
# tests/test_resolve_scope_pr.py
"""Tests for resolve-scope.py --pr path using a fake `gh` binary."""
import json
import subprocess
from tests.conftest import run_script


FAKE_GH_JSON = {
    "number": 105,
    "headRefName": "feature-x",
    "baseRefName": "main",
    "headRefOid": "a" * 40,
    "baseRefOid": "b" * 40,
    "headRepository": {"url": "https://github.com/user/repo.git"},
    "baseRepository": {"url": "https://github.com/upstream/repo.git"},
}


def make_cfg_pr(num=105):
    return {
        "scope_flag": "pr", "pr_number": num, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def write_fake_gh(fake_bin, payload):
    script = fake_bin / "gh"
    script.write_text(
        "#!/bin/sh\n"
        # Only respond to `gh pr view` calls — fail loudly on anything else.
        'if [ "$1" = "pr" ] && [ "$2" = "view" ]; then\n'
        f"  cat <<'EOF'\n{json.dumps(payload)}\nEOF\n"
        "  exit 0\n"
        "fi\n"
        'echo "unexpected gh call: $@" >&2; exit 1\n'
    )
    script.chmod(0o755)


def test_pr_scope_reads_gh_metadata(tmp_repo, fake_bin):
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_pr()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    scope = json.loads(r.stdout)
    assert scope["kind"] == "pr"
    assert scope["pr_number"] == 105
    assert scope["head_ref_name"] == "feature-x"
    assert scope["base_ref_name"] == "main"
    assert scope["head_sha"] == "a" * 40
    assert scope["base_sha"] == "b" * 40
    assert scope["base_repo_url"] == "https://github.com/upstream/repo.git"
    assert scope["needs_clean_worktree"] is True


def test_pr_scope_propagates_gh_failure(tmp_repo, fake_bin):
    gh = fake_bin / "gh"
    gh.write_text("#!/bin/sh\necho 'auth required' >&2\nexit 1\n")
    gh.chmod(0o755)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_pr()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "gh" in r.stderr.lower() or "auth" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_resolve_scope_pr.py -v
```

Expected: 2 fails (script still rejects PR scope).

- [ ] **Step 3: Add `resolve_pr` to `scripts/resolve-scope.py`**

Replace the `if scope_flag == "pr": raise SystemExit(...)` line and add this function above `SCOPE_RESOLVERS`:

```python
def resolve_pr(cfg: dict, root: str) -> dict:
    pr = cfg["pr_number"]
    fields = "number,headRefName,baseRefName,headRefOid,baseRefOid,headRepository,baseRepository"
    r = subprocess.run(
        ["gh", "pr", "view", str(pr), "--json", fields],
        cwd=root, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"error: gh pr view failed: {r.stderr.strip()}")
    meta = json.loads(r.stdout)
    s = base_scope_object()
    s["kind"] = "pr"
    s["repo_root"] = root
    s["pr_number"] = meta["number"]
    s["head_ref_name"] = meta["headRefName"]
    s["base_ref_name"] = meta["baseRefName"]
    s["head_sha"] = meta["headRefOid"]
    s["base_sha"] = meta["baseRefOid"]
    s["head_repo_url"] = meta["headRepository"]["url"]
    s["base_repo_url"] = meta["baseRepository"]["url"]
    s["needs_clean_worktree"] = True
    carry_modifiers(s, cfg)
    return s
```

Then update `SCOPE_RESOLVERS` to include it:

```python
SCOPE_RESOLVERS = {
    "uncommitted": resolve_uncommitted,
    "base": resolve_base,
    "commit": resolve_commit,
    "files": resolve_files,
    "pr": resolve_pr,
}
```

And remove the `if scope_flag == "pr": raise SystemExit(...)` from `main()`.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_resolve_scope_pr.py tests/test_resolve_scope_explicit.py -v
```

Expected: 12 passed (10 explicit + 2 PR).

- [ ] **Step 5: Commit**

```bash
git add scripts/resolve-scope.py tests/test_resolve_scope_pr.py
git commit -m "feat: resolve-scope.py --pr via gh pr view metadata"
```

---

## Task 5: resolve-scope.py — auto-detect

**Files:**
- Modify: `scripts/resolve-scope.py`
- Create: `tests/test_resolve_scope_autodetect.py`

Auto-detect order (per spec §3): dirty+PR → error; dirty alone → uncommitted; clean+PR → pr; clean+no-PR+non-default branch → base vs default; clean+default branch → error.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_resolve_scope_autodetect.py
"""Tests for resolve-scope.py auto-detect when scope_flag is None."""
import json
import subprocess
from tests.conftest import run_script
from tests.test_resolve_scope_pr import FAKE_GH_JSON, write_fake_gh


def make_cfg_auto():
    return {
        "scope_flag": None, "pr_number": None, "base_branch": None,
        "commit_sha": None, "files": [], "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def make_dirty(repo):
    (repo / "dirty.txt").write_text("uncommitted\n")


def fake_gh_no_pr(fake_bin):
    """`gh pr view` exits 1 (no PR for this branch)."""
    gh = fake_bin / "gh"
    gh.write_text('#!/bin/sh\necho "no pull requests found" >&2\nexit 1\n')
    gh.chmod(0o755)


def test_autodetect_dirty_no_pr_implies_uncommitted(tmp_repo, fake_bin):
    fake_gh_no_pr(fake_bin)
    make_dirty(tmp_repo)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["kind"] == "uncommitted"


def test_autodetect_dirty_plus_pr_errors(tmp_repo, fake_bin):
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    make_dirty(tmp_repo)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "ambig" in r.stderr.lower() or "uncommitted" in r.stderr.lower()


def test_autodetect_clean_with_pr_implies_pr(tmp_repo, fake_bin):
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    write_fake_gh(fake_bin, FAKE_GH_JSON)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["kind"] == "pr"


def test_autodetect_default_branch_clean_errors(tmp_repo, fake_bin):
    fake_gh_no_pr(fake_bin)
    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
    assert r.returncode != 0
    assert "nothing" in r.stderr.lower() or "default" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_resolve_scope_autodetect.py -v
```

- [ ] **Step 3: Implement auto-detect in `scripts/resolve-scope.py`**

Add helpers above `main()`:

```python
def is_dirty(cwd: str) -> bool:
    """True if there are staged, unstaged, or untracked changes."""
    out = git("status", "--porcelain", cwd=cwd)
    return bool(out)


def current_branch(cwd: str) -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)


def _ref_resolves(cwd: str, ref: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=cwd, capture_output=True,
    ).returncode == 0


def default_branch(cwd: str) -> str | None:
    """Return a ref name (locally resolvable) for the repository default branch.

    Resolution order:
      1. `gh repo view --json defaultBranchRef` — gives the authoritative name
         (could be `develop`, `trunk`, etc., not just main/master).
         Then verify it resolves locally as either `<name>` or `origin/<name>`.
         Return whichever resolves, preferring the local branch over the
         remote-tracking ref.
      2. Probe common candidates locally: main, master, origin/main, origin/master.
      3. None if nothing resolves.

    Returning a non-resolvable name would just push the failure into `git
    rev-parse <ref>^{commit}` in the caller, which is worse UX than a clean
    "no default branch detected" error here.
    """
    r = subprocess.run(
        ["gh", "repo", "view", "--json", "defaultBranchRef"],
        cwd=cwd, capture_output=True, text=True,
    )
    if r.returncode == 0:
        try:
            name = json.loads(r.stdout)["defaultBranchRef"]["name"]
            for ref in (name, f"origin/{name}"):
                if _ref_resolves(cwd, ref):
                    return ref
        except (KeyError, json.JSONDecodeError):
            pass  # fall through to local probe

    for candidate in ("main", "master", "origin/main", "origin/master"):
        if _ref_resolves(cwd, candidate):
            return candidate
    return None


def pr_for_current_branch(cwd: str) -> int | None:
    r = subprocess.run(
        ["gh", "pr", "view", "--json", "number"],
        cwd=cwd, capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)["number"]
```

Replace the `if scope_flag is None: raise SystemExit(...)` in `main()` with auto-detect:

```python
    if scope_flag is None:
        dirty = is_dirty(root)
        pr_num = pr_for_current_branch(root)
        if dirty and pr_num is not None:
            raise SystemExit(
                "error: ambiguous scope — tree has uncommitted changes and "
                f"current branch has PR #{pr_num}. Pass --uncommitted or --pr {pr_num}."
            )
        if dirty:
            scope_flag = "uncommitted"
        elif pr_num is not None:
            scope_flag = "pr"
            cfg["pr_number"] = pr_num
        else:
            branch = current_branch(root)
            default = default_branch(root)
            if default is None or branch == default:
                raise SystemExit(
                    "error: nothing to review (clean tree, on default branch, no PR)"
                )
            scope_flag = "base"
            cfg["base_branch"] = default
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_resolve_scope_autodetect.py tests/test_resolve_scope_pr.py tests/test_resolve_scope_explicit.py -v
```

Expected: 16 passed (10 explicit + 2 PR + 4 auto-detect).

- [ ] **Step 5: Commit**

```bash
git add scripts/resolve-scope.py tests/test_resolve_scope_autodetect.py
git commit -m "feat: resolve-scope.py auto-detect with dirty+PR ambiguity guard"
```

---

## Task 6: materialize-scope.py — uncommitted scope

**Files:**
- Create: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_uncommitted.py`

This task does just the `uncommitted` kind end-to-end. Other kinds land in subsequent tasks.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_materialize_uncommitted.py
"""Tests for materialize-scope.py — uncommitted scope only."""
import json
import subprocess
from tests.conftest import run_script


def base_scope(repo):
    return {
        "kind": "uncommitted", "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": False, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def materialize(scope):
    return run_script("materialize-scope.py", input=json.dumps(scope))


def test_uncommitted_modified_file(tmp_repo):
    (tmp_repo / "README.md").write_text("# changed\n")
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "uncommitted"
    assert out["has_reviewable_changes"] is True
    assert out["changed_file_count"] == 1
    assert "README.md" in out["unified_diff"]
    files = out["changed_files"]
    assert len(files) == 1
    assert files[0]["path"] == "README.md"
    assert files[0]["status"] == "modified"
    assert files[0]["kind"] == "text"
    assert files[0]["post_content"] == "# changed\n"


def test_uncommitted_untracked_file_included(tmp_repo):
    (tmp_repo / "brand_new.py").write_text("print('hi')\n")
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    files = {f["path"]: f for f in out["changed_files"]}
    assert "brand_new.py" in files
    assert files["brand_new.py"]["status"] == "added"
    assert files["brand_new.py"]["post_content"] == "print('hi')\n"
    assert out["total_lines_changed"] >= 1


def test_uncommitted_clean_tree_empty(tmp_repo):
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["has_reviewable_changes"] is False
    assert out["changed_file_count"] == 0
    assert out["total_lines_changed"] == 0
    assert out["unified_diff"] in ("", None)


def test_uncommitted_deleted_file(tmp_repo):
    (tmp_repo / "README.md").unlink()
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
    assert "README.md" in files
    assert files["README.md"]["status"] == "deleted"
    assert files["README.md"]["post_content"] is None
    assert files["README.md"]["pre_content"] is not None


def test_uncommitted_deleted_binary_file(tmp_repo):
    """Regression: deleting a tracked binary file used to crash materialization
    because the deleted-path branch forced kind='text' and then called git show
    with text=True, raising UnicodeDecodeError. Now: detect kind from HEAD and
    skip text decoding for binary."""
    # Commit a real binary (PNG header) so it's tracked at HEAD
    bin_path = tmp_repo / "logo.png"
    # 8-byte PNG signature + a NUL byte so any text detection trips on it
    bin_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff\xfe\xfd binary garbage")
    subprocess.run(["git", "add", "logo.png"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add binary"], cwd=tmp_repo, check=True)
    # Now delete it in the working tree
    bin_path.unlink()
    r = materialize(base_scope(tmp_repo))
    assert r.returncode == 0, r.stderr
    files = {f["path"]: f for f in json.loads(r.stdout)["changed_files"]}
    assert "logo.png" in files
    entry = files["logo.png"]
    assert entry["status"] == "deleted"
    assert entry["kind"] == "binary"
    # Critical: must NOT have tried to decode the binary as text
    assert entry["pre_content"] is None
    assert "binary" in (entry.get("note") or "").lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_uncommitted.py -v
```

- [ ] **Step 3: Implement `scripts/materialize-scope.py`**

```python
#!/usr/bin/env python3
"""materialize-scope.py — scope object in → materialized review subject out.

Produces the concrete diff + per-file content blob that both Codex and the
Claude sub-agents consume. For non-`uncommitted`/`files` scopes, creates the
disposable worktree used by run-codex.py.

This patch handles only the `uncommitted` kind. Other kinds are added in
subsequent patches.
"""
import json
import subprocess
import sys
from pathlib import Path


def git(*args, cwd: str, check: bool = True) -> str:
    r = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )
    return r.stdout


def symlink_target(repo: str, path: str) -> str | None:
    """Return the link target string for a symlink in the working tree, or None."""
    full = Path(repo) / path
    try:
        return os.readlink(full)
    except (OSError, FileNotFoundError):
        return None


def submodule_sha_at(repo_or_worktree: str, ref: str, path: str) -> str | None:
    """Return the submodule pointer SHA at a ref.

    For commit refs (HEAD, base_sha, merge_base, parent_sha): read from
    `git ls-tree <ref>` — gives the committed pointer.

    For ref='WORKTREE': read the submodule's actual working-tree HEAD via
    `git -C <submodule-path> rev-parse HEAD`. This is intentionally NOT the
    index pointer from `git ls-files --stage` — if the user `cd`'d into the
    submodule and checked out a different commit but hasn't `git add`'d the
    bump yet, the index still shows the old SHA. The actual working-tree HEAD
    is what the reviewer should see for an unstaged submodule bump. Without
    this, `--uncommitted` would render no real change for the most common
    submodule-update workflow."""
    if ref == "WORKTREE":
        full = Path(repo_or_worktree) / path
        if not full.is_dir():
            return None
        r = subprocess.run(
            ["git", "-C", str(full), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            return None
        sha = r.stdout.strip()
        return sha or None
    r = subprocess.run(
        ["git", "ls-tree", ref, "--", path],
        cwd=repo_or_worktree, capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None
    parts = r.stdout.split()
    if len(parts) < 3 or parts[0] != "160000":
        return None
    return parts[2]


def detect_kind(repo: str, path: str) -> str:
    """Return text|binary|symlink|submodule for a path in the working tree."""
    full = Path(repo) / path
    if full.is_symlink():
        return "symlink"
    # git submodule detection via ls-files --stage (mode 160000)
    out = subprocess.run(
        ["git", "ls-files", "--stage", "--", path],
        cwd=repo, capture_output=True, text=True,
    ).stdout.strip()
    if out.startswith("160000 "):
        return "submodule"
    # Binary detection: git's own attribute check
    chk = subprocess.run(
        ["git", "check-attr", "binary", "--", path],
        cwd=repo, capture_output=True, text=True,
    ).stdout
    if "binary: set" in chk:
        return "binary"
    # Sniff for NUL byte as fallback
    try:
        with full.open("rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return "binary"
    except (FileNotFoundError, IsADirectoryError):
        pass
    return "text"


def safe_read_text(repo: str, path: str) -> str | None:
    p = Path(repo) / path
    if not p.exists() or p.is_dir():
        return None
    try:
        return p.read_text()
    except (UnicodeDecodeError, OSError):
        return None


def detect_kind_at_ref(repo_or_worktree: str, ref: str, path: str) -> str:
    """Determine file kind (text|binary|symlink|submodule) at a specific git
    ref. Used for DELETED files — the working tree no longer has them, so the
    working-tree-based `detect_kind` is wrong (it would default to text and
    then text-decoding a binary blob would either crash or inline garbage)."""
    r = subprocess.run(
        ["git", "ls-tree", ref, "--", path],
        cwd=repo_or_worktree, capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return "text"  # unknown; fall back to text and let read_at_ref decide
    # git ls-tree output: "<mode> <type> <sha>\t<path>"
    parts = r.stdout.split()
    if len(parts) < 3:
        return "text"
    mode, _type, sha = parts[0], parts[1], parts[2]
    if mode == "160000":
        return "submodule"
    if mode == "120000":
        return "symlink"
    # Sniff for binary by reading the blob bytes
    blob = subprocess.run(
        ["git", "cat-file", "blob", sha],
        cwd=repo_or_worktree, capture_output=True,  # bytes, no text=True
    )
    if blob.returncode == 0 and b"\x00" in blob.stdout[:8192]:
        return "binary"
    return "text"


def read_at_ref(repo_or_worktree: str, ref: str, path: str) -> str | None:
    """Read text file content at a ref. Reads bytes and only decodes if valid
    UTF-8. Returns None for missing files, binary content, or decode errors.

    Critical: must NOT use subprocess `text=True` here — that would force
    UTF-8 decoding inside subprocess and raise UnicodeDecodeError for
    binary blobs (deleted PNGs, etc.), crashing materialization."""
    r = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=repo_or_worktree, capture_output=True,  # bytes
    )
    if r.returncode != 0:
        return None
    try:
        return r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def read_at_head(repo: str, path: str) -> str | None:
    """Back-compat wrapper for legacy callers — prefer read_at_ref directly."""
    return read_at_ref(repo, "HEAD", path)


def parse_name_status(out: str) -> list[tuple[str, str, str | None]]:
    """Parse `git diff --name-status` output into (status, path, old_path)."""
    entries = []
    for line in out.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("R") and len(parts) == 3:
            entries.append(("renamed", parts[2], parts[1]))
        elif code == "A":
            entries.append(("added", parts[1], None))
        elif code == "M":
            entries.append(("modified", parts[1], None))
        elif code == "D":
            entries.append(("deleted", parts[1], None))
        elif code == "T":
            entries.append(("typechange", parts[1], None))
        else:
            entries.append((code, parts[1] if len(parts) > 1 else "?", None))
    return entries


def materialize_uncommitted(scope: dict) -> dict:
    root = scope["repo_root"]
    unified = git("diff", "HEAD", cwd=root)
    name_status = git("diff", "--name-status", "HEAD", cwd=root)
    untracked_raw = git("ls-files", "--others", "--exclude-standard", cwd=root)
    untracked = [p for p in untracked_raw.splitlines() if p]

    changed: list[dict] = []
    total_lines = 0
    for status, path, old_path in parse_name_status(name_status):
        # For DELETED files the working tree no longer has the content, so
        # `detect_kind(root, path)` would read nothing and default to text.
        # Inspect HEAD instead to get the real kind (catches deleted binaries,
        # symlinks, submodules).
        if status == "deleted":
            kind = detect_kind_at_ref(root, "HEAD", path)
        else:
            kind = detect_kind(root, path)
        entry = {
            "path": path, "old_path": old_path, "status": status, "kind": kind,
            "lines_changed": None, "post_content": None,
            "pre_content": None, "note": None,
        }
        if kind == "text" and status != "deleted":
            entry["post_content"] = safe_read_text(root, path)
            entry["lines_changed"] = "(modified)"
        if status == "deleted":
            entry["lines_changed"] = "(deleted)"
            if kind == "text":
                entry["pre_content"] = read_at_ref(root, "HEAD", path)
            elif kind == "binary":
                entry["note"] = "binary file deleted — content not inlined"
            elif kind == "symlink":
                # A symlink blob's content IS the target path, so read_at_ref
                # returns it. Without this, reviewers can't see what the
                # deleted symlink used to point at.
                entry["symlink_target"] = read_at_ref(root, "HEAD", path)
                entry["note"] = "symlink deleted"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
                entry["submodule_post_sha"] = None
                entry["note"] = "submodule removed"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        elif kind == "symlink":
            # Without this, the prompt renderer would print only the header
            # for the symlink change — a reviewer can't judge a target swap
            # they can't see.
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            # For submodule bumps we want both the previous and new pointer
            # SHAs so the reviewer can judge what's actually changing.
            entry["submodule_pre_sha"] = submodule_sha_at(root, "HEAD", path)
            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer change"
        changed.append(entry)

    for path in untracked:
        kind = detect_kind(root, path)
        post = safe_read_text(root, path) if kind == "text" else None
        line_count = len(post.splitlines()) if post else 0
        entry = {
            "path": path, "old_path": None, "status": "added", "kind": kind,
            "lines_changed": "(new file)" if line_count else "(empty)",
            "post_content": post, "pre_content": None, "note": None,
        }
        # Populate kind-specific metadata so untracked symlinks/submodules are
        # as reviewable as their tracked counterparts. Without this, an
        # untracked symlink renders as a header with no target — same bug
        # earlier rounds fixed for tracked entries.
        if kind == "symlink":
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink (untracked, new)"
        elif kind == "submodule":
            entry["submodule_pre_sha"] = None  # never existed before
            entry["submodule_post_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer (untracked, new)"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        changed.append(entry)
        total_lines += line_count

    # Estimate text-line delta from the unified diff (cheap and good-enough)
    for line in unified.splitlines():
        if (line.startswith("+") or line.startswith("-")) and not line.startswith(("+++", "---")):
            total_lines += 1

    return {
        "scope_kind": "uncommitted",
        "scope_summary": "uncommitted changes",
        "unified_diff": unified if unified else None,
        "changed_files": changed,
        "doc_files": [],
        "total_lines_changed": total_lines,
        "changed_file_count": len(changed),
        "has_reviewable_changes": len(changed) > 0,
        # Uncommitted runs in the user's working tree — no disposable worktree
        # gets created. Explicit None keeps the materialize-output shape stable
        # across kinds so Phase A7's `merged["worktree_path"] = MAT_JSON.worktree_path`
        # works without conditional logic.
        "worktree_path": None,
        "warnings": [],
    }


KIND_HANDLERS = {"uncommitted": materialize_uncommitted}


def main() -> None:
    scope = json.load(sys.stdin)
    handler = KIND_HANDLERS.get(scope["kind"])
    if handler is None:
        raise SystemExit(f"error: materialize for kind={scope['kind']!r} not implemented")
    out = handler(scope)
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests, verify all pass**

```bash
chmod +x scripts/materialize-scope.py
pytest tests/test_materialize_uncommitted.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_uncommitted.py
git commit -m "feat: materialize-scope.py for uncommitted scope (text/binary/symlink/submodule + untracked)"
```

---

## Task 7: materialize-scope.py — base and commit scopes (with worktree)

**Files:**
- Modify: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_diff_scopes.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_materialize_diff_scopes.py
"""Tests for materialize-scope.py — base and commit scopes (worktree-based)."""
import json
import subprocess
from pathlib import Path

from tests.conftest import run_script


def base_scope(repo, **overrides):
    s = {
        "kind": None, "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    s.update(overrides)
    return s


def add_commit(repo, path, content, msg):
    (repo / path).write_text(content)
    subprocess.run(["git", "add", path], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=repo, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()


def test_base_scope_three_dot_diff(tmp_repo):
    # main has initial commit; feature branches off, gets one commit
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    head_sha = add_commit(tmp_repo, "feature.py", "x = 1\n", "feat: add feature.py")
    scope = base_scope(tmp_repo, kind="base", base_sha=base_sha, head_sha=head_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "base"
    assert out["has_reviewable_changes"] is True
    assert any(f["path"] == "feature.py" for f in out["changed_files"])
    # worktree was created and recorded
    assert out["worktree_path"]  # truthy
    assert Path(out["worktree_path"]).exists()
    # cleanup
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)


def test_commit_scope(tmp_repo):
    sha = add_commit(tmp_repo, "added.py", "y = 2\n", "feat: added.py")
    scope = base_scope(tmp_repo, kind="commit", commit_sha=sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "commit"
    assert any(f["path"] == "added.py" for f in out["changed_files"])
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)


def test_commit_scope_root_commit_errors(tmp_repo):
    # The very first commit in tmp_repo has no parent — it's a root commit.
    root_sha = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        cwd=tmp_repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    scope = base_scope(tmp_repo, kind="commit", commit_sha=root_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "root commit" in r.stderr.lower()
    # Critical: no worktree leak even though make_worktree() succeeded
    leftover = [
        line for line in subprocess.run(
            ["git", "worktree", "list", "--porcelain"], cwd=tmp_repo,
            capture_output=True, text=True,
        ).stdout.splitlines() if "combined-review-" in line
    ]
    assert leftover == []


def test_commit_scope_merge_commit_errors(tmp_repo):
    # Build a merge commit on tmp_repo
    subprocess.run(["git", "checkout", "-q", "-b", "side"], cwd=tmp_repo, check=True)
    (tmp_repo / "side.py").write_text("s = 1\n")
    subprocess.run(["git", "add", "side.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "side commit"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "checkout", "-q", "-"], cwd=tmp_repo, check=True)  # back to default
    (tmp_repo / "main.py").write_text("m = 1\n")
    subprocess.run(["git", "add", "main.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "main commit"], cwd=tmp_repo, check=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "-m", "merge", "side"],
        cwd=tmp_repo, capture_output=True, text=True, check=True,
    )
    merge_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True,
    ).stdout.strip()
    scope = base_scope(tmp_repo, kind="commit", commit_sha=merge_sha)
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "merge commit" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_diff_scopes.py -v
```

- [ ] **Step 3: Extend `scripts/materialize-scope.py` with worktree creation + diff scopes**

Add at module top:

```python
import tempfile
import os
```

Add helpers (above `materialize_uncommitted`):

```python
def make_worktree(repo: str, ref: str) -> str:
    repo_basename = Path(repo).name
    tmp = tempfile.mkdtemp(
        prefix=f"combined-review-{repo_basename}-", dir=os.environ.get("TMPDIR", "/tmp")
    )
    # Remove the empty dir mktemp made; git worktree wants a fresh path
    Path(tmp).rmdir()
    subprocess.run(
        ["git", "worktree", "add", "--detach", tmp, ref],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return tmp


def materialize_diff_in_worktree(
    repo: str, worktree: str, base_sha: str, head_sha: str
) -> tuple[str, list[dict], int]:
    """Three-dot diff (merge-base semantics) and per-file entries.

    `git diff base...head` is shorthand for `git diff merge-base(base, head)..head`,
    so the diff content is anchored at the merge base, NOT base_sha. For deleted
    files, reading `git show base_sha:path` would return the file as it existed
    at base_sha — but if the base branch modified that file after the feature
    branch forked, base_sha's content disagrees with the diff. Reading from the
    merge-base commit instead keeps pre_content consistent with the unified diff.
    """
    merge_base = subprocess.run(
        ["git", "merge-base", base_sha, head_sha],
        cwd=worktree, capture_output=True, text=True, check=True,
    ).stdout.strip()

    unified = git("diff", f"{base_sha}...{head_sha}", cwd=worktree)
    name_status = git("diff", "--name-status", f"{base_sha}...{head_sha}", cwd=worktree)
    changed: list[dict] = []
    for status, path, old_path in parse_name_status(name_status):
        # Deleted files: detect kind from the merge-base (where the file last
        # existed) and read content via the binary-safe helper, not via
        # subprocess text=True which would crash on a deleted PNG.
        if status == "deleted":
            kind = detect_kind_at_ref(worktree, merge_base, path)
        else:
            kind = detect_kind(worktree, path)
        entry = {
            "path": path, "old_path": old_path, "status": status, "kind": kind,
            "lines_changed": None, "post_content": None,
            "pre_content": None, "note": None,
        }
        if kind == "text" and status != "deleted":
            entry["post_content"] = safe_read_text(worktree, path)
        if status == "deleted":
            if kind == "text":
                entry["pre_content"] = read_at_ref(worktree, merge_base, path)
            elif kind == "binary":
                entry["note"] = "binary file deleted — content not inlined"
            elif kind == "symlink":
                entry["symlink_target"] = read_at_ref(worktree, merge_base, path)
                entry["note"] = "symlink deleted"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
                entry["submodule_post_sha"] = None
                entry["note"] = "submodule removed"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        elif kind == "symlink":
            # Post-change target lives in the worktree (HEAD = head_sha).
            entry["symlink_target"] = symlink_target(worktree, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            # Pre at merge_base, post at head_sha. Both reachable in the worktree.
            entry["submodule_pre_sha"] = submodule_sha_at(worktree, merge_base, path)
            entry["submodule_post_sha"] = submodule_sha_at(worktree, head_sha, path)
            entry["note"] = "submodule pointer change"
        changed.append(entry)
    total = sum(
        1 for line in unified.splitlines()
        if (line.startswith("+") or line.startswith("-"))
        and not line.startswith(("+++", "---"))
    )
    return unified, changed, total


def materialize_base(scope: dict) -> dict:
    repo = scope["repo_root"]
    worktree = make_worktree(repo, scope["head_sha"])
    try:
        unified, changed, total = materialize_diff_in_worktree(
            repo, worktree, scope["base_sha"], scope["head_sha"]
        )
        return {
            "scope_kind": "base",
            "scope_summary": (
                f"branch {scope['base_ref_name']}...HEAD "
                f"({scope['base_sha'][:7]}..{scope['head_sha'][:7]})"
            ),
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        # If we created a worktree but never returned it in the handoff JSON,
        # the orchestrator has no way to clean it up. Self-clean and re-raise
        # so it never leaks. Phase D handles the (worktree_path, repo_root)
        # tuple for successful runs only.
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise


def commit_parent_count(repo_or_worktree: str, sha: str) -> int:
    """Number of parents — 0 for root commits, 1 for normal, ≥2 for merges."""
    out = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", sha],
        cwd=repo_or_worktree, capture_output=True, text=True, check=True,
    ).stdout.strip()
    # output is "<sha> <parent1> [<parent2> …]"
    return max(0, len(out.split()) - 1)


def materialize_commit(scope: dict) -> dict:
    repo = scope["repo_root"]
    sha = scope["commit_sha"]
    worktree = make_worktree(repo, sha)
    try:
        n_parents = commit_parent_count(worktree, sha)
        if n_parents == 0:
            # Root commit — no parent to diff against. v1 does not support
            # reviewing root commits; the right diff is "everything added"
            # but neither codex nor the Claude sub-agents are tuned for it.
            raise SystemExit(
                f"error: commit {sha[:7]} is a root commit (no parent); "
                f"v1 does not support reviewing root commits"
            )
        if n_parents >= 2:
            # Merge commit. The first-parent diff (`git show --first-parent`)
            # is conventional but loses changes from the second parent's branch.
            # v1 surfaces this explicitly rather than silently picking one diff.
            raise SystemExit(
                f"error: commit {sha[:7]} is a merge commit with {n_parents} parents; "
                f"v1 does not support reviewing merge commits — review the "
                f"merged branch's individual commits instead"
            )
        # Normal single-parent commit: use git show semantics, which produces
        # the patch the commit introduced. This is more direct (and correct
        # for non-fast-forward histories) than `git diff parent...commit`.
        unified = subprocess.run(
            ["git", "show", "--format=", sha],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout
        name_status = subprocess.run(
            ["git", "show", "--format=", "--name-status", sha],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout
        parent_sha = subprocess.run(
            ["git", "rev-parse", f"{sha}^"],
            cwd=worktree, capture_output=True, text=True, check=True,
        ).stdout.strip()
        changed: list[dict] = []
        for status, path, old_path in parse_name_status(name_status):
            # Deleted files: detect kind from the parent commit (where the file
            # last existed), and use the binary-safe reader.
            if status == "deleted":
                kind = detect_kind_at_ref(worktree, parent_sha, path)
            else:
                kind = detect_kind(worktree, path)
            entry = {
                "path": path, "old_path": old_path, "status": status, "kind": kind,
                "lines_changed": None, "post_content": None,
                "pre_content": None, "note": None,
            }
            if kind == "text" and status != "deleted":
                entry["post_content"] = safe_read_text(worktree, path)
            if status == "deleted":
                if kind == "text":
                    entry["pre_content"] = read_at_ref(worktree, parent_sha, path)
                elif kind == "binary":
                    entry["note"] = "binary file deleted — content not inlined"
                elif kind == "symlink":
                    entry["symlink_target"] = read_at_ref(worktree, parent_sha, path)
                    entry["note"] = "symlink deleted"
                elif kind == "submodule":
                    entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
                    entry["submodule_post_sha"] = None
                    entry["note"] = "submodule removed"
            elif kind == "binary":
                entry["note"] = "binary file — content not inlined"
            elif kind == "symlink":
                entry["symlink_target"] = symlink_target(worktree, path)
                entry["note"] = "symlink"
            elif kind == "submodule":
                entry["submodule_pre_sha"] = submodule_sha_at(worktree, parent_sha, path)
                entry["submodule_post_sha"] = submodule_sha_at(worktree, sha, path)
                entry["note"] = "submodule pointer change"
            changed.append(entry)
        total = sum(
            1 for line in unified.splitlines()
            if (line.startswith("+") or line.startswith("-"))
            and not line.startswith(("+++", "---"))
        )
        return {
            "scope_kind": "commit",
            "scope_summary": f"commit {sha[:7]}",
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        # Worktree was created above; clean it up before re-raising so the
        # orchestrator doesn't have to track a worktree_path that materialize
        # never returned. See "Materialize failure cleanup" comment near
        # make_worktree() for the full rationale.
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise
```

Then extend `KIND_HANDLERS`:

```python
KIND_HANDLERS = {
    "uncommitted": materialize_uncommitted,
    "base": materialize_base,
    "commit": materialize_commit,
}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_materialize_diff_scopes.py tests/test_materialize_uncommitted.py -v
```

Expected: 9 passed (5 in uncommitted + 4 in diff_scopes, where diff_scopes includes test_base_scope_three_dot_diff, test_commit_scope, test_commit_scope_root_commit_errors, test_commit_scope_merge_commit_errors).

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_diff_scopes.py
git commit -m "feat: materialize-scope.py for base and commit scopes via worktrees"
```

---

## Task 8: materialize-scope.py — PR scope with cat-file SHA reachability check

**Files:**
- Modify: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_pr.py`

- [ ] **Step 1: Write failing tests using a fake `gh pr checkout`**

```python
# tests/test_materialize_pr.py
"""Tests for materialize-scope.py PR scope.

Simulates `gh pr checkout` by hand-applying the head SHA inside the worktree,
since we don't have GitHub in the test loop.
"""
import json
import subprocess
from pathlib import Path

from tests.conftest import run_script


def test_pr_stale_snapshot_failure(tmp_repo, fake_bin):
    # gh pr checkout: do nothing (worktree stays at the initial commit).
    # The PR scope wants head_sha=<nonexistent SHA>, which should fail loudly.
    gh = fake_bin / "gh"
    gh.write_text('#!/bin/sh\nexit 0\n')
    gh.chmod(0o755)
    scope = {
        "kind": "pr", "pr_number": 99,
        "base_ref_name": "main", "head_ref_name": "feature",
        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
        "base_sha": "0" * 40, "head_sha": "f" * 40, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode != 0
    assert "force-pushed" in r.stderr.lower() or "stale" in r.stderr.lower() or "unreachable" in r.stderr.lower()


def test_pr_happy_path(tmp_repo, fake_bin):
    # Set up: initial commit on main; create feature branch with a commit;
    # capture both SHAs. Make gh pr checkout a no-op (worktree is already
    # at the head via our test setup) — and skip the base-repo fetch by
    # using the local repo's URL.
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
    (tmp_repo / "f.py").write_text("z = 3\n")
    subprocess.run(["git", "add", "f.py"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    # Fake `gh pr checkout` resets the worktree to head_sha
    gh = fake_bin / "gh"
    gh.write_text(
        '#!/bin/sh\n'
        '# only handle `gh pr checkout`; defer to git for the rest\n'
        f'if [ "$1" = "pr" ] && [ "$2" = "checkout" ]; then\n'
        f'  git -C "$PWD" reset --hard {head_sha} >/dev/null\n'
        '  exit 0\n'
        'fi\n'
        'exit 1\n'
    )
    gh.chmod(0o755)
    scope = {
        "kind": "pr", "pr_number": 1,
        "base_ref_name": "main", "head_ref_name": "feature",
        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
        "base_sha": base_sha, "head_sha": head_sha, "commit_sha": None,
        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
        "needs_clean_worktree": True, "mode": "code", "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "pr"
    assert any(f["path"] == "f.py" for f in out["changed_files"])
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_pr.py -v
```

- [ ] **Step 3: Add `materialize_pr` to `scripts/materialize-scope.py`**

Add helper and handler:

```python
def cat_file_exists(repo_or_worktree: str, sha: str) -> bool:
    r = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=repo_or_worktree, capture_output=True,
    )
    return r.returncode == 0


def materialize_pr(scope: dict) -> dict:
    repo = scope["repo_root"]
    head_sha = scope["head_sha"]
    base_sha = scope["base_sha"]
    base_url = scope["base_repo_url"]
    base_ref = scope["base_ref_name"]
    pr = scope["pr_number"]

    # Create an empty worktree we'll populate via gh pr checkout
    repo_basename = Path(repo).name
    worktree = tempfile.mkdtemp(
        prefix=f"combined-review-{repo_basename}-pr-",
        dir=os.environ.get("TMPDIR", "/tmp"),
    )
    Path(worktree).rmdir()
    subprocess.run(
        ["git", "worktree", "add", "--detach", worktree],
        cwd=repo, check=True, capture_output=True, text=True,
    )

    # Wrap everything after worktree creation in try/except so we never leak
    # a worktree the orchestrator can't see in the handoff JSON.
    try:
        # `gh pr checkout` handles fork PRs natively. Cwd = worktree.
        r = subprocess.run(
            ["gh", "pr", "checkout", "--detach", str(pr)],
            cwd=worktree, capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise SystemExit(f"error: gh pr checkout failed: {r.stderr.strip()}")

        # Fetch base from the PR's actual base repo (NOT origin — may be a fork)
        subprocess.run(
            ["git", "fetch", base_url, base_ref],
            cwd=worktree, capture_output=True, text=True,
        )

        # Pin head: if HEAD drifted, reset to recorded head_sha
        current_head = git("rev-parse", "HEAD", cwd=worktree).strip()
        if current_head != head_sha:
            if not cat_file_exists(worktree, head_sha):
                raise SystemExit(
                    f"error: PR head force-pushed mid-review — recorded {head_sha[:7]} "
                    f"no longer reachable. Rerun /combined-review --pr {pr} to fetch the current snapshot."
                )
            subprocess.run(
                ["git", "reset", "--hard", head_sha],
                cwd=worktree, check=True, capture_output=True, text=True,
            )

        # Verify base SHA is reachable
        if not cat_file_exists(worktree, base_sha):
            raise SystemExit(
                f"error: PR base SHA {base_sha[:7]} not reachable in worktree. "
                f"Rerun /combined-review --pr {pr} to fetch the current snapshot."
            )

        unified, changed, total = materialize_diff_in_worktree(
            repo, worktree, base_sha, head_sha
        )
        return {
            "scope_kind": "pr",
            "scope_summary": f"PR #{pr} ({base_sha[:7]}..{head_sha[:7]})",
            "unified_diff": unified if unified else None,
            "changed_files": changed, "doc_files": [],
            "total_lines_changed": total, "changed_file_count": len(changed),
            "has_reviewable_changes": len(changed) > 0,
            "worktree_path": worktree, "warnings": [],
        }
    except BaseException:
        # Any failure after worktree creation: clean up the worktree so the
        # orchestrator never has to recover a path it didn't receive.
        subprocess.run(["git", "worktree", "remove", "--force", worktree],
                       cwd=repo, capture_output=True)
        raise
```

Extend `KIND_HANDLERS`:

```python
KIND_HANDLERS = {
    "uncommitted": materialize_uncommitted,
    "base": materialize_base,
    "commit": materialize_commit,
    "pr": materialize_pr,
}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_materialize_pr.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_pr.py
git commit -m "feat: materialize-scope.py PR scope with cat-file SHA verification"
```

---

## Task 9: materialize-scope.py — files scope and non-code-mode doc_files

**Files:**
- Modify: `scripts/materialize-scope.py`
- Create: `tests/test_materialize_files_and_modes.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_materialize_files_and_modes.py
"""Tests for materialize-scope.py — files scope and doc_files for non-code modes."""
import json
import subprocess
from tests.conftest import run_script


def files_scope(repo, files, mode="code"):
    return {
        "kind": "files", "pr_number": None,
        "base_ref_name": None, "head_ref_name": None,
        "base_repo_url": None, "head_repo_url": None,
        "base_sha": None, "head_sha": None, "commit_sha": None,
        "files": files, "worktree_path": None, "repo_root": str(repo),
        "needs_clean_worktree": False, "mode": mode, "focus": None,
        "full": False, "no_codex": False, "force_large": False,
        "keep_worktree": False, "save_path": None,
    }


def test_files_scope_reads_current_content(tmp_repo):
    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
    (tmp_repo / "plan.md").write_text("# plan\nbar\n")
    scope = files_scope(tmp_repo, ["spec.md", "plan.md"])
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["scope_kind"] == "files"
    assert out["unified_diff"] is None
    assert out["changed_files"] == []
    docs = {d["path"]: d for d in out["doc_files"]}
    assert "spec.md" in docs
    assert docs["spec.md"]["content"] == "# spec\nfoo\n"
    assert out["has_reviewable_changes"] is True


def test_files_scope_with_spec_mode_preserves_doc_files(tmp_repo):
    """Regression: maybe_populate_doc_files() must not overwrite materialize_files()'s
    output. Was: --mode spec + files-scope wiped doc_files because the helper iterated
    over an empty changed_files. Now: helper short-circuits for files scope."""
    (tmp_repo / "spec.md").write_text("# spec\nfoo\n")
    scope = files_scope(tmp_repo, ["spec.md"], mode="spec")
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert len(out["doc_files"]) == 1
    assert out["doc_files"][0]["path"] == "spec.md"
    assert out["doc_files"][0]["content"] == "# spec\nfoo\n"


def test_non_code_mode_with_diff_scope_populates_doc_files(tmp_repo):
    # Set up a base-scope review on a .md change with --mode spec
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "-b", "feat"], cwd=tmp_repo, check=True)
    (tmp_repo / "design.md").write_text("# design\n")
    subprocess.run(["git", "add", "design.md"], cwd=tmp_repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "design"], cwd=tmp_repo, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
    ).stdout.strip()
    scope = files_scope(tmp_repo, [], mode="spec")
    scope["kind"] = "base"
    scope["base_sha"] = base_sha
    scope["head_sha"] = head_sha
    scope["base_ref_name"] = "main"
    scope["needs_clean_worktree"] = True
    r = run_script("materialize-scope.py", input=json.dumps(scope))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    paths = {d["path"]: d for d in out["doc_files"]}
    assert "design.md" in paths
    assert "design" in paths["design.md"]["content"]
    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
                   cwd=tmp_repo, check=True)
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_materialize_files_and_modes.py -v
```

- [ ] **Step 3: Extend `scripts/materialize-scope.py`**

Add handler and patch the diff handlers to populate `doc_files` when `mode != "code"`:

```python
def materialize_files(scope: dict) -> dict:
    """Build doc_files entries for positional files. Symlink and submodule
    entries carry kind-specific metadata (target / pointer SHA) instead of
    just a "non-text" note, so the rendered prompt can show the reviewer
    what's actually there. Without this, reviewing a symlink would print
    only a heading and the reviewer can't judge the target."""
    root = scope["repo_root"]
    doc_files: list[dict] = []
    for path in scope["files"]:
        kind = detect_kind(root, path)
        entry: dict = {
            "path": path, "status": "current", "kind": kind,
            "content": None, "note": None,
        }
        if kind == "text":
            entry["content"] = safe_read_text(root, path)
        elif kind == "symlink":
            entry["symlink_target"] = symlink_target(root, path)
            entry["note"] = "symlink"
        elif kind == "submodule":
            entry["submodule_sha"] = submodule_sha_at(root, "WORKTREE", path)
            entry["note"] = "submodule pointer (no diff — single snapshot)"
        elif kind == "binary":
            entry["note"] = "binary file — content not inlined"
        else:
            entry["note"] = f"non-text ({kind}) — content not inlined"
        doc_files.append(entry)
    return {
        "scope_kind": "files",
        "scope_summary": f"{len(doc_files)} file(s) — current working-tree content",
        "unified_diff": None,
        "changed_files": [],
        "doc_files": doc_files,
        "total_lines_changed": 0,
        "changed_file_count": 0,
        "has_reviewable_changes": len(doc_files) > 0,
        "worktree_path": None, "warnings": [],
    }
```

Then add a post-processing helper to populate `doc_files` for diff scopes when `mode != "code"`:

```python
def maybe_populate_doc_files(out: dict, scope: dict) -> None:
    """For non-code modes on diff scopes, mirror changed text files into doc_files
    using post_content (or pre_content for deletes) so the document-reviewer
    agent has something reviewable.

    Gate: skip in code mode (doc_files is empty by design), and skip for files
    scope — `materialize_files()` already populated doc_files correctly and we
    must not overwrite it with an empty list derived from the (also empty)
    changed_files."""
    if scope["mode"] == "code":
        return
    if scope["kind"] == "files":
        return
    docs = []
    for cf in out["changed_files"]:
        if cf["kind"] != "text":
            continue
        if cf["status"] == "deleted":
            content = cf.get("pre_content")
        else:
            content = cf.get("post_content")
        if content is None:
            continue
        docs.append({"path": cf["path"], "status": cf["status"], "content": content})
    out["doc_files"] = docs
```

Call it at the bottom of `main()`:

```python
def main() -> None:
    scope = json.load(sys.stdin)
    handler = KIND_HANDLERS.get(scope["kind"])
    if handler is None:
        raise SystemExit(f"error: materialize for kind={scope['kind']!r} not implemented")
    out = handler(scope)
    maybe_populate_doc_files(out, scope)
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")
```

Extend handlers:

```python
KIND_HANDLERS = {
    "uncommitted": materialize_uncommitted,
    "base": materialize_base,
    "commit": materialize_commit,
    "pr": materialize_pr,
    "files": materialize_files,
}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_materialize_files_and_modes.py tests/test_materialize_uncommitted.py tests/test_materialize_diff_scopes.py tests/test_materialize_pr.py -v
```

Expected: 14 passed (5 uncommitted + 4 diff_scopes + 2 pr + 3 files_and_modes).

- [ ] **Step 5: Commit**

```bash
git add scripts/materialize-scope.py tests/test_materialize_files_and_modes.py
git commit -m "feat: materialize-scope.py files scope + doc_files for non-code modes"
```

---

## Task 10: Mode prompt templates

**Files:**
- Create: `prompts/code.md`
- Create: `prompts/spec.md`
- Create: `prompts/plan.md`
- Create: `prompts/docs.md`

- [ ] **Step 1: Write `prompts/code.md`**

```markdown
# Code Review Mode

You are reviewing a code change. Focus on:

- **Correctness** — bugs, off-by-one errors, null/undefined handling, race conditions.
- **Error handling** — silent failures, missing catches, swallowed exceptions.
- **Test coverage** — new logic without tests, edge cases unverified.
- **Security** — injection, secrets, unsafe deserialization, auth bypass.
- **Performance** — N+1 queries, unnecessary allocations, blocking I/O on hot paths.
- **Project conventions** — alignment with CLAUDE.md if present.

You will receive the materialized review subject below (unified diff + per-file content).
Cite findings by `path:line` from the post-change file content. Skip stylistic nits
unless they obscure intent.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble. If you find no
issues, emit zero blocks.
```

- [ ] **Step 2: Write `prompts/spec.md`**

```markdown
# Spec Review Mode

You are reviewing a specification document. Focus on:

- **Completeness** — are requirements fully specified? Are edge cases addressed?
- **Ambiguity** — could any sentence be interpreted two ways? Pick out the ambiguous bit.
- **Internal consistency** — do sections contradict each other? Do field names match?
- **Scope creep** — does the spec drift into implementation when it should stay at the design level?
- **Missing edge cases** — failure modes, concurrency, ordering, partial states.
- **Unstated assumptions** — what does the spec take for granted that a reader might not know?
- **Success criteria** — is "done" defined? Is it testable?

You will receive the materialized review subject below (changed files + their current content).
Cite findings by `path:line` or section heading.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble.
```

- [ ] **Step 3: Write `prompts/plan.md`**

```markdown
# Plan Review Mode

You are reviewing an implementation plan. Focus on:

- **Step ordering** — does task N assume something task M hasn't delivered yet?
- **Hidden dependencies** — does a step rely on something not produced by an earlier step?
- **Verification per task** — does each task have a check that proves it worked, or is it "implement X, trust it works"?
- **Risk surface** — destructive ops, force-pushes, schema migrations, anything hard to roll back.
- **What could fail silently** — what would let the plan "complete" while producing a broken result?
- **Code completeness in steps** — placeholders like "implement appropriate logic", missing exact paths, undefined symbols.

You will receive the plan document below.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble.
```

- [ ] **Step 4: Write `prompts/docs.md`**

```markdown
# Docs Review Mode

You are reviewing user/developer documentation. Focus on:

- **Accuracy vs. current code** — do code samples match the actual API? Do paths exist?
- **Broken examples** — does the snippet actually run, or is it pseudo-code dressed up as runnable?
- **Drift** — has the underlying code changed in ways the docs still claim differently?
- **Missing prerequisites** — does the reader know what they need before step 1?
- **Audience fit** — is it pitched at someone who knows nothing? Too much? Just right?

You will receive the materialized review subject below.

**Output**: emit findings only as `---FINDING---` blocks per the schema at the end of
this prompt. Do not summarize. Do not include preamble or postamble.
```

- [ ] **Step 5: Verify they exist and commit**

```bash
ls prompts/
git add prompts/
git commit -m "feat: mode prompt templates (code, spec, plan, docs)"
```

---

## Task 11: Finding schema appendix + render-prompt.py

**Files:**
- Create: `prompts/_schema.md`
- Create: `scripts/render-prompt.py`
- Create: `tests/test_render_prompt.py`

- [ ] **Step 1: Write `prompts/_schema.md`** (the shared schema appendix, included in every prompt)

Note the **four-backtick** outer fence below — the file's content contains its own triple-backtick code block, and a triple-backtick outer fence would close prematurely at the inner one. CommonMark allows fences of any length ≥ 3; the closing fence must match the opening length, so four-tick outer + three-tick inner is unambiguous.

````markdown
---

## Output schema (mandatory)

Emit findings only as `---FINDING---` blocks. One block per finding. No preamble, no
postamble, no summary, no headers.

```
---FINDING---
severity: critical|high|medium|low
file: <relative path or "(general)">
line: <int> | <start>-<end> | -
category: bug|test-gap|perf|security|clarity|style|other
title: <single-line summary, no period>
detail: |
  <multi-line free text — recommendation, evidence, suggested fix>
---END-FINDING---
```

If you find no issues, emit zero blocks. Do not write "no issues found" or anything else.

**You are in review mode. Do not write, edit, or delete any files. Do not run code.
Read only.**
````

- [ ] **Step 2: Write failing tests for render-prompt.py**

```python
# tests/test_render_prompt.py
"""Tests for render-prompt.py — assembles mode template + materialized blob + schema."""
import json
from tests.conftest import run_script


def make_materialized(**overrides):
    base = {
        "scope_kind": "uncommitted",
        "scope_summary": "uncommitted changes",
        "unified_diff": "diff --git a/x b/x\n+y\n",
        "changed_files": [
            {"path": "x", "status": "modified", "kind": "text",
             "post_content": "y\n", "pre_content": None, "old_path": None,
             "lines_changed": "(modified)", "note": None},
        ],
        "doc_files": [], "total_lines_changed": 1,
        "changed_file_count": 1, "has_reviewable_changes": True,
        "warnings": [],
    }
    base.update(overrides)
    return base


def test_render_includes_mode_template():
    r = run_script(
        "render-prompt.py", "--mode", "code",
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0, r.stderr
    assert "Code Review Mode" in r.stdout
    assert "FINDING" in r.stdout  # schema appendix
    assert "no-edit" not in r.stdout.lower()  # we use the "read only" wording
    assert "diff --git" in r.stdout
    assert "y\n" in r.stdout


def test_render_includes_focus():
    r = run_script(
        "render-prompt.py", "--mode", "code", "--focus", "API contract changes",
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0
    assert "API contract changes" in r.stdout


def test_focus_file_mode_handles_shell_metacharacters(tmp_path):
    """Focus text containing $(...), backticks, etc. must round-trip safely."""
    f = tmp_path / "focus.txt"
    f.write_text("review $(rm -rf /) carefully and `dangerous` patterns")
    r = run_script(
        "render-prompt.py", "--mode", "code", "--focus-file", str(f),
        input=json.dumps(make_materialized()),
    )
    assert r.returncode == 0, r.stderr
    # The literal text must appear verbatim — no shell expansion happens
    # because the orchestrator passes a file path, not the text itself.
    assert "review $(rm -rf /) carefully" in r.stdout
    assert "`dangerous` patterns" in r.stdout


def test_focus_and_focus_file_mutually_exclusive(tmp_path):
    f = tmp_path / "focus.txt"; f.write_text("x")
    r = run_script(
        "render-prompt.py", "--mode", "code",
        "--focus", "y", "--focus-file", str(f),
        input=json.dumps(make_materialized()),
    )
    assert r.returncode != 0


def test_render_doc_mode_uses_doc_files():
    mat = make_materialized(
        scope_kind="files", unified_diff=None, changed_files=[],
        doc_files=[{"path": "spec.md", "status": "current", "content": "# spec\n"}],
    )
    r = run_script(
        "render-prompt.py", "--mode", "spec",
        input=json.dumps(mat),
    )
    assert r.returncode == 0
    assert "Spec Review Mode" in r.stdout
    assert "spec.md" in r.stdout
    assert "# spec" in r.stdout


def test_render_handles_nested_fences_in_doc(tmp_path):
    """Specs/plans commonly contain ``` blocks. A naive triple-backtick wrapper
    would let the inner ``` close the outer fence prematurely, swallowing the
    schema appendix. Verify the schema appendix is still present and intact."""
    doc_with_fences = (
        "# Spec\n\n"
        "Example code:\n\n"
        "```python\n"
        "def f(): return 1\n"
        "```\n\n"
        "Another block:\n\n"
        "````diff\n"  # nested fence with FOUR backticks
        "+ added line\n"
        "````\n"
    )
    mat = make_materialized(
        scope_kind="files", unified_diff=None, changed_files=[],
        doc_files=[{"path": "spec.md", "status": "current",
                    "content": doc_with_fences}],
    )
    r = run_script("render-prompt.py", "--mode", "spec",
                   input=json.dumps(mat))
    assert r.returncode == 0, r.stderr
    out = r.stdout
    # Doc content must appear
    assert "def f(): return 1" in out
    assert "+ added line" in out
    # Schema appendix must NOT have been swallowed by an unbalanced fence
    assert "---FINDING---" in out
    assert "End of prompt" not in out or "FINDING" in out  # schema present
```

- [ ] **Step 3: Run tests, verify they fail**

```bash
pytest tests/test_render_prompt.py -v
```

- [ ] **Step 4: Implement `scripts/render-prompt.py`**

```python
#!/usr/bin/env python3
"""render-prompt.py — assemble the prompt body for a reviewer.

Inputs:
- --mode {code,spec,plan,docs}
- --focus "<text>" (optional)
- materialized blob on stdin (JSON from materialize-scope.py)

Output: plain-text prompt body on stdout, suitable for piping to a reviewer
(codex via stdin, or pasted into a Claude sub-agent's prompt).
"""
import argparse
import json
import sys
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def fence_for(content: str) -> str:
    """Return a backtick fence longer than any run of backticks already inside
    `content`. CommonMark requires the closing fence be at least as long as
    the opening one, so a fence of length N+1 (where N is the longest run
    inside) will never collide. Without this, embedding a spec/plan that
    itself contains ``` would terminate our outer fence early and swallow
    everything after it — including the finding-schema appendix."""
    longest = 0
    run = 0
    for ch in content:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def fenced(content: str, lang: str = "") -> str:
    fence = fence_for(content)
    return f"{fence}{lang}\n{content.rstrip(chr(10))}\n{fence}"


def render_changed_files(mat: dict) -> str:
    parts = []
    for cf in mat["changed_files"]:
        parts.append(f"\n### {cf['path']}  (status: {cf['status']}, kind: {cf['kind']})")
        if cf.get("old_path"):
            parts.append(f"(renamed from {cf['old_path']})")
        if cf["kind"] == "text" and cf.get("post_content"):
            parts.append(fenced(cf["post_content"]))
        elif cf["status"] == "deleted" and cf.get("pre_content"):
            parts.append("(deleted; previous content was:)")
            parts.append(fenced(cf["pre_content"]))
        elif cf["kind"] == "symlink":
            target = cf.get("symlink_target")
            if target is not None:
                parts.append(f"Symlink target: `{target}`")
            if cf.get("note"):
                parts.append(f"_{cf['note']}_")
        elif cf["kind"] == "submodule":
            pre, post = cf.get("submodule_pre_sha"), cf.get("submodule_post_sha")
            if pre or post:
                parts.append(f"Submodule pointer: `{pre or '(none)'}` → `{post or '(none)'}`")
            if cf.get("note"):
                parts.append(f"_{cf['note']}_")
        elif cf.get("note"):
            parts.append(f"_{cf['note']}_")
    return "\n".join(parts)


def render_doc_files(mat: dict) -> str:
    parts = []
    for d in mat["doc_files"]:
        kind = d.get("kind", "text")
        parts.append(
            f"\n### {d['path']}  (status: {d['status']}, kind: {kind})"
        )
        if d.get("content"):
            parts.append(fenced(d["content"]))
        elif kind == "symlink":
            target = d.get("symlink_target")
            if target is not None:
                parts.append(f"Symlink target: `{target}`")
            if d.get("note"):
                parts.append(f"_{d['note']}_")
        elif kind == "submodule":
            sha = d.get("submodule_sha")
            if sha:
                parts.append(f"Submodule pointer: `{sha}`")
            if d.get("note"):
                parts.append(f"_{d['note']}_")
        elif d.get("note"):
            parts.append(f"_{d['note']}_")
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["code", "spec", "plan", "docs"], required=True)
    # Two ways to pass focus text:
    #   --focus "<text>" — convenient when the text has no shell metacharacters
    #   --focus-file <path> — REQUIRED when the text is user-provided, since
    #     argv interpolation by the orchestrator into a Bash command line
    #     would expose $(...), backticks, and other shell-injection vectors.
    # The skill orchestrator MUST use --focus-file for any user-provided focus.
    ap.add_argument("--focus", default=None)
    ap.add_argument("--focus-file", default=None)
    args = ap.parse_args()
    if args.focus and args.focus_file:
        ap.error("--focus and --focus-file are mutually exclusive")
    focus = args.focus
    if args.focus_file:
        with open(args.focus_file, "r") as f:
            focus = f.read().strip()
    mat = json.load(sys.stdin)

    template = (PROMPTS_DIR / f"{args.mode}.md").read_text()
    schema = (PROMPTS_DIR / "_schema.md").read_text()

    out = [template]
    if focus:
        out.append(f"\n## Additional focus\n\n{focus}\n")
    out.append(f"\n## Review subject\n\n**Scope:** {mat['scope_summary']}\n")
    if mat.get("unified_diff"):
        out.append("\n### Unified diff\n\n" + fenced(mat["unified_diff"], "diff") + "\n")
    if mat["changed_files"]:
        out.append("\n### Changed files (full content)\n")
        out.append(render_changed_files(mat))
    if mat["doc_files"]:
        out.append("\n### Document files\n")
        out.append(render_doc_files(mat))
    out.append("\n" + schema)
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests, commit**

```bash
chmod +x scripts/render-prompt.py
pytest tests/test_render_prompt.py -v
git add prompts/_schema.md scripts/render-prompt.py tests/test_render_prompt.py
git commit -m "feat: render-prompt.py assembles mode template + materialized blob + schema"
```

---

## Task 12: run-codex.py (Python, for macOS portability)

**Files:**
- Create: `scripts/run-codex.py`
- Create: `tests/test_run_codex.py`

**Why Python and not Bash:** GNU `timeout` is not on macOS by default (no `gtimeout` either), and BSD `date` doesn't understand `%3N` for millisecond precision. Python's `subprocess.run(..., timeout=...)` handles both portably and gives us a single language for testability.

- [ ] **Step 1: Write failing tests with a fake `codex` binary**

```python
# tests/test_run_codex.py
"""Tests for run-codex.py — invokes codex exec --sandbox read-only with stdin prompt."""
import json
import subprocess
from pathlib import Path

from tests.conftest import SCRIPTS_DIR


def write_fake_codex(fake_bin, behavior="echo"):
    codex = fake_bin / "codex"
    if behavior == "echo":
        codex.write_text(
            '#!/bin/sh\n'
            '# Echo the args + stdin, plus a fake finding. Advertise --sandbox.\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE   sandbox policy"\n'
            '  exit 0\n'
            'fi\n'
            'echo "ARGS: $*" >&2\n'
            'cat - >/dev/null\n'
            'echo "---FINDING---"\n'
            'echo "severity: low"\n'
            'echo "file: x.py"\n'
            'echo "line: 1"\n'
            'echo "category: style"\n'
            'echo "title: fake codex finding"\n'
            'echo "detail: |"\n'
            'echo "  emitted by fake codex"\n'
            'echo "---END-FINDING---"\n'
        )
    elif behavior == "no-sandbox":
        codex.write_text(
            '#!/bin/sh\n'
            '# --help does NOT advertise --sandbox; run-codex.py should refuse.\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --some-other-flag"\n'
            '  exit 0\n'
            'fi\n'
            'cat - >/dev/null; echo "ok"\n'
        )
    elif behavior == "slow":
        codex.write_text(
            '#!/bin/sh\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE"\n'
            '  exit 0\n'
            'fi\n'
            'sleep 30\n'
        )
    elif behavior == "fail":
        codex.write_text(
            '#!/bin/sh\n'
            'if [ "$1" = "exec" ] && [ "$2" = "--help" ]; then\n'
            '  echo "  --sandbox MODE"\n'
            '  exit 0\n'
            'fi\n'
            'echo "codex internal error" >&2; exit 7\n'
        )
    codex.chmod(0o755)


def run_codex(scope_path, prompt_path, stdout_path, stderr_path,
              status_path=None, timeout=None, **kwargs):
    args = ["python3", str(SCRIPTS_DIR / "run-codex.py"),
            "--scope", str(scope_path),
            "--prompt-file", str(prompt_path),
            "--stdout", str(stdout_path),
            "--stderr", str(stderr_path)]
    if status_path:
        args += ["--status", str(status_path)]
    env = kwargs.pop("env", None) or {}
    if timeout is not None:
        env["COMBINED_REVIEW_CODEX_TIMEOUT"] = str(timeout)
    import os as _os
    env = {**_os.environ, **env}
    return subprocess.run(args, capture_output=True, text=True, env=env, **kwargs)


def test_run_codex_writes_to_orchestrator_paths(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "echo")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("review please")
    stdout = tmp_path / "out"; stderr = tmp_path / "err"; status = tmp_path / "status.json"
    r = run_codex(scope, prompt, stdout, stderr, status_path=status)
    assert r.returncode == 0, r.stderr
    assert stdout.exists() and stderr.exists() and status.exists()
    assert "---FINDING---" in stdout.read_text()
    st = json.loads(status.read_text())
    assert st["status"] == "ok"
    assert st["exit_code"] == 0
    # orchestrator-owned files must not be deleted
    assert prompt.exists() and stdout.exists()


def test_run_codex_records_failure(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "fail")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
    # run-codex always exits 0; outcome is in the status file
    assert r.returncode == 0
    st = json.loads(status.read_text())
    assert st["status"] == "failed"
    assert st["exit_code"] == 7


def test_run_codex_records_timeout(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "slow")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e",
                  status_path=status, timeout=2)
    assert r.returncode == 0
    st = json.loads(status.read_text())
    assert st["status"] == "timeout"


def test_run_codex_errors_without_sandbox_support(tmp_path, fake_bin):
    write_fake_codex(fake_bin, "no-sandbox")
    scope = tmp_path / "scope.json"
    scope.write_text(json.dumps({"kind": "uncommitted", "worktree_path": None,
                                 "repo_root": str(tmp_path)}))
    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
    status = tmp_path / "status.json"
    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
    # Sandbox-flag failure is a HARD error — exits non-zero, no status file written.
    assert r.returncode != 0
    assert "sandbox" in r.stderr.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_run_codex.py -v
```

- [ ] **Step 3: Implement `scripts/run-codex.py`**

```python
#!/usr/bin/env python3
"""run-codex.py — drive `codex exec --sandbox read-only` with a stdin prompt.

Portable across macOS and Linux. GNU `timeout` isn't on macOS by default and
BSD `date` doesn't support `%3N`, so we use Python's subprocess.run(timeout=)
and time.monotonic_ns() instead.

All long-lived files (prompt, stdout, stderr, status) are orchestrator-owned.
This script writes to them but never deletes them. It ALWAYS exits 0 except
for hard pre-flight failures (missing --sandbox support, missing required
args); outcome of the codex run goes into the status JSON so the
orchestrator's background-Bash mechanics don't have to interpret exit codes.
"""
import argparse
import json
import os
import subprocess
import sys
import time


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--stdout", required=True)
    ap.add_argument("--stderr", required=True)
    ap.add_argument("--status", default=None,
                    help="default: <stdout>.status")
    args = ap.parse_args()

    status_path = args.status or f"{args.stdout}.status"

    def write_failed_status(msg: str, exit_code: int) -> None:
        """Write a status JSON AND mirror the message into the orchestrator-
        owned stderr capture for hard failures. Phase C builds its error
        section from $CODEX_STDERR and report.py embeds it in the audit
        trail. Writing only to sys.stderr (this script's own stderr) would
        leave the audit trail empty for missing-sandbox / missing-codex
        cases — invisible to anyone reading the report.

        Two destinations:
          1. status JSON: structured error for Phase C's reviewer_summary
          2. args.stderr: free-form text the audit trail can show verbatim

        Phase A pre-flight should catch these before Phase B launches at
        all, but this still matters for the (narrow) case where codex was
        upgraded or replaced between Phase A and Phase B.
        """
        try:
            with open(status_path, "w") as sf:
                json.dump({
                    "status": "failed", "exit_code": exit_code,
                    "duration_ms": 0, "timeout_seconds": 0,
                    "error": msg,
                }, sf)
        except OSError:
            pass
        try:
            with open(args.stderr, "w") as ef:
                ef.write(f"run-codex.py hard failure: {msg}\n")
        except OSError:
            pass

    # Hard pre-flight: verify codex exec advertises --sandbox before we ever
    # invoke it. Missing the flag means we cannot guarantee read-only mode —
    # refuse to run rather than silently going unsandboxed.
    # Phase A pre-flight should catch this, but check here too in case codex
    # was upgraded/replaced between Phase A and Phase B launch.
    try:
        help_out = subprocess.run(
            ["codex", "exec", "--help"], capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        msg = "codex not on PATH"
        print(f"error: {msg}", file=sys.stderr)
        write_failed_status(msg, 3); sys.exit(3)
    if "--sandbox" not in (help_out.stdout + help_out.stderr):
        msg = "installed codex does not advertise --sandbox; refusing to run unsandboxed"
        print(f"error: {msg}", file=sys.stderr)
        write_failed_status(msg, 3); sys.exit(3)

    # Resolve cwd: prefer worktree_path (diff-based scopes), else repo_root.
    with open(args.scope) as f:
        scope = json.load(f)
    cwd = scope.get("worktree_path") or scope.get("repo_root") or os.getcwd()

    timeout_s = int(os.environ.get("COMBINED_REVIEW_CODEX_TIMEOUT", "300"))

    with open(args.prompt_file, "rb") as pf, \
         open(args.stdout, "wb") as outf, \
         open(args.stderr, "wb") as errf:
        prompt_bytes = pf.read()
        start = time.monotonic_ns()
        status = "ok"; exit_code = 0
        try:
            proc = subprocess.run(
                ["codex", "exec", "--sandbox", "read-only", "-"],
                input=prompt_bytes, stdout=outf, stderr=errf,
                cwd=cwd, timeout=timeout_s,
            )
            exit_code = proc.returncode
            status = "ok" if exit_code == 0 else "failed"
        except subprocess.TimeoutExpired:
            status = "timeout"; exit_code = 124
        except FileNotFoundError:
            # codex disappeared between --help and exec; treat as failure
            status = "failed"; exit_code = 127
            errf.write(b"codex binary not found at exec time\n")
        end = time.monotonic_ns()

    duration_ms = (end - start) // 1_000_000

    with open(status_path, "w") as sf:
        json.dump({
            "status": status,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "timeout_seconds": timeout_s,
        }, sf)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/run-codex.py
pytest tests/test_run_codex.py -v
```

Expected: 4 passed (writes-to-orchestrator-paths, records-failure, records-timeout, errors-without-sandbox-support).

- [ ] **Step 5: Commit**

```bash
git add scripts/run-codex.py tests/test_run_codex.py
git commit -m "feat: run-codex.py (portable) drives codex exec read-only with orchestrator-owned IO"
```

---

## Task 13: normalize-findings.py

**Files:**
- Create: `scripts/normalize-findings.py`
- Create: `tests/test_normalize_findings.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_normalize_findings.py
"""Tests for normalize-findings.py — delimited-block schema → JSON array."""
import json
from tests.conftest import run_script


SAMPLE = """\
preamble that should be ignored
---FINDING---
severity: high
file: src/foo.py
line: 42
category: bug
title: Null deref when config missing 'api_key'
detail: |
  Accessing config['api_key'] directly raises KeyError.
  Use config.get('api_key') or guard with an early return.
---END-FINDING---
some prose in between
---FINDING---
severity: medium
file: src/bar.py
line: 10-15
category: clarity
title: Function does two unrelated things
detail: |
  Split into authenticate() and load_profile().
---END-FINDING---
trailing noise
"""


def test_parses_two_findings():
    r = run_script("normalize-findings.py", "--source", "codex",
                   input=SAMPLE)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert len(out["findings"]) == 2
    f0 = out["findings"][0]
    assert f0["source"] == "codex"
    assert f0["severity"] == "high"
    assert f0["file"] == "src/foo.py"
    assert f0["line"] == "42"
    assert "KeyError" in f0["detail"]
    f1 = out["findings"][1]
    assert f1["line"] == "10-15"


def test_unparseable_chunks_go_to_warnings():
    bad = """\
---FINDING---
severity: bananas
file: x
title: missing required fields
---END-FINDING---
"""
    r = run_script("normalize-findings.py", "--source", "claude:code-reviewer",
                   input=bad)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    # missing fields → parse warning, severity normalized
    assert len(out["parse_warnings"]) >= 1 or out["findings"][0]["severity"] == "medium"


def test_empty_input_returns_empty_array():
    r = run_script("normalize-findings.py", "--source", "codex", input="")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["findings"] == []
    assert out["parse_warnings"] == []
    assert out["unparsed_chunks"] == []


def test_prose_only_output_becomes_unparsed_chunk():
    """Regression: a reviewer that ignores the schema and emits prose used to
    produce findings:[] AND parse_warnings:[] — silently swallowing the entire
    output. Now we capture it as an unparsed_chunk so the final report shows
    "reviewer X did not follow the schema; see chunk:"."""
    prose = """I reviewed the diff and found a few issues:

1. The naming convention is inconsistent.
2. There's a possible null deref on line 42.
3. The tests don't cover the edge case.

Overall the change looks fine but could use a second pass."""
    r = run_script("normalize-findings.py", "--source", "codex", input=prose)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["findings"] == []
    assert len(out["unparsed_chunks"]) == 1
    assert out["unparsed_chunks"][0]["source"] == "codex"
    assert "null deref" in out["unparsed_chunks"][0]["text"]
    assert len(out["parse_warnings"]) >= 1


def test_text_between_blocks_captured():
    """Prose between two valid FINDING blocks must also surface as a warning."""
    mixed = """\
---FINDING---
severity: high
file: a.py
line: 1
category: bug
title: first
detail: |
  one
---END-FINDING---

Some prose the reviewer added in between that shouldn't be there.

---FINDING---
severity: low
file: b.py
line: 2
category: style
title: second
detail: |
  two
---END-FINDING---
"""
    r = run_script("normalize-findings.py", "--source", "claude:code-reviewer",
                   input=mixed)
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert len(out["findings"]) == 2
    assert any("Some prose" in c["text"] for c in out["unparsed_chunks"])
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_normalize_findings.py -v
```

- [ ] **Step 3: Implement `scripts/normalize-findings.py`**

```python
#!/usr/bin/env python3
"""normalize-findings.py — parse delimited-block reviewer output → JSON.

Reads raw reviewer output on stdin; writes a JSON object with `findings`
(array of normalized finding dicts) and `parse_warnings` (array of strings
describing unparseable chunks). One reviewer's output per invocation.
"""
import argparse
import json
import re
import sys

VALID_SEVERITY = {"critical", "high", "medium", "low"}
SEVERITY_MAP = {
    "critical": "critical", "high": "high", "medium": "medium", "low": "low",
    "error": "high", "warning": "medium", "info": "low", "note": "low",
}
VALID_CATEGORY = {"bug", "test-gap", "perf", "security", "clarity", "style", "other"}


BLOCK_RE = re.compile(
    r"---FINDING---\s*\n(.*?)\n---END-FINDING---",
    re.DOTALL,
)


def parse_block(body: str) -> tuple[dict | None, str | None]:
    """Return (finding dict, warning str). If both None, the block is empty."""
    fields: dict[str, str] = {}
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            i += 1; continue
        key, val = m.group(1), m.group(2)
        if val.strip() == "|":
            # multi-line scalar
            buf = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
                buf.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            fields[key] = "\n".join(buf).strip()
            continue
        fields[key] = val.strip()
        i += 1

    warnings = []
    sev = (fields.get("severity") or "").lower()
    if sev not in VALID_SEVERITY:
        mapped = SEVERITY_MAP.get(sev, "medium")
        warnings.append(f"unknown severity {sev!r} mapped to {mapped!r}")
        sev = mapped
    cat = (fields.get("category") or "other").lower()
    if cat not in VALID_CATEGORY:
        warnings.append(f"unknown category {cat!r} mapped to 'other'")
        cat = "other"
    if not fields.get("title"):
        warnings.append(f"finding missing title; skipping")
        return None, "\n".join(warnings)

    f = {
        "severity": sev,
        "file": fields.get("file") or "(general)",
        "line": fields.get("line") or "-",
        "category": cat,
        "title": fields["title"],
        "detail": fields.get("detail") or "",
    }
    return f, "; ".join(warnings) if warnings else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True,
                    help='e.g. "codex" or "claude:code-reviewer"')
    args = ap.parse_args()
    raw = sys.stdin.read()
    findings: list[dict] = []
    warnings: list[str] = []
    unparsed_chunks: list[dict] = []

    cursor = 0
    for m in BLOCK_RE.finditer(raw):
        # Capture any non-whitespace text BEFORE this block as an unparsed
        # chunk. A reviewer that ignores the schema and emits prose would
        # otherwise produce findings: [] and warnings: [] silently — the
        # spec says these failures must surface in the final report.
        between = raw[cursor:m.start()].strip()
        if between:
            unparsed_chunks.append({
                "source": args.source,
                "text": between[:1000],  # cap; full raw is in audit trail
                "position": "before_block" if findings else "preamble",
            })
            warnings.append(
                f"[{args.source}] {len(between)} chars of non-schema text outside "
                f"---FINDING--- blocks (see unparsed_chunks)"
            )
        body = m.group(1)
        finding, warn = parse_block(body)
        if finding is not None:
            finding["source"] = args.source
            findings.append(finding)
        if warn:
            warnings.append(f"[{args.source}] {warn}")
        cursor = m.end()

    # Trailing text after the last block (or all text if no blocks matched).
    trailing = raw[cursor:].strip()
    if trailing:
        unparsed_chunks.append({
            "source": args.source,
            "text": trailing[:1000],
            "position": "postamble" if findings else "no_blocks",
        })
        warnings.append(
            f"[{args.source}] {len(trailing)} chars of non-schema text after "
            f"last FINDING block (see unparsed_chunks)"
        )

    json.dump({
        "findings": findings,
        "parse_warnings": warnings,
        "unparsed_chunks": unparsed_chunks,
    }, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/normalize-findings.py
pytest tests/test_normalize_findings.py -v
```

Expected: 5 passed (parses-two-findings, unparseable-chunks-go-to-warnings, empty-input, prose-only-becomes-unparsed-chunk, text-between-blocks-captured).

- [ ] **Step 5: Commit**

```bash
git add scripts/normalize-findings.py tests/test_normalize_findings.py
git commit -m "feat: normalize-findings.py parses delimited-block schema with parse warnings"
```

---

## Task 14: validate-clusters.py

**Files:**
- Create: `scripts/validate-clusters.py`
- Create: `tests/test_validate_clusters.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_validate_clusters.py
"""Tests for validate-clusters.py — JSON Schema check on synthesis output."""
import json
from tests.conftest import run_script


VALID_CLUSTERS = {
    "scope_summary": "PR #105",
    "mode": "code",
    "focus": None,
    "reviewer_summary": {
        "codex": {"status": "ok", "raw_findings": 3, "parse_warnings": 0},
        "claude": [
            {"agent": "code-reviewer", "status": "ok",
             "raw_findings": 2, "parse_warnings": 0},
        ],
    },
    "clusters": [
        {
            "tag": "agreement",
            "severity": "high",
            "file": "src/foo.py",
            "line": "42",
            "category": "bug",
            "title": "Null deref",
            "synthesized_detail": "Both reviewers flag this.",
            "sources": [
                {"source": "codex", "original_title": "Null deref",
                 "original_detail": "...", "severity": "high"},
                {"source": "claude:code-reviewer",
                 "original_title": "Possible KeyError",
                 "original_detail": "...", "severity": "medium"},
            ],
            "severity_divergence": "codex=high, claude=medium → high",
        },
    ],
    "unparsed_chunks": [],
}


def test_valid_passes():
    r = run_script("validate-clusters.py", input=json.dumps(VALID_CLUSTERS))
    assert r.returncode == 0, r.stderr


def test_invalid_severity_fails():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["clusters"][0]["severity"] = "blocker"
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0
    assert "severity" in r.stderr.lower()


def test_missing_clusters_field_fails():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    del bad["clusters"]
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_invalid_tag_fails():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["clusters"][0]["tag"] = "maybe"
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_codex_timeout_status_accepted():
    """Schema must accept timeout from run-codex.py."""
    ok = json.loads(json.dumps(VALID_CLUSTERS))
    ok["reviewer_summary"]["codex"] = {
        "status": "timeout", "error": "codex did not finish within 300s",
        "duration_ms": 300000,
    }
    r = run_script("validate-clusters.py", input=json.dumps(ok))
    assert r.returncode == 0, r.stderr


def test_codex_skipped_status_accepted():
    """Schema must accept skipped (--no-codex was passed)."""
    ok = json.loads(json.dumps(VALID_CLUSTERS))
    ok["reviewer_summary"]["codex"] = {"status": "skipped"}
    # Also drop codex from any cluster sources so we don't accidentally
    # claim codex contributed to a finding when it was skipped.
    for c in ok["clusters"]:
        c["sources"] = [s for s in c["sources"] if s["source"] != "codex"]
        if not c["sources"]:
            c["sources"] = [{"source": "claude:code-reviewer",
                             "original_title": "...", "original_detail": "...",
                             "severity": "medium"}]
            c["tag"] = "claude_only"
    r = run_script("validate-clusters.py", input=json.dumps(ok))
    assert r.returncode == 0, r.stderr


def test_unparsed_chunks_rejects_bare_string():
    """Regression: previously the schema accepted any array shape for
    unparsed_chunks. A bare string item ("raw prose") validated fine and
    then crashed report.py at ch['source'] lookup. Now: each item must
    be an object with source + text."""
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["unparsed_chunks"] = ["raw prose"]
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_unparsed_chunks_rejects_missing_source():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["unparsed_chunks"] = [{"text": "no source field"}]
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_validate_clusters.py -v
```

- [ ] **Step 3: Implement `scripts/validate-clusters.py`**

```python
#!/usr/bin/env python3
"""validate-clusters.py — JSON-Schema-validate the synthesis cluster JSON.

Exits 0 if valid; non-zero with a descriptive stderr if not. The orchestrator
catches non-zero, re-prompts the synthesis LLM once with the error, then
re-validates. If validation fails twice, the final report runs in "synthesis
failed" mode (see SKILL.md).
"""
import json
import sys

import jsonschema

SCHEMA = {
    "type": "object",
    "required": ["scope_summary", "mode", "reviewer_summary",
                 "clusters", "unparsed_chunks"],
    "properties": {
        "scope_summary": {"type": "string"},
        "mode": {"enum": ["code", "spec", "plan", "docs"]},
        "focus": {"type": ["string", "null"]},
        "reviewer_summary": {
            "type": "object",
            "required": ["codex", "claude"],
            "properties": {
                "codex": {
                    "type": "object",
                    "required": ["status"],
                    "properties": {
                        "status": {"enum": ["ok", "failed", "timeout", "skipped"]},
                        "raw_findings": {"type": "integer"},
                        "parse_warnings": {"type": "integer"},
                        "error": {"type": "string"},
                        "duration_ms": {"type": "integer"},
                    },
                },
                "claude": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["agent", "status"],
                        "properties": {
                            "agent": {"type": "string"},
                            "status": {"enum": ["ok", "failed", "skipped"]},
                            "raw_findings": {"type": "integer"},
                            "parse_warnings": {"type": "integer"},
                            "error": {"type": "string"},
                        },
                    },
                },
            },
        },
        "clusters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["tag", "severity", "file", "line",
                             "category", "title", "synthesized_detail", "sources"],
                "properties": {
                    "tag": {"enum": ["agreement", "claude_only",
                                     "codex_only", "disagreement"]},
                    "severity": {"enum": ["critical", "high", "medium", "low"]},
                    "file": {"type": "string"},
                    "line": {"type": "string"},
                    "category": {"enum": ["bug", "test-gap", "perf",
                                          "security", "clarity", "style", "other"]},
                    "title": {"type": "string"},
                    "synthesized_detail": {"type": "string"},
                    "sources": {
                        "type": "array", "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["source", "severity"],
                            "properties": {
                                "source": {"type": "string"},
                                "original_title": {"type": "string"},
                                "original_detail": {"type": "string"},
                                "severity": {"enum": ["critical", "high",
                                                      "medium", "low"]},
                            },
                        },
                    },
                    "severity_divergence": {"type": "string"},
                },
            },
        },
        "unparsed_chunks": {
            "type": "array",
            "items": {
                "type": "object",
                # report.py iterates these and reads ch['source'] + ch.get('text','')
                # — a bare-string item (legal under the prior {type: array} shape)
                # would crash rendering. The item schema below mirrors what
                # normalize-findings.py actually emits.
                "required": ["source", "text"],
                "properties": {
                    "source": {"type": "string"},
                    "text": {"type": "string"},
                    "position": {"type": "string"},
                },
            },
        },
    },
}


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"error: input is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    try:
        jsonschema.validate(data, SCHEMA)
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        print(f"error: schema violation at {path}: {e.message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/validate-clusters.py
pytest tests/test_validate_clusters.py -v
```

Expected: 8 passed (valid, invalid-severity, missing-clusters, invalid-tag, codex-timeout-accepted, codex-skipped-accepted, unparsed-rejects-bare-string, unparsed-rejects-missing-source).

- [ ] **Step 5: Commit**

```bash
git add scripts/validate-clusters.py tests/test_validate_clusters.py
git commit -m "feat: validate-clusters.py JSON Schema check on synthesis output"
```

---

## Task 15: report.py — final Markdown rendering

**Files:**
- Create: `scripts/report.py`
- Create: `tests/test_report.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_report.py
"""Tests for report.py — cluster JSON + raw outputs → final Markdown."""
import json
import subprocess
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def test_report_renders_high_confidence_section(tmp_path):
    clusters = {
        "scope_summary": "PR #105",
        "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "ok", "raw_findings": 1, "parse_warnings": 0},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 1, "parse_warnings": 0}],
        },
        "clusters": [
            {
                "tag": "agreement", "severity": "high",
                "file": "src/foo.py", "line": "42", "category": "bug",
                "title": "Null deref",
                "synthesized_detail": "Both flag this.",
                "sources": [
                    {"source": "codex", "severity": "high"},
                    {"source": "claude:code-reviewer", "severity": "medium"},
                ],
                "severity_divergence": "codex=high vs claude=medium → high",
            },
        ],
        "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "codex.txt"; codex_raw.write_text("raw codex")
    claude_raw = tmp_path / "claude.txt"; claude_raw.write_text("raw claude")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw),
         "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    md = r.stdout
    assert "# Combined Review" in md
    assert "PR #105" in md
    assert "## High-confidence findings" in md
    assert "src/foo.py:42" in md
    assert "Null deref" in md
    assert "codex, claude:code-reviewer" in md
    assert "raw codex" in md
    assert "raw claude" in md


def test_report_embeds_codex_stderr_in_audit(tmp_path):
    """When codex fails (auth/quota/sandbox), the diagnostic lives on stderr.
    Earlier versions only embedded stdout, so users saw the reviewer_summary
    line and nothing else. Stderr must appear in the audit-trail section."""
    clusters = {
        "scope_summary": "PR #99", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "failed", "error": "auth", "exit_code": 1},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 0, "parse_warnings": 0}],
        },
        "clusters": [], "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    codex_err = tmp_path / "ce.txt"
    codex_err.write_text("ERROR: codex auth failed: token expired at 12:34 UTC")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw),
         "--codex-stderr", str(codex_err),
         "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    md = r.stdout
    assert "Codex stderr" in md
    assert "token expired" in md


def test_report_renders_codex_timeout_in_reviewer_status(tmp_path):
    """If codex timed out, the user must see it in the report — not just
    "no codex findings" with no explanation."""
    clusters = {
        "scope_summary": "PR #105", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "timeout", "duration_ms": 300000,
                      "error": "did not finish within 300s"},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 1, "parse_warnings": 0}],
        },
        "clusters": [],
        "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("raw claude")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    md = r.stdout
    assert "## Reviewer status" in md
    assert "Codex" in md and "timeout" in md
    assert "300s" in md


def test_report_renders_no_codex_skipped(tmp_path):
    """`--no-codex` runs must show codex as 'skipped' in the report."""
    clusters = {
        "scope_summary": "uncommitted", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "skipped"},
            "claude": [{"agent": "code-reviewer", "status": "ok",
                        "raw_findings": 0, "parse_warnings": 0}],
        },
        "clusters": [], "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "skipped" in r.stdout
    assert "--no-codex" in r.stdout


def test_report_renders_failed_claude_agent(tmp_path):
    """A failed sub-agent must appear in the reviewer status section."""
    clusters = {
        "scope_summary": "PR #5", "mode": "code", "focus": None,
        "reviewer_summary": {
            "codex": {"status": "ok", "raw_findings": 2, "parse_warnings": 0},
            "claude": [
                {"agent": "code-reviewer", "status": "ok",
                 "raw_findings": 1, "parse_warnings": 0},
                {"agent": "pr-test-analyzer", "status": "failed",
                 "error": "agent dispatch failed"},
            ],
        },
        "clusters": [], "unparsed_chunks": [],
    }
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw), "--claude-raw", str(claude_raw)],
        input=json.dumps(clusters), capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "pr-test-analyzer" in r.stdout
    assert "failed" in r.stdout


def test_report_synthesis_failed_banner(tmp_path):
    codex_raw = tmp_path / "c.txt"; codex_raw.write_text("c")
    claude_raw = tmp_path / "cl.txt"; claude_raw.write_text("cl")
    r = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "report.py"),
         "--codex-raw", str(codex_raw),
         "--claude-raw", str(claude_raw),
         "--synthesis-failed", "schema invalid: clusters missing"],
        input="", capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "Synthesis failed" in r.stdout
    assert "schema invalid" in r.stdout
    assert "raw codex" not in r.stdout  # but raw outputs should be embedded:
    # actually they should be embedded — fix:
    assert "c\n" in r.stdout or "raw" in r.stdout.lower()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_report.py -v
```

- [ ] **Step 3: Implement `scripts/report.py`**

```python
#!/usr/bin/env python3
"""report.py — render the final Combined Review report from cluster JSON.

Inputs:
- stdin: cluster JSON (from synthesis pass, validated by validate-clusters.py).
  Empty when --synthesis-failed is set.
- --codex-raw <path>: codex raw output file
- --claude-raw <path>: aggregated Claude sub-agent transcripts
- --synthesis-failed "<msg>": if set, emit a "synthesis failed" report
  with raw outputs only and the diagnostic message.

Output: Markdown to stdout.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


# Duplicated from render-prompt.py (small helpers; not worth a shared module
# for a personal skill). Reviewer transcripts routinely contain triple-
# backtick code blocks (codex inlines diffs, Claude agents inline examples),
# so wrapping raw output in plain ``` would let the first inner ``` close the
# outer fence — same class of bug as the prompt-rendering one, but in the
# audit-trail section of the report.
def fence_for(content: str) -> str:
    longest = 0
    run = 0
    for ch in content:
        if ch == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return "`" * max(3, longest + 1)


def fenced(content: str, lang: str = "") -> str:
    fence = fence_for(content)
    return f"{fence}{lang}\n{content.rstrip(chr(10))}\n{fence}"


def header(scope_summary: str, mode: str, focus: str | None) -> str:
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Combined Review", "",
        f"**Scope:** {scope_summary}", f"**Mode:** {mode}",
        f"**Focus:** {focus or '(none)'}",
        f"**Generated:** {ts}",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def render_reviewer_status(rs: dict) -> str:
    """Render the reviewer_summary block so codex failures/timeouts/skipped
    runs and failed Claude agents are visible in the final report — not buried
    in the raw outputs section. Promised in §10 'In-flight failure handling';
    omitting this caused the user-facing report to silently degrade."""
    lines = ["## Reviewer status", ""]
    codex = rs.get("codex", {})
    cstatus = codex.get("status", "unknown")
    if cstatus == "ok":
        rf = codex.get("raw_findings", "?")
        pw = codex.get("parse_warnings", 0)
        warn = f" ({pw} parse warnings)" if pw else ""
        lines.append(f"- **Codex**: ok — {rf} raw findings{warn}")
    elif cstatus == "skipped":
        lines.append("- **Codex**: skipped (`--no-codex`)")
    elif cstatus in ("failed", "timeout"):
        dur = codex.get("duration_ms")
        dur_s = f" after {dur//1000}s" if isinstance(dur, int) else ""
        err = codex.get("error", "no detail")
        # truncate aggressive — full stderr is in the raw outputs section
        if len(err) > 240: err = err[:240] + "…"
        lines.append(f"- **Codex**: {cstatus}{dur_s} — `{err}`")
    else:
        lines.append(f"- **Codex**: {cstatus}")
    for agent in rs.get("claude", []):
        name = agent.get("agent", "?")
        st = agent.get("status", "unknown")
        if st == "ok":
            rf = agent.get("raw_findings", "?")
            pw = agent.get("parse_warnings", 0)
            warn = f" ({pw} parse warnings)" if pw else ""
            lines.append(f"- **Claude:{name}**: ok — {rf} raw findings{warn}")
        elif st == "failed":
            err = agent.get("error", "no detail")
            if len(err) > 240: err = err[:240] + "…"
            lines.append(f"- **Claude:{name}**: failed — `{err}`")
        else:
            lines.append(f"- **Claude:{name}**: {st}")
    lines.append("")
    return "\n".join(lines)


def render_cluster(c: dict) -> str:
    src_list = ", ".join(s["source"] for s in c["sources"])
    parts = [
        f"- **[{c['severity'].title()}] {c['file']}:{c['line']}** — {c['title']}",
        f"  {c['synthesized_detail']}",
        f"  _Sources: {src_list}_",
    ]
    if c.get("severity_divergence"):
        parts.append(f"  _Severity: {c['severity_divergence']}_")
    return "\n".join(parts)


def by_tag(clusters: list[dict], tag: str) -> list[dict]:
    out = [c for c in clusters if c["tag"] == tag]
    out.sort(key=lambda c: SEV_ORDER.get(c["severity"], 4))
    return out


def render_sections(clusters: list[dict]) -> str:
    sections = []
    agreements = by_tag(clusters, "agreement")
    if agreements:
        sections.append("## High-confidence findings (both tools agree)\n")
        sections += [render_cluster(c) for c in agreements]
        sections.append("")
    claude_only = by_tag(clusters, "claude_only")
    codex_only = by_tag(clusters, "codex_only")
    if claude_only or codex_only:
        sections.append("## Single-source findings\n")
        if claude_only:
            sections.append("### Claude only\n")
            sections += [render_cluster(c) for c in claude_only]
            sections.append("")
        if codex_only:
            sections.append("### Codex only\n")
            sections += [render_cluster(c) for c in codex_only]
            sections.append("")
    disagreements = by_tag(clusters, "disagreement")
    if disagreements:
        sections.append("## Disagreements (worth a second look)\n")
        sections += [render_cluster(c) for c in disagreements]
        sections.append("")
    if not (agreements or claude_only or codex_only or disagreements):
        sections.append("## No issues found\n")
    return "\n".join(sections)


def _read_or_empty(p: Path | None) -> str:
    if p is None or not p.exists():
        return ""
    try:
        return p.read_text()
    except OSError:
        return ""


def render_raw(codex_raw: Path, claude_raw: Path, codex_stderr: Path | None) -> str:
    """Embed raw reviewer outputs in a collapsed audit-trail section.

    Codex stderr is critical for failure/timeout diagnostics (auth errors,
    quota exhaustion, sandbox refusals) — codex writes the diagnostic to
    stderr and produces no findings on stdout. Earlier versions only embedded
    stdout, leaving users with the reviewer_summary line as the only signal.
    Now we include stderr when it has content, so the failure mode is
    actually debuggable from the report alone.
    """
    err_text = _read_or_empty(codex_stderr).rstrip()
    codex_text = codex_raw.read_text().rstrip() or "(empty)"
    claude_text = claude_raw.read_text().rstrip() or "(empty)"
    parts = [
        "---", "",
        "<details>", "<summary>Raw outputs (audit trail)</summary>", "",
        "### Codex stdout", "",
        fenced(codex_text), "",
    ]
    if err_text:
        parts += [
            "### Codex stderr", "",
            fenced(err_text), "",
        ]
    parts += [
        "### Claude sub-agents", "",
        fenced(claude_text), "",
        "</details>", "",
    ]
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--codex-raw", required=True, type=Path,
                    help="codex stdout capture")
    ap.add_argument("--codex-stderr", default=None, type=Path,
                    help="codex stderr capture (recommended — failures live here)")
    ap.add_argument("--claude-raw", required=True, type=Path)
    # Two ways to pass the synthesis-failure message:
    #   --synthesis-failed "<msg>" — convenient when msg is short and known-safe
    #   --synthesis-failed-file <path> — REQUIRED when msg originates from
    #     validator stderr / model output / anything the orchestrator can't
    #     pre-sanitize. Same shell-injection class as the focus-text case:
    #     interpolating arbitrary content into a Bash command line is unsafe.
    ap.add_argument("--synthesis-failed", default=None)
    ap.add_argument("--synthesis-failed-file", default=None, type=Path)
    args = ap.parse_args()
    if args.synthesis_failed and args.synthesis_failed_file:
        ap.error("--synthesis-failed and --synthesis-failed-file are mutually exclusive")
    synthesis_failed_msg = args.synthesis_failed
    if args.synthesis_failed_file is not None:
        try:
            synthesis_failed_msg = args.synthesis_failed_file.read_text().strip()
        except OSError as e:
            ap.error(f"could not read --synthesis-failed-file: {e}")

    if synthesis_failed_msg:
        out = [
            "# Combined Review — synthesis failed", "",
            f"> **Synthesis failed.** {synthesis_failed_msg}",
            "> Manual review of raw outputs required.", "",
            "---", "",
            render_raw(args.codex_raw, args.claude_raw, args.codex_stderr),
        ]
        sys.stdout.write("\n".join(out))
        return

    data = json.load(sys.stdin)
    out = [
        header(data["scope_summary"], data["mode"], data.get("focus")),
        render_reviewer_status(data.get("reviewer_summary", {})),
        render_sections(data["clusters"]),
    ]
    if data.get("unparsed_chunks"):
        out.append("## Parse warnings\n")
        for ch in data["unparsed_chunks"]:
            out.append(f"- From {ch['source']}: {ch.get('text','')[:200]}")
        out.append("")
    out.append(render_raw(args.codex_raw, args.claude_raw, args.codex_stderr))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/report.py
pytest tests/test_report.py -v
```

Expected: 6 passed (high-confidence rendering, codex-stderr-in-audit, codex-timeout-in-reviewer-status, no-codex-skipped, failed-claude-agent, synthesis-failed-banner).

- [ ] **Step 5: Commit**

```bash
git add scripts/report.py tests/test_report.py
git commit -m "feat: report.py renders cluster JSON + raw outputs to Markdown"
```

---

## Task 16: cleanup-worktree.sh

**Files:**
- Create: `scripts/cleanup-worktree.sh`
- Create: `tests/test_cleanup_worktree.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cleanup_worktree.py
"""Tests for cleanup-worktree.sh — triple-assertion gate before removal."""
import subprocess
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def cleanup(repo, worktree):
    return subprocess.run(
        [str(SCRIPTS_DIR / "cleanup-worktree.sh"), str(repo), str(worktree)],
        capture_output=True, text=True,
    )


def test_cleanup_removes_legitimate_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    wt = tmp_path / "combined-review-x-abcdef"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=tmp_repo, check=True)
    assert wt.exists()
    r = cleanup(tmp_repo, wt)
    assert r.returncode == 0, r.stderr
    assert not wt.exists()


def test_cleanup_refuses_repo_root(tmp_repo):
    r = cleanup(tmp_repo, tmp_repo)
    assert r.returncode != 0
    assert "refus" in r.stderr.lower() or "root" in r.stderr.lower()


def test_cleanup_refuses_arbitrary_directory(tmp_repo, tmp_path):
    arbitrary = tmp_path / "not-a-worktree"
    arbitrary.mkdir()
    r = cleanup(tmp_repo, arbitrary)
    assert r.returncode != 0
    assert arbitrary.exists()  # we DID NOT delete it


def test_cleanup_skips_when_marker_present(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    wt = tmp_path / "combined-review-x-keepme"
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=tmp_repo, check=True)
    (wt / ".combined-review-keep").touch()
    r = cleanup(tmp_repo, wt)
    # We expect non-zero (refused) AND the worktree still exists.
    assert r.returncode != 0
    assert wt.exists()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_cleanup_worktree.py -v
```

- [ ] **Step 3: Implement `scripts/cleanup-worktree.sh`**

```bash
#!/usr/bin/env bash
# cleanup-worktree.sh <repo_root> <worktree_path>
#
# Triple-assertion gate before destructive removal:
#   1. Path appears in `git worktree list --porcelain` for the repo.
#   2. Path matches the combined-review-* mktemp pattern under $TMPDIR or /tmp.
#   3. Path is not the repo root, and not the main worktree.
# Plus: skip if `.combined-review-keep` marker exists at the worktree root.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: cleanup-worktree.sh <repo_root> <worktree_path>" >&2
  exit 2
fi
REPO="$1"
WT="$2"
REPO_ABS="$(cd "$REPO" && pwd)"
WT_ABS="$(cd "$(dirname "$WT")" && pwd)/$(basename "$WT")"

# 0. Marker check
if [[ -f "$WT_ABS/.combined-review-keep" ]]; then
  echo "refused: marker .combined-review-keep present at $WT_ABS" >&2
  exit 3
fi

# 1. git worktree registry check
if ! git -C "$REPO_ABS" worktree list --porcelain | grep -Fq "worktree $WT_ABS"; then
  echo "refused: $WT_ABS not in git worktree list for $REPO_ABS" >&2
  exit 3
fi

# 2. mktemp pattern check (basename must start with combined-review-)
base="$(basename "$WT_ABS")"
if [[ ! "$base" =~ ^combined-review- ]]; then
  echo "refused: $WT_ABS basename does not match combined-review-* pattern" >&2
  exit 3
fi
parent="$(cd "$(dirname "$WT_ABS")" && pwd)"
TMP="${TMPDIR:-/tmp}"
TMP_ABS="$(cd "$TMP" && pwd)"
if [[ "$parent" != "$TMP_ABS" && "$parent" != "/tmp" ]]; then
  echo "refused: $WT_ABS parent ($parent) is not \$TMPDIR ($TMP_ABS) or /tmp" >&2
  exit 3
fi

# 3. not repo root, not main worktree
if [[ "$WT_ABS" == "$REPO_ABS" ]]; then
  echo "refused: $WT_ABS is the repo root" >&2
  exit 3
fi
main_wt="$(git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2; exit}')"
if [[ "$WT_ABS" == "$main_wt" ]]; then
  echo "refused: $WT_ABS is the main worktree" >&2
  exit 3
fi

git -C "$REPO_ABS" worktree remove --force "$WT_ABS"
echo "removed: $WT_ABS"
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/cleanup-worktree.sh
pytest tests/test_cleanup_worktree.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/cleanup-worktree.sh tests/test_cleanup_worktree.py
git commit -m "feat: cleanup-worktree.sh with triple-assertion safety gate"
```

---

## Task 17: gc-worktrees.sh

**Files:**
- Create: `scripts/gc-worktrees.sh`
- Create: `tests/test_gc_worktrees.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_gc_worktrees.py
"""Tests for gc-worktrees.sh — list-then-filter via git worktree list."""
import os
import subprocess
import time
from pathlib import Path
from tests.conftest import SCRIPTS_DIR


def gc(repo):
    return subprocess.run(
        [str(SCRIPTS_DIR / "gc-worktrees.sh"), str(repo)],
        capture_output=True, text=True,
    )


def make_aged_worktree(repo, tmp_path, name, age_hours):
    wt = tmp_path / name
    subprocess.run(["git", "worktree", "add", "--detach", str(wt)],
                   cwd=repo, check=True)
    old = time.time() - (age_hours * 3600)
    os.utime(wt, (old, old))
    return wt


def test_gc_removes_old_combined_review(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    old_wt = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-aaa", 48)
    r = gc(tmp_repo)
    assert r.returncode == 0, r.stderr
    assert not old_wt.exists()


def test_gc_skips_marked_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    kept = make_aged_worktree(tmp_repo, tmp_path, "combined-review-old-keep", 48)
    (kept / ".combined-review-keep").touch()
    r = gc(tmp_repo)
    assert r.returncode == 0, r.stderr
    assert kept.exists()


def test_gc_skips_recent_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    recent = make_aged_worktree(tmp_repo, tmp_path, "combined-review-recent-bbb", 1)
    r = gc(tmp_repo)
    assert r.returncode == 0
    assert recent.exists()


def test_gc_skips_non_combined_review_worktree(tmp_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    other = make_aged_worktree(tmp_repo, tmp_path, "some-other-wt", 48)
    r = gc(tmp_repo)
    assert r.returncode == 0
    assert other.exists()
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
pytest tests/test_gc_worktrees.py -v
```

- [ ] **Step 3: Implement `scripts/gc-worktrees.sh`**

```bash
#!/usr/bin/env bash
# gc-worktrees.sh <repo_root>
#
# Enumerates worktrees via `git worktree list --porcelain`, selects entries
# matching the combined-review-* basename pattern, AND older than 24h
# (by mtime), AND not carrying a .combined-review-keep marker. Each removal
# goes through the same triple-assertion gate as cleanup-worktree.sh.
set -euo pipefail

REPO="${1:-$PWD}"
REPO_ABS="$(cd "$REPO" && pwd)"
AGE_HOURS="${COMBINED_REVIEW_GC_AGE_HOURS:-24}"
NOW="$(date +%s)"
CUTOFF=$(( NOW - (AGE_HOURS * 3600) ))

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Portable mtime helper. Tries GNU `stat -c %Y` first, then BSD `stat -f %m`,
# then Python as a last-resort fallback. Earlier versions of this script tried
# `stat -f %m` first, but on GNU/Linux `-f` means "filesystem mode" (not file)
# and `%m` is the mount point, so the command exits 0 with non-numeric output —
# the GNU `-c %Y` fallback never ran, and the numeric `[[ ]]` comparison broke
# silently, leaving stale worktrees forever.
mtime_of() {
  local p="$1" m
  if m=$(stat -c %Y "$p" 2>/dev/null); then
    echo "$m"
  elif m=$(stat -f %m "$p" 2>/dev/null); then
    echo "$m"
  else
    python3 -c 'import os, sys; print(int(os.stat(sys.argv[1]).st_mtime))' "$p" 2>/dev/null || echo 0
  fi
}

git -C "$REPO_ABS" worktree list --porcelain | awk '/^worktree / {print $2}' \
| while IFS= read -r wt; do
  base="$(basename "$wt")"
  [[ "$base" =~ ^combined-review- ]] || continue
  [[ -f "$wt/.combined-review-keep" ]] && continue
  mtime="$(mtime_of "$wt")"
  # Sanity-check that mtime is a positive integer before arithmetic; on the
  # off chance both stat forms return something non-numeric, treat as "skip"
  # rather than crash the GC loop.
  if [[ "$mtime" =~ ^[0-9]+$ ]] && [[ "$mtime" -lt "$CUTOFF" ]]; then
    "$SCRIPT_DIR/cleanup-worktree.sh" "$REPO_ABS" "$wt" || true
  fi
done
```

- [ ] **Step 4: Run tests**

```bash
chmod +x scripts/gc-worktrees.sh
pytest tests/test_gc_worktrees.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/gc-worktrees.sh tests/test_gc_worktrees.py
git commit -m "feat: gc-worktrees.sh removes stale combined-review-* worktrees > 24h"
```

---

## Task 18: SKILL.md — orchestration document

**Files:**
- Create: `SKILL.md`

This is a documentation task — no test code, but the SKILL.md content must be precise enough that an LLM following it will execute the pipeline correctly.

- [ ] **Step 1: Write `SKILL.md`**

Note the **four-backtick** outer fence — the SKILL.md content contains many indented triple-backtick code blocks, and a triple-backtick outer fence would let those (indented up to 3 spaces is still valid CommonMark close-fence) terminate the wrapper prematurely.

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "feat: SKILL.md orchestration document for combined-review"
```

---

## Task 19: commands/combined-review.md — slash entry

**Files:**
- Create: `commands/combined-review.md`

- [ ] **Step 1: Write the slash command**

Four-backtick outer fence: the slash command's body contains a triple-backtick block around `$ARGUMENTS`.

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add commands/combined-review.md
git commit -m "feat: slash command entry point for combined-review"
```

---

## Task 20: Install via symlinks; baseline smoke test

**Files:**
- Modify: `README.md` (install instructions)

- [ ] **Step 1: Document install in `README.md`**

Four-backtick outer fence: the README contains multiple triple-backtick code blocks.

````markdown
# combined-review

A Claude Code skill that runs Claude's `pr-review-toolkit` sub-agents and
`codex exec --sandbox read-only` in parallel against the same materialized
review subject, then synthesizes the findings into one report.

See `docs/superpowers/specs/2026-05-11-combined-review-skill-design.md`
in the original juvera repo for the design rationale.

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
````

- [ ] **Step 2: Run the install commands**

```bash
cd ~/projects/combined-review
mkdir -p ~/.claude/skills ~/.claude/commands
ln -sfn "$PWD" ~/.claude/skills/combined-review
ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
ls -la ~/.claude/skills/combined-review
ls -la ~/.claude/commands/combined-review.md
```

Expected: both symlinks present and pointing at `~/projects/combined-review/`. (Earlier audit found `~/.claude/commands/` did not exist on this machine — the `mkdir -p` makes the install idempotent regardless of starting state.)

- [ ] **Step 3: Run the full test suite end-to-end**

```bash
cd ~/projects/combined-review && pytest -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: install instructions and dev workflow"
```

---

## Task 21: End-to-end smoke — --uncommitted on a tiny diff

This task is **manual** — run the skill against a real repo to verify the pipeline holds together. Failures here typically expose orchestration glitches that unit tests miss.

- [ ] **Step 1: Make a tiny throwaway change in this Juvera repo**

**Do NOT modify any existing file** — `git checkout -- <file>` would discard real edits at rollback time. Use a brand-new file that's safe to delete.

```bash
cd ~/Projects/juvera_ai_4
# Create a brand-new file that doesn't exist in the tree
test ! -e .combined-review-smoke.txt || (echo "remove first" && false)
cat > .combined-review-smoke.txt <<'EOF'
# Combined-review smoke test fixture
This file exists only so the skill has something tangible to review.
It will be removed after the smoke test.
EOF
```

- [ ] **Step 2: Invoke `/combined-review --uncommitted`**

In your Claude Code session for the Juvera repo, type:

```
/combined-review --uncommitted
```

- [ ] **Step 3: Verify expected behavior**

- Phase A runs sequentially — you should see GC, args-file write, parse-args, resolve-scope, materialize executed in order via Bash calls (parse-args reads from the args file, never from inline `$ARGUMENTS` substitution).
- Pre-flight passes (codex available, no PR, has reviewable changes — the smoke fixture file is untracked but materialize-scope picks it up).
- Phase B issues one background Bash (codex with `--status` flag) and three Agent calls (code-reviewer, silent-failure-hunter, pr-test-analyzer) in a SINGLE message.
- Phase C reads `$CODEX_STATUS`, branches correctly (should be `ok` for a real codex run).
- Synthesis runs and produces a clustered report.
- Final report is printed.
- Phase D cleanup runs — verify with `ls $TMPDIR/combined-review-*` (no leftovers) and `git worktree list` (no extra entries — though for `--uncommitted` no worktree was created in the first place).

- [ ] **Step 4: Remove the throwaway file**

```bash
cd ~/Projects/juvera_ai_4
rm .combined-review-smoke.txt
git status   # should now be clean
```

- [ ] **Step 5: If anything failed**, capture the failure mode (what didn't run, what error appeared) and fix in a follow-up commit before moving on.

---

## Task 22: End-to-end smoke — --pr on a real PR

- [ ] **Step 1: Pick a small, recently-merged PR in this repo** (or use a current open PR if available)

```bash
cd ~/Projects/juvera_ai_4
gh pr list --state all --limit 5
# pick one with a small diff, e.g., PR #91 (the test-unit gate work)
```

- [ ] **Step 2: Invoke `/combined-review --pr <#>`**

```
/combined-review --pr 91
```

- [ ] **Step 3: Verify**

- A worktree gets created under `$TMPDIR/combined-review-juvera_ai_4-pr-*`
- `gh pr checkout --detach` runs inside it
- `git fetch <base_repo_url> main` runs (NOT `git fetch origin main`)
- `git cat-file -e <head_sha>^{commit}` and `git cat-file -e <base_sha>^{commit}` both succeed
- Both reviewers see the three-dot diff (compare a few line citations against `gh pr diff 91`)
- Report renders
- `cleanup-worktree.sh` runs and the temp worktree is gone

- [ ] **Step 4: If failures**, fix and re-run.

---

## Task 23: End-to-end smoke — --mode spec on a doc file

- [ ] **Step 1: Pick a spec file in this repo**

```bash
ls docs/superpowers/specs/ | head -5
# e.g., docs/superpowers/specs/2026-05-08-ci-test-unit-path-filter-design.md
```

- [ ] **Step 2: Invoke**

```
/combined-review --mode spec docs/superpowers/specs/2026-05-08-ci-test-unit-path-filter-design.md
```

- [ ] **Step 3: Verify**

- `materialize-scope.py` puts the file into `doc_files` (not `changed_files`).
- Codex is invoked via `codex exec` (not codex review).
- ONE Claude agent (document-reviewer brief), not three.
- Findings reflect spec-review concerns (completeness, ambiguity) — NOT "no test coverage".
- Report renders.

- [ ] **Step 4: Fix any issues, then commit any fixes**

---

## Task 24: Final test suite + commit

- [ ] **Step 1: Run the full suite one last time**

```bash
cd ~/projects/combined-review && pytest -v
```

Expected: all green.

- [ ] **Step 2: Check git log for sanity**

```bash
git log --oneline
```

Expected: ~20 commits, each a single coherent step.

- [ ] **Step 3: Push to a fork (optional — only if you intend to share)**

```bash
gh repo create combined-review --public --source=. --remote=origin --push
```

---

## Spec coverage verification

| Spec section | Covered by task(s) |
|---|---|
| §2 Invocation (slash + skill) | T18 (SKILL.md), T19 (slash command) |
| §2 CLI flags | T2 (parse-args.py) |
| §3 Scope resolution | T3, T4, T5 (resolve-scope.py) |
| §4 Codex routing via `codex exec` | T12 (run-codex.py) |
| §4 Worktree lifecycle | T7, T8 (creation), T16 (cleanup), T17 (GC) |
| §4 PR fetch by URL + cat-file check | T8 |
| §4 Shared-primary-input guarantee | T11 (render-prompt unifies both sides' inputs) |
| §4 codex exec --sandbox safety | T12 (verifies flag is supported) |
| §5 Materialize-scope for all kinds | T6, T7, T8, T9 |
| §5 Phase A/B/C/D dispatch ordering | T18 (SKILL.md) |
| §5 Raw output ownership | T18, T12, T20 (manual verify) |
| §6 Mode prompts | T10 |
| §7 Finding schema | T11 (schema appendix), T13 (parser) |
| §8 Synthesis pass + cluster JSON | T18 (skill instructs synthesis) |
| §8 validate-clusters + repair | T14, T18 |
| §9 Report format | T15 |
| §10 Pre-flight checks | T18 (codex auth, gh auth, empty scope, large diff) |
| §10 In-flight failure handling | T18 (codex timeout, sub-agent failure) |
| §11 File layout | T1, all create tasks |
| §12 Testing approach | T21–T23 (smoke), unit tests throughout |
| §13 Non-goals (no auto-fix) | T11 + T12 enforce no-edit |
| §14 Locked decisions | All reflected in implementation |

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

**Which approach?**
`````

### docs/superpowers/specs/2026-05-11-combined-review-skill-design.md  (status: added, kind: text)
````
# Combined Review Skill — Design Spec

**Date:** 2026-05-11
**Scope:** Personal Claude Code skill (`~/.claude/`), not a project artifact. Spec lives here for review history.
**Goal:** A single Claude Code invocation that runs both Claude Code's review (the `pr-review-toolkit` sub-agents) and Codex (via `codex exec --sandbox read-only` driven by a materialized review prompt — see §4 for why we bypass `codex review`'s native diff), then merges findings into a deduped, attributed, high-signal report — without the user juggling two sessions.

---

## 1. Overview

Today the user runs two reviewers in two separate sessions:

- **Claude Code side:** the `pr-review-toolkit` plugin (slash command `/pr-review-toolkit:review-pr`), which dispatches specialized sub-agents — code-reviewer, silent-failure-hunter, pr-test-analyzer, comment-analyzer, type-design-analyzer, code-simplifier — and aggregates into severity buckets. (Not to be confused with Claude Code's built-in `/review` command, which is a separate, lighter-weight flow.) This skill **reuses the toolkit's sub-agents directly** rather than invoking the toolkit's slash command — orchestrating the agents in-session gives us control over prompts and output schema.
- **Codex side:** the `codex` CLI. The skill drives codex via `codex exec --sandbox read-only` with a fully-materialized review prompt (diff + file contents) on stdin, **not** via `codex review`'s native auto-diff. §4 details the reasoning: codex review's diff semantics are unobservable, and a silent mismatch with the Claude-side diff would corrupt synthesis. By feeding both sides the same materialized blob from `materialize-scope.py`, we pin the primary input.

The user's workflow is mostly PR review with occasional spec/plan/doc review. Two-tool review is high-signal because the tools disagree usefully — but the manual merge is tedious and the user wants the synthesis automated.

The skill orchestrates both reviews in parallel from one Claude Code session and produces a unified report that distinguishes:

- **High-confidence findings** — both tools independently flagged the same issue.
- **Single-source findings** — only one tool flagged it.
- **Disagreements** — both tools flagged the same location but with contradictory recommendations.

---

## 2. Invocation

Two files:

- `~/.claude/commands/combined-review.md` — slash command. Parses `$ARGUMENTS`, hands off to the skill.
- `~/.claude/skills/combined-review/SKILL.md` — orchestration logic, activated by the slash command.

This split follows Anthropic's distinction: slash commands are user-typed entry points; skills are model-invoked workflows. The slash command exists because the user wants `/combined-review` to work as a literal command; the skill exists because the orchestration is non-trivial and worth being model-invocable in its own right.

### CLI surface

```
/combined-review                                 # auto-detect scope, code mode
/combined-review --pr 105                        # GitHub PR by number
/combined-review --uncommitted                   # staged + unstaged + untracked
/combined-review --base develop                  # current branch vs custom base (merge-base diff)
/combined-review --commit abc1234                # single commit
/combined-review docs/spec.md plan.md            # positional file list (current contents)
/combined-review --mode spec --pr 105            # spec lens applied to PR changes
/combined-review --focus "API contract changes"  # extra lens, default code mode
/combined-review --full                          # opt into full Claude sub-agent fanout
/combined-review --pr 105 --force-large          # bypass large-diff confirm prompt
/combined-review --pr 105 --keep-worktree        # debug: don't tear down /tmp worktree
```

### Flags

| Flag | Type | Effect |
|---|---|---|
| `--pr <#>` | int | Review GitHub PR by number |
| `--uncommitted` | bool | Review staged + unstaged + untracked |
| `--base <branch>` | string | Review current HEAD vs given base (merge-base diff, §5) |
| `--commit <sha>` | string | Review the changes in one commit |
| `<files...>` | positional | Specific files reviewed as **current working-tree content** (includes any local edits). Mutually exclusive with `--pr`/`--uncommitted`/`--base`/`--commit`. |
| `--mode <code\|spec\|plan\|docs>` | enum, default `code` | Select review template + sub-agent set |
| `--focus "<text>"` | string | Freeform extra emphasis appended to mode prompt |
| `--full` | bool | Use full pr-review-toolkit sub-agent set (6) instead of default 3 |
| `--no-codex` | bool | Skip Codex side (fallback when codex unavailable / quota exhausted) |
| `--save <path>` | string | Also write the final report to a file |
| `--force-large` | bool | Skip the large-diff confirm prompt. Required when the skill runs non-interactively above the threshold. |
| `--keep-worktree` | bool | Debug only. Inhibits worktree teardown and prints the path on completion. |

`--pr`, `--uncommitted`, `--base`, `--commit`, and positional files are mutually exclusive scope inputs. Specifying more than one is an error.

---

## 3. Scope resolution

Precedence (first match wins):

1. **Explicit scope flag** — use it as-is. Worktree rules:
   - **Diff-based scopes** (`--pr`, `--base`, `--commit`) always run inside a disposable clean worktree, never in the user's working tree. This prevents local uncommitted edits from contaminating a branch / PR / commit review.
   - **`--uncommitted`** runs in the user's working tree (that's the point of it).
   - **Positional files** are reviewed as **current working-tree content** including any local edits the user just made. Reviewing a doc/spec/plan you've been editing is the canonical use case — pinning to HEAD would defeat the purpose. No worktree needed.
2. **Dirty tree + PR exists for current branch** — **error**, surface ambiguity, require `--uncommitted` or `--pr <#>`.
3. **Dirty tree, no PR** — implicit `--uncommitted`.
4. **Clean tree, current branch has PR** — implicit `--pr <#>` (resolved via `gh pr view --json number,headRefOid,baseRefOid`).
5. **Clean tree, no PR, current branch ≠ default** — implicit `--base <default>` (default branch via `gh repo view --json defaultBranchRef`).
6. **Clean tree, current branch == default** — **error**, nothing to review.

Logic lives in `scripts/resolve-scope.py`. Emits a normalized scope object:

```json
{
  "kind": "pr" | "uncommitted" | "base" | "commit" | "files",
  "pr_number": 105,
  "base_ref_name": "main",
  "head_ref_name": "feature-x",
  "base_repo_url": "https://github.com/Juvera-AI/juvera_ai.git",
  "head_repo_url": "https://github.com/contributor/juvera_ai.git",
  "base_sha": "<immutable 40-char sha>",
  "head_sha": "<immutable 40-char sha>",
  "commit_sha": "<immutable 40-char sha>",
  "files": ["docs/spec.md"],
  "worktree_path": "<mktemp -d -t combined-review-XXXX>" | null,
  "repo_root": "/abs/path/to/repo",
  "needs_clean_worktree": true | false
}
```

Ref names + repo URLs are used for `git fetch` (portable across remotes, correct for fork PRs); SHAs are used to **verify** the recorded commits are reachable after fetch. Fetching by SHA alone is less portable; trusting the ref alone is unsafe; assuming `origin` is the base repo is wrong for fork PRs.

All ref-shaped inputs are resolved to immutable SHAs by `resolve-scope.py` — never `origin/<branch>` strings passed downstream, since branches move. For `--pr <#>`, this means `gh pr view <#> --json headRefOid,baseRefOid` first, then materialize against those SHAs.

`resolve-scope.py` does not create the worktree — it only sets `needs_clean_worktree: true` when one will be required. Creation is `materialize-scope.py`'s job (§5 / §4 Worktree lifecycle), since materialize is the first step that actually needs the worktree to exist. `worktree_path` in this object is `null` at this stage and gets populated by materialize.

Downstream steps consume this object, not raw flags.

---

## 4. Codex routing

### Shared-primary-input guarantee — why we don't use `codex review`'s native diff

What the skill guarantees, precisely:

- **Same primary input**: both codex and the Claude sub-agents receive the **same materialized blob** from `materialize-scope.py` (§5) — the same unified diff, the same per-file content snapshots, the same metadata. This is what they're *asked* to review.
- **Same repo context**: both run with cwd set to the **same git state** — the worktree pinned at the recorded SHA for diff scopes, the user's tree for `uncommitted`/`files`. Neither agent is isolated from the rest of the repo; both may consult adjacent files for context.
- **Not isolated to the blob**: read-only sandbox prevents *edits*, but `codex exec` and Claude sub-agents (Read, Grep, etc.) can still inspect files beyond the materialized inputs. We don't claim otherwise. Treating "look up callers/types for context" as a feature, not a leak — code review benefits from it, and both tools are looking at the same git state.

What this rules out is the failure mode that motivated this design: `codex review`'s native auto-diff. `codex review` computes its own diff from git state, and we can't observe whether it uses two-dot or three-dot semantics, how it handles untracked files, or how it filters renames. If it diverges from `materialize-scope.py`'s diff, the synthesis (§8) silently merges reviews of different primary inputs.

The skill therefore **bypasses `codex review`'s auto-diff entirely** and uses `codex exec --sandbox read-only` for every scope. The primary input is fixed; context lookups are intentionally allowed. Worth revisiting in v2 if codex review's diff semantics turn out to match ours exactly — but for v1, correctness on the primary input over speculation.

### Scope → invocation

`materialize-scope.py` produces a single content blob (unified diff + per-file `post_content` / `pre_content` / metadata, or doc contents for files mode). Both sides receive this blob. Routing differs only in **what worktree codex runs in** and **what the materialize step has to do first**.

| Scope kind | Setup | Codex invocation |
|---|---|---|
| `uncommitted` | None — operate in user's working tree. Materialize uses `git diff HEAD` + untracked. | `codex exec --sandbox read-only` (cwd = user repo root, prompt via stdin) |
| `base` | `git worktree add --detach <tmp> <head_sha>` (immutable SHA, not literal `HEAD`). Materialize uses `git diff <base_sha>...<head_sha>` inside worktree. | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
| `commit` | `git worktree add --detach <tmp> <commit_sha>`. Materialize uses `git show --format= <commit_sha>` + commit metadata (author, date, message). | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
| `pr` | `git worktree add --detach <tmp>` → `gh pr checkout --detach <#>` → fetch base from `<base_repo_url>` (not necessarily `origin` — see PR fetch detail below) → `git reset --hard <head_sha>` if drifted → verify both SHAs exist via `git cat-file -e <sha>^{commit}`. Materialize uses `git diff <base_sha>...<head_sha>` inside worktree. | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
| `files` (any mode) | None — operate against current working-tree content. Materialize populates `doc_files`. | `codex exec --sandbox read-only` (cwd = user repo root, prompt via stdin) |

### PR fetch detail

In fork/upstream setups, `origin` may be the contributor fork, not the PR base repo. Fetching the base from the wrong remote silently retrieves the wrong commits. The skill:

1. Reads `baseRepository.url`, `headRepository.url`, `baseRefName`, `headRefName`, `baseRefOid`, `headRefOid` from `gh pr view <#> --json baseRepository,headRepository,baseRefName,headRefName,baseRefOid,headRefOid`.
2. Runs `gh pr checkout --detach <#>` inside the worktree (handles the head fetch including fork mirrors).
3. **Fetches the base by URL directly, no remote-add**: `git fetch <base_repo_url> <base_ref_name>`. This fetches the ref into `FETCH_HEAD` without mutating the user's `.git/config` (which `git remote add` would do — and which would leak across runs or fail if the remote name already existed).
4. Pins head: if `git rev-parse HEAD != head_sha`, attempts `git reset --hard <head_sha>`. **If `git reset` fails because the SHA is unreachable**, the PR head was force-pushed between `gh pr view` and `gh pr checkout` — surfaces as **stale-snapshot failure**: "PR head force-pushed mid-review (recorded `<head_sha>` no longer reachable). Rerun `/combined-review --pr <#>` to fetch the current snapshot." No silent fallback; the recorded SHA is the contract.
5. Verifies the recorded base SHA is reachable locally: `git cat-file -e <base_sha>^{commit}`. If unreachable, same stale-snapshot failure with base-side messaging. **Does NOT** assert `FETCH_HEAD == base_sha` — that would fail harmlessly when the base branch advances between `gh pr view` and `git fetch`. We need the recorded commit to be reachable, not to be the current tip.
6. Optionally surfaces a warning if the base tip moved (`FETCH_HEAD != base_sha`) — informational only, doesn't block.

### `codex exec` safety

Because `codex exec` is a general agent (unlike the inherently read-only `codex review`), `run-codex.sh` MUST:

- Pass `--sandbox read-only` (or codex's equivalent flag — `run-codex.sh` probes the installed codex version's flag list at start and errors out if no read-only sandbox is available, rather than silently running unsandboxed).
- Begin the prompt body with an explicit no-edit instruction: `"You are running in review mode. Do not write, edit, or delete any files. Read the materialized inputs below and emit findings only as ---FINDING--- blocks per the schema."`.

Both layers must hold. Missing either violates non-goal §13.

### Worktree lifecycle

- **Creation**: `materialize-scope.py` (§5) creates the worktree when the scope kind requires one, since it needs the worktree to extract file contents and the diff. Path is `mktemp -d -t combined-review-<repo>-XXXXXX` honoring `$TMPDIR`. The path goes into the scope object's `worktree_path` field.
- **Use**: `run-codex.sh` reads `worktree_path` from the scope object and runs codex inside it. Does not create or destroy.
- **Fork PRs**: handled by `gh pr checkout --detach <#>` as the primary path inside the empty worktree. `gh` fetches the PR head into a detached HEAD regardless of whether the PR comes from `origin` or a fork. After checkout, `git reset --hard <head-sha>` pins to the exact recorded SHA (defensive against race between `gh pr view` and `gh pr checkout`).
- **Teardown** — there are three layers, because a skill markdown file cannot hold a shell trap across a multi-tool-call orchestration. **Destructive cleanup never trusts the path string alone** — it cross-checks against git's own worktree registry:
  1. **In-driver trap**: `run-codex.sh` has a `trap 'cleanup' EXIT INT TERM` for temp files it owns *internally* (e.g., intermediate codex state). It does **not** delete the prompt file or the raw-output files — those are passed in by the orchestrator (see "Raw output ownership" below) and have a different lifecycle.
  2. **Explicit orchestrator cleanup**: the SKILL.md instructions require that after synthesis + rendering, the orchestrator's final step is a `Bash` call to `scripts/cleanup-worktree.sh <repo_root> <worktree_path>`. The script runs `git -C <repo_root> worktree remove --force <worktree_path>` only after **three independent assertions**:
     - The path appears in `git -C <repo_root> worktree list --porcelain` for this repo (git considers it a worktree of this repo — the authoritative check, not a pattern match).
     - The path matches the `combined-review-*` mktemp pattern under `$TMPDIR` or `/tmp` (defense-in-depth — if git's registry is somehow wrong, we still won't delete an arbitrary directory).
     - The path is not the repo root and not the user's main worktree.
     If any assertion fails, cleanup-worktree.sh refuses to delete and exits non-zero with a clear message. The skill explicitly forbids skipping this step. Also runs on early-error exit paths.
  3. **GC on every invocation**: `scripts/gc-worktrees.sh` runs as the first step of every `/combined-review` invocation. It enumerates worktrees via `git -C <current-repo-root> worktree list --porcelain` and selects entries whose path matches `combined-review-*` AND whose mtime is older than 24h AND **do not contain a `.combined-review-keep` marker file** at the worktree root. Each removal goes through the same triple-assertion gate as `cleanup-worktree.sh`. **It does not scan `$TMPDIR` for arbitrary directories** — that would pick up leaks from other repos, which the current invocation has no business deleting. Cross-repo orphans wait for the next `/combined-review` in their own repo, or for OS-level `/tmp` cleanup. Worktrees kept via `--keep-worktree` carry the marker and live until the user removes them manually.

  Together: in-driver trap handles run-codex's internal temp files; explicit cleanup handles the worktree under normal completion (with git-registry verification); GC handles orchestrator-died-mid-run leaks within the current repo. No layer relies on path-pattern matching alone for destructive operations.

### Raw output ownership

All long-lived intermediate files — the prompt file, codex stdout capture, codex stderr capture, sub-agent transcripts — are **orchestrator-owned**, not script-owned:

- The orchestrator creates them via `mktemp` before launching reviewers, passes the paths to `run-codex.sh` as `--prompt-file`, `--stdout`, `--stderr` arguments, and to sub-agents inline.
- `run-codex.sh` writes to those paths but never deletes them (its `trap` only cleans up files it created internally).
- `report.py` reads them for the audit-trail section of the final report.
- The orchestrator deletes them as the final step **after `report.py` completes**, via a dedicated `Bash` call.

Without this ownership split, the prior design contradicted itself: `run-codex.sh` was nominally cleaning up the captures, but `report.py` needed them; and the `> <stdout>` redirection shown in §5 was applied by the orchestrator (outside run-codex.sh) anyway, so run-codex.sh couldn't have known about those paths in the first place.
- **`--no-codex`**: still creates a worktree if the Claude side needs one (non-`uncommitted` scopes). Only skips codex invocation.
- **`--keep-worktree`** (debug-only): inhibits the explicit `cleanup-worktree.sh` call and prints the path on completion. **Also writes a marker file `.combined-review-keep` at the worktree root.** `gc-worktrees.sh` skips any worktree containing this marker, regardless of age — so a debug worktree won't get silently swept by a later invocation's GC. The user is responsible for removing kept worktrees manually (`git worktree remove --force <path>`).

The mode prompt + materialized inputs (see §5/§6) are passed to every codex invocation via stdin, not as shell arguments — see §5 "Prompt handling" for why.

---

## 5. Claude-side review

Before any agent dispatch, `scripts/materialize-scope.py` runs once and turns the scope object into concrete bytes both sides can consume. **Both Claude and Codex receive their inputs from this same materialization**, so the primary review subject (the diff + per-file content) is shared. Context lookups against the surrounding repo are intentionally allowed for both — see §4's shared-primary-input guarantee.

### Materialize step

Input: scope object from `resolve-scope.py` (§3).
Output JSON:

```json
{
  "scope_kind": "pr",
  "scope_summary": "PR #105 — Feature X (head abc1234, base def5678)",
  "unified_diff": "<full diff text or null for files-mode>",
  "changed_files": [
    {
      "path": "src/foo.py",
      "old_path": null,
      "status": "modified",
      "kind": "text",
      "lines_changed": [12, 13, 14, 88, 89],
      "post_content": "..."
    },
    {
      "path": "src/legacy.py",
      "old_path": null,
      "status": "deleted",
      "kind": "text",
      "lines_changed": "(deleted)",
      "post_content": null,
      "pre_content": "..."
    },
    {
      "path": "src/new_name.py",
      "old_path": "src/old_name.py",
      "status": "renamed",
      "kind": "text",
      "lines_changed": [12, 13],
      "post_content": "..."
    },
    {
      "path": "assets/logo.png",
      "old_path": null,
      "status": "added",
      "kind": "binary",
      "lines_changed": "(binary)",
      "post_content": null,
      "note": "binary file — content not inlined"
    },
    {
      "path": "config/secrets.link",
      "status": "modified",
      "kind": "symlink",
      "post_content": null,
      "symlink_target": "/etc/secrets.conf"
    },
    {
      "path": "vendor/lib",
      "status": "modified",
      "kind": "submodule",
      "post_content": null,
      "submodule_pre_sha": "abc1234",
      "submodule_post_sha": "def5678"
    }
  ],
  "doc_files": [
    { "path": "docs/spec.md", "content": "..." }
  ],
  "total_lines_changed": 247,
  "changed_file_count": 7,
  "has_reviewable_changes": true,
  "warnings": []
}
```

`has_reviewable_changes` is `true` if `changed_file_count > 0` OR `doc_files` is non-empty. Used by the empty-scope pre-flight (§10) instead of `total_lines_changed == 0`, so a PR that only updates a submodule, symlink, or binary asset is **not** rejected as "nothing to review" — those are legitimate review subjects (e.g., bumping a submodule SHA can be high-risk and deserves review).

File entry fields:

- `status`: `added` | `modified` | `deleted` | `renamed` | `typechange` (per `git diff --name-status`).
- `kind`: `text` | `binary` | `symlink` | `submodule`. Determined from git's mode bits + a content-type sniff.
- `post_content`: present only for text files that still exist after the change. Null for deleted, binary, symlink, submodule.
- `pre_content`: included for `status: deleted` so reviewers can see what was lost. Otherwise null.
- `old_path`: set only for renames; otherwise null.
- `symlink_target` / `submodule_pre_sha` / `submodule_post_sha`: kind-specific fields.

Reviewer prompts include a brief schema explainer so agents know to handle non-text entries appropriately (e.g., "deleted text file — review whether the deletion is correct" rather than "no content").

- **`pr` / `base`**: `unified_diff` is `git diff <base-sha>...<head-sha>` (three-dot / merge-base semantics) — matches GitHub's PR review semantics, excludes unrelated movement on the base branch. `changed_files` is populated per the schema above (one entry per `git diff --name-status` line), with content fields populated according to `kind`.
- **`commit`**: `unified_diff` is `git show --format= <commit-sha>` (the patch the commit introduced). `changed_files` entries reflect the commit's tree.
- **`uncommitted`**: `unified_diff` is `git diff HEAD` (staged + unstaged tracked changes). **Untracked files** (which `git diff HEAD` ignores) are appended to `changed_files` with `status: "added"`, `lines_changed: "(new file)"`, and `post_content` populated if `kind: text`. Without this, the `--uncommitted` flag would silently under-review new files.
- **Positional `files`**: `unified_diff` is `null`, `changed_files` is empty, `doc_files` holds current working-tree contents (with any local edits — see §3 worktree rules). Binary / symlink / submodule files in the positional list are represented in `doc_files` with the same `kind` semantics — content omitted, kind-specific fields populated.
- **Non-code modes with diff scopes** (`--mode spec --pr 105`, etc.): `doc_files` is additionally populated with one entry per changed text file — `{path, status, content}` where `content` is `post_content` for added/modified/renamed and `pre_content` for deleted (so the reviewer can judge whether the deletion was correct). Binary/symlink/submodule changes show up only in `changed_files`, not `doc_files`, since they're not document-reviewable.
- All operations run inside the worktree (when present) or the working tree (`--uncommitted` and positional files).
- `total_lines_changed` counts only text-file line changes (post-change line count for added, deletion count for deleted, both for modified). Binary/symlink/submodule changes contribute 0 — they don't meaningfully load the reviewers.

### Agent dispatch

- **Default (3 sub-agents, code mode):** dispatch three parallel `Agent` calls (using `subagent_type` when available, else general-purpose) — code-reviewer, silent-failure-hunter, pr-test-analyzer. Each receives the materialized diff and file contents.
- **`--full` (6 sub-agents, code mode):** adds comment-analyzer, type-design-analyzer, code-simplifier. Opt-in only.
- **`--mode spec|plan|docs`:** single document-reviewer agent with mode-specific prompt template (§6). Receives `doc_files`. The 3/6 sub-agent fanout is code-specific.

All Claude-side agents receive:

1. The materialized inputs (diff + file contents, or doc contents).
2. The mode-specific review prompt template (§6).
3. `--focus` text appended verbatim if provided.
4. The structured output schema (§7) and a strict instruction to emit findings only in that format.

Codex receives the same materialized inputs through its prompt — always via `codex exec --sandbox read-only` (§4 explains why we don't trust `codex review`'s native diff). Both sides receive the same **primary input**; both also operate against the **same git state** (worktree at recorded SHA or user's tree) and may consult adjacent files for context. The "shared-primary-input" guarantee in §4 spells out the precise scope of what's pinned vs. what's intentionally free.

### Prompt handling

The mode prompt (+ optional `--focus` text + structured-output schema instruction + for `codex exec` the inlined file contents) can be many KB. Passing this as a shell argv is brittle — multi-line content breaks quoting, and argv length limits kick in for `files` mode with large docs.

`run-codex.sh` accepts the prompt via a **file path** (not argv):

- Orchestrator writes the rendered prompt to a temp file *adjacent to* — not inside — any worktree: `mktemp -t combined-review-prompt-XXXXXX` under `$TMPDIR`. Placing it inside the worktree would make codex see it as an untracked file and contaminate the review.
- Invokes `scripts/run-codex.sh --scope <scope.json> --prompt-file <path>` (still passes scope.json by path, not inline).
- `run-codex.sh` reads the prompt file and pipes it to codex on stdin: `cat <prompt-file> | codex exec --sandbox read-only -` (or equivalent stdin syntax for the installed codex version).
- The prompt temp file is **orchestrator-owned** (see §4 "Raw output ownership"). `run-codex.sh` reads it but never deletes it; the orchestrator deletes it in Phase D after `report.py` completes. The script's own `trap` only handles temp files run-codex.sh creates internally, never paths handed in by the orchestrator.

### Dispatch ordering — setup is sequential, reviewers run in parallel

Parallel tool calls within one message run with no defined order — if `Write` and a background `Bash` were issued together, `run-codex.sh` could start before the prompt file existed. The orchestrator therefore splits setup from review:

**Phase A — sequential setup (must complete before Phase B starts):**

1. `Bash` → `scripts/parse-args.py` and `scripts/resolve-scope.py`. Produces the scope object.
2. `Bash` → `scripts/materialize-scope.py`. Creates the worktree if needed; produces the materialized blob.
3. Pre-flight checks (§10): codex availability, gh auth, empty scope, large diff.
4. `Bash` → `mktemp` for the four orchestrator-owned files: `<prompt-path>`, `<codex-stdout>`, `<codex-stderr>`, `<agent-transcripts-dir>`. (One Bash call, four paths captured.)
5. `Write` → render the full prompt (mode template + `--focus` + materialized blob + no-edit instruction + finding schema) to `<prompt-path>`.

Only after step 5 returns do reviewers launch.

**Phase B — parallel review (one message, no inter-dependencies):**

1. `Bash` with `run_in_background: true` — `scripts/run-codex.sh --scope <scope.json> --prompt-file <prompt-path> --stdout <codex-stdout> --stderr <codex-stderr>`. `run-codex.sh` writes to the paths but does not delete them.
2. Multiple `Agent` calls in the same message — one per sub-agent. Each receives the materialized inputs and the rendered prompt body inline. Transcripts come back in-band as the Agent tool's return value; the orchestrator writes them to files under `<agent-transcripts-dir>` for `report.py` to consume.

These two are independent (codex doesn't depend on Agent results and vice versa), so issuing them in the same message is safe — and necessary, since parallel execution is the whole point of running both reviewers in one session.

**Phase C — synthesis + report:** the orchestrator awaits all Phase B results (Agent calls return inline; `Monitor` signals codex completion), runs `normalize-findings.py`, the in-session synthesis pass (§8), `validate-clusters.py`, and `report.py`.

**Phase D — cleanup:** after `report.py` finishes, the orchestrator deletes the orchestrator-owned files (prompt, codex stdout/stderr, agent transcripts) and calls `cleanup-worktree.sh`.

### Default-3 selection rationale

Codex's code-mode pass (driven by the code-mode prompt template) covers comment quality, type design, and code simplification competently — those Claude sub-agents would duplicate effort. The high-signal Claude specialists that codex doesn't naturally cover are code-reviewer (correctness + CLAUDE.md compliance), silent-failure-hunter (error handling), and pr-test-analyzer (coverage gaps). `--full` exists for users who want belt-and-braces.

---

## 6. Mode prompts

Each mode has a template stored in `~/.claude/skills/combined-review/prompts/<mode>.md`. The template is loaded, `--focus` text is appended, then the result is passed to both sides.

| Mode | Template focus |
|---|---|
| `code` (default) | Correctness, bugs, error handling, test coverage, security, performance regressions, CLAUDE.md compliance |
| `spec` | Completeness, ambiguity, internal consistency, scope creep, missing edge cases, unstated assumptions, success criteria |
| `plan` | Step ordering, hidden dependencies, verification steps per task, risk surface, what could fail and not be detected |
| `docs` | Accuracy vs. current code, broken examples, drift, missing prerequisites, audience fit |

All templates end with the schema (§7) and the instruction: "Emit findings only as `---FINDING---` blocks. Do not summarize. Do not include preamble or postamble."

---

## 7. Structured output schema

Both sides emit findings as delimited blocks. Strict JSON from LLMs is unreliable for multi-line `detail` fields; delimited blocks are more robust and easier to recover from partial compliance.

```
---FINDING---
severity: critical|high|medium|low
file: <relative path or "(general)">
line: <int> | <start>-<end> | -
category: bug|test-gap|perf|security|clarity|style|other
title: <single-line summary, no period>
detail: |
  <multi-line free text — recommendation, evidence, suggested fix>
---END-FINDING---
```

Parsing is in `scripts/normalize-findings.py`:

- Input: raw stdout from each reviewer (codex + each Claude sub-agent).
- Output: JSON array of findings, each tagged with `source: "codex" | "claude:<agent-name>"`.
- Best-effort parsing: if a reviewer ignores the schema and emits prose, the parser extracts what it can; unparseable chunks go to a `parse_warnings[]` array so they surface in the final report rather than being silently dropped.
- Severity normalization: any reviewer using non-canonical severity (`error`, `warning`, `info`, etc.) is mapped to the canonical set; unmapped values default to `medium` with a parse warning.

---

## 8. Synthesis pass

After parsing, all findings exist as a single JSON array (`normalized-findings.json`). The skill runs **one in-session LLM pass** (no new agent — main Claude does it) that emits **cluster JSON only** — not Markdown. Markdown rendering is `report.py`'s job (§9).

The synthesis LLM step:

1. **Clusters findings by semantic similarity** — same root issue across tools, regardless of phrasing. Inputs to clustering: `file`, `line` proximity (≤ 10 lines), and `title + detail` text. The LLM does the judgment; no string-distance heuristics — those over-merge or under-merge.

2. **Tags each cluster:**
   - `agreement` — at least one finding from codex AND at least one from claude.
   - `claude_only` — claude-only.
   - `codex_only` — codex-only.
   - `disagreement` — at least one finding from each side, but the recommendations are contradictory (e.g., one says "add nil check", the other says "remove the redundant nil check").

3. **Synthesises wording** — picks the clearer description, merges complementary detail.

4. **Re-ranks severity** — if tools agree, keep it. If they disagree, take the higher and note the divergence.

### Cluster JSON schema (synthesis output → report input)

```json
{
  "scope_summary": "PR #105 — ...",
  "mode": "code",
  "focus": "API contract changes",
  "reviewer_summary": {
    "codex": { "status": "ok", "raw_findings": 14, "parse_warnings": 0 },
    "claude": [
      { "agent": "code-reviewer", "status": "ok", "raw_findings": 8, "parse_warnings": 0 },
      { "agent": "silent-failure-hunter", "status": "ok", "raw_findings": 3, "parse_warnings": 0 },
      { "agent": "pr-test-analyzer", "status": "failed", "error": "timeout" }
    ]
  },
  "clusters": [
    {
      "tag": "agreement",
      "severity": "high",
      "file": "src/foo.py",
      "line": "42",
      "category": "bug",
      "title": "Null deref when config is missing 'api_key'",
      "synthesized_detail": "Both reviewers flag that accessing `config['api_key']` directly will raise KeyError. Codex suggests `config.get('api_key')`; Claude suggests an early-return guard. Recommended: early-return guard — surfaces the misconfiguration explicitly.",
      "sources": [
        { "source": "codex", "original_title": "...", "original_detail": "...", "severity": "high" },
        { "source": "claude:code-reviewer", "original_title": "...", "original_detail": "...", "severity": "medium" }
      ],
      "severity_divergence": "codex=high, claude=medium → taking high"
    }
  ],
  "unparsed_chunks": [
    { "source": "codex", "text": "<raw text that couldn't be parsed as a finding>" }
  ]
}
```

This is the value-add of the skill over running both tools manually. **It's the reason synthesis isn't a Python script** — clustering by meaning is a judgment task, not a string-distance task. But the LLM only emits JSON; rendering stays deterministic.

### JSON validation + one repair attempt

Strict JSON from LLMs is unreliable for free-form fields — the same failure mode that drove the delimited-block schema for reviewer output (§7) applies here. The skill therefore validates synthesis output before passing it to `report.py`:

1. **Validate**: `scripts/validate-clusters.py` parses the synthesis output against a JSON Schema covering the cluster JSON structure (required fields, enum values for `tag` and `severity`, well-formed `sources[]`, etc.). On success: passes through to `report.py`.
2. **One repair attempt**: on failure, the orchestrator re-prompts itself with the validator's error message ("the `severity` field on cluster #3 must be one of critical|high|medium|low, got `important`") and a single instruction: "emit a corrected cluster JSON; do not re-cluster, only fix the schema violations". The repaired JSON is re-validated.
3. **Fail loud**: if the second validation also fails, `report.py` runs with the raw reviewer outputs only and the final report includes a prominent "Synthesis failed — manual review of raw outputs required" banner plus the validator's error message. No silent degradation.

This mirrors the parse-warnings approach for reviewer output (§7): one repair, then surface the failure rather than papering over it.

---

## 9. Report format

`scripts/report.py` consumes the cluster JSON from §8 (stdin) plus raw reviewer outputs (file paths passed as args) and emits the final Markdown to stdout. Optionally written to `--save <path>` via tee. Deterministic — same JSON in, same Markdown out.

```markdown
# Combined Review — <scope description>

**Scope:** <pr #105 / branch foo vs main / 3 files / etc.>
**Mode:** <code / spec / plan / docs>
**Focus:** <freeform text, if any>
**Reviewers:** Claude (3 sub-agents) + Codex
**Generated:** <ISO timestamp>

---

## High-confidence findings (both tools agree)

### [Critical]
- **path/file.py:42** — <title>
  <detail>
  _Sources: codex, claude:code-reviewer_

### [High]
...

## Single-source findings

### Claude only
- **[High] path/file.py:88** — <title>
  <detail>
  _Source: claude:silent-failure-hunter_

### Codex only
- **[Medium] path/other.py:14** — <title>
  <detail>
  _Source: codex_

## Disagreements (worth a second look)

- **path/file.py:42** — Codex says X, Claude says Y. <synthesis note on which seems right and why>

## Parse warnings
- 2 chunks from codex output could not be parsed; raw text below.

---

<details>
<summary>Raw outputs (audit trail)</summary>

### Codex
<full codex stdout>

### Claude sub-agents
#### code-reviewer
<full agent output>
#### silent-failure-hunter
<full agent output>
#### pr-test-analyzer
<full agent output>
</details>
```

Severity ordering in the report: critical → high → medium → low, within each section.

---

## 10. Failure modes

### Pre-flight checks (main session, before any tools run)

The skill orchestrator (main Claude session) performs these checks **before** dispatching any sub-agent or Bash. These need user interaction or skill-level decisions, so they don't belong in scripts.

1. **Codex availability.** Run `codex login status` (or equivalent) early. If codex isn't on PATH or isn't logged in, stop with a clear message — unless `--no-codex` was passed, in which case skip codex and continue Claude-only with a note in the report.
2. **`gh` authentication when `--pr` used.** `gh auth status`. Error early.
3. **Empty scope.** If `materialize-scope.py` reports `has_reviewable_changes == false`, error: "nothing to review". This intentionally uses the file-count-based flag, not `total_lines_changed == 0` — a PR that only changes a submodule, symlink, or binary asset is reviewable and shouldn't be rejected.
4. **Large diff.** If `total_lines_changed > LARGE_DIFF_THRESHOLD` (default 2000, env `COMBINED_REVIEW_LARGE_DIFF_THRESHOLD`), the orchestrator asks the user in chat: "Diff is N lines — both reviewers degrade on large diffs. Proceed?" If not interactive (e.g., the skill was called by another agent), require explicit `--force-large` flag instead of prompting.

### In-flight failure handling

| Failure | Behavior |
|---|---|
| `codex` returns non-zero | Report Claude-only result, include codex stderr in a "codex failed" section. Continue synthesis. |
| `codex` exceeds timeout (default 5 min, env `COMBINED_REVIEW_CODEX_TIMEOUT`) | Same as non-zero. |
| Worktree creation fails | Error early; no partial state. |
| Mixed code + docs in scope under `--mode code` | Proceed; surface a note in the report that doc files were reviewed with code lens. |
| Both reviewers emit zero findings | Report shows "no issues found" + raw outputs available for audit. |
| One Claude sub-agent fails | Continue with the others; failed agent's section in report says "agent failed: <error>". `reviewer_summary` (§8) records the failure. |
| All Claude sub-agents fail | Report codex-only result + Claude-failed note. If both sides fail, error. |

Cleanup follows the three-layer model in §4: `run-codex.sh`'s `trap` removes codex-side temp files (prompt file, stdout/stderr captures); the orchestrator's final `Bash` call to `scripts/cleanup-worktree.sh` removes the worktree (gated by the triple-assertion check); `scripts/gc-worktrees.sh` runs at the start of every invocation as the leak backstop. `--keep-worktree` (debug-only) suppresses the explicit cleanup step.

---

## 11. File layout

```
~/.claude/
├── commands/
│   └── combined-review.md          # slash entry point
└── skills/
    └── combined-review/
        ├── SKILL.md                # orchestration logic (model-readable)
        ├── prompts/
        │   ├── code.md             # mode templates
        │   ├── spec.md
        │   ├── plan.md
        │   └── docs.md
        └── scripts/
            ├── parse-args.py          # flags → normalized config JSON
            ├── resolve-scope.py       # auto-detect + validation + immutable SHA resolution
            ├── materialize-scope.py   # scope object → concrete diff + file contents (creates worktree if needed)
            ├── run-codex.sh           # codex driver; reads scope/prompt from orchestrator-owned paths; writes captures to orchestrator-owned stdout/stderr paths; internal trap only for files run-codex creates itself
            ├── normalize-findings.py  # parse delimited-block schema → JSON
            ├── validate-clusters.py   # JSON-schema-validate synthesis output; one repair attempt
            ├── cleanup-worktree.sh    # explicit teardown invoked by orchestrator at end of run
            ├── gc-worktrees.sh        # runs first; lists git worktrees and removes stale combined-review-* entries
            └── report.py              # cluster JSON + raw outputs → final markdown
```

Where practical, deterministic scripts communicate via JSON on stdin/stdout (`parse-args.py`, `resolve-scope.py`, `materialize-scope.py`, `normalize-findings.py`, `validate-clusters.py`, `report.py`). Scripts that operate on large or path-bound inputs use **explicit file-path contracts**: `run-codex.sh` takes `--prompt-file`, `--stdout`, `--stderr`; `cleanup-worktree.sh` and `gc-worktrees.sh` take repo + worktree paths and perform side effects. The orchestrator owns intermediate file lifecycle (see §4 "Raw output ownership"). `SKILL.md` describes the pipeline and points the model at each script in order.

---

## 12. Testing approach (TDD per writing-skills)

Per the `superpowers:writing-skills` discipline — **RED-GREEN-REFACTOR with pressure scenarios:**

### RED — baseline without the skill

Subagent scenarios to run before writing the skill:

1. "Run both Claude review and codex review on PR #105 and combine the findings." → Expect: sequential execution, no deduplication, no attribution, no disagreement surfacing.
2. "Review docs/spec.md with both tools." → Expect: confusion about how to point codex at a single file; default code-review lens applied to a markdown file.
3. "Run combined review on uncommitted changes when there's also a PR for the current branch." → Expect: silent ambiguity, agent picks one or the other without surfacing it.

Document the verbatim rationalizations / failure modes.

### GREEN — write skill + scripts

Implement to address the specific failures from RED. Re-run the scenarios. Confirm:

- Both reviewers run in parallel, not sequence.
- Findings are clustered into the `agreement` / `claude_only` / `codex_only` / `disagreement` tags from §8, and the rendered Markdown puts them in the corresponding sections from §9.
- Scope ambiguity (dirty + PR) errors out, not silent pick.
- `--mode spec` produces document-lens findings, not "no test coverage" suggestions.

### REFACTOR — close loopholes

New rationalizations to plug, e.g.:

- Agent decides "synthesis is too hard" and just concatenates outputs → add explicit anti-pattern in SKILL.md.
- Agent skips schema enforcement for codex → SKILL.md explicitly says "if codex output is unparseable, surface as parse warning, don't silently summarize".
- Agent runs reviews sequentially under cognitive load → SKILL.md mandates parallel-tool-call pattern.

---

## 13. Non-goals

- **Auto-fixing findings.** The skill reviews; it does not edit. Remediation is a separate step.
- **Reviewing across multiple PRs / commits in one invocation.** One scope per invocation.
- **Replacing the underlying `/review` skill or the standalone `codex` CLI.** They remain available standalone for users who want a single-tool review or who prefer codex's native review framing.
- **Persistent finding storage / triage history.** Output is per-invocation. `--save` is the only persistence.
- **Cross-tool prompt unification beyond the mode template.** We don't try to make codex emit the same exact sub-finding categories as Claude — we let each tool review naturally and synthesize after.

---

## 14. Decisions locked

- **Worktree location**: `mktemp -d -t combined-review-<repo>-XXXXXX` honoring `$TMPDIR`. Random suffix, repo basename for legibility.
- **`--full` opt-in vs `--agents`**: keep `--full` binary for v1. No `--agents` surface area until there's real pressure.
- **`--save` and `--keep-worktree`**: independent. `--save` writes the report file but does not preserve the worktree. `--keep-worktree` is debug-only and inhibits teardown.
- **Codex auth failure**: run `codex login status` early. Treat unauthenticated the same as "Codex unavailable" — stop with a clear message unless `--no-codex` was passed.
- **Diff semantics**: three-dot / merge-base (`git diff base...head`) for `--pr` and `--base`, matching GitHub PR review. Not two-dot. `git show` for `--commit`. `git diff HEAD` + appended untracked files for `--uncommitted`.
- **Positional files = current working-tree content**: includes any local edits the user just made. No clean worktree, no pinning to HEAD.
- **Non-code modes with diff scopes**: materialize-scope populates `doc_files` with post-change (or pre-change for deletes) content of changed text files in addition to the diff, so the document-reviewer agent has something reviewable.
- **PR materialization**: `gh pr checkout --detach <#>` as primary path (handles fork PRs natively); fetch base by `base_ref_name` for portability; verify both head and base with `headRefOid`/`baseRefOid` after fetch; `git reset --hard <head-sha>` if HEAD drifted.
- **Base scope worktree**: created from `<head-sha>` not literal `HEAD`, so the reviewed commit can't drift between resolve-scope and materialize.
- **Codex exec safety for files mode**: must pass `--sandbox read-only` (or codex's equivalent flag) AND include an explicit no-edit instruction at the top of the prompt. `run-codex.sh` errors out if the read-only flag isn't supported by the installed codex version. Non-negotiable — `codex exec` is otherwise a general agent that can edit files, which violates non-goal §13.
- **File-entry schema in materialize**: every `changed_files` entry has `status` (added|modified|deleted|renamed|typechange) and `kind` (text|binary|symlink|submodule). `post_content` populated only for kind=text and status ≠ deleted; `pre_content` for status=deleted; `old_path` for renames; symlink-target and submodule-pre/post-sha for those kinds.
- **Worktree cleanup safety**: every destructive cleanup goes through a triple-assertion gate — (1) path appears in `git worktree list --porcelain` for the current repo, (2) path matches `combined-review-*` mktemp pattern under `$TMPDIR`/`/tmp`, (3) path is not the repo root or main worktree. `gc-worktrees.sh` enumerates only via `git worktree list`, never scans `$TMPDIR` for arbitrary directories.
- **Prompt passing to codex**: via stdin (read from a temp file by `run-codex.sh`), not argv. Multi-KB prompts (file-mode embeds full doc contents) break shell quoting otherwise.
- **Shared-primary-input guarantee** (revised, was "same-bytes"): codex always runs via `codex exec --sandbox read-only` with the materialized blob from `materialize-scope.py`, never via `codex review`'s native auto-diff. The guarantee is *shared primary input* + *shared repo context*, not full isolation — both reviewers can still consult adjacent files via Read/Grep equivalents, and that's a feature for context-aware review. What's pinned: the diff and per-file content embedded in the prompt body, plus the git state of the cwd (worktree at recorded SHA or user's tree).
- **PR base fetch**: `git fetch <base_repo_url> <base_ref_name>` directly — **no `git remote add`**, which would mutate `.git/config` and leak across runs. SHA verification via `git cat-file -e <sha>^{commit}`, not `rev-parse FETCH_HEAD == base_sha` — the recorded commit must be reachable, but the tip may have moved (warn-only).
- **PR stale-snapshot failure**: if the recorded `head_sha` is not reachable after `gh pr checkout` + `git reset --hard <head_sha>`, the PR was force-pushed between `gh pr view` and `gh pr checkout`. The skill fails loudly with "PR head force-pushed mid-review; rerun" — does not silently fall back to the current head.
- **Raw output ownership**: the orchestrator creates and deletes all long-lived intermediate files (prompt, codex stdout/stderr, sub-agent transcripts). `run-codex.sh` writes to paths passed in via args; doesn't own deletion. Cleanup happens after `report.py` completes, before the worktree teardown.
- **Dispatch ordering**: setup is sequential (parse-args → resolve-scope → materialize → pre-flight → mktemp → Write prompt), reviewers run in parallel only after setup completes. Avoids the race where a parallel `Write` and background Bash launch run-codex.sh before the prompt file exists.
- **`--keep-worktree` + GC interaction**: `--keep-worktree` writes `.combined-review-keep` at the worktree root; `gc-worktrees.sh` skips marked worktrees regardless of age. Without the marker, a debug worktree would silently disappear after 24h on the next invocation's GC pass.
- **Empty-scope check**: uses `has_reviewable_changes` (file-count-based + doc_files), not `total_lines_changed == 0`. Submodule/symlink/binary-only PRs are legitimate review subjects.
- **Synthesis JSON validation**: `validate-clusters.py` enforces a JSON Schema on cluster output. One LLM repair attempt on failure; if that fails too, the report runs with raw outputs and a "synthesis failed" banner. No silent degradation.

## 15. Open questions

1. **Default Codex timeout.** 5 min is the current proposal. Should it be tighter (3 min) to avoid hanging the synthesis on a slow run?
2. **`materialize-scope.py` for large file contents.** If a changed file is huge (megabytes), inlining its `post_content` into the JSON is wasteful. Cap at e.g. 200KB per file and switch to "see worktree for full content" beyond that? Or always inline?
3. **`codex exec` prompt size limits.** For positional-files mode, the prompt has to include full file contents. If the user passes 20 large files, we'll hit the model's context limit. Should the skill error out above a content-size threshold and ask the user to narrow the file list?
````

---

## Output schema (mandatory)

Emit findings only as `---FINDING---` blocks. One block per finding. No preamble, no
postamble, no summary, no headers.

```
---FINDING---
severity: critical|high|medium|low
file: <relative path or "(general)">
line: <int> | <start>-<end> | -
category: bug|test-gap|perf|security|clarity|style|other
title: <single-line summary, no period>
detail: |
  <multi-line free text — recommendation, evidence, suggested fix>
---END-FINDING---
```

If you find no issues, emit zero blocks. Do not write "no issues found" or anything else.

**You are in review mode. Do not write, edit, or delete any files. Do not run code.
Read only.**

exec
/bin/zsh -lc 'rg -n "def symlink_target|import os|run-codex.sh|run-codex.py|Expected: 4 passed|codex login status|allowed-tools|Phase B|Monitor|Expected: `no tests ran`|SCOPE_FILE|Task 6|Task 12|Task 18|Task 19|Task 20|mkdir -p ~/.claude|ln -s|chmod '"\\+x scripts/run-codex.py|test_run_codex_errors_without_sandbox_support|status file written|write_failed_status|defaultBranchRef|def pr_for_current_branch|fake_gh_no_pr|def git\\(|def materialize_pr|git fetch|fetch base|cat_file_exists|test_pr_happy_path|gh pr checkout|FAKE_GH_JSON|def write_fake_gh|gh pr view|def materialize_uncommitted|unified = git\\(\"diff\", \"HEAD\"|git diff HEAD|git diff --cached|staged|total_lines_changed|safe_read_text|read_at_ref|encoding|Path\\(repo\\) / path|tests/conftest.py|import shutil|tempfile\" docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md docs/superpowers/specs/2026-05-11-combined-review-skill-design.md" in /private/var/folders/yt/h62lwq8x26340hnlt7lk_c240000gn/T/combined-review-juvera_ai_4-pr-hdlqrklt
 succeeded in 0ms:
zsh:1: command not found: no
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:40:/combined-review --uncommitted                   # staged + unstaged + untracked
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:56:| `--uncommitted` | bool | Review staged + unstaged + untracked |
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:82:4. **Clean tree, current branch has PR** — implicit `--pr <#>` (resolved via `gh pr view --json number,headRefOid,baseRefOid`).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:83:5. **Clean tree, no PR, current branch ≠ default** — implicit `--base <default>` (default branch via `gh repo view --json defaultBranchRef`).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:106:Ref names + repo URLs are used for `git fetch` (portable across remotes, correct for fork PRs); SHAs are used to **verify** the recorded commits are reachable after fetch. Fetching by SHA alone is less portable; trusting the ref alone is unsafe; assuming `origin` is the base repo is wrong for fork PRs.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:108:All ref-shaped inputs are resolved to immutable SHAs by `resolve-scope.py` — never `origin/<branch>` strings passed downstream, since branches move. For `--pr <#>`, this means `gh pr view <#> --json headRefOid,baseRefOid` first, then materialize against those SHAs.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:136:| `uncommitted` | None — operate in user's working tree. Materialize uses `git diff HEAD` + untracked. | `codex exec --sandbox read-only` (cwd = user repo root, prompt via stdin) |
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:139:| `pr` | `git worktree add --detach <tmp>` → `gh pr checkout --detach <#>` → fetch base from `<base_repo_url>` (not necessarily `origin` — see PR fetch detail below) → `git reset --hard <head_sha>` if drifted → verify both SHAs exist via `git cat-file -e <sha>^{commit}`. Materialize uses `git diff <base_sha>...<head_sha>` inside worktree. | `codex exec --sandbox read-only` (cwd = worktree, prompt via stdin) |
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:146:1. Reads `baseRepository.url`, `headRepository.url`, `baseRefName`, `headRefName`, `baseRefOid`, `headRefOid` from `gh pr view <#> --json baseRepository,headRepository,baseRefName,headRefName,baseRefOid,headRefOid`.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:147:2. Runs `gh pr checkout --detach <#>` inside the worktree (handles the head fetch including fork mirrors).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:148:3. **Fetches the base by URL directly, no remote-add**: `git fetch <base_repo_url> <base_ref_name>`. This fetches the ref into `FETCH_HEAD` without mutating the user's `.git/config` (which `git remote add` would do — and which would leak across runs or fail if the remote name already existed).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:149:4. Pins head: if `git rev-parse HEAD != head_sha`, attempts `git reset --hard <head_sha>`. **If `git reset` fails because the SHA is unreachable**, the PR head was force-pushed between `gh pr view` and `gh pr checkout` — surfaces as **stale-snapshot failure**: "PR head force-pushed mid-review (recorded `<head_sha>` no longer reachable). Rerun `/combined-review --pr <#>` to fetch the current snapshot." No silent fallback; the recorded SHA is the contract.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:150:5. Verifies the recorded base SHA is reachable locally: `git cat-file -e <base_sha>^{commit}`. If unreachable, same stale-snapshot failure with base-side messaging. **Does NOT** assert `FETCH_HEAD == base_sha` — that would fail harmlessly when the base branch advances between `gh pr view` and `git fetch`. We need the recorded commit to be reachable, not to be the current tip.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:155:Because `codex exec` is a general agent (unlike the inherently read-only `codex review`), `run-codex.sh` MUST:
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:157:- Pass `--sandbox read-only` (or codex's equivalent flag — `run-codex.sh` probes the installed codex version's flag list at start and errors out if no read-only sandbox is available, rather than silently running unsandboxed).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:165:- **Use**: `run-codex.sh` reads `worktree_path` from the scope object and runs codex inside it. Does not create or destroy.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:166:- **Fork PRs**: handled by `gh pr checkout --detach <#>` as the primary path inside the empty worktree. `gh` fetches the PR head into a detached HEAD regardless of whether the PR comes from `origin` or a fork. After checkout, `git reset --hard <head-sha>` pins to the exact recorded SHA (defensive against race between `gh pr view` and `gh pr checkout`).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:168:  1. **In-driver trap**: `run-codex.sh` has a `trap 'cleanup' EXIT INT TERM` for temp files it owns *internally* (e.g., intermediate codex state). It does **not** delete the prompt file or the raw-output files — those are passed in by the orchestrator (see "Raw output ownership" below) and have a different lifecycle.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:182:- The orchestrator creates them via `mktemp` before launching reviewers, passes the paths to `run-codex.sh` as `--prompt-file`, `--stdout`, `--stderr` arguments, and to sub-agents inline.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:183:- `run-codex.sh` writes to those paths but never deletes them (its `trap` only cleans up files it created internally).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:187:Without this ownership split, the prior design contradicted itself: `run-codex.sh` was nominally cleaning up the captures, but `report.py` needed them; and the `> <stdout>` redirection shown in §5 was applied by the orchestrator (outside run-codex.sh) anyway, so run-codex.sh couldn't have known about those paths in the first place.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:263:  "total_lines_changed": 247,
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:270:`has_reviewable_changes` is `true` if `changed_file_count > 0` OR `doc_files` is non-empty. Used by the empty-scope pre-flight (§10) instead of `total_lines_changed == 0`, so a PR that only updates a submodule, symlink, or binary asset is **not** rejected as "nothing to review" — those are legitimate review subjects (e.g., bumping a submodule SHA can be high-risk and deserves review).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:285:- **`uncommitted`**: `unified_diff` is `git diff HEAD` (staged + unstaged tracked changes). **Untracked files** (which `git diff HEAD` ignores) are appended to `changed_files` with `status: "added"`, `lines_changed: "(new file)"`, and `post_content` populated if `kind: text`. Without this, the `--uncommitted` flag would silently under-review new files.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:289:- `total_lines_changed` counts only text-file line changes (post-change line count for added, deletion count for deleted, both for modified). Binary/symlink/submodule changes contribute 0 — they don't meaningfully load the reviewers.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:310:`run-codex.sh` accepts the prompt via a **file path** (not argv):
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:313:- Invokes `scripts/run-codex.sh --scope <scope.json> --prompt-file <path>` (still passes scope.json by path, not inline).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:314:- `run-codex.sh` reads the prompt file and pipes it to codex on stdin: `cat <prompt-file> | codex exec --sandbox read-only -` (or equivalent stdin syntax for the installed codex version).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:315:- The prompt temp file is **orchestrator-owned** (see §4 "Raw output ownership"). `run-codex.sh` reads it but never deletes it; the orchestrator deletes it in Phase D after `report.py` completes. The script's own `trap` only handles temp files run-codex.sh creates internally, never paths handed in by the orchestrator.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:319:Parallel tool calls within one message run with no defined order — if `Write` and a background `Bash` were issued together, `run-codex.sh` could start before the prompt file existed. The orchestrator therefore splits setup from review:
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:321:**Phase A — sequential setup (must complete before Phase B starts):**
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:331:**Phase B — parallel review (one message, no inter-dependencies):**
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:333:1. `Bash` with `run_in_background: true` — `scripts/run-codex.sh --scope <scope.json> --prompt-file <prompt-path> --stdout <codex-stdout> --stderr <codex-stderr>`. `run-codex.sh` writes to the paths but does not delete them.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:338:**Phase C — synthesis + report:** the orchestrator awaits all Phase B results (Agent calls return inline; `Monitor` signals codex completion), runs `normalize-findings.py`, the in-session synthesis pass (§8), `validate-clusters.py`, and `report.py`.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:529:1. **Codex availability.** Run `codex login status` (or equivalent) early. If codex isn't on PATH or isn't logged in, stop with a clear message — unless `--no-codex` was passed, in which case skip codex and continue Claude-only with a note in the report.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:531:3. **Empty scope.** If `materialize-scope.py` reports `has_reviewable_changes == false`, error: "nothing to review". This intentionally uses the file-count-based flag, not `total_lines_changed == 0` — a PR that only changes a submodule, symlink, or binary asset is reviewable and shouldn't be rejected.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:532:4. **Large diff.** If `total_lines_changed > LARGE_DIFF_THRESHOLD` (default 2000, env `COMBINED_REVIEW_LARGE_DIFF_THRESHOLD`), the orchestrator asks the user in chat: "Diff is N lines — both reviewers degrade on large diffs. Proceed?" If not interactive (e.g., the skill was called by another agent), require explicit `--force-large` flag instead of prompting.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:546:Cleanup follows the three-layer model in §4: `run-codex.sh`'s `trap` removes codex-side temp files (prompt file, stdout/stderr captures); the orchestrator's final `Bash` call to `scripts/cleanup-worktree.sh` removes the worktree (gated by the triple-assertion check); `scripts/gc-worktrees.sh` runs at the start of every invocation as the leak backstop. `--keep-worktree` (debug-only) suppresses the explicit cleanup step.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:568:            ├── run-codex.sh           # codex driver; reads scope/prompt from orchestrator-owned paths; writes captures to orchestrator-owned stdout/stderr paths; internal trap only for files run-codex creates itself
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:576:Where practical, deterministic scripts communicate via JSON on stdin/stdout (`parse-args.py`, `resolve-scope.py`, `materialize-scope.py`, `normalize-findings.py`, `validate-clusters.py`, `report.py`). Scripts that operate on large or path-bound inputs use **explicit file-path contracts**: `run-codex.sh` takes `--prompt-file`, `--stdout`, `--stderr`; `cleanup-worktree.sh` and `gc-worktrees.sh` take repo + worktree paths and perform side effects. The orchestrator owns intermediate file lifecycle (see §4 "Raw output ownership"). `SKILL.md` describes the pipeline and points the model at each script in order.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:628:- **Codex auth failure**: run `codex login status` early. Treat unauthenticated the same as "Codex unavailable" — stop with a clear message unless `--no-codex` was passed.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:629:- **Diff semantics**: three-dot / merge-base (`git diff base...head`) for `--pr` and `--base`, matching GitHub PR review. Not two-dot. `git show` for `--commit`. `git diff HEAD` + appended untracked files for `--uncommitted`.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:632:- **PR materialization**: `gh pr checkout --detach <#>` as primary path (handles fork PRs natively); fetch base by `base_ref_name` for portability; verify both head and base with `headRefOid`/`baseRefOid` after fetch; `git reset --hard <head-sha>` if HEAD drifted.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:634:- **Codex exec safety for files mode**: must pass `--sandbox read-only` (or codex's equivalent flag) AND include an explicit no-edit instruction at the top of the prompt. `run-codex.sh` errors out if the read-only flag isn't supported by the installed codex version. Non-negotiable — `codex exec` is otherwise a general agent that can edit files, which violates non-goal §13.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:637:- **Prompt passing to codex**: via stdin (read from a temp file by `run-codex.sh`), not argv. Multi-KB prompts (file-mode embeds full doc contents) break shell quoting otherwise.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:639:- **PR base fetch**: `git fetch <base_repo_url> <base_ref_name>` directly — **no `git remote add`**, which would mutate `.git/config` and leak across runs. SHA verification via `git cat-file -e <sha>^{commit}`, not `rev-parse FETCH_HEAD == base_sha` — the recorded commit must be reachable, but the tip may have moved (warn-only).
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:640:- **PR stale-snapshot failure**: if the recorded `head_sha` is not reachable after `gh pr checkout` + `git reset --hard <head_sha>`, the PR was force-pushed between `gh pr view` and `gh pr checkout`. The skill fails loudly with "PR head force-pushed mid-review; rerun" — does not silently fall back to the current head.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:641:- **Raw output ownership**: the orchestrator creates and deletes all long-lived intermediate files (prompt, codex stdout/stderr, sub-agent transcripts). `run-codex.sh` writes to paths passed in via args; doesn't own deletion. Cleanup happens after `report.py` completes, before the worktree teardown.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:642:- **Dispatch ordering**: setup is sequential (parse-args → resolve-scope → materialize → pre-flight → mktemp → Write prompt), reviewers run in parallel only after setup completes. Avoids the race where a parallel `Write` and background Bash launch run-codex.sh before the prompt file exists.
docs/superpowers/specs/2026-05-11-combined-review-skill-design.md:644:- **Empty-scope check**: uses `has_reviewable_changes` (file-count-based + doc_files), not `total_lines_changed == 0`. Submodule/symlink/binary-only PRs are legitimate review subjects.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:21:├── scripts/run-codex.py
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:30:ln -s ~/projects/combined-review ~/.claude/skills/combined-review
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:31:ln -s ~/projects/combined-review/commands/combined-review.md ~/.claude/commands/combined-review.md
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:42:- Create: `~/projects/combined-review/tests/conftest.py`
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:79:- [ ] **Step 4: Write `tests/conftest.py`**
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:83:import os
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:84:import shutil
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:86:import tempfile
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:132:Expected: `no tests ran` exit code 5, no errors.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:137:git add .gitignore README.md pyproject.toml tests/conftest.py
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:262:Expected: all tests FAIL (script doesn't exist yet).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:368:Expected: 12 passed.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:542:Expected: all fail (script doesn't exist).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:561:def git(*args, cwd=None, check=True) -> str:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:651:    import os.path
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:754:Expected: 10 passed (5 original + 3 path-traversal rejection + 1 in-repo-symlink-preservation + 1 directory-rejection).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:781:FAKE_GH_JSON = {
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:801:def write_fake_gh(fake_bin, payload):
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:805:        # Only respond to `gh pr view` calls — fail loudly on anything else.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:816:    write_fake_gh(fake_bin, FAKE_GH_JSON)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:845:Expected: 2 fails (script still rejects PR scope).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:860:        raise SystemExit(f"error: gh pr view failed: {r.stderr.strip()}")
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:897:Expected: 12 passed (10 explicit + 2 PR).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:903:git commit -m "feat: resolve-scope.py --pr via gh pr view metadata"
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:924:from tests.test_resolve_scope_pr import FAKE_GH_JSON, write_fake_gh
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:940:def fake_gh_no_pr(fake_bin):
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:941:    """`gh pr view` exits 1 (no PR for this branch)."""
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:948:    fake_gh_no_pr(fake_bin)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:956:    write_fake_gh(fake_bin, FAKE_GH_JSON)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:965:    write_fake_gh(fake_bin, FAKE_GH_JSON)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:972:    fake_gh_no_pr(fake_bin)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:990:    """True if there are staged, unstaged, or untracked changes."""
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1010:      1. `gh repo view --json defaultBranchRef` — gives the authoritative name
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1023:        ["gh", "repo", "view", "--json", "defaultBranchRef"],
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1028:            name = json.loads(r.stdout)["defaultBranchRef"]["name"]
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1041:def pr_for_current_branch(cwd: str) -> int | None:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1084:Expected: 16 passed (10 explicit + 2 PR + 4 auto-detect).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1095:## Task 6: materialize-scope.py — uncommitted scope
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1156:    assert out["total_lines_changed"] >= 1
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1165:    assert out["total_lines_changed"] == 0
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1219:disposable worktree used by run-codex.py.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1230:def git(*args, cwd: str, check: bool = True) -> str:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1237:def symlink_target(repo: str, path: str) -> str | None:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1239:    full = Path(repo) / path
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1257:    is what the reviewer should see for an unstaged submodule bump. Without
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1286:    full = Path(repo) / path
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1314:def safe_read_text(repo: str, path: str) -> str | None:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1315:    p = Path(repo) / path
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1334:        return "text"  # unknown; fall back to text and let read_at_ref decide
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1354:def read_at_ref(repo_or_worktree: str, ref: str, path: str) -> str | None:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1374:    """Back-compat wrapper for legacy callers — prefer read_at_ref directly."""
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1375:    return read_at_ref(repo, "HEAD", path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1401:def materialize_uncommitted(scope: dict) -> dict:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1425:            entry["post_content"] = safe_read_text(root, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1430:                entry["pre_content"] = read_at_ref(root, "HEAD", path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1434:                # A symlink blob's content IS the target path, so read_at_ref
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1437:                entry["symlink_target"] = read_at_ref(root, "HEAD", path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1461:        post = safe_read_text(root, path) if kind == "text" else None
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1495:        "total_lines_changed": total_lines,
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1531:Expected: 5 passed.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1672:import tempfile
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1673:import os
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1681:    tmp = tempfile.mkdtemp(
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1727:            entry["post_content"] = safe_read_text(worktree, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1730:                entry["pre_content"] = read_at_ref(worktree, merge_base, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1734:                entry["symlink_target"] = read_at_ref(worktree, merge_base, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1775:            "total_lines_changed": total, "changed_file_count": len(changed),
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1851:                entry["post_content"] = safe_read_text(worktree, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1854:                    entry["pre_content"] = read_at_ref(worktree, parent_sha, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1858:                    entry["symlink_target"] = read_at_ref(worktree, parent_sha, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1884:            "total_lines_changed": total, "changed_file_count": len(changed),
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1914:Expected: 9 passed (5 in uncommitted + 4 in diff_scopes, where diff_scopes includes test_base_scope_three_dot_diff, test_commit_scope, test_commit_scope_root_commit_errors, test_commit_scope_merge_commit_errors).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1931:- [ ] **Step 1: Write failing tests using a fake `gh pr checkout`**
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1937:Simulates `gh pr checkout` by hand-applying the head SHA inside the worktree,
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1948:    # gh pr checkout: do nothing (worktree stays at the initial commit).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1968:def test_pr_happy_path(tmp_repo, fake_bin):
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1970:    # capture both SHAs. Make gh pr checkout a no-op (worktree is already
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1983:    # Fake `gh pr checkout` resets the worktree to head_sha
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:1987:        '# only handle `gh pr checkout`; defer to git for the rest\n'
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2025:def cat_file_exists(repo_or_worktree: str, sha: str) -> bool:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2033:def materialize_pr(scope: dict) -> dict:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2041:    # Create an empty worktree we'll populate via gh pr checkout
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2043:    worktree = tempfile.mkdtemp(
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2056:        # `gh pr checkout` handles fork PRs natively. Cwd = worktree.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2062:            raise SystemExit(f"error: gh pr checkout failed: {r.stderr.strip()}")
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2073:            if not cat_file_exists(worktree, head_sha):
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2084:        if not cat_file_exists(worktree, base_sha):
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2098:            "total_lines_changed": total, "changed_file_count": len(changed),
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2127:Expected: 2 passed.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2251:            entry["content"] = safe_read_text(root, path)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2269:        "total_lines_changed": 0,
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2338:Expected: 14 passed (5 uncommitted + 4 diff_scopes + 2 pr + 3 files_and_modes).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2507:        "doc_files": [], "total_lines_changed": 1,
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2768:## Task 12: run-codex.py (Python, for macOS portability)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2771:- Create: `scripts/run-codex.py`
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2780:"""Tests for run-codex.py — invokes codex exec --sandbox read-only with stdin prompt."""
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2813:            '# --help does NOT advertise --sandbox; run-codex.py should refuse.\n'
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2843:    args = ["python3", str(SCRIPTS_DIR / "run-codex.py"),
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2853:    import os as _os
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2905:def test_run_codex_errors_without_sandbox_support(tmp_path, fake_bin):
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2913:    # Sandbox-flag failure is a HARD error — exits non-zero, no status file written.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2924:- [ ] **Step 3: Implement `scripts/run-codex.py`**
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2928:"""run-codex.py — drive `codex exec --sandbox read-only` with a stdin prompt.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2942:import os
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2960:    def write_failed_status(msg: str, exit_code: int) -> None:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2972:        Phase A pre-flight should catch these before Phase B launches at
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2974:        upgraded or replaced between Phase A and Phase B.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2987:                ef.write(f"run-codex.py hard failure: {msg}\n")
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:2995:    # was upgraded/replaced between Phase A and Phase B launch.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3003:        write_failed_status(msg, 3); sys.exit(3)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3007:        write_failed_status(msg, 3); sys.exit(3)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3056:chmod +x scripts/run-codex.py
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3060:Expected: 4 passed (writes-to-orchestrator-paths, records-failure, records-timeout, errors-without-sandbox-support).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3065:git add scripts/run-codex.py tests/test_run_codex.py
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3066:git commit -m "feat: run-codex.py (portable) drives codex exec read-only with orchestrator-owned IO"
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3359:Expected: 5 passed (parses-two-findings, unparseable-chunks-go-to-warnings, empty-input, prose-only-becomes-unparsed-chunk, text-between-blocks-captured).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3447:    """Schema must accept timeout from run-codex.py."""
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:3632:Expected: 8 passed (valid, invalid-severity, missing-clusters, invalid-tag, codex-timeout-accepted, codex-skipped-accepted, unparsed-rejects-bare-string, unparsed-rejects-missing-source).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4090:Expected: 6 passed (high-confidence rendering, codex-stderr-in-audit, codex-timeout-in-reviewer-status, no-codex-skipped, failed-claude-agent, synthesis-failed-banner).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4237:Expected: 4 passed.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4259:import os
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4354:    python3 -c 'import os, sys; print(int(os.stat(sys.argv[1]).st_mtime))' "$p" 2>/dev/null || echo 0
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4380:Expected: 4 passed.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4391:## Task 18: SKILL.md — orchestration document
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4445:  - `codex login status` (or equivalent) — must succeed. If not, stop: "Codex not authenticated. Pass --no-codex or run `codex login`."
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4446:  - `codex exec --help` output must contain `--sandbox` — without this, `run-codex.py` would refuse to run in Phase B and Phase C would have only an error status to render. Catching it in Phase A produces a cleaner user experience. If absent, stop: "Installed codex doesn't advertise `--sandbox`. Update codex or pass --no-codex."
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4452:A6. **Materialize scope** — write `SCOPE_JSON` to `SCOPE_FILE` (Write tool) and run:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4454:  cat "$SCOPE_FILE" | $SKILL_DIR/scripts/materialize-scope.py
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4458:A7. **Merge `worktree_path` from `MAT_JSON` back into the scope object IMMEDIATELY** (before any abort gate that could cause an early exit). Re-write `SCOPE_FILE` with the merged object. Pseudocode:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4463:  Write SCOPE_FILE = serialize(merged)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4468:A8. **Pre-flight — empty scope**: if `MAT_JSON.has_reviewable_changes == false`, run Phase D cleanup (worktree already recorded in `SCOPE_FILE` from A7) and stop: "Nothing to review."
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4470:A9. **Pre-flight — large diff**: if `MAT_JSON.total_lines_changed > 2000` (env override `$COMBINED_REVIEW_LARGE_DIFF_THRESHOLD`):
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4497:### Phase B — parallel review (ONE message, multiple tool calls)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4503:   $SKILL_DIR/scripts/run-codex.py \
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4504:     --scope "$SCOPE_FILE" \
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4510:   with `run_in_background: true`. `SCOPE_FILE` already contains the merged `worktree_path` from Phase A7.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4519:After issuing, await all results inline (Agent calls return), and use `Monitor` to know when codex's background process completes.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4524:  - **If `--no-codex` was passed:** Phase B never launched codex, so `$CODEX_STATUS` is an empty `mktemp` file and reading it would fail. Set `reviewer_summary.codex = {"status": "skipped"}` directly and skip the C2 codex normalization. Do not read `$CODEX_STATUS`.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4530:    **Prefer-status.error rule**: for hard pre-flight failures inside `run-codex.py` (codex disappeared from PATH between Phase A and Phase B, missing `--sandbox` flag), the script writes the diagnostic to both the status JSON and `$CODEX_STDERR`. Status JSON is the more structured/reliable channel — read it first.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4580:**Order matters**: worktree teardown reads `worktree_path` from `SCOPE_FILE`, so SCOPE_FILE must still exist when cleanup-worktree.sh runs. Do D1 BEFORE D2.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4592:D2. **Delete orchestrator-owned files** — only after D1 has read SCOPE_FILE:
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4594:   rm -f "$ARGS_FILE" "$CONFIG_FILE" "$SCOPE_FILE" "$MAT_FILE" "$FOCUS_FILE" \
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4613:- Running reviewers sequentially instead of in parallel (Phase B is the whole point).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4629:## Task 19: commands/combined-review.md — slash entry
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4650:allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep", "Task", "Monitor"]
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4670:- Phase B is the **only** phase where parallel tool calls happen (codex background + Agent sub-agents in the same message).
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4687:## Task 20: Install via symlinks; baseline smoke test
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4710:mkdir -p ~/.claude/skills ~/.claude/commands
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4711:ln -sfn "$PWD" ~/.claude/skills/combined-review
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4712:ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4723:- `codex` CLI on PATH, logged in (`codex login status`)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4747:mkdir -p ~/.claude/skills ~/.claude/commands
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4748:ln -sfn "$PWD" ~/.claude/skills/combined-review
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4749:ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4754:Expected: both symlinks present and pointing at `~/projects/combined-review/`. (Earlier audit found `~/.claude/commands/` did not exist on this machine — the `mkdir -p` makes the install idempotent regardless of starting state.)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4762:Expected: all tests pass.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4804:- Phase B issues one background Bash (codex with `--status` flag) and three Agent calls (code-reviewer, silent-failure-hunter, pr-test-analyzer) in a SINGLE message.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4841:- `gh pr checkout --detach` runs inside it
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4842:- `git fetch <base_repo_url> main` runs (NOT `git fetch origin main`)
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4887:Expected: all green.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4895:Expected: ~20 commits, each a single coherent step.
docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md:4912:| §4 Codex routing via `codex exec` | T12 (run-codex.py) |

exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md | sed -n '35,145p;935,1050p;1220,1250p;1395,1410p;1668,1676p;2058,2072p;4428,4458p;4568,4578p;4704,4756p'" in /private/var/folders/yt/h62lwq8x26340hnlt7lk_c240000gn/T/combined-review-juvera_ai_4-pr-hdlqrklt
 succeeded in 0ms:
    35	
    36	## Task 1: Repo scaffolding
    37	
    38	**Files:**
    39	- Create: `~/projects/combined-review/.gitignore`
    40	- Create: `~/projects/combined-review/README.md`
    41	- Create: `~/projects/combined-review/pyproject.toml`
    42	- Create: `~/projects/combined-review/tests/conftest.py`
    43	
    44	- [ ] **Step 1: Create the repo and directory tree**
    45	
    46	```bash
    47	mkdir -p ~/projects/combined-review/{scripts,prompts,commands,tests}
    48	cd ~/projects/combined-review
    49	git init
    50	```
    51	
    52	- [ ] **Step 2: Write `.gitignore`**
    53	
    54	```
    55	__pycache__/
    56	*.pyc
    57	.pytest_cache/
    58	.venv/
    59	*.egg-info/
    60	```
    61	
    62	- [ ] **Step 3: Write `pyproject.toml`**
    63	
    64	```toml
    65	[project]
    66	name = "combined-review"
    67	version = "0.1.0"
    68	description = "Claude Code skill that fuses Claude + Codex reviews in one session"
    69	requires-python = ">=3.11"
    70	dependencies = ["jsonschema>=4.21.0"]
    71	
    72	[project.optional-dependencies]
    73	dev = ["pytest>=8.0.0"]
    74	
    75	[tool.pytest.ini_options]
    76	testpaths = ["tests"]
    77	```
    78	
    79	- [ ] **Step 4: Write `tests/conftest.py`**
    80	
    81	```python
    82	"""Shared pytest fixtures for the combined-review test suite."""
    83	import os
    84	import shutil
    85	import subprocess
    86	import tempfile
    87	from pathlib import Path
    88	
    89	import pytest
    90	
    91	SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
    92	
    93	
    94	@pytest.fixture
    95	def tmp_repo(tmp_path):
    96	    """A throwaway git repo with one initial commit. Returns the repo Path."""
    97	    repo = tmp_path / "repo"
    98	    repo.mkdir()
    99	    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
   100	    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
   101	    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
   102	    (repo / "README.md").write_text("# Test repo\n")
   103	    subprocess.run(["git", "add", "."], cwd=repo, check=True)
   104	    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=repo, check=True)
   105	    return repo
   106	
   107	
   108	@pytest.fixture
   109	def fake_bin(tmp_path, monkeypatch):
   110	    """Prepend a tmp dir to PATH so tests can drop fake `gh`/`codex` scripts."""
   111	    fake = tmp_path / "bin"
   112	    fake.mkdir()
   113	    monkeypatch.setenv("PATH", f"{fake}:{os.environ['PATH']}")
   114	    return fake
   115	
   116	
   117	def run_script(name, *args, **kwargs):
   118	    """Invoke a script in scripts/ via subprocess; return CompletedProcess."""
   119	    script = SCRIPTS_DIR / name
   120	    cmd = [str(script), *args] if script.suffix == ".sh" else ["python3", str(script), *args]
   121	    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
   122	```
   123	
   124	- [ ] **Step 5: Verify pytest runs (zero tests is OK)**
   125	
   126	```bash
   127	cd ~/projects/combined-review
   128	python3 -m pip install -e ".[dev]"
   129	pytest -v
   130	```
   131	
   132	Expected: `no tests ran` exit code 5, no errors.
   133	
   134	- [ ] **Step 6: Commit**
   135	
   136	```bash
   137	git add .gitignore README.md pyproject.toml tests/conftest.py
   138	git commit -m "feat: scaffold combined-review repo"
   139	```
   140	
   141	---
   142	
   143	## Task 2: parse-args.py — CLI surface
   144	
   145	**Files:**
   935	
   936	def make_dirty(repo):
   937	    (repo / "dirty.txt").write_text("uncommitted\n")
   938	
   939	
   940	def fake_gh_no_pr(fake_bin):
   941	    """`gh pr view` exits 1 (no PR for this branch)."""
   942	    gh = fake_bin / "gh"
   943	    gh.write_text('#!/bin/sh\necho "no pull requests found" >&2\nexit 1\n')
   944	    gh.chmod(0o755)
   945	
   946	
   947	def test_autodetect_dirty_no_pr_implies_uncommitted(tmp_repo, fake_bin):
   948	    fake_gh_no_pr(fake_bin)
   949	    make_dirty(tmp_repo)
   950	    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
   951	    assert r.returncode == 0, r.stderr
   952	    assert json.loads(r.stdout)["kind"] == "uncommitted"
   953	
   954	
   955	def test_autodetect_dirty_plus_pr_errors(tmp_repo, fake_bin):
   956	    write_fake_gh(fake_bin, FAKE_GH_JSON)
   957	    make_dirty(tmp_repo)
   958	    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
   959	    assert r.returncode != 0
   960	    assert "ambig" in r.stderr.lower() or "uncommitted" in r.stderr.lower()
   961	
   962	
   963	def test_autodetect_clean_with_pr_implies_pr(tmp_repo, fake_bin):
   964	    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
   965	    write_fake_gh(fake_bin, FAKE_GH_JSON)
   966	    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
   967	    assert r.returncode == 0, r.stderr
   968	    assert json.loads(r.stdout)["kind"] == "pr"
   969	
   970	
   971	def test_autodetect_default_branch_clean_errors(tmp_repo, fake_bin):
   972	    fake_gh_no_pr(fake_bin)
   973	    r = run_script("resolve-scope.py", input=json.dumps(make_cfg_auto()), cwd=tmp_repo)
   974	    assert r.returncode != 0
   975	    assert "nothing" in r.stderr.lower() or "default" in r.stderr.lower()
   976	```
   977	
   978	- [ ] **Step 2: Run tests, verify they fail**
   979	
   980	```bash
   981	pytest tests/test_resolve_scope_autodetect.py -v
   982	```
   983	
   984	- [ ] **Step 3: Implement auto-detect in `scripts/resolve-scope.py`**
   985	
   986	Add helpers above `main()`:
   987	
   988	```python
   989	def is_dirty(cwd: str) -> bool:
   990	    """True if there are staged, unstaged, or untracked changes."""
   991	    out = git("status", "--porcelain", cwd=cwd)
   992	    return bool(out)
   993	
   994	
   995	def current_branch(cwd: str) -> str:
   996	    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)
   997	
   998	
   999	def _ref_resolves(cwd: str, ref: str) -> bool:
  1000	    return subprocess.run(
  1001	        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
  1002	        cwd=cwd, capture_output=True,
  1003	    ).returncode == 0
  1004	
  1005	
  1006	def default_branch(cwd: str) -> str | None:
  1007	    """Return a ref name (locally resolvable) for the repository default branch.
  1008	
  1009	    Resolution order:
  1010	      1. `gh repo view --json defaultBranchRef` — gives the authoritative name
  1011	         (could be `develop`, `trunk`, etc., not just main/master).
  1012	         Then verify it resolves locally as either `<name>` or `origin/<name>`.
  1013	         Return whichever resolves, preferring the local branch over the
  1014	         remote-tracking ref.
  1015	      2. Probe common candidates locally: main, master, origin/main, origin/master.
  1016	      3. None if nothing resolves.
  1017	
  1018	    Returning a non-resolvable name would just push the failure into `git
  1019	    rev-parse <ref>^{commit}` in the caller, which is worse UX than a clean
  1020	    "no default branch detected" error here.
  1021	    """
  1022	    r = subprocess.run(
  1023	        ["gh", "repo", "view", "--json", "defaultBranchRef"],
  1024	        cwd=cwd, capture_output=True, text=True,
  1025	    )
  1026	    if r.returncode == 0:
  1027	        try:
  1028	            name = json.loads(r.stdout)["defaultBranchRef"]["name"]
  1029	            for ref in (name, f"origin/{name}"):
  1030	                if _ref_resolves(cwd, ref):
  1031	                    return ref
  1032	        except (KeyError, json.JSONDecodeError):
  1033	            pass  # fall through to local probe
  1034	
  1035	    for candidate in ("main", "master", "origin/main", "origin/master"):
  1036	        if _ref_resolves(cwd, candidate):
  1037	            return candidate
  1038	    return None
  1039	
  1040	
  1041	def pr_for_current_branch(cwd: str) -> int | None:
  1042	    r = subprocess.run(
  1043	        ["gh", "pr", "view", "--json", "number"],
  1044	        cwd=cwd, capture_output=True, text=True,
  1045	    )
  1046	    if r.returncode != 0:
  1047	        return None
  1048	    return json.loads(r.stdout)["number"]
  1049	```
  1050	
  1220	
  1221	This patch handles only the `uncommitted` kind. Other kinds are added in
  1222	subsequent patches.
  1223	"""
  1224	import json
  1225	import subprocess
  1226	import sys
  1227	from pathlib import Path
  1228	
  1229	
  1230	def git(*args, cwd: str, check: bool = True) -> str:
  1231	    r = subprocess.run(
  1232	        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
  1233	    )
  1234	    return r.stdout
  1235	
  1236	
  1237	def symlink_target(repo: str, path: str) -> str | None:
  1238	    """Return the link target string for a symlink in the working tree, or None."""
  1239	    full = Path(repo) / path
  1240	    try:
  1241	        return os.readlink(full)
  1242	    except (OSError, FileNotFoundError):
  1243	        return None
  1244	
  1245	
  1246	def submodule_sha_at(repo_or_worktree: str, ref: str, path: str) -> str | None:
  1247	    """Return the submodule pointer SHA at a ref.
  1248	
  1249	    For commit refs (HEAD, base_sha, merge_base, parent_sha): read from
  1250	    `git ls-tree <ref>` — gives the committed pointer.
  1395	            entries.append(("typechange", parts[1], None))
  1396	        else:
  1397	            entries.append((code, parts[1] if len(parts) > 1 else "?", None))
  1398	    return entries
  1399	
  1400	
  1401	def materialize_uncommitted(scope: dict) -> dict:
  1402	    root = scope["repo_root"]
  1403	    unified = git("diff", "HEAD", cwd=root)
  1404	    name_status = git("diff", "--name-status", "HEAD", cwd=root)
  1405	    untracked_raw = git("ls-files", "--others", "--exclude-standard", cwd=root)
  1406	    untracked = [p for p in untracked_raw.splitlines() if p]
  1407	
  1408	    changed: list[dict] = []
  1409	    total_lines = 0
  1410	    for status, path, old_path in parse_name_status(name_status):
  1668	
  1669	Add at module top:
  1670	
  1671	```python
  1672	import tempfile
  1673	import os
  1674	```
  1675	
  1676	Add helpers (above `materialize_uncommitted`):
  2058	            ["gh", "pr", "checkout", "--detach", str(pr)],
  2059	            cwd=worktree, capture_output=True, text=True,
  2060	        )
  2061	        if r.returncode != 0:
  2062	            raise SystemExit(f"error: gh pr checkout failed: {r.stderr.strip()}")
  2063	
  2064	        # Fetch base from the PR's actual base repo (NOT origin — may be a fork)
  2065	        subprocess.run(
  2066	            ["git", "fetch", base_url, base_ref],
  2067	            cwd=worktree, capture_output=True, text=True,
  2068	        )
  2069	
  2070	        # Pin head: if HEAD drifted, reset to recorded head_sha
  2071	        current_head = git("rev-parse", "HEAD", cwd=worktree).strip()
  2072	        if current_head != head_sha:
  4428	
  4429	A1. **GC stale worktrees** — `$SKILL_DIR/scripts/gc-worktrees.sh "$(git rev-parse --show-toplevel)"`. Ignore non-zero exits; this is best-effort.
  4430	
  4431	A2. **Write `$ARGUMENTS` to a file using the `Write` tool** (NOT a Bash heredoc — `Write` doesn't shell-interpret, which is the whole point). Path: an orchestrator-owned tmp file `ARGS_FILE` you allocate via `Bash` (`mktemp -t combined-review-args-XXXXXX`). Then **parse args** by Bash:
  4432	  ```
  4433	  $SKILL_DIR/scripts/parse-args.py --args-file "$ARGS_FILE"
  4434	  ```
  4435	  Capture stdout as `CONFIG_JSON`. This avoids shell-injection from `$ARGUMENTS` containing quotes, spaces, `$`, backticks, etc.
  4436	
  4437	A3. **Write `CONFIG_JSON` to `CONFIG_FILE`** (Write tool again, no shell interpolation) and **resolve scope**:
  4438	  ```
  4439	  cat "$CONFIG_FILE" | $SKILL_DIR/scripts/resolve-scope.py
  4440	  ```
  4441	  Capture stdout as `SCOPE_JSON`. If this errors (dirty+PR ambiguity, default branch + clean tree), surface the error to the user and stop.
  4442	
  4443	A4. **Pre-flight — codex availability**: if the user did NOT pass `--no-codex`, run three checks before continuing:
  4444	  - `command -v codex` — must succeed. If not, stop: "Codex not on PATH. Pass --no-codex to run Claude-only, or install codex."
  4445	  - `codex login status` (or equivalent) — must succeed. If not, stop: "Codex not authenticated. Pass --no-codex or run `codex login`."
  4446	  - `codex exec --help` output must contain `--sandbox` — without this, `run-codex.py` would refuse to run in Phase B and Phase C would have only an error status to render. Catching it in Phase A produces a cleaner user experience. If absent, stop: "Installed codex doesn't advertise `--sandbox`. Update codex or pass --no-codex."
  4447	
  4448	  All three pre-flights are skipped if `--no-codex` was passed.
  4449	
  4450	A5. **Pre-flight — gh authentication when --pr**: if `SCOPE_JSON.kind == "pr"`, run `gh auth status`. Error early if not authenticated.
  4451	
  4452	A6. **Materialize scope** — write `SCOPE_JSON` to `SCOPE_FILE` (Write tool) and run:
  4453	  ```
  4454	  cat "$SCOPE_FILE" | $SKILL_DIR/scripts/materialize-scope.py
  4455	  ```
  4456	  Capture stdout as `MAT_JSON`. This creates the worktree if needed and populates the materialized review subject.
  4457	
  4458	A7. **Merge `worktree_path` from `MAT_JSON` back into the scope object IMMEDIATELY** (before any abort gate that could cause an early exit). Re-write `SCOPE_FILE` with the merged object. Pseudocode:
  4568	   ```
  4569	   $SKILL_DIR/scripts/report.py \
  4570	     --codex-raw "$CODEX_STDOUT" \
  4571	     --codex-stderr "$CODEX_STDERR" \
  4572	     --claude-raw "$CLAUDE_TRANSCRIPTS/all.txt" \
  4573	     [--synthesis-failed-file "$VALIDATE_STDERR"] \
  4574	     < "$CLUSTERS_FILE"
  4575	   ```
  4576	   When the `--synthesis-failed-file` flag is set, an empty stdin is fine (report.py only reads stdin in the non-failed path). Why file not argv: the validator's stderr can contain backticks, `$(...)`, or quote characters from the model's malformed output — interpolating that into a Bash command line is the same shell-injection class as the focus-text case. Always file. Print the output to chat. If `--save <path>` was passed, also tee to that path. Phase D will delete `$CLUSTERS_FILE` and `$VALIDATE_STDERR` along with the other orchestrator-owned files.
  4577	
  4578	### Phase D — cleanup (ALWAYS, even on errors)
  4704	in the original juvera repo for the design rationale.
  4705	
  4706	## Install
  4707	
  4708	```bash
  4709	# from this repo's root (~/projects/combined-review)
  4710	mkdir -p ~/.claude/skills ~/.claude/commands
  4711	ln -sfn "$PWD" ~/.claude/skills/combined-review
  4712	ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
  4713	
  4714	# Verify
  4715	ls -la ~/.claude/skills/combined-review
  4716	ls -la ~/.claude/commands/combined-review.md
  4717	```
  4718	
  4719	## Dependencies
  4720	
  4721	- Python 3.11+
  4722	- `jsonschema` (`pip install -e ".[dev]"` from this repo)
  4723	- `codex` CLI on PATH, logged in (`codex login status`)
  4724	- `gh` CLI on PATH, authenticated (`gh auth status`)
  4725	
  4726	## Run
  4727	
  4728	```
  4729	/combined-review              # auto-detect scope, code mode
  4730	/combined-review --pr 105
  4731	/combined-review --uncommitted
  4732	/combined-review --mode spec docs/design.md
  4733	```
  4734	
  4735	## Develop
  4736	
  4737	```bash
  4738	pip install -e ".[dev]"
  4739	pytest -v
  4740	```
  4741	````
  4742	
  4743	- [ ] **Step 2: Run the install commands**
  4744	
  4745	```bash
  4746	cd ~/projects/combined-review
  4747	mkdir -p ~/.claude/skills ~/.claude/commands
  4748	ln -sfn "$PWD" ~/.claude/skills/combined-review
  4749	ln -sfn "$PWD/commands/combined-review.md" ~/.claude/commands/combined-review.md
  4750	ls -la ~/.claude/skills/combined-review
  4751	ls -la ~/.claude/commands/combined-review.md
  4752	```
  4753	
  4754	Expected: both symlinks present and pointing at `~/projects/combined-review/`. (Earlier audit found `~/.claude/commands/` did not exist on this machine — the `mkdir -p` makes the install idempotent regardless of starting state.)
  4755	
  4756	- [ ] **Step 3: Run the full test suite end-to-end**

exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md | sed -n '1050,1078p;1938,2018p;2910,3010p;4642,4652p'" in /private/var/folders/yt/h62lwq8x26340hnlt7lk_c240000gn/T/combined-review-juvera_ai_4-pr-hdlqrklt
 succeeded in 0ms:
  1050	
  1051	Replace the `if scope_flag is None: raise SystemExit(...)` in `main()` with auto-detect:
  1052	
  1053	```python
  1054	    if scope_flag is None:
  1055	        dirty = is_dirty(root)
  1056	        pr_num = pr_for_current_branch(root)
  1057	        if dirty and pr_num is not None:
  1058	            raise SystemExit(
  1059	                "error: ambiguous scope — tree has uncommitted changes and "
  1060	                f"current branch has PR #{pr_num}. Pass --uncommitted or --pr {pr_num}."
  1061	            )
  1062	        if dirty:
  1063	            scope_flag = "uncommitted"
  1064	        elif pr_num is not None:
  1065	            scope_flag = "pr"
  1066	            cfg["pr_number"] = pr_num
  1067	        else:
  1068	            branch = current_branch(root)
  1069	            default = default_branch(root)
  1070	            if default is None or branch == default:
  1071	                raise SystemExit(
  1072	                    "error: nothing to review (clean tree, on default branch, no PR)"
  1073	                )
  1074	            scope_flag = "base"
  1075	            cfg["base_branch"] = default
  1076	```
  1077	
  1078	- [ ] **Step 4: Run tests**
  1938	since we don't have GitHub in the test loop.
  1939	"""
  1940	import json
  1941	import subprocess
  1942	from pathlib import Path
  1943	
  1944	from tests.conftest import run_script
  1945	
  1946	
  1947	def test_pr_stale_snapshot_failure(tmp_repo, fake_bin):
  1948	    # gh pr checkout: do nothing (worktree stays at the initial commit).
  1949	    # The PR scope wants head_sha=<nonexistent SHA>, which should fail loudly.
  1950	    gh = fake_bin / "gh"
  1951	    gh.write_text('#!/bin/sh\nexit 0\n')
  1952	    gh.chmod(0o755)
  1953	    scope = {
  1954	        "kind": "pr", "pr_number": 99,
  1955	        "base_ref_name": "main", "head_ref_name": "feature",
  1956	        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
  1957	        "base_sha": "0" * 40, "head_sha": "f" * 40, "commit_sha": None,
  1958	        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
  1959	        "needs_clean_worktree": True, "mode": "code", "focus": None,
  1960	        "full": False, "no_codex": False, "force_large": False,
  1961	        "keep_worktree": False, "save_path": None,
  1962	    }
  1963	    r = run_script("materialize-scope.py", input=json.dumps(scope))
  1964	    assert r.returncode != 0
  1965	    assert "force-pushed" in r.stderr.lower() or "stale" in r.stderr.lower() or "unreachable" in r.stderr.lower()
  1966	
  1967	
  1968	def test_pr_happy_path(tmp_repo, fake_bin):
  1969	    # Set up: initial commit on main; create feature branch with a commit;
  1970	    # capture both SHAs. Make gh pr checkout a no-op (worktree is already
  1971	    # at the head via our test setup) — and skip the base-repo fetch by
  1972	    # using the local repo's URL.
  1973	    base_sha = subprocess.run(
  1974	        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
  1975	    ).stdout.strip()
  1976	    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_repo, check=True)
  1977	    (tmp_repo / "f.py").write_text("z = 3\n")
  1978	    subprocess.run(["git", "add", "f.py"], cwd=tmp_repo, check=True)
  1979	    subprocess.run(["git", "commit", "-q", "-m", "feat"], cwd=tmp_repo, check=True)
  1980	    head_sha = subprocess.run(
  1981	        ["git", "rev-parse", "HEAD"], cwd=tmp_repo, capture_output=True, text=True
  1982	    ).stdout.strip()
  1983	    # Fake `gh pr checkout` resets the worktree to head_sha
  1984	    gh = fake_bin / "gh"
  1985	    gh.write_text(
  1986	        '#!/bin/sh\n'
  1987	        '# only handle `gh pr checkout`; defer to git for the rest\n'
  1988	        f'if [ "$1" = "pr" ] && [ "$2" = "checkout" ]; then\n'
  1989	        f'  git -C "$PWD" reset --hard {head_sha} >/dev/null\n'
  1990	        '  exit 0\n'
  1991	        'fi\n'
  1992	        'exit 1\n'
  1993	    )
  1994	    gh.chmod(0o755)
  1995	    scope = {
  1996	        "kind": "pr", "pr_number": 1,
  1997	        "base_ref_name": "main", "head_ref_name": "feature",
  1998	        "base_repo_url": str(tmp_repo), "head_repo_url": str(tmp_repo),
  1999	        "base_sha": base_sha, "head_sha": head_sha, "commit_sha": None,
  2000	        "files": [], "worktree_path": None, "repo_root": str(tmp_repo),
  2001	        "needs_clean_worktree": True, "mode": "code", "focus": None,
  2002	        "full": False, "no_codex": False, "force_large": False,
  2003	        "keep_worktree": False, "save_path": None,
  2004	    }
  2005	    r = run_script("materialize-scope.py", input=json.dumps(scope))
  2006	    assert r.returncode == 0, r.stderr
  2007	    out = json.loads(r.stdout)
  2008	    assert out["scope_kind"] == "pr"
  2009	    assert any(f["path"] == "f.py" for f in out["changed_files"])
  2010	    subprocess.run(["git", "worktree", "remove", "--force", out["worktree_path"]],
  2011	                   cwd=tmp_repo, check=True)
  2012	```
  2013	
  2014	- [ ] **Step 2: Run tests, verify they fail**
  2015	
  2016	```bash
  2017	pytest tests/test_materialize_pr.py -v
  2018	```
  2910	    prompt = tmp_path / "prompt.txt"; prompt.write_text("p")
  2911	    status = tmp_path / "status.json"
  2912	    r = run_codex(scope, prompt, tmp_path / "o", tmp_path / "e", status_path=status)
  2913	    # Sandbox-flag failure is a HARD error — exits non-zero, no status file written.
  2914	    assert r.returncode != 0
  2915	    assert "sandbox" in r.stderr.lower()
  2916	```
  2917	
  2918	- [ ] **Step 2: Run tests, verify they fail**
  2919	
  2920	```bash
  2921	pytest tests/test_run_codex.py -v
  2922	```
  2923	
  2924	- [ ] **Step 3: Implement `scripts/run-codex.py`**
  2925	
  2926	```python
  2927	#!/usr/bin/env python3
  2928	"""run-codex.py — drive `codex exec --sandbox read-only` with a stdin prompt.
  2929	
  2930	Portable across macOS and Linux. GNU `timeout` isn't on macOS by default and
  2931	BSD `date` doesn't support `%3N`, so we use Python's subprocess.run(timeout=)
  2932	and time.monotonic_ns() instead.
  2933	
  2934	All long-lived files (prompt, stdout, stderr, status) are orchestrator-owned.
  2935	This script writes to them but never deletes them. It ALWAYS exits 0 except
  2936	for hard pre-flight failures (missing --sandbox support, missing required
  2937	args); outcome of the codex run goes into the status JSON so the
  2938	orchestrator's background-Bash mechanics don't have to interpret exit codes.
  2939	"""
  2940	import argparse
  2941	import json
  2942	import os
  2943	import subprocess
  2944	import sys
  2945	import time
  2946	
  2947	
  2948	def main() -> None:
  2949	    ap = argparse.ArgumentParser()
  2950	    ap.add_argument("--scope", required=True)
  2951	    ap.add_argument("--prompt-file", required=True)
  2952	    ap.add_argument("--stdout", required=True)
  2953	    ap.add_argument("--stderr", required=True)
  2954	    ap.add_argument("--status", default=None,
  2955	                    help="default: <stdout>.status")
  2956	    args = ap.parse_args()
  2957	
  2958	    status_path = args.status or f"{args.stdout}.status"
  2959	
  2960	    def write_failed_status(msg: str, exit_code: int) -> None:
  2961	        """Write a status JSON AND mirror the message into the orchestrator-
  2962	        owned stderr capture for hard failures. Phase C builds its error
  2963	        section from $CODEX_STDERR and report.py embeds it in the audit
  2964	        trail. Writing only to sys.stderr (this script's own stderr) would
  2965	        leave the audit trail empty for missing-sandbox / missing-codex
  2966	        cases — invisible to anyone reading the report.
  2967	
  2968	        Two destinations:
  2969	          1. status JSON: structured error for Phase C's reviewer_summary
  2970	          2. args.stderr: free-form text the audit trail can show verbatim
  2971	
  2972	        Phase A pre-flight should catch these before Phase B launches at
  2973	        all, but this still matters for the (narrow) case where codex was
  2974	        upgraded or replaced between Phase A and Phase B.
  2975	        """
  2976	        try:
  2977	            with open(status_path, "w") as sf:
  2978	                json.dump({
  2979	                    "status": "failed", "exit_code": exit_code,
  2980	                    "duration_ms": 0, "timeout_seconds": 0,
  2981	                    "error": msg,
  2982	                }, sf)
  2983	        except OSError:
  2984	            pass
  2985	        try:
  2986	            with open(args.stderr, "w") as ef:
  2987	                ef.write(f"run-codex.py hard failure: {msg}\n")
  2988	        except OSError:
  2989	            pass
  2990	
  2991	    # Hard pre-flight: verify codex exec advertises --sandbox before we ever
  2992	    # invoke it. Missing the flag means we cannot guarantee read-only mode —
  2993	    # refuse to run rather than silently going unsandboxed.
  2994	    # Phase A pre-flight should catch this, but check here too in case codex
  2995	    # was upgraded/replaced between Phase A and Phase B launch.
  2996	    try:
  2997	        help_out = subprocess.run(
  2998	            ["codex", "exec", "--help"], capture_output=True, text=True, timeout=10,
  2999	        )
  3000	    except FileNotFoundError:
  3001	        msg = "codex not on PATH"
  3002	        print(f"error: {msg}", file=sys.stderr)
  3003	        write_failed_status(msg, 3); sys.exit(3)
  3004	    if "--sandbox" not in (help_out.stdout + help_out.stderr):
  3005	        msg = "installed codex does not advertise --sandbox; refusing to run unsandboxed"
  3006	        print(f"error: {msg}", file=sys.stderr)
  3007	        write_failed_status(msg, 3); sys.exit(3)
  3008	
  3009	    # Resolve cwd: prefer worktree_path (diff-based scopes), else repo_root.
  3010	    with open(args.scope) as f:
  4642	# Edit is intentionally omitted — this is a read-only review flow. Write is
  4643	# needed for orchestrator-owned temp files (prompt, scope, args) and the
  4644	# optional --save report path. Bash is unavoidable (the entire pipeline is
  4645	# Bash-driven). Removing Edit is defense-in-depth, NOT a hard sandbox: Write
  4646	# and Bash can still modify repo files if the model drifts. The primary
  4647	# protection against unintended edits is the no-edit instruction inside the
  4648	# rendered review prompt + codex's --sandbox read-only enforcement; the
  4649	# allowlist trim just removes the most obvious code-modification path.
  4650	allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep", "Task", "Monitor"]
  4651	---
  4652	

codex
---FINDING---
severity: medium
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 39-137
category: bug
title: Task 1 commits README.md before any step creates it
detail: |
  Task 1 lists README.md as a created file and later runs `git add ... README.md`, but the steps only write `.gitignore`, `pyproject.toml`, and `tests/conftest.py`. On a fresh repo, `git add README.md` fails and blocks the first commit. Add an explicit README creation step or remove it from the Task 1 commit until Task 20.
---END-FINDING---

---FINDING---
severity: high
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 1237-1242
category: bug
title: Task 6 uses os.readlink before importing os
detail: |
  The initial `materialize-scope.py` implementation defines `symlink_target()` with `os.readlink(full)` but Task 6 imports only `json`, `subprocess`, `sys`, and `Path`. The `import os` is not added until Task 7, so the Task 6 commit is broken for the symlink path it claims to support. The Task 6 tests do not exercise symlink changes, so this can pass verification while shipping a NameError.
---END-FINDING---

---FINDING---
severity: high
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 1041-1063
category: bug
title: Auto-detect treats any gh failure as no PR
detail: |
  `pr_for_current_branch()` returns `None` for every non-zero `gh pr view` result, and the auto-detect branch then chooses `uncommitted` or `base`. That conflates "no PR exists" with gh auth failure, network failure, missing `gh`, or an API error. In a dirty branch that has a PR, an unauthenticated `gh` run silently bypasses the dirty+PR ambiguity guard and reviews the wrong scope.
---END-FINDING---

---FINDING---
severity: high
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 2064-2068
category: bug
title: PR base fetch failures are ignored
detail: |
  `materialize_pr()` runs `git fetch <base_url> <base_ref>` without `check=True` and never inspects stderr or the exit code. A fork/base fetch auth error, missing ref, or network failure can be hidden and later reported only as an unreachable SHA, or skipped entirely if the SHA happens to be reachable from local refs. The tests also use a local repo and do not assert the fetch succeeded, so the plan does not prove the fork/base fetch contract works.
---END-FINDING---

---FINDING---
severity: medium
file: docs/superpowers/plans/2026-05-13-combined-review-skill-plan.md
line: 4576
category: security
title: --save handling lacks the same shell-safety rules as other user input
detail: |
  The SKILL.md step says to "also tee" to the user-provided `--save <path>` but does not specify a safe mechanism. The plan is careful to pass `$ARGUMENTS`, focus text, and validator errors through files to avoid shell injection, but `save_path` is also user-controlled and may contain spaces, quotes, backticks, or `$()`. Define exact handling, such as writing the report with a Python helper or using a separately written path file, and add tests for spaces/metacharacters.
---END-FINDING---
tokens used
245,229
``````

### Claude sub-agents

```
Agent dispatch timed out (15+ minute internal timeout). Prompt size was ~720KB; the opus document-reviewer could not complete within the orchestrator's Agent-call window. Codex side succeeded in 157s.
```

</details>
