# Part-001 Worker Report

## Scope

- Translated all source content owned by local PDF pages 1-10.
- Read the full current PDF, all instruction files, `vi/GLOSSARY.md`, and the first two pages of `part-002.pdf` as read-only context.

## Extraction

- Compared `pdftotext -layout` and `pdftotext -raw` for the current PDF.
- Rendered page 1 because the cover text was not present in text extraction; the visible cover prose was included.
- No unresolved extraction issue remains.

## Self-review

- Front matter, dedications, contributor biographies, Discord notice, and all table-of-contents entries through `Making a database copy • 79` are present.
- The repeated cover/title-page material is intentional source content, not an accidental duplicate.
- URL, ISBN, names, version number, numeric literal, executable/tool names, identifiers, and other technical literals were preserved.
- No SQL, code, command, output, table result, or query plan occurs in this part.
- No neighbor content was copied into the output.
- Boundary metadata records that the source ends inside the Chapter 4 table-of-contents list.

## Output check

- `vi/parts/part-001.md` is non-empty.
- `vi/metadata/part-001.md` is non-empty.
- `vi/reports/part-001-worker.md` is non-empty.
