# Part 036 Worker Report

- Part: `part-036`
- Source: `parts/part-036.pdf`, pages 1-10 (printed pages 318-327)
- Source extraction: compared `pdftotext -layout` with raw `pdftotext` for all 10 pages; rendered all 10 pages for visual verification. No unresolved extraction ambiguity was found.
- Context: Read the last 2 pages of `part-035.pdf` and the first 2 pages of `part-037.pdf` for boundary context only.
- Translation output: `vi/parts/part-036.md`
- Metadata output: `vi/metadata/part-036.md`
- Prose coverage: complete for the current part; all paragraphs, headings, bullets, table content, explanations, ACL examples, and the `Default ACLs` opening material were translated without summary or additions. The continuation of the `\dp perm_test` result belongs to part-037 and was not copied.
- Code/SQL/command/output fidelity: preserved; SQL, GRANT/REVOKE statements, shell commands, `psql` prompts, result sets, ACL strings, identifiers, flags, and error messages were not translated, modernized, repaired, or completed from neighbor context.
- Boundary state: begins cleanly after the complete paragraph at the end of part-035; ends inside a `psql` output/result-set block after its column headers, before the continuation in part-037. No neighbor content was copied into the output.
- Self-review: checked omissions, duplication, source ownership, terminology, Markdown fences, code/output fidelity, table rows and order, list continuity, and both boundary states against layout extraction, raw extraction, and rendered pages.
- Verification: output, metadata, and report are non-empty and are limited to the assigned part.
- Unresolved issues: none.
