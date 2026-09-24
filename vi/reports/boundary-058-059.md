# Boundary Review: part-058 <-> part-059

- Wave: `B`
- Scope: `part-058` final source/translation page and `part-059` initial source/translation page only.
- Source checked: `parts/part-058.pdf` printed page 547 and `parts/part-059.pdf` printed page 548, using layout and raw extraction.
- Translation checked: `vi/parts/part-058.md` lines 307-320 and `vi/parts/part-059.md` lines 1-27.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Continuity:** The source boundary is a paragraph boundary within the `Limiting the amount of data to backup` section. Part 058 ends with the complete paragraph describing separate schema/content backups and the `-s`, `-a`, `COPY`, and `--inserts` commands. Part 059 begins the next complete paragraph about `-t` and `-T` table filters. No sentence is cut.
- **Ownership:** The closing paragraph is present only in part 058 (translation line 320), and the table-scope paragraph is present only in part 059 (translation line 1). No prose, heading, list, or code/output block is moved across the boundary.
- **Technical structures:** No SQL statement, `psql` session, terminal-output block, result set, table, figure/caption, or query-plan tree continues across this boundary. The part-059 opening commands are correctly fenced as `text` and preserve command flags and identifiers.
- **Fidelity defect corrected:** Source printed page 548 uses `forum.users_pk_seq` in both the include and exclude commands. The translation previously had `forum.user_pk_seq` at lines 4 and 10, which changed the sequence identifier. Both occurrences were corrected to `forum.users_pk_seq`.
- **Terminology:** `pg_dump`, `schema`, `table`, `sequence`, `-t`, `-T`, `-s`, `-a`, `COPY`, `INSERT`, and `--inserts` remain technically recognizable and consistent across the boundary.
- **Duplication/missing text:** No duplicated or missing source content was found at the boundary after the identifier correction.

## Changes

- Corrected `forum.user_pk_seq` to `forum.users_pk_seq` in the two opening `pg_dump` commands in `vi/parts/part-059.md`.
- No changes were needed in `vi/parts/part-058.md`.

## Result

Boundary passes after the minimal identifier correction; no unresolved issue remains.
