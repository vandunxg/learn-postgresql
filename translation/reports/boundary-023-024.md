# Boundary Review: part-023 <-> part-024

## Scope

- Wave A boundary only: `part-023` -> `part-024`.
- Compared the final two source pages of `parts/part-023.pdf` (PDF pages 9-10, printed pages 196-197) with the initial two source pages of `parts/part-024.pdf` (PDF pages 1-2, printed pages 198-199).
- Checked the translated junction in `vi/parts/part-023.md` lines 389-414 and `vi/parts/part-024.md` lines 1-78 against the core, glossary, Markdown, SQL/code/output, table/plan, and boundary rules.

## Boundary Evidence

- The source boundary falls between printed pages 197 and 198. Part 023 ends with the complete `The NoSQL data type` heading and its complete introductory paragraph. Part 024 begins with the next complete paragraph listing PostgreSQL's supported NoSQL data types (`hstore`, `xml`, and `json/jsonb`).
- Translation part 023 preserves the heading and complete paragraph at lines 412-414. Translation part 024 resumes with the matching list at lines 1-5, followed by the source sentence introducing `hstore` and `json`.
- The first `hstore` SQL example and its result set are wholly owned by part 024. They do not continue from part 023 or cross back over the boundary.

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Sentence/paragraph continuation | PASS | The final source paragraph is complete in part 023; part 024 starts a new paragraph and does not repeat or fabricate a continuation. |
| List/table continuation | PASS | The three-item NoSQL list starts and ends in source part 024 and is preserved in translation with no missing or duplicated item. No table crosses the junction. |
| SQL/code block continuation | PASS | No SQL or code block crosses the boundary. The first `create extension hstore` block belongs wholly to part 024. |
| `psql` session continuation | PASS | No `psql` session is active at the boundary. The first prompt in part 024 starts a new example and is preserved. |
| Query result continuation | PASS | No query result crosses the boundary. The first `hstore` result set is complete within part 024. |
| `EXPLAIN` plan tree continuation | N/A | No `EXPLAIN` or query-plan output occurs at this boundary. |
| Caption/figure continuation | N/A | No figure or caption occurs at this boundary. |
| Terminology continuity | PASS | `NoSQL`, `data type`, `PostgreSQL`, `hstore`, `json/jsonb`, and `extension` remain source-faithful and consistent with the glossary. |
| Duplicated or missing text | PASS | The source heading, introductory paragraph, list, and transition sentence are each represented once in the correct part; no neighboring content was re-owned. |
| Source ownership | PASS | Part 023 contains only the source content through printed page 197; part 024 begins with printed page 198 content. |

## Changes

- No edit was justified in `vi/parts/part-023.md` or `vi/parts/part-024.md`.
- This report is the only file added by the boundary review.

## Verification

- Checked `pdftotext -layout` and `pdftotext -raw` extraction at the source tail/head.
- Checked translated tail/head against source order, paragraph/list structure, ownership, terminology, and code/result boundaries.
- Boundary review result: **pass; no unresolved issue**.
