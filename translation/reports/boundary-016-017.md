# Boundary Review: part-016 <-> part-017

- Wave: B
- Scope: Only the `part-016` -> `part-017` junction
- Source authority: `parts/part-016.pdf` last 2 pages (printed pages 126-127; PDF pages 9-10) and `parts/part-017.pdf` first 2 pages (printed pages 128-129; PDF pages 1-2)
- Translation files: `vi/parts/part-016.md`, `vi/parts/part-017.md`
- Rules checked: core, translation style, PostgreSQL glossary, boundary context, Markdown preservation, SQL/code/output fidelity, and table/diagram/query-plan preservation

## Boundary Evidence

- Source part 016 ends item 3 of the `FULL OUTER JOIN` example with its complete SQL block, result set, and the explanation that the query returns records having posts and categories.
- Source part 017 begins numbered item 4, continuing the `FULL OUTER JOIN` example. Its complete `full outer join` SQL/result, Figure 5.5 caption, comparison with `cross join`, and the beginning of the next `LATERAL JOIN` section are owned by part 017.
- Translation part 016 preserves the item-3 SQL/output and now includes the missing closing explanation at `vi/parts/part-016.md:351`; the same sentence was also removed from its incorrect earlier location after the first INNER JOIN result.
- Translation part 017 begins at numbered item 4 and preserves the full outer join SQL/output, Figure 5.5 caption, cross-join SQL/output, and the `LATERAL JOIN` heading/prose in source order.

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Sentence/paragraph continuation | PASS after fix | Part 016 now ends with the source's item-3 explanation. Part 017 starts a new numbered item and does not fabricate a sentence continuation. |
| List continuation | PASS | The `FULL OUTER JOIN` procedure ends at item 3 in part 016 and continues at item 4 in part 017; numbering and ownership are preserved. |
| SQL/code block continuation | PASS | Part 016's item-3 `INNER JOIN` block is complete. Part 017's item-4 `FULL OUTER JOIN` block starts and ends within part 017. |
| `psql` session continuation | PASS | Prompts and command/output ordering are preserved; no prompt or session state is missing at the junction. |
| Query result continuation | PASS | The item-3 three-row result belongs to part 016, while the item-4 seven-row result belongs to part 017. Neither is duplicated or split across this boundary. |
| Table/result-set fidelity | PASS | Column order, row order, NULL literals, row counts, identifiers, and output values in the checked source pages are retained. |
| `EXPLAIN` plan tree continuation | N/A | No `EXPLAIN` or query-plan output occurs at this boundary. |
| Caption/figure continuation | PASS | Figure 5.5 and its caption occur wholly in part 017 and are retained at `vi/parts/part-017.md:18-20`. |
| Terminology continuity | PASS | `FULL OUTER JOIN`, `left join`, `right join`, `cross join`, `Cartesian product`, `table`, `record`, `category`, and `result` remain consistent across the junction. |
| Duplicated or missing text | PASS after fix | One source sentence was missing at the end of part 016 and had been duplicated at an earlier unrelated location; it was restored at the source location and removed from the misplaced location. No other omission or duplication was found in the checked boundary pages. |
| Source ownership | PASS | Part 016 retains item 3 and its explanation; part 017 owns item 4 onward. No content was moved across the boundary. |

## Fixes

- Restored the source's item-3 closing explanation in `vi/parts/part-016.md:351`:
  `Query này trả về tất cả record có post (trong table new_post) và category.`
- Removed the same misplaced sentence from the earlier INNER JOIN section in `vi/parts/part-016.md`.
- No other translation or formatting change was made.

## Unresolved Fields

- Boundary issue: none after the fix.
- Figure asset packaging: no separate Figure 5.5 asset exists in the repository; the source caption is retained. This is not a continuity defect.
