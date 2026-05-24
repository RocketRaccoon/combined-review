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
    base_repo_url = (payload.get("baseRepository") or {}).get(
        "url", "https://github.com/upstream/repo.git"
    )
    script.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "pr" ] && [ "$2" = "view" ]; then\n'
        f"  cat <<'EOF'\n{json.dumps(payload)}\nEOF\n"
        "  exit 0\n"
        "fi\n"
        # `gh repo view --json url` is used by resolve_pr to get base_repo_url
        # since `gh pr view` does not expose baseRepository.
        'if [ "$1" = "repo" ] && [ "$2" = "view" ]; then\n'
        f'  printf \'{{"url":"{base_repo_url}"}}\\n\'\n'
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
