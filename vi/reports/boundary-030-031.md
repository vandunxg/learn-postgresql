# Boundary Review: part-030 <-> part-031

## Scope

- Wave B boundary only: `part-030` -> `part-031`.
- Compared the last two pages of `parts/part-030.pdf` (PDF pages 9-10, printed pages 266-267) with the first two pages of `parts/part-031.pdf` (PDF pages 1-2, printed pages 268-269), using layout extraction, raw extraction, and rendered-page checks.
- Checked the translated tail of `vi/parts/part-030.md` (lines 306-382) and head of `vi/parts/part-031.md` (lines 1-57) against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is a paragraph boundary. Part 030 ends with the complete `Summary` paragraph on printed page 267; part 031 begins with the complete paragraph introducing trigger variables. No sentence or paragraph continues across the junction.
- The executable and output blocks near the left boundary are closed before `Summary`. Part 031 begins with prose and a new bullet list, so no SQL, code, `psql` session, terminal output, query result, or code fence crosses the boundary.
- No table, query plan, figure/caption, or list is split across this part boundary. The knowledge-check list starts wholly in part 031 and continues within that part only.
- Technical terminology is continuous and source-grounded across the junction, including `trigger`, `rule`, `event trigger`, `DDL`, `NEW`, `OLD`, and `TG_OP`. Technical identifiers, SQL fragments, URLs, and output in the checked source blocks are preserved.
- No missing or duplicated source content was found at the junction. The translated `Summary` and the opening trigger-variable paragraph preserve source order and meaning without preference-only rewrites.

## Changes

- No edit was justified in `vi/parts/part-030.md` or `vi/parts/part-031.md`.
- Added this boundary report only.

## Verification

- Verified both source PDFs contain 10 pages with `pdfinfo`.
- Compared `pdftotext -layout` and raw `pdftotext` for part-030 pages 9-10 and part-031 pages 1-2.
- Rendered and visually checked the same source pages.
- Re-read the translated tail/head and confirmed paragraph order, list ownership, closed code fences, technical terminology, and source ownership.
- Boundary review result: **pass; no unresolved issue**.
