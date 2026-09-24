# Boundary Review: part-025 <-> part-026

## Scope

- Wave A boundary only: `part-025` -> `part-026`.
- Compared the final two source pages of `parts/part-025.pdf` with the initial two source pages of `parts/part-026.pdf`.
- Checked the translated junction in `vi/parts/part-025.md` lines 359-381 and `vi/parts/part-026.md` lines 1-82 against the core, glossary, and boundary rules.

## Findings

- The source boundary is between printed pages 217 and 218, inside the `psql` result for `select now();` in numbered item 1. Part 025 correctly ends after the column header and separator; part 026 correctly begins with the timestamp, `(1 row)`, and the remaining transaction examples.
- The fenced `psql` session continues correctly across the boundary and closes after the final `COMMIT` in item 1. Prompts, SQL, output values, and row counts are preserved without missing or duplicated content.
- Numbered-list continuity is correct: item 1 is completed in part 026, followed by its note, then item 2 begins. The source's `select now();` example under the immutable-function item is preserved as-is.
- Function-volatility terminology and technical meaning remain continuous across the junction, including `VOLATILE`, `STABLE`, `IMMUTABLE`, `now()`, `lower(string_expression)`, transaction, and `psql` prompt behavior.
- No sentence, paragraph, list, table, query plan, figure, or caption is incorrectly continued or duplicated at this boundary.

## Changes

- No edit was justified in either `vi/parts/part-025.md` or `vi/parts/part-026.md`.
- This report is the only file added by the boundary review.

## Verification

- Checked `pdftotext -layout` extraction for the final two pages of part 025 and initial two pages of part 026.
- Checked the translated tail/head against source order, content, fenced-code continuation, `psql` session continuation, numbered-list ownership, and terminology.
- Boundary review result: **pass; no unresolved issue**.
