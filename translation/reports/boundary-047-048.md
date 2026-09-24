# Boundary Review: part-047 <-> part-048

- Wave: `A`
- Scope: `part-047` final two PDF pages and `part-048` initial two PDF pages only.
- Source checked: `parts/part-047.pdf` printed pages 436-437 and `parts/part-048.pdf` printed pages 438-439, using layout extraction and rendered-page inspection.
- Translation checked: `vi/parts/part-047.md` lines 287-316 and `vi/parts/part-048.md` lines 1-32.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Sentence/paragraph continuity:** Source printed page 437 ends the `Removing an installed extension` subsection with a complete paragraph: removing unused extensions keeps the cluster clean and avoids unwanted object dependencies. The translation ends the same thought at `part-047.md:314-316`. Source printed page 438 then starts a new paragraph about issuing `DROP EXTENSION`; `part-048.md:1` starts the same new paragraph. There is no sentence or paragraph cut, duplication, or omission.
- **SQL/code/`psql`/output continuity:** The final `psql` blocks in part 047 are complete before the boundary. Part 048 owns a complete `psql` session for `DROP EXTENSION orafce` and a complete `\dx`/error output block (`part-048.md:3-30`). Prompts, SQL, identifiers, literals, output text, and the source `ù` glyph are preserved. No executable block requires reconciliation across the boundary.
- **Table/result/list continuity:** The `\dx` result in part 048 is self-contained and ends with `(2 rows)` before the following query/error output. No table, result set, numbered/bullet list, or other structured list crosses the boundary.
- **Query-plan continuity:** No `EXPLAIN` or query-plan tree appears at either endpoint.
- **Caption/figure continuity:** No figure or caption appears at either endpoint.
- **Terminology:** `extension`, `database`, `cluster`, `superuser`, `statement`, `DROP EXTENSION`, `orafce`, `psql`, `\\dx`, and `DUAL` remain technically consistent across the junction and preserve required casing/inline-code treatment.
- **Ownership:** Part 047 retains the complete removal introduction; part 048 begins with the source-owned `DROP EXTENSION` explanation and example. No neighbor content was copied into either translation.

## Result

No boundary issue found. No edits were made to either assigned part.
