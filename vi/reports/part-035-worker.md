# Part 035 Worker Report

- Part: `part-035`
- Source: `parts/part-035.pdf`, pages 1-10 (printed pages 308-317)
- Source extraction: read full `pdftotext -layout` and raw extraction for all 10 pages; rendered all 10 pages and visually checked representative pages containing headings, callouts, code, `psql` output, and the right boundary. No unresolved extraction ambiguity was found.
- Context: Read the last 2 pages of `part-034.pdf` and the first 2 pages of `part-036.pdf` for boundary context only.
- Translation output: `vi/parts/part-035.md`
- Metadata output: `vi/metadata/part-035.md`
- Prose coverage: complete for the current part; all headings, paragraphs, callout text, bullets, explanations, examples, and result-set context were translated without summary or invention. No content from either neighbor was copied.
- Code/SQL/command/output fidelity: preserved; SQL, DDL, shell commands, `psql` meta-command, prompts, result sets, catalog names, identifiers, function/parameter names, URL, and password/hash samples were not translated, modernized, repaired, or completed from neighbor context.
- Boundary state: begins cleanly with `Technical requirements` after the part-034 chapter overview; ends after a complete paragraph under `Role kế thừa từ role khác`, before part-036's new demonstration paragraph. Sentence, paragraph, SQL/code, table/result, query-plan, and list boundaries are clean.
- Self-review: checked omissions, duplication, source ownership, terminology, Markdown headings/fences, code/output fidelity, list continuity, and both boundaries against layout extraction, raw extraction, and rendered pages.
- Verification: output, metadata, and report are non-empty and limited to the assigned part.
- Unresolved issues: none.
