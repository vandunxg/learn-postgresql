# Boundary Review: part-040 <-> part-041

- Wave: `B`
- Scope: `part-040` final source/translation pages and `part-041` initial source/translation pages only.
- Source checked: `parts/part-040.pdf` PDF pages 9-10 (printed pages 366-367) and `parts/part-041.pdf` PDF pages 1-2 (printed pages 368-369), using layout and raw text extraction.
- Translation checked: `vi/parts/part-040.md:192-255` and `vi/parts/part-041.md:1-78`.
- Instructions checked: `00-core-rules.md`, `01-translation-style.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, `07-table-diagram-query-plan.md`, `08-semantic-review.md`, and `09-qa-validation.md`.

## Findings

- **Continuity:** Source part 040 ends with the complete paragraph explaining that an explicit transaction is needed to keep the online-shopping workflow consistent. Source part 041 begins with the complete `Time within transactions` heading and paragraph. The boundary is not inside a sentence, paragraph, section, list, table/result set, SQL/code block, `psql` session, query plan, caption, or figure.
- **Ownership:** The translation keeps the explicit-transaction discussion in part 040 and starts the new time section in part 041. No neighbor content is copied across the boundary.
- **Fidelity:** The final source prose and executable blocks in the checked part-040 pages, and the initial source prose and `psql` blocks in the checked part-041 pages, are represented without missing or duplicated boundary content. Prompts, SQL, identifiers, literals, error/output text, and numeric values remain unchanged. No code or result reconciliation is required at this boundary.
- **Terminology:** `transaction`, `explicit transaction`, `implicit transaction`, `xid`, `VACUUM`, `database`, `tuple`, `table`, `snapshot`, `MVCC`, and `lock` are used consistently across the junction and match the source/glossary baseline.

## Result

No boundary issue found. No edits were made to `vi/parts/part-040.md` or `vi/parts/part-041.md`.
