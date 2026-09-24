# Boundary Review: part-074 <-> part-075

- Wave: `B`
- Scope: `part-074` final two source/translation pages and `part-075` initial two source/translation pages only.
- Source checked: `parts/part-074.pdf` PDF pages 9-10 (printed pages 706-707) and `parts/part-075.pdf` PDF pages 1-2 (printed pages 708-709), using layout/plain text extraction and rendered-page checks.
- Translation checked: `vi/parts/part-074.md` tail and `vi/parts/part-075.md` head.
- Instructions checked: `prompts/boundary-review-agent.md`, `instructions/00-core-rules.md`, `instructions/01-translation-style.md`, `instructions/02-postgresql-glossary.md`, `instructions/04-boundary-context.md`, `instructions/05-markdown-preservation.md`, `instructions/06-sql-code-output-fidelity.md`, and `instructions/07-table-diagram-query-plan.md`.

## Findings

- **Continuity:** The source boundary is inside the alphabetical index. Part 074 ends printed page 707 with the complete `subqueries` entry and its five child entries (`EXISTS`, `IN`, `NOT EXISTS`, `NOT IN`, and `using`). Part 075 begins printed page 708 with the next top-level entry, `synchronous replication`, followed by its `cascading replication` and `delayed replication` children and the separate PostgreSQL-settings entry. The translation preserves this order and ownership.
- **Markdown:** The `S` section and nested list remain in part 074; part 075 correctly continues the list without inventing or repeating an `S` heading, then starts `T` at the source boundary. Indentation and list nesting are valid; running headers, page numbers, and blank source-page artifacts are not copied into the boundary content.
- **Fidelity:** Index labels, technical terms, identifiers, and page references match the source at both endpoints. `synchronous replication`, `cascading replication`, `delayed replication`, `PostgreSQL`, `primary server`, and `standby server` retain appropriate technical spelling/casing. Natural-language index labels are translated without changing their references.
- **Other constructs:** No sentence, prose paragraph, SQL/code block, `psql` session, terminal output, query result, table, `EXPLAIN` plan, figure, or caption crosses this boundary.
- **Missing/duplicate content:** None found. The complete `subqueries` group is present only in part 074, and the complete `synchronous replication` group begins only in part 075.

## Result

Boundary passes. No edits were made to `vi/parts/part-074.md` or `vi/parts/part-075.md`.
