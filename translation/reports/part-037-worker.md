# Part 037 Worker Report

- Part: `part-037`
- Source: `parts/part-037.pdf`, pages 1-10 (printed pages 328-337)
- Source extraction: compared `pdftotext -layout` with raw `pdftotext` for all 10 pages and rendered all 10 pages for visual verification. Layout extraction was used as the primary reconstruction; raw extraction was checked where table/output wrapping was ambiguous. No unresolved extraction ambiguity was found.
- Context: Read the last 2 pages of `part-036.pdf` and the first 2 pages of `part-038.pdf` for boundary context only.
- Translation output: `vi/parts/part-037.md`
- Metadata output: `vi/metadata/part-037.md`
- Prose coverage: complete for the current part; all paragraphs, headings, bullets, explanations, examples, permission synopses, and sequence-permission discussion were translated without summary or additions.
- Code/SQL/command/output fidelity: preserved; SQL, `psql` commands, prompts, result sets, ACL strings, identifiers, comments, and error/output text were not translated, modernized, repaired, or completed from neighbor context.
- Boundary state: begins inside the `perm_test` result-set/output block continued from part-036 and ends after a complete paragraph, before the next paragraph in part-038. No neighbor prose or output was copied into the output.
- Self-review: checked omissions, duplication, source ownership, terminology, Markdown fences, code/output fidelity, list continuity, table/result-set wrapping, and both boundary states against layout extraction, raw extraction, and rendered pages.
- Verification: output, metadata, and report are non-empty and are limited to the assigned part.
- Unresolved issues: none.
