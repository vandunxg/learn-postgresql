# Boundary Review: part-024 <-> part-025

## Scope

- Wave B boundary only: `part-024` -> `part-025`.
- Compared the final two source pages of `parts/part-024.pdf` (PDF pages 9-10, printed pages 206-207) with the initial two source pages of `parts/part-025.pdf` (PDF pages 1-2, printed pages 208-209).
- Checked the translated junction in `vi/parts/part-024.md` lines 363-384 and `vi/parts/part-025.md` lines 1-80 against the core, glossary, Markdown, SQL/code/output, table/plan, and boundary rules.

## Boundary Evidence

- The source boundary falls between printed pages 207 and 208. Part 024 ends with the complete `delete_posts` function definition and the complete result set showing the state before the function call, including `(3 rows)`.
- Part 025 begins with a new complete paragraph explaining deletion of the record whose title is `A view of Data types in C++`, then introduces the foreign-key cleanup and its complete `delete from j_posts_tags` example.
- Translation part 024 preserves the complete ending result set at lines 374-384. Translation part 025 starts the matching paragraph at lines 1-8 and preserves the SQL/output block at lines 3-6 without importing or repeating part-024 content.
- The later `delete_posts` result and the `setof` explanation are wholly owned by part 025. The source's stray closing `)` after the later `(1 row)` is also present in the translation at line 66, so it is not a boundary duplication or omission.

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Sentence/paragraph continuation | PASS | Part 024 ends at a complete paragraph/result example; part 025 starts a complete new paragraph and does not repeat or fabricate a continuation. |
| List/table continuation | PASS | No numbered or bulleted list, Markdown table, or source table crosses the junction. The result set at the end of part 024 is complete. |
| SQL/code block continuation | PASS | The `delete_posts` definition and pre-call query block close in part 024. Part 025 starts a separate `delete from j_posts_tags` block; no SQL statement or fence crosses the boundary. |
| `psql` session continuation | PASS | No active fenced `psql` session is cut at the boundary. The `forumdb=>` example in part 025 begins a new source example and its prompt/output are preserved. |
| Query result continuation | PASS | The part-024 `select pk,title from posts order by pk` result is complete through `(3 rows)`; part 025's delete-call result is complete within part 025. |
| `EXPLAIN` plan tree continuation | N/A | No `EXPLAIN` or query-plan output occurs at this boundary. |
| Caption/figure continuation | N/A | No figure or caption occurs at this boundary. |
| Terminology continuity | PASS | `function`, `primary key`, `foreign key`, `table`, `record`, `result set`, `data type`, `setof`, `posts`, and `j_posts_tags` remain source-faithful and consistent with the glossary. |
| Duplicated or missing text | PASS | The ending function/result in part 024 and the opening deletion paragraph/SQL in part 025 each appear once in the correct part; no neighboring content was re-owned. |
| Source ownership | PASS | Part 024 contains source content through printed page 207; part 025 begins with printed page 208 content. |

## Changes

- No edit was justified in `vi/parts/part-024.md` or `vi/parts/part-025.md`.
- This report is the only file added by the boundary review.

## Verification

- Checked `pdftotext -layout` and `pdftotext -raw` extraction for the source tails and heads.
- Checked translated tail/head against source order, paragraph and code-fence structure, SQL/output fidelity, result-set completeness, ownership, terminology, and duplicate/missing content.
- Boundary review result: **pass; no unresolved issue**.
