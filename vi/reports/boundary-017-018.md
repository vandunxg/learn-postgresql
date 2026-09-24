# Boundary Review: part-017 <-> part-018

## Scope

- Wave A boundary only: `part-017` -> `part-018`.
- Compared the source tails/heads from `parts/part-017.pdf` and `parts/part-018.pdf` using both `pdftotext -layout` and `pdftotext -raw`.
- Checked `vi/parts/part-017.md` lines 350-394 and `vi/parts/part-018.md` lines 1-131, with the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary falls inside item 1 of the UPSERT example and inside the `\d j_posts_tags` result. Part 017 correctly ends after the `j_posts_tags_post_pk_fkey` row and `posts(pk)`; part 018 correctly resumes with the `j_posts_tags_tag_pk_fkey` row and `tags(pk)`.
- The fenced `text` blocks are separate file fragments of one source result. Their boundary preserves the result order, identifiers, `psql` output, and technical values; no row or continuation line is duplicated or missing.
- List continuity is correct: item 1 begins in part 017 and continues in part 018, item 2 begins in part 018, and the following items continue in order. The prose and paragraph boundary around the split are not duplicated or prematurely closed.
- Part 018 preserves the source’s step-2 prose wording `j_posts_add`, while its SQL and output remain `j_posts_tags`. This apparent source inconsistency is not a translation error and was not modernized or corrected.
- No `EXPLAIN` plan, figure/caption, table outside the `psql` result, or query-result continuation crosses this boundary. UPSERT terminology and identifiers remain continuous.
- No missing or duplicated source content was found at the boundary.

## Changes

- No edit was justified in `vi/parts/part-017.md` or `vi/parts/part-018.md`.
- This report is the only file added by the boundary review.

## Verification

- `pdftotext -layout` and `pdftotext -raw` were run for both source PDFs and checked at the junction.
- Translation tails and heads were checked against source order, ownership, list numbering, code fences, `psql` prompts, output rows, and identifiers.
- Boundary review result: **pass; no unresolved issue**.
