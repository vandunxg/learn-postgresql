# Boundary Review: part-043 <-> part-044

- Wave: `A`
- Scope: `part-043` final source/translation pages and `part-044` initial source/translation pages only.
- Source checked: `parts/part-043.pdf` pages 9-10 (printed pages 396-397) and `parts/part-044.pdf` pages 1-2 (printed pages 398-399), using layout extraction and rendered pages.
- Translation checked: `vi/parts/part-043.md` lines 171-238 and `vi/parts/part-044.md` lines 1-92.
- Instructions checked: `prompts/boundary-review-agent.md`, `instructions/00-core-rules.md`, `instructions/02-postgresql-glossary.md`, `instructions/04-boundary-context.md`, `instructions/05-markdown-preservation.md`, `instructions/06-sql-code-output-fidelity.md`, and `instructions/07-table-diagram-query-plan.md`.

## Findings

- **Continuity:** The source ends part 043 with the complete paragraph explaining that normal operation can resume after crash recovery. Part 044 begins the next source paragraph, which continues the recovery explanation with “This process...” and then starts the `Checkpoints` section. The Vietnamese tail/head preserves this ownership and continuity: part 043 ends with `bình thường có thể bắt đầu lại.` and part 044 begins `Quy trình này...`.
- **Ownership:** No prose is duplicated or omitted at the boundary. The continuation paragraph is present only in part 044; the `Checkpoints` heading and its opening explanation also remain in part 044.
- **Diagram/caption:** Figure 11.4 is wholly contained in the opening page of part 044 and is not a cross-boundary continuation. Its caption, `Hình 11.4: Một ví dụ về CHECKPOINT`, is retained. The embedded image labels are not retyped because no image asset/source text is available, consistent with the diagram rule and part-044 metadata.
- **SQL/output/plans:** No SQL block, `psql` session, query result, terminal output, or `EXPLAIN` plan crosses this boundary. The first executable block in part 044 is later in the part, after the reviewed opening pages.
- **Terminology:** `WALs`, `crash recovery`, `WAL replay`, `checkpoint`, and `CHECKPOINT` remain technically recognizable and consistent across the two parts. No boundary terminology correction is required.

## Result

No boundary issue found. No edits were made to `vi/parts/part-043.md` or `vi/parts/part-044.md`.
