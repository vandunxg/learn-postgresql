# Semantic Review Report

- Scope: Full `parts/part-047.pdf` (printed pages 428-437) compared with `vi/parts/part-047.md`, including the `part-046` and `part-048` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose, headings, callouts, lists, captions, examples, installation workflows, PGXN command explanations, `psql` sessions, result sets, and the closing removal paragraph against the complete 10-page source PDF in paragraph context.
- Checked the PGXN client model, executable aliases, package installation paths, source installation workflow, command meanings, cluster versus database scope, extension deployment versus `CREATE EXTENSION`, and the `orafce` usage examples.
- Checked PostgreSQL terminology, subject/action/object relationships, conditions, negation, recommendation strength, qualifiers, version context, and both part boundaries.
- Preserved source inconsistencies such as `PXGN`, `pgxnclient-3.1.2`, the `orafce` 4.2.1/4.5.0 discrepancy, and the wrapped `Oracl`/`e RDBMS` output rather than correcting source content.
- Shell commands, `pgxn` help output, `psql` prompts, SQL, identifiers, literals, version values, result sets, and output text were not edited.
- No edit was made to `vi/parts/part-047.md`; this report is the only semantic-review artifact written.
