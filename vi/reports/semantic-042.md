# Semantic Review Report

- Scope: Full `parts/part-042.pdf` (printed pages 378-387) compared with `vi/parts/part-042.md`, including the `part-041` and `part-043` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-042.md:93` | The subsection heading misspelled the isolation level as `READ UNCOMITTED`. | The source heading is `READ UNCOMMITTED`; the misspelling occurs only in the source prose at the next line. | Corrected the heading to `READ UNCOMMITTED`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, callouts, SQL, `psql` prompts, result sets, identifiers, literals, and error messages against the complete 10-page source PDF in paragraph context.
- Checked lock behavior, MVCC tuple versions and visibility, `VACUUM`, dirty/unrepeatable/phantom reads, isolation-level conditions, `SET TRANSACTION` timing and abort behavior, serializable failures, `xmin`/`xmax`/`cmin`/`cmax`, cursor snapshots, and savepoint semantics.
- Preserved the source prose misspelling `READ UNCOMITTED` at `vi/parts/part-042.md:95`, the source's `READ committed` wording beside the `REPEATABLE READ` example, and the source's apparent `transaction` wording at `vi/parts/part-042.md:165`; none was inferred or modernized.
- SQL, commands, prompts, identifiers, literals, output, and error messages were not edited.
