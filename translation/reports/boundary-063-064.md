# Boundary Review: part-063 <-> part-064

- Wave: `A`
- Scope: Wave A boundary `part-063` -> `part-064` only; no adjacent boundary was reviewed.
- Source checked: `parts/part-063.pdf` final page (printed page 597) and `parts/part-064.pdf` opening page (printed page 598), using layout and raw text extraction.
- Translation checked: `vi/parts/part-063.md:211-228` and `vi/parts/part-064.md:1-18`.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Sentence/paragraph continuity:** The source part 063 endpoint contains the complete `pg_stat_user_tables` query and the first result fragment through `n_tup_del | 63`. Part 064 starts with the next result row, then continues with the source's prose explanation. No sentence or prose paragraph is incorrectly closed, duplicated, or moved across the boundary.
- **List/table/result continuity:** The `pg_stat_user_tables` query result is intentionally cut between `n_tup_del | 63` and `n_tup_upd | 200030`. The translation resumes at exactly that row and preserves the remaining row order, values, blank fields, and `last_autoanalyze` timestamp through the closing fence.
- **SQL/code/`psql` continuity:** The `psql` prompt and complete SQL statement belong to part 063. The output continuation is represented as separate valid `text` fragments: part 063 closes its fragment after the owned final row, and part 064 opens its continuation fragment. No SQL, prompt, identifier, output value, or row is missing or duplicated.
- **Query-plan continuity:** No `EXPLAIN` or query-plan output crosses this boundary.
- **Caption/figure continuity:** No figure or caption crosses this boundary.
- **Terminology:** Technical identifiers and terms remain source-faithful and consistent, including `pg_stat_user_tables`, `n_tup_hot_upd`, `n_live_tup`, `n_dead_tup`, `MVCC`, and `pg_stat_user_indexes`.
- **Duplication/missing text:** No duplicated or missing source content was found at the junction. The existing metadata correctly records that part 063 ends and part 064 begins inside code/output and inside a query result.

## Changes

No edits were made to either assigned translation part; the boundary representation is already valid and requires no pair-only correction.

## Result

Boundary review result: **pass; no unresolved issue**.
