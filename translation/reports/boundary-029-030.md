# Boundary Review: part-029 <-> part-030

## Scope

- Wave A boundary only: `part-029` -> `part-030`.
- Compared the final two pages of `parts/part-029.pdf` (PDF pages 9-10, printed pages 256-257) with the initial two pages of `parts/part-030.pdf` (PDF pages 1-2, printed pages 258-259).
- Checked the translated tail of `vi/parts/part-029.md` and head of `vi/parts/part-030.md` against the core rules, PostgreSQL glossary, SQL/code fidelity rules, Markdown rules, and boundary rules.

## Findings

- The actual part boundary is a paragraph boundary. Part 029 ends after the paragraph explaining that the next step is to extend the function for `DELETE` and `UPDATE`; part 030 begins with the paragraph introducing `fcopy_tags()` for all three events. No sentence, paragraph, list, SQL statement, `psql` session, result set, or code block is incorrectly continued across the part boundary.
- The final source result set for `new_a_tags` continues across printed pages 256-257. The translation had incorrectly closed and reopened the fenced block between the query prompt and its rows. The result set is now represented as one continuous fenced `text` block.
- The source SQL, PL/pgSQL, prompts, output values, identifiers, row counts, headings, URL, and ordered list items in the checked pages are present with no duplicate or missing content. No source typo was modernized or corrected inside executable/output content.
- Trigger terminology and identifiers remain continuous across the junction, including `TG_OP`, `NEW`, `OLD`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `fcopy_tags()`, and `tcopy_tags`.
- Replaced the isolated English adjective `elegant` with `gọn gàng` in the translated prose; this does not alter the technical meaning.

## Changes

- `vi/parts/part-029.md`: merged the split `new_a_tags` result into one Markdown fence and made the minimal prose wording correction noted above.
- `vi/parts/part-030.md`: no edit required.

## Verification

- Verified both PDFs contain 10 pages with `pdfinfo`.
- Verified source extraction with `pdftotext -layout` for part-029 pages 9-10 and part-030 pages 1-2.
- Re-read the edited tail/head and confirmed the result-set rows, code-fence ownership, boundary paragraph order, and technical identifiers.
- `git diff --no-index --check /dev/null vi/parts/part-029.md` and the equivalent report-file check produced no whitespace errors; the checked part files have balanced Markdown fence counts (20 and 34 markers).
- Boundary review result: **pass; no unresolved issue**.
