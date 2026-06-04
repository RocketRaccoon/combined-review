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


def test_top_level_must_be_object():
    r = run_script("validate-clusters.py", input=json.dumps([]))
    assert r.returncode != 0
    assert "root" in r.stderr.lower()


def test_empty_sources_violates_min_items():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["clusters"][0]["sources"] = []
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0
    assert "sources" in r.stderr.lower()


def test_nested_source_item_must_be_object():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["clusters"][0]["sources"] = ["not-an-object"]
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_focus_accepts_string_and_null_but_not_number():
    ok_str = json.loads(json.dumps(VALID_CLUSTERS))
    ok_str["focus"] = "auth surface"
    assert run_script("validate-clusters.py", input=json.dumps(ok_str)).returncode == 0

    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["focus"] = 123
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0
    assert "focus" in r.stderr.lower()


def test_integer_field_rejects_bool():
    # bool is an int subclass in Python; JSON-Schema "integer" must exclude it.
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["reviewer_summary"]["codex"]["raw_findings"] = True
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0


def test_deep_violation_path_is_rendered():
    bad = json.loads(json.dumps(VALID_CLUSTERS))
    bad["clusters"][0]["sources"][0]["severity"] = "blocker"
    r = run_script("validate-clusters.py", input=json.dumps(bad))
    assert r.returncode != 0
    assert "clusters/0/sources/0/severity" in r.stderr
