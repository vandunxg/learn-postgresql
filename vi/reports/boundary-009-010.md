# Boundary Review: part-009 <-> part-010

## Scope

- Wave A boundary only: `part-009` -> `part-010`.
- Compared the final two source pages of `parts/part-009.pdf` with the initial two source pages of `parts/part-010.pdf`.
- Checked `vi/parts/part-009.md` lines 225-240 and `vi/parts/part-010.md` lines 1-17, together with the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is between printed pages 57 and 58. Part 009 ends with the complete `DROP ROLE this_role_does_not_exist` `psql` session and its error output. Part 010 begins with the complete explanatory paragraph, "As you can see, PostgreSQL warns...".
- The sentence and paragraph continuation is correct. There is no sentence fragment, paragraph duplication, or missing transition.
- The `psql` session and error output remain wholly owned by part 009. Part 010 starts prose and then begins its own complete `DROP ROLE IF EXIST` session; no code block is split or duplicated at the junction.
- No list, table, query result, `EXPLAIN` plan tree, figure, or caption crosses this boundary.
- Terminology is continuous for `role`, `DROP ROLE`, `IF EXIST`, `error`, `notice`, and `statement`. The source spelling `IF EXIST` is preserved in both the synopsis and executable session.
- No missing or duplicated source text was found at the boundary.

## Changes

- No edit was justified in either `vi/parts/part-009.md` or `vi/parts/part-010.md`.
- This report is the only file added by the boundary review.

## Verification

- `pdftotext -layout` and `pdftotext -raw` were checked for both source page ranges.
- Translation tails and heads were checked against the source order and ownership.
- Boundary review result: **pass; no unresolved issue**.
