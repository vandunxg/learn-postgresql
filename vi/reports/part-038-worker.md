# Part 038 Worker Report

- Part: `part-038`
- Source: `parts/part-038.pdf`, pages 1-10 (printed pages 338-347)
- Source extraction: compared `pdftotext -layout` with raw `pdftotext` for all 10 pages; rendered all 10 pages for visual verification. No unresolved extraction ambiguity was found.
- Context: Read the last 2 pages of `part-037.pdf` and the first 2 pages of `part-039.pdf` for boundary context only.
- Translation output: `vi/parts/part-038.md`
- Metadata output: `vi/metadata/part-038.md`
- Prose coverage: complete for the current part; all continuation prose, headings, paragraphs, bullets, callouts, examples, and the policy syntax fragment were translated without summary or additions. The continuation of the policy syntax and its explanations in part-039 were not copied.
- Code/SQL/command/output fidelity: preserved; SQL, routine definitions, shell commands, `psql` prompts, result sets, identifiers, catalog names, error messages, ACL output, and the cut-off policy syntax were not translated, modernized, repaired, or completed from neighbor context.
- Boundary state: begins inside the paragraph continuing sequence permissions from part-037; ends inside the policy SQL/code block after `FOR <statement>`, before the continuation in part-039. No neighbor content was copied into the output.
- Self-review: checked omissions, duplication, source ownership, terminology, Markdown fences, code/output fidelity, list continuity, callouts, and both boundary states against layout extraction, raw extraction, and rendered pages.
- Verification: output, metadata, and report are non-empty and limited to the assigned part.
- Unresolved issues: none.
