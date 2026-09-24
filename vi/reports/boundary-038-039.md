# Boundary Review: part-038 <-> part-039

## Scope

- Wave B boundary only: `part-038` -> `part-039`.
- Compared the source tail of `parts/part-038.pdf` (printed page 347) with the source head of `parts/part-039.pdf` (printed page 348) using `pdftotext -layout` and raw extraction.
- Checked the translated junction in `vi/parts/part-038.md:385-397` and `vi/parts/part-039.md:1-17` against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is inside one policy synopsis code block. Part 038 ends after `CREATE POLICY <name>`, `ON <table>`, and `FOR <statement>`; part 039 continues with `TO <role>`, `USING <filtering condition>`, and `WITH CHECK <writing condition>`.
- The translation preserves the exact source-owned code fragments and technical tokens. `CREATE POLICY`, `TO`, `USING`, `WITH CHECK`, placeholders, and the `text` fence are not translated or reconstructed. No SQL statement, `psql` session, terminal output, query result, `EXPLAIN` plan, table, list, figure, or caption other than this split code block crosses the boundary.
- Before review, part 038 had no closing fence while part 039 opened a new fence. In the merged Markdown, that opening marker would terminate the part-038 block and leave the continuation outside code. The pair now uses separate valid `text` fragments while preserving source order and ownership.
- The surrounding prose is complete and correctly ordered: part 038 introduces the policy synopsis, part 039 continues the syntax and then starts the explanatory bullets. No sentence, paragraph, syntax line, or explanatory text is duplicated or missing.
- Terminology remains continuous for `policy`, `tuple`, `role`, `table`, `statement`, `filtering condition`, `writing condition`, `USING`, and `WITH CHECK`.

## Changes

- Added the missing closing `text` fence at `vi/parts/part-038.md:397`.
- No source content or translation wording was changed, and `vi/parts/part-039.md` was not edited.

## Verification

- Checked layout and raw PDF extraction for the source tail/head, including the split policy synopsis.
- Re-read the translated tail/head after the edit and checked source order, code-fence structure, SQL/code fidelity, terminology, ownership, duplication, and omissions.
- Confirmed no whitespace errors with `git diff --check` against the edited part.
- Boundary review result: **pass after minimal correction; no unresolved issue**.
