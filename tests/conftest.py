"""Shared pytest fixtures for the combined-review test suite."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "plugins" / "combined-review" / "scripts"


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
