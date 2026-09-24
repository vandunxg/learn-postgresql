# Part 009 Worker Report

## Scope

- Read `prompts/worker-agent.md`, every file in `instructions/`, and `vi/GLOSSARY.md` before translation.
- Read all 10 pages of `parts/part-009.pdf` with `pdftotext -layout`.
- Checked `pdftotext -raw` as alternate extraction.
- Read pages 9-10 of `part-008.pdf` and pages 1-2 of `part-010.pdf` as read-only boundary context.
- Wrote only `vi/parts/part-009.md`, `vi/metadata/part-009.md`, and this report.

## Boundary Review

- Start: complete paragraph on printed page 48; no sentence or SQL fragment is carried over from the previous part.
- Chapter 2 content ends with the Discord section and URL, followed by the Chapter 3 heading and introduction.
- End: after the exact `DROP ROLE` error output on printed page 57. The next part continues with prose explaining that output, so no next-part prose was copied.
- The subsection `Removing an existing role` continues into part-010; this is recorded in metadata.

## Fidelity Self-Review

- Translated all prose, headings, lists, notes/callouts, references, captions/labels, and the Discord invitation in the current part.
- Preserved SQL/DDL statements, shell/psql sessions, commands, identifiers, literals, prompts, notices/errors, spacing-sensitive values, and the source typo `IF EXIST`.
- Removed running headers and printed page numbers; preserved source URLs.
- No extracted QR image asset was available; the Discord invitation prose and URL were preserved, with no invented image reference.
- Checked for omission and duplication against the complete layout extraction and used raw extraction to resolve line-wrap ambiguity.
- Neighbor pages were used only to verify continuity; no neighbor-owned content was added.

## Verification

- `vi/parts/part-009.md` is non-empty.
- `vi/metadata/part-009.md` is non-empty.
- This report is non-empty.
- Output scope is limited to the three assigned part-009 files.
