#!/usr/bin/env python3
"""validate-clusters.py — JSON-Schema-validate the synthesis cluster JSON.

Exits 0 if valid; non-zero with a descriptive stderr if not. The orchestrator
catches non-zero, re-prompts the synthesis LLM once with the error, then
re-validates. If validation fails twice, the final report runs in "synthesis
failed" mode (see SKILL.md).

Validation is a small pure-stdlib walk over the constrained JSON-Schema subset
this file uses (type / required / enum / minItems / properties / items). It has
no third-party dependency on purpose: a marketplace-installed plugin runs from
a copied cache where no `pip install` ever runs.
"""
import json
import sys

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


class _SchemaError(Exception):
    def __init__(self, path, message):
        self.path = path
        self.message = message


_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    # bool is an int subclass in Python; JSON-Schema "integer" excludes bools.
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "null": lambda v: v is None,
}


def _fmt(path):
    return "/".join(str(p) for p in path) or "(root)"


def _check_type(value, type_spec, path):
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    for t in types:
        if t not in _TYPE_CHECKS:
            # A SCHEMA-definition bug, not a data violation: fail loudly with a
            # clear message instead of a bare KeyError, and don't silently treat
            # the unknown type as never-matching (which would mis-reject data).
            raise ValueError(
                f"validate-clusters.py: SCHEMA uses unsupported type {t!r}; "
                f"add it to _TYPE_CHECKS")
    if not any(_TYPE_CHECKS[t](value) for t in types):
        raise _SchemaError(path, f"{value!r} is not of type {type_spec!r}")


def _validate(value, schema, path):
    if "type" in schema:
        _check_type(value, schema["type"], path)
    if "enum" in schema and value not in schema["enum"]:
        raise _SchemaError(path, f"{value!r} is not one of {schema['enum']!r}")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                raise _SchemaError(path + [req], f"{req!r} is a required property")
        for key, subschema in schema.get("properties", {}).items():
            if key in value:
                _validate(value[key], subschema, path + [key])
    if isinstance(value, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            raise _SchemaError(
                path, f"array is too short: {len(value)} < minItems {min_items}")
        item_schema = schema.get("items")
        if item_schema is not None:
            for i, item in enumerate(value):
                _validate(item, item_schema, path + [i])


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"error: input is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    try:
        _validate(data, SCHEMA, [])
    except _SchemaError as e:
        print(f"error: schema violation at {_fmt(e.path)}: {e.message}",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
