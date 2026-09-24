# Boundary Review: part-046 <-> part-047

- Wave: `B`
- Scope: `part-046` final two PDF pages and `part-047` initial two PDF pages only.
- Source checked: `parts/part-046.pdf` PDF pages 9-10 (printed pages 426-427) and `parts/part-047.pdf` PDF pages 1-2 (printed pages 428-429), using layout extraction.
- Translation checked: `vi/parts/part-046.md` lines 280-315 and `vi/parts/part-047.md` lines 1-80.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Sentence/paragraph continuity:** Source part 046 ends with a complete paragraph explaining that `CASCADE` drops the dependent user-defined `get_max()` function. Source part 047 then starts with a separate complete callout explaining what `get_max()` is, followed by a new summary paragraph. The translation preserves the same separation and meaning; no sentence or paragraph is cut, duplicated, or omitted at the boundary.
- **List/table/result/code continuity:** Part 046's final `DROP EXTENSION plperl, plpgsql CASCADE` `psql` block is complete, including the `NOTICE` and `DROP EXTENSION` output. Part 047 begins with prose and then starts new sections and complete command blocks. No list, table, result set, SQL statement, code fence, or `psql` session crosses the junction.
- **Query-plan continuity:** No `EXPLAIN` output or query-plan tree appears at either endpoint.
- **Caption/figure continuity:** No caption or figure crosses this boundary.
- **Technical fidelity:** The translation preserves `get_max()`, `PL/PgSQL`, `PostgreSQL`, `Docker`, `CASCADE`, extension terminology, and the executable/output block without translating or modernizing technical content.
- **Terminology:** `extension`, `database`, `cluster`, `function`, `PGXN`, `pgxnclient`, `psql`, and command-line terminology remain coherent across the junction and follow the glossary baseline.
- **Duplication/omission and ownership:** The source's final `get_max()` dependency explanation belongs to part 046, while the explanatory callout and summary belong to part 047; each appears once in the corresponding translation. No neighbor content was copied across ownership.

## Result

Boundary review result: **pass; no unresolved issue**. No edits were made to either assigned part; this report is the only pair-scoped file added.
