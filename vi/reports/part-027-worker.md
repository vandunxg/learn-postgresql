# Part 027 Worker Report

- Part: part-027
- Source: `parts/part-027.pdf`, pages 1-10
- Source extraction: `pdftotext -layout` completed for all 10 pages; fallback `pdftotext` was also run and checked for extraction consistency. Running headers, footers, page numbers, and form-feed markers were excluded from the translation output.
- Context: Read the last 2 pages of part-026 and the first 2 pages of part-028 for boundary context only.
- Translation output: `vi/parts/part-027.md`
- Metadata output: `vi/metadata/part-027.md`
- Prose coverage: complete for current-part prose, headings, quotations, references, lists, and examples; no summary or added explanation.
- Code/SQL/command/output fidelity: preserved; PL/pgSQL, SQL fragments, shell commands, `psql` prompts, result sets, identifiers, URLs, and error/output text were not translated or modernized.
- Boundary state: begins at a complete section heading; ends inside the `r_tags2` SQL code block after `as on INSERT to tags`, with the continuation owned by part-028.
- Self-review: checked source coverage page by page, omissions, duplication, current-part ownership, terminology, Markdown fences, list structure, code/output fidelity, and both boundary states against layout and fallback extraction.
- Unresolved issues: none; the intentional incomplete SQL boundary is recorded in metadata.
