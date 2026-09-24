# Boundary Review: part-036 <-> part-037

- Wave: `B`
- Scope: Boundary `part-036` -> `part-037` only.
- Source checked: `parts/part-036.pdf` printed page 327 (PDF page 10) and `parts/part-037.pdf` printed page 328 (PDF page 1), using parsed text and `pdftotext -layout`.
- Translation checked: `vi/parts/part-036.md:295-299` and `vi/parts/part-037.md:1-8`.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- The source boundary is inside the `psql` `\\dp perm_test` output/result set. Part 036 ends after the `Schema`, `Name`, `Type`, `Access privileges`, `Column privileges`, and `Policies` headers; part 037 continues with the separator, the `forum | perm_test | table` row, and `(1 row)`.
- The translation preserves the exact output order and fixed-width structure at the junction. The output fragment is represented by a closing `text` fence in part 036 and a new valid `text` fragment in part 037; no separator, row, prompt, or row count is missing or duplicated.
- The following prose begins after the completed result set and correctly explains default privileges. No sentence or paragraph continues across the boundary. The `ACL`, `PUBLIC`, `default privileges`, `role`, and `object` terminology remains coherent.
- No SQL statement, query plan, list, figure, or caption crosses this boundary. The `psql` session/result-set continuation is the only structured construct crossing it.

## Continuity Checklist

- Sentence continuity: pass
- Paragraph continuity: pass
- SQL/code continuity: pass; output fragment is preserved across the boundary
- `psql` session continuity: pass
- Query result continuity: pass
- Table/result continuity: pass
- List continuity: n-a
- Query plan continuity: n-a
- Figure/caption continuity: n-a
- Terminology continuity: pass
- Missing/duplicate content: none found

## Changes

- No edits were made to `vi/parts/part-036.md` or `vi/parts/part-037.md`; the boundary representation is faithful and requires no pair-only correction.
- This report is the only file added by this review.

## Verification

- Compared layout extraction and parsed PDF text for the final source page of part 036 and the opening source page of part 037.
- Rechecked the translated tail/head against source ownership, `psql` output headers and rows, fixed-width separators, code-fence structure, terminology, and missing/duplicate status.
- Boundary review result: **pass; no unresolved issue**.
