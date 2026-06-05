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
