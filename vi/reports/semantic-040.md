# Semantic Review Report

- Scope: Full `parts/part-040.pdf` (printed pages 358-367) compared with `vi/parts/part-040.md`, including the `part-039` and `part-041` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| HIGH | `vi/parts/part-040.md:186` | The explanation after `UPDATE tags SET tag = upper( tag )` said that all descriptions were changed to uppercase. | The preceding SQL changes the `tag` values; the `SELECT` shows those uppercase tags before `ROLLBACK` restores the original values. | Changed `description` to `tag`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 1
- MEDIUM fixed: 0
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, callouts, SQL, `psql` prompts, result sets, identifiers, literals, and error messages against the complete 10-page source PDF in paragraph context.
- Checked implicit versus explicit transactions, transaction boundaries, `xid`/`xmin`, `COMMIT`/`ROLLBACK`, aborted transactions, constraint failure behavior, and the recommendation for explicit transactions.
- Checked PostgreSQL terminology, conditions, negation, recommendation strength, and the `part-039` to `part-040` and `part-040` to `part-041` boundaries.
- SQL, commands, prompts, identifiers, literals, output, and error messages were not edited.
