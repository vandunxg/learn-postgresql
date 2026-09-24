# Boundary Review: part-010 <-> part-011

## Scope

- Wave B boundary only: `part-010` -> `part-011`.
- Compared the final two source pages of `parts/part-010.pdf` with the initial two source pages of `parts/part-011.pdf` (printed pages 66-67 and 68-69), using `pdftotext -layout`, raw extraction, and rendered-page checks.
- Checked `vi/parts/part-010.md:269-314` and `vi/parts/part-011.md:1-18` against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is inside the `pg_hba_file_rules` query result. Part 010 ends after the source rows for line numbers 89, 91, 93, 96, 97, and 98; part 011 continues with line 100, the wrapped `scram-`/`sha-256` value, and `(7 rows)`.
- The translation preserves the `psql` prompt, query, headers, separators, result values, nonconsecutive source line numbers, wrapped value, and row count. The split `text` fences are valid part-local fragments, with no duplicate or missing result content.
- The continuation row in part 011 had lost its ten output-indentation spaces relative to the common code-block margin. Those spaces were restored at `vi/parts/part-011.md:2`; no executable value or wording was changed.
- The prose after the result is a new complete paragraph. It does not continue a sentence or paragraph from part 010, and no prose was duplicated or re-owned.
- No numbered/bulleted list, standalone table beyond the result continuation, query plan, figure, or caption crosses this boundary. Terminology and identifiers remain continuous for `pg_hba_file_rules`, `pg_hba.conf`, `line_number`, `user_name`, `auth_method`, and the HBA directives.

## Changes

- Restored the ten source-faithful leading spaces before the `100` result row in `vi/parts/part-011.md:2`.
- No other translation file was changed.

## Verification

- Rechecked layout/raw extraction and rendered source pages for the final two pages of part 010 and initial two pages of part 011.
- Rechecked the translation junction for code-fence structure, `psql`/result continuity, output indentation, terminology, ownership, duplication, and omissions.
- Boundary review result: **pass after minimal correction; no unresolved issue**.
