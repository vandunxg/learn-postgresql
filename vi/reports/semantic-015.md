# Semantic Review Report

- Scope: Full `parts/part-015.pdf` (printed pages 108-117) compared with `vi/parts/part-015.md`, including the `part-014` and `part-016` boundary context.
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-015.md:331,370` | `post value` was a literal and unnatural rendering for the posts being searched. | The source describes searching for posts that do not belong to the `Database` category; the adjacent `NOT IN`/`NOT EXISTS` queries return post rows. | Changed `post value` to `post` in both parallel explanations. | fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Reviewed all prose in the complete 10-page source part against the translation in paragraph and query context.
- Checked `ilike`, `coalesce`, `NULL`, aliases, `DISTINCT`, `LIMIT`/`OFFSET`, identity wording, subqueries, `IN`/`NOT IN`, `EXISTS`/`NOT EXISTS`, semi-joins, and the Cartesian-product join example.
- SQL, `psql` commands, prompts, identifiers, literals, terminal output, result sets, and the complete 15-row Cartesian-product block were left unchanged.
- Source claims such as `SELECT 0` and the source's `pk` wording in the subquery explanation were not technically corrected.
- Boundary reports `boundary-014-015.md` and `boundary-015-016.md` were checked for continuity and ownership.
