# Boundary Review: part-073 <-> part-074

- Wave: `A`
- Scope: `part-073` final two source/translation pages and `part-074` initial two source/translation pages only.
- Source checked: `parts/part-073.pdf` PDF pages 9-10 (printed pages 696-697) and `parts/part-074.pdf` PDF pages 1-2 (printed pages 698-699), using layout/raw text extraction and rendered-page checks.
- Translation checked: `vi/parts/part-073.md` tail and `vi/parts/part-074.md` head.
- Instructions checked: `00-core-rules.md`, `01-translation-style.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Continuity:** The source boundary is inside the book index list. Part 073 ends the `basic statement window functions` group with `LEAD 164`; part 074 continues the same group with `NTILE 165, 166`, followed by `ORDER BY clause`, `PARTITION BY function`, `RANK`, `ROW_NUMBER`, and `WINDOW clause`. The translation preserves this order and the two-space nested-list indentation.
- **Ownership:** Part 073 contains the source-owned Packt notices and index entries through `LEAD 164`. Part 074 starts with `NTILE 165, 166` and contains only its visible continuation through `DELETE rules` on printed page 699. No neighbor content was copied across the boundary.
- **Constructs:** No sentence, prose paragraph, SQL/code block, `psql` session, terminal output, table/result set, query plan, figure, or caption crosses this boundary. The only continuing construct is the index list.
- **Fidelity:** Index labels, function names, PostgreSQL terms, configuration parameters, command names, and page references at both edges are present with no missing or duplicated boundary entry. The repeated `configuration errors` entry within part 074 is present in the source twice and is therefore not a duplicate error.
- **Terminology:** Technical terms and identifiers such as `NTILE`, `ORDER BY`, `PARTITION BY`, `ROW_NUMBER`, `WINDOW`, `Bitmap Heap Scan`, `BRIN`, `PostgreSQL`, `pg_ctl`, `psql`, and `COPY` retain their source spelling/casing and remain continuous.
- **Missing/duplicate content:** None found.

## Result

Boundary passes. No edits were made to either assigned translation part.
