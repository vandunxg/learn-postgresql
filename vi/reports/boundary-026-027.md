# Boundary Review: part-026 <-> part-027

## Scope

- Wave A boundary only: `part-026` -> `part-027`.
- Compared the final source page of `parts/part-026.pdf` with the initial source page of `parts/part-027.pdf` (printed pages 227 and 228 respectively).
- Checked the translated junction in `vi/parts/part-026.md:402-413` and `vi/parts/part-027.md:1-18` against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is between the complete expanded `psql` result for `select * from my_first_fun(5);` on printed page 227 and the new `Exception handling statements` section on printed page 228. No sentence, paragraph, list, table, query result, plan, figure, or caption continues across the source boundary.
- The expanded result is preserved at the end of part 026, including the `psql` prompt, `RECORD 1` marker, `id`, `title`, `record_data`, and the wrapped output line. There is no missing or duplicated output row.
- Part 027 begins with the complete exception-handling heading and prose, followed by the complete `my_first_except` definition. The `psql` session and executable blocks do not continue from part 026.
- Terminology remains continuous for `PL/pgSQL`, `record`, `%ROWTYPE`, function, `psql`, and exception handling. SQL, identifiers, output, and error text remain unchanged.
- The final `text` block in part 026 is closed before the new prose in part 027. The Markdown fence structure is valid at the junction.

## Changes

- No part Markdown file was edited.

## Verification

- Checked `pdftotext -layout` and `pdftotext -raw` extraction for the final source page of part 026 and the initial source page of part 027.
- Checked source order, expanded result ownership, `psql`/output fidelity, terminology, and Markdown fence structure at the junction.
- Boundary review result: **pass; no edit justified; no unresolved issue**.
