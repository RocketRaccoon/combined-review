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
