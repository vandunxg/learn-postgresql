# Boundary Review: part-039 <-> part-040

- Wave: `A`
- Scope: `part-039` final source/translation pages and `part-040` initial source/translation pages only.
- Source checked: `parts/part-039.pdf` printed pages 356-357 and `parts/part-040.pdf` opening pages (the first PDF page is blank; Chapter 11 starts on the following page).
- Translation checked: `vi/parts/part-039.md` tail and `vi/parts/part-040.md` head.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Continuity:** The source ends part 039 after the complete Chapter 10 references and Discord section, including the URL. Part 040 starts with the complete Chapter 11 heading, introduction, and topic list. No sentence, paragraph, section, list, table, caption, figure, `psql` session, SQL/code block, query result, or `EXPLAIN` plan continues across this boundary.
- **Ownership:** The translation keeps the Chapter 10 references and Discord URL in part 039 and starts Chapter 11 in part 040. The blank source PDF page is correctly not emitted as book content.
- **Fidelity:** The Discord URL, headings, list items, identifiers, and technical terms at both endpoints are preserved with no duplicated or missing boundary content. No code/output or table/plan reconciliation is required.
- **Terminology:** `transaction`, `MVCC`, `WALs`, `checkpoint`, and related technical terms remain consistent across the boundary and comply with the glossary/source casing.

## Result

No boundary issue found. No edits were made to either assigned part.
