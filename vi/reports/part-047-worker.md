# Part 047 Worker Report

- Part: `part-047`
- Source: `parts/part-047.pdf`, pages 1-10 (printed pages 428-437)
- Source extraction: ran full `pdftotext -layout` for part-047 and both neighboring PDFs, compared the current part with raw `pdftotext`, and rendered all 10 current-part pages plus the last 2 pages of part-046 and first 2 pages of part-048. No unresolved extraction ambiguity was found.
- Context: Read the last 2 pages of `part-046.pdf` and the first 2 pages of `part-048.pdf` for boundary context only.
- Translation output: `vi/parts/part-047.md`
- Metadata output: `vi/metadata/part-047.md`
- Prose coverage: complete for the current part; the opening callouts, PGXN client explanation, installation subsections, command-line help, extension installation workflow, screenshot captions, `orafce` examples, `psql` sessions, and closing removal section were translated without summary or additions.
- Code/SQL/command/output fidelity: preserved; shell commands, `pgxn` help output, `psql` prompts, SQL, result sets, identifiers, literals, version values, and source line wrapping were not translated, modernized, repaired, or completed from neighbor context.
- Figures: Figures 12.1-12.3 are present in the PDF as screenshots. Their captions were translated and retained. The repository has no source image assets, so no unsupported image references were added.
- Boundary state: begins with a complete callout after part-046's completed `get_max()` dependency example and ends with a complete paragraph before part-048's `DROP EXTENSION orafce` example. No neighbor content was copied into the output.
- Self-review: checked omissions, duplication, source ownership, terminology, Markdown headings/lists/blockquotes/fences, command and output fidelity, figure captions, and both boundaries against layout extraction, raw extraction, and rendered pages.
- Verification: the three requested output files were written and are non-empty; no other repository files were modified by this worker.
- Unresolved issues: none. Source inconsistencies noted in metadata were preserved as source content, not treated as extraction uncertainty.
