# Boundary Report

- Left part: `part-006`
- Right part: `part-007`
- Source checked: yes (part-006 PDF pages 9-10; part-007 PDF pages 1-2)
- Translation checked: yes
- Sentence continuity: pass
- Paragraph continuity: pass
- SQL/code continuity: pass (the surrounding command and output blocks are complete; no executable block crosses the boundary)
- `psql` session continuity: n-a
- Table/result continuity: n-a
- Query plan continuity: n-a
- List continuity: pass
- Caption/figure continuity: n-a
- Terminology continuity: pass
- Missing/duplicate content: none
- Changes made: none; the junction already matches source ownership and no edit was justified
- Unresolved issues: none

## Findings

- The source ends part 006 after the complete `fast` shutdown-mode bullet on PDF page 27 (local page 10). Part 007 starts with the remaining `immediate` bullet on PDF page 28 (local page 1).
- The translation preserves this list continuation: `vi/parts/part-006.md:260-263` ends with the complete `fast` bullet, and `vi/parts/part-007.md:1-3` begins with the `immediate` bullet. No list item was duplicated or omitted.
- The source's following paragraph and command/output example remain wholly in part 007. The `pg_ctl stop -m smart` command, prompts, output, and error text are preserved as executable/output content in `vi/parts/part-007.md:5-21`.
- The shutdown terminology remains consistent across the junction: `smart mode`, `fast mode`, `immediate mode`, `stop mode`, `cluster`, `client`, and `data integrity` are represented without changing technical meaning.

## Verification

- Reviewed source last two pages of part 006 and first two pages of part 007 with `pdftotext -layout`.
- Reviewed translation tail of part 006 and head of part 007.
- Confirmed the existing metadata records `ends_inside_list: yes` for part 006 and `begins_inside_list: yes` for part 007, matching the observed source boundary.
