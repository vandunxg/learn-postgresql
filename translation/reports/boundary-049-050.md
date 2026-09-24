# Boundary Review: part-049 <-> part-050

- Wave: `A`
- Scope: `part-049` final PDF page and `part-050` initial PDF page only.
- Source checked: `parts/part-049.pdf` printed page 457 and `parts/part-050.pdf` printed page 458, using layout and raw text extraction.
- Translation checked: `vi/parts/part-049.md:183-185` and `vi/parts/part-050.md:1-5`.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Sentence/paragraph continuity:** The source completes the `Gather nodes` paragraph in part-049 with `Gather Merge node.` Part-050 then starts a new paragraph, `Gather nodes are responsible...`; it does not continue the preceding sentence. The translation had omitted the source-owned `Gather Merge node.` and used singular `Gather node` at the new paragraph head. Both issues were corrected locally.
- **List/table/result/code continuity:** No list, table, query result, SQL statement, code block, or `psql` session crosses this boundary.
- **Query-plan continuity:** No `EXPLAIN` plan or plan tree appears at either endpoint.
- **Caption/figure continuity:** No caption or figure crosses this boundary.
- **Terminology:** `Gather`, `Gather Merge`, parallel nodes, and `parallel execution plan` remain technically identifiable and consistent with the source.
- **Duplication/missing content:** Before correction, `Gather Merge node.` was missing from the translation. After correction, the source tail and head are complete with no duplicated prose or neighbor content copied across ownership.

## Changes

- Restored `Gather Merge node.` at `vi/parts/part-049.md:185`.
- Changed the opening of `vi/parts/part-050.md:1` to plural `Các Gather node` to match source `Gather nodes`.
- No other translation or source-owned content was changed.

## Result

Boundary review result: **pass; no unresolved issue**.
