# Boundary Review: part-004 <-> part-005

## Scope

- Wave B boundary only: `part-004` -> `part-005`.
- Compared the final two source pages of `parts/part-004.pdf` with the initial two source pages of `parts/part-005.pdf`.
- Checked the translated junction in `vi/parts/part-004.md` lines 181-206 and `vi/parts/part-005.md` lines 1-15 against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary falls between the complete paragraph stating that PostgreSQL stores user data and internal status on the local filesystem and the next paragraph explaining persistence and the `PGDATA` directory. The Vietnamese translation preserves this paragraph boundary; no sentence or paragraph continues across the boundary.
- No numbered or bulleted list, table, result set, SQL statement, code block, `psql` session, terminal output, `EXPLAIN` plan, figure, or caption crosses the boundary.
- Boundary terminology is continuous: `filesystem`, `PGDATA`, `WALs`, `catalog`, `postmaster`, and `backend process` are represented consistently on both sides. No identifier, command, or literal crosses the boundary.
- The junction contains no duplicated source text and no missing source text. Part 004 retains the final filesystem sentence, while part 005 begins with the complete `PGDATA` paragraph from its own source.

## Changes

- No edit was justified in either `vi/parts/part-004.md` or `vi/parts/part-005.md`.
- This report is the only file added by the boundary review.

## Verification

- Reviewed source PDF local pages 9-10 of part 004 and local pages 1-2 of part 005 with `pdftotext -layout`; both PDFs contain 10 pages.
- Reviewed the translation tail and head against source order, content ownership, paragraph structure, executable-content rules, terminology, and duplicate/missing-text checks.
- Boundary review result: **pass; no unresolved issue**.
