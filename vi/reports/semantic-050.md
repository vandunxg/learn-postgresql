# Semantic Review Report

- Scope: Full `parts/part-050.pdf` (printed pages 458-467) compared with `vi/parts/part-050.md`, including the `part-049` and `part-051` boundary context
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

- Compared all prose, headings, the callout, examples, SQL, `psql` prompts, result-set output, identifiers, literals, and configuration values against the complete 10-page source PDF in paragraph context.
- Checked parallel `Gather`/`Gather Merge` behavior, parallel scans/joins/aggregations, planner conditions and restrictions for parallel plans, utility nodes, cost estimates versus computational effort, index types, selectivity guidance, `CREATE INDEX` clauses, concurrent index creation wording, and index inspection semantics.
- Checked PostgreSQL terminology, subject/action/object relationships, conditions, negation, cause/effect, recommendation strength, qualifiers, PostgreSQL 16 context, and both part boundaries.
- Preserved the source's wording and apparent contradiction about table locking during `CONCURRENTLY` index creation rather than correcting the source from current PostgreSQL knowledge.
- The SQL, commands, `psql` prompts, output tables, result-set rows, identifiers, literals, and the intentionally incomplete fourth result record at the right boundary were not edited. No query-plan tree appears in this part.
- No edit was made to `vi/parts/part-050.md`; this report is the only semantic-review artifact written.
