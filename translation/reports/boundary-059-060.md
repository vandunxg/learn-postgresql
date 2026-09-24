# Boundary Review: part-059 <-> part-060

- Wave: `A`
- Scope: `part-059` final source/translation pages and `part-060` initial source/translation pages only.
- Source checked: `parts/part-059.pdf` printed page 557 (PDF page 10) and `parts/part-060.pdf` printed page 558 (PDF page 1), using `pdftotext -layout`, raw extraction, and rendered-page checks.
- Translation checked: `vi/parts/part-059.md` tail and `vi/parts/part-060.md` head.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- The source boundary is inside one `pg_restore` terminal-output block. Part 059 ends after `pg_restore: finished item 3387 SEQUENCE SET tags_pk_seq`; part 060 continues with `pg_restore: finished item 3220 FK CONSTRAINT ...`, `pg_restore: finished main parallel loop`, and the following explanatory paragraph.
- The source then starts the `Backup automation` section in part 060. No sentence, prose paragraph, numbered/bullet list, table/result set, SQL statement, `psql` session, `EXPLAIN` plan, figure, or caption crosses this boundary.
- Before review, part 059 incorrectly continued with the entire `Backup automation` section and the beginning of `COPY`, while part 060 already contained that source-owned content. This caused duplicated content and assigned part-060 material to part 059.
- The misowned tail was removed from part 059. Part 060 was left unchanged because its opening output continuation and subsequent prose match the source ownership.
- The `pg_restore` commands, prompts, output lines, identifiers, and technical terminology at the junction remain unchanged. No source content is missing after the ownership correction.

## Changes

- Truncated `vi/parts/part-059.md` at its source-owned final `pg_restore` output line.
- Corrected the part-059 metadata and worker report to record the right-boundary code/output continuation.

## Verification

- Compared source layout/raw extraction and rendered images for printed pages 557-558.
- Checked translation tail/head for code-fence ownership, output fidelity, prose/list continuity, terminology, duplication, and omissions.
- Boundary review result: **pass after minimal correction; no unresolved issue**.
