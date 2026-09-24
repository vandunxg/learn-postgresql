# Boundary Review: part-037 <-> part-038

## Scope

- Wave A boundary only: `part-037` -> `part-038`.
- Compared the final two source pages of `parts/part-037.pdf` with the initial two source pages of `parts/part-038.pdf` using `pdftotext -layout`, raw extraction, and rendered-page checks.
- Checked the translated junction in `vi/parts/part-037.md` lines 358-364 and `vi/parts/part-038.md` lines 1-54 against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is in the sequence-permission discussion. Part 037 ends after the complete sentence explaining that `USAGE` permits actions requiring `SELECT` and `UPDATE`; part 038 begins with the following sentence, “The latter two permissions...”. Sentence continuity and source ownership are correct.
- The translation preserves the sequence-permission relationship: “Hai permission sau” correctly refers to `SELECT` and `UPDATE`. The synopsis and all sequence examples begin in part 038, with no SQL, `psql` session, query result, or code block split across this boundary.
- Technical structures are intact. `GRANT`, `REVOKE`, `ALL`, `USAGE`, `SELECT`, `UPDATE`, `categories_pk_seq`, role names, prompts, error text, output values, and identifiers remain unchanged in executable blocks. No table/result set, query plan, list, figure, or caption crosses the boundary.
- Terminology remains consistent for `sequence`, `privilege`, `permission`, `role`, and `schema`. No source sentence, paragraph content, command, output, or transition is duplicated or missing.

## Changes

- No edit was justified in `vi/parts/part-037.md` or `vi/parts/part-038.md`.
- This report is the only file added by the boundary review.

## Verification

- Checked `pdftotext -layout` and raw extraction for source pages 9-10 of part 037 and pages 1-2 of part 038.
- Rendered and visually checked printed pages 337-338 at the junction.
- Checked translation tails/heads against source order, sentence and paragraph continuity, code-block ownership, technical terminology, and duplicate/omission status.
- Boundary review result: **pass; no unresolved issue**.
