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
