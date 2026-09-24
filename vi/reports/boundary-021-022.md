# Boundary Report

- Left part: `part-021` (Wave A)
- Right part: `part-022` (Wave A)
- Source checked: yes - `parts/part-021.pdf` pages 9-10 (printed pages 176-177) and `parts/part-022.pdf` pages 1-2 (printed pages 178-179), using layout extraction and rendered-page review
- Translation checked: yes - `vi/parts/part-021.md` lines 220-291 and `vi/parts/part-022.md` lines 1-76
- Sentence continuity: pass - part-021 ends with the complete explanation and `RANGE` query/result; part-022 starts a new sentence introducing the `ROWS` query
- Paragraph continuity: pass - the source paragraph transition is preserved without an invented continuation or boundary duplication
- SQL/code continuity: pass - the `RANGE` and `ROWS` blocks are complete, with prompts, identifiers, SQL, output values, and row counts preserved
- Table/result continuity: pass - the result tables and frame table match the source; the source page break inside the frame table is reconstructed in part-021 Markdown
- Query plan continuity: n-a
- List continuity: pass - the final numbered item and its associated explanation in part-021 are complete; no list fragment crosses into part-022
- Terminology continuity: pass - `RANGE`, `ROWS`, frame, row, window function, aggregate, `ORDER BY`, and function/identifier casing remain consistent
- Missing/duplicate content: none
- Changes made: none to either translation; this report is the only boundary-review file added
- Unresolved issues: none
