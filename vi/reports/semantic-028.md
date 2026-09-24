# Semantic Review Report

- Scope: Full `parts/part-028.pdf` (printed pages 238-247) compared with `vi/parts/part-028.md`, including the `part-027` and `part-029` boundary context
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

- Compared all prose, headings, numbered steps, bullets, figure caption/description, SQL, `psql` prompts, result sets, and the incomplete right-boundary query against the complete 10-page source PDF in paragraph context.
- Checked rule behavior for `DO INSTEAD`, `DO ALSO`, `NOTHING`, `INSERT`/`DELETE`/`UPDATE`, `NEW`/`OLD`, `UNION ALL`, `LIKE`/`ILIKE`, and the `move_record` function.
- Checked PostgreSQL terminology and technical relationships for tables, constraints, indexes, primary keys, parent/child tables, and rule-driven copying/deletion.
- Preserved the source's wording and behavior claims without modernizing or correcting the example. SQL, commands, identifiers, literals, prompts, output, and result formatting were not edited.
- Boundary reports `boundary-027-028.md` and `boundary-028-029.md` were checked for SQL, list, result-set, and Markdown-fence continuity.
- No edit was required in `vi/parts/part-028.md`; this report is the only file added by the semantic review.
