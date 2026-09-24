# Boundary Review: part-070 <-> part-071

- Wave: `B`
- Scope: `part-070` final two source/translation pages and `part-071` initial two source/translation pages only.
- Source checked: `parts/part-070.pdf` printed pages 666-667 (PDF pages 9-10) and `parts/part-071.pdf` printed pages 668-669 (PDF pages 1-2), using layout extraction and raw text comparison.
- Translation checked: `vi/parts/part-070.md:289-295` and `vi/parts/part-071.md:1-67`.
- Instructions checked: `prompts/boundary-review-agent.md`, `00-core-rules.md`, `01-translation-style.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Sentence/paragraph continuity:** Part 070 ends after the complete `Disaster recovery with pgbackrest` introduction and the three-item list `WAL-E`, `pgbarman`, and `OmniPITR`. Part 071 begins with the complete new paragraph corresponding to “There are many others”; no sentence or paragraph is cut across the junction.
- **List/table/result/code continuity:** The source list is complete in part 070 and is complete in the translation. Part 071's feature list starts after the new paragraph and remains source-owned by part 071. No table, result set, SQL statement, `psql` session, or terminal block crosses this boundary.
- **Query plan continuity:** No `EXPLAIN` plan or plan tree crosses the boundary.
- **Caption/figure continuity:** No figure or caption crosses the boundary.
- **Terminology:** `pgbackrest`, disaster recovery, PITR, tool, server, repository, backup, base backup, incremental backup, differential backup, stanza, and public key exchange remain technically identifiable and continuous across the junction. Executable identifiers and URLs in the checked pages are preserved.
- **Duplication/missing content:** The final part-070 tool list is not repeated in part 071, and the opening comparison paragraph and subsequent `pgbackrest` feature/setup content are present in the expected source order. No source-owned content is duplicated or omitted at the junction.
- **Markdown:** Part 070 ends with ordinary list items, and part 071 starts with ordinary prose. There is no open code fence, list continuation, heading transition, or malformed Markdown construct at the junction. The first code block in part 071 is opened and closed within part 071.

## Changes

- No translation, metadata, or worker-report edit was required; the junction already matches source ownership, continuity, and structure.

## Verification

- Compared source layout/raw extraction and the translated first/last regions at printed pages 666-669.
- Rechecked the junction for sentence and list boundaries, technical terminology, duplication, omission, executable-content fidelity, and Markdown structure.
- Boundary review result: **pass; no unresolved issue**.
