# Boundary Review: part-035 <-> part-036

## Scope

- Wave A boundary only: `part-035` -> `part-036`.
- Compared the final two source pages of `parts/part-035.pdf` (printed pages 316-317) with the initial two source pages of `parts/part-036.pdf` (printed pages 318-319).
- Checked the translated junction in `vi/parts/part-035.md` lines 312-365 and `vi/parts/part-036.md` lines 1-84 against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary is clean: part 035 ends with the complete paragraph explaining that `enrico`, as a member of `forum_admins`, can perform any action on the `users` table. Part 036 begins with the next complete paragraph introducing the demonstration of those permissions. No sentence or paragraph is prematurely closed, duplicated, or missing.
- Part 036 preserves the source `psql` sessions, prompts, SQL statements, identifiers, error messages, output values, row counts, and result-set structure for the `enrico` and `luca` examples. These examples begin and end within part 036; no `psql` session or result set crosses this boundary.
- The source and translation have no list, table, `EXPLAIN` plan, figure, or caption continuation at this junction. The ACL and privilege terminology remains continuous across the boundary, including `role`, `group`, `permission`, `privilege`, `INHERIT`, `GRANT`, `forum_admins`, `forum_stats`, `enrico`, and `luca`.
- No source content is missing or duplicated across the two translated parts. The existing wording was left unchanged where it reflects the source's own repetition or style; no preference rewrite is justified.

## Continuity Checklist

- Sentence continuity: pass
- Paragraph continuity: pass
- SQL/code continuity: pass
- `psql` session continuity: pass; no cross-boundary session
- Query result continuity: pass; no cross-boundary result set
- Table/result continuity: pass; no cross-boundary table
- List continuity: n-a
- Query plan continuity: n-a
- Figure/caption continuity: n-a
- Terminology continuity: pass
- Missing/duplicate content: none found

## Changes

- No edit was justified in `vi/parts/part-035.md` or `vi/parts/part-036.md`.
- This report is the only file added by the boundary review.

## Verification

- Checked `pdftotext -layout` and raw extraction for the final two pages of part 035 and initial two pages of part 036.
- Checked the translated tail and head against source order, paragraph ownership, code fences, `psql` prompts, SQL, output rows, identifiers, and terminology.
- Boundary review result: **pass; no unresolved issue**.
