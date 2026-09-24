# Boundary Review: part-015 <-> part-016

- Wave: A
- Scope: Only the 015 -> 016 junction
- Source authority: `parts/part-015.pdf` printed pages 116-117 and `parts/part-016.pdf` printed pages 118-119 (PDF pages 9-10 and 1-2 respectively)
- Translation files: `vi/parts/part-015.md`, `vi/parts/part-016.md`

## Boundary Evidence

- Source part 015 ends with the complete comma-join query and its complete 15-row result set, ending with `(15 rows)`.
- Source part 016 begins with the explanation that this query creates a Cartesian product, then gives the Figure 5.1 caption and the equivalent `CROSS JOIN` query with its complete 15-row result set.
- Translation part 015 preserves the introductory paragraph, SQL block, all 15 result rows, and `(15 rows)` at lines 390-413.
- Translation part 016 resumes with the matching explanation at lines 1-5, preserves the Figure 5.1 caption, and preserves the equivalent SQL/output at lines 7-28.

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Sentence/paragraph continuation | PASS | Part 015's introductory paragraph ends with a colon before the complete result block; part 016 starts the next source paragraph, not a fabricated continuation or closure. |
| List/table continuation | PASS | The part 015 result set is complete with 15 rows. No table or list is cut across the junction. |
| SQL/code block continuation | PASS | The comma-join SQL block ends in part 015. The separate `CROSS JOIN` block starts and ends in part 016. |
| `psql` session continuation | PASS | Prompts and session text are preserved on both sides; no prompt or session state is missing at the junction. |
| Query result continuation | PASS | Both source result sets are complete and retained. The repeated rows are intentional because the source demonstrates equivalent query forms. |
| `EXPLAIN` plan tree continuation | N/A | No `EXPLAIN` or query-plan output occurs at this boundary. |
| Caption/figure continuation | PASS | Figure 5.1 and its caption belong to the opening content of part 016; the caption is retained at `vi/parts/part-016.md:3`. |
| Terminology continuity | PASS | `Cartesian product`, `cross join`, `category`, `posts`, `table`, and `query` remain consistent with the source and glossary baseline. |
| Duplicated or missing text | PASS | No cross-boundary prose, code, output, or caption is duplicated or omitted. |
| Source ownership | PASS | No content from part 016 was copied into part 015, and no part 015 content was improperly re-owned by part 016. |

## Fixes

- No boundary fix required.
- No preference rewrite made.

## Unresolved Fields

- Boundary issue: none.
- Figure asset packaging: no separate Figure 5.1 asset exists in the repository; the caption is retained. This is not a 015 -> 016 continuity defect and is not changed by this review.
