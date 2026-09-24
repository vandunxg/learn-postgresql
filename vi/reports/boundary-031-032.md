# Boundary Review: part-031 <-> part-032

## Scope

- Wave A boundary only: `part-031` -> `part-032`.
- Compared the source tails/heads from `parts/part-031.pdf` and `parts/part-032.pdf` using `pdftotext -layout` and raw extraction, with the adjacent `part-033` head checked for the part-032 right boundary.
- Checked the translated junction in `vi/parts/part-031.md` lines 313-318, `vi/parts/part-032.md` lines 1-22 and 439-455, and `vi/parts/part-033.md` lines 1-22 against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The left boundary falls inside numbered item 3 and the `\d table_b` `psql` table-description output. Part 031 correctly ends after the prompt and `Table "forum.table_b"` heading; part 032 correctly resumes with the remaining columns, indexes, and `Inherits: table_a` row, then continues with the source prose identifying `table_b` as a child of `table_a`.
- The split `text` code fences preserve the source fragment ownership. No output row, identifier, prompt, or continuation prose is duplicated or missing at the junction, and numbered item 4 starts in part 032 exactly where the source starts it.
- The right boundary falls inside numbered step 5 under `Range partitioning`, in the `part_tags_date_02_2023` query-result output. Part 032 correctly ends after the header separator; part 033 correctly resumes with `2 | 2023-02-01 | Linux | 1`, closes the result block, and continues with the remaining partition results and prose.
- SQL, `psql` commands/prompts, output values, table names, column names, dates, row counts, and code-block structure remain continuous and faithful. No sentence, paragraph, list, table/result-set, query plan, figure/caption, or terminology continuation is incorrectly handled at this boundary.
- No missing or duplicated source content was found in the checked junctions. The source's technical output is preserved rather than translated or repaired.

## Changes

- No edit was justified in `vi/parts/part-031.md`, `vi/parts/part-032.md`, or `vi/parts/part-033.md`.
- This report is the only file added by the boundary review.

## Verification

- Checked source tail/head extraction for parts 031 and 032, plus the part-033 source head needed to verify the part-032 result-set continuation.
- Checked translation tails and heads against source order, ownership, list numbering, code fences, `psql` prompts, output rows, identifiers, and result-set boundaries.
- Boundary review result: **pass; no unresolved issue**.
