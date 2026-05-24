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
