# Boundary Review: part-002 <-> part-003

## Scope

- Wave B boundary only: `part-002` -> `part-003`.
- Compared the final two source pages of `parts/part-002.pdf` with the initial two source pages of `parts/part-003.pdf`.
- Checked the translated junction in `vi/parts/part-002.md` and `vi/parts/part-003.md` against instructions 00, 02, 04, 05, 06, and 07.

## Findings

- The source boundary is a clean table-of-contents transition: part-002 ends with Chapter 13 References, and part-003 starts with Chapter 14. No sentence or paragraph continues across the boundary.
- The source TOC hierarchy shows `The control file` nested under `Extension components`, while `The script file` is its sibling. The translation had incorrectly nested `Script file` under `Control file`'s parent.
- No SQL, code block, `psql` session, query result, `EXPLAIN` plan, table, figure, or caption crosses the boundary.
- Technical terms, identifiers, commands, and page references are continuous and preserved, including `pgxnclient`, `EXPLAIN`, `EXPLAIN ANALYZE`, `ANALYZE`, `COPY`, `pg_restore`, `pg_verifybackup`, `PITR`, `WAL`, `pgBadger`, `PgAudit`, and `pg_stat_statements`.
- No source-owned TOC entry is duplicated or omitted in the checked pages.

## Changes

- Corrected the Markdown nesting of `Script file • 420` in `vi/parts/part-002.md` to match the source hierarchy.
- Removed the translated `# Mục lục` running header from the start of `vi/parts/part-003.md`; the Markdown rules require page headers to be omitted.
- No prose, technical term, page reference, or cross-part ownership was rewritten.

## Verification

- Reviewed source local pages 9-10 of part-002 and 1-2 of part-003 with `pdftotext -layout` and rendered-page inspection; both PDFs contain 10 pages.
- Re-read the corrected translation tails/heads and checked source order, entry count, hierarchy, terminology, duplicate/missing text, and Markdown structure.
- Ran `git diff --no-index --check` against each untracked assigned file; no whitespace errors were reported.
- Boundary review result: **pass; no unresolved issue**.
