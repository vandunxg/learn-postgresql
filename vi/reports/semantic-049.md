# Semantic Review Report

- Scope: Full `parts/part-049.pdf` (PDF pages 1-10; printed pages 450-457) compared with `vi/parts/part-049.md`, including the `part-048` and `part-050` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-049.md:91` | The sequential-node list rendered the final item as `Gather và Merge`, which can be read as separate `Gather` and `Merge` nodes. | The source's later paragraph identifies the two parallel node types as a plain `Gather` node and a `Gather Merge` node. | Changed to `Gather và Gather Merge`. | Fixed |
| LOW | `vi/parts/part-049.md:149` | `join key` was singular although the source says `join key(s)`. | A Merge Join may sort both tables by one or more join keys. | Changed to `các join key`. | Fixed |
| MEDIUM | `vi/parts/part-049.md:48` | Figure 13.1 contains source labels inside the diagram. | The rendered figure labels the stages and flow as `SQL statement` -> `PARSER` -> `REWRITER (rule system)` -> `OPTIMIZER` -> `EXECUTOR` -> `STORAGE`. | Preserved the source diagram as an extracted asset referenced from the Markdown; no image text was invented or altered. | Resolved |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, chapter requirements, execution stages, optimizer cost explanation, node descriptions, conditions, examples, pseudo-Java blocks, the `Gather` boundary paragraph, and the figure caption against the complete source PDF in paragraph context.
- Checked planner/optimizer/executor roles, access paths, cost-based selection, the `> 12` join threshold, sequential versus parallel execution conditions, `Nested Loop`/`Hash Join`/`Merge Join`, `Index Scan`/`Index-Only Scan`/`Bitmap Index Scan`, and `Gather`/`Gather Merge` terminology.
- SQL and pseudo-Java literals, identifiers, casing, punctuation, and indentation were preserved. No `EXPLAIN` or structured query-plan output occurs in this part; the planner/node explanation remains prose and was not converted into a plan or altered based on current PostgreSQL behavior.
- Checked the `part-048` to `part-049` chapter boundary and the `part-049` to `part-050` `Gather Merge` boundary; no neighbor prose was copied.
- The source's optimizer/executor wording and other source-level technical quirks were preserved rather than modernized or corrected.
