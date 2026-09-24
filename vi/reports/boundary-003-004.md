# Boundary Review: part-003 <-> part-004

## Scope

- Wave A boundary only: `part-003` -> `part-004`.
- Compared the final two source pages of `parts/part-003.pdf` with the initial two source pages of `parts/part-004.pdf`.
- Checked the translated junction in `vi/parts/part-003.md` lines 225-233 and `vi/parts/part-004.md` lines 1-17 against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is between the complete “Download the color images” material at the end of part 003 and the “Conventions used” section at the start of part 004. No sentence or paragraph continues across the boundary.
- The part-003 software/OS table is complete and no list or table continues into part 004.
- Part 003 has no executable block at the boundary. Part 004 begins its code-convention examples as complete blocks; no SQL, `psql` session, query result, or `EXPLAIN` plan is split.
- No figure or caption continuation crosses the boundary; the color-image PDF URL is preserved at the end of part 003.
- Technical names, URLs, and identifiers remain consistent. No source text is missing or duplicated at the junction.

## Changes

- No edit was justified in either `vi/parts/part-003.md` or `vi/parts/part-004.md`.
- This report is the only file added by the boundary review.

## Verification

- Reviewed source PDF local pages 9-10 of part 003 and 1-2 of part 004, with 10 pages confirmed in each PDF.
- Translation tails and heads were checked against source order, content, ownership, terminology, and Markdown structure.
- Boundary review result: **pass; no unresolved issue**.
