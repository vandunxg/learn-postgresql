# Boundary Report

- Left part: `part-020` (Wave B)
- Right part: `part-021` (Wave B)
- Source checked: yes - `parts/part-020.pdf` page 10 (printed page 167) and `parts/part-021.pdf` pages 1-2 (printed pages 168-169), using layout extraction and rendered-page review
- Translation checked: yes - `vi/parts/part-020.md` lines 394-401 and `vi/parts/part-021.md` lines 1-68
- Sentence continuity: pass - part-020 ends after the complete frame-clause introduction and two-item list; part-021 begins a complete sentence explaining when the frame clause is meaningful
- Paragraph continuity: pass - the source paragraph transition is preserved without an invented continuation, omission, or boundary duplication
- SQL/code continuity: pass - no SQL/code block crosses the part boundary; the SQL blocks beginning in part-021 retain prompts, identifiers, commands, output values, and row counts
- Table/result continuity: pass - no table or query result crosses the part boundary; the incremental-sum table and result set in part-021 match the source
- Query plan continuity: n-a - no query plan is present at this boundary
- List continuity: pass - the complete two-item frame-clause list remains in part-020, and part-021 starts a new section without a list fragment
- Terminology continuity: pass - `frame clause`, `ROWS BETWEEN`, `RANGE BETWEEN`, `ORDER BY`, `row`, `partition`, `window`, `frame_set`, and `PostgreSQL` remain technically consistent
- Missing/duplicate content: none - the source tail and head are represented once, with no cross-boundary text loss
- Changes made: none to either translation; this report is the only file added
- Unresolved issues: none
