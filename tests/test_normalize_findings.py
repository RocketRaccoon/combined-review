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
