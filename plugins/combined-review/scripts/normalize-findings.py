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
