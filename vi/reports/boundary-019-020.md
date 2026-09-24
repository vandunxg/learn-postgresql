# Boundary Review: part-019 <-> part-020

## Scope

- Wave A boundary only: `part-019` -> `part-020`.
- Compared the final two source pages of `parts/part-019.pdf` with the initial two source pages of `parts/part-020.pdf`.
- Checked the translated junction in `vi/parts/part-019.md` lines 237-284 and `vi/parts/part-020.md` lines 1-80 against the core, glossary, and boundary rules.

## Findings

- The source boundary is between printed pages 157 and 158, inside the `psql` result set for the window-function query. Part 019 correctly ends after the result header and the first row (`1 | 2 | 3`); part 020 correctly begins with the remaining rows (`3 | 1 | 3`, `(3 rows)`) and closes the code block.
- SQL, prompts, identifiers, output values, row count, and code-block ownership are continuous. No output row is missing or duplicated.
- The following prose beginning with “Or if we want to remove all duplicate rows” is correctly owned by part 020 and follows the completed result set without an invented transition.
- Window-function terminology and technical meaning remain continuous across the junction, including `window function`, `PARTITION BY`, `WINDOW`, aggregate, `category`, and `generate_series`.
- The checked source prose and examples are faithfully represented. No sentence, paragraph, list, table, query plan, figure, or caption is incorrectly continued or duplicated at this boundary.

## Changes

- No edit was justified in either `vi/parts/part-019.md` or `vi/parts/part-020.md`.
- This report is the only file added by the boundary review.

## Verification

- Checked `pdftotext -layout` extraction for the final two pages of part 019 and initial two pages of part 020.
- Checked the translated tail/head against source order, content, result-set continuation, and ownership.
- Boundary review result: **pass; no unresolved issue**.
