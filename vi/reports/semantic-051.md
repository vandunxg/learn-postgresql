# Semantic Review Report

- Scope: Full `parts/part-051.pdf` (PDF pages 1-10; printed pages 468-477) compared with `vi/parts/part-051.md`, including `part-050` and `part-052` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-051.md:34` | The access-path study case must remain distinct from the problematic-index case: invalidation may be useful for forcing another path during cluster-behavior study, but may be necessary when an index has a problem. | Invalidation can be useful for forcing another access path during cluster-behavior study, and can be necessary when an index is problematic. | The current translation says `hoặc có thể cần thiết khi index gặp vấn đề`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, qualifiers, examples, SQL, commands, `psql` prompts, result sets, identifiers, literals, and query-plan output against the complete 10-page source PDF in paragraph context.
- Checked index invalidation/drop/rebuild semantics, `REINDEX` transaction restrictions, `EXPLAIN` planner terminology, estimated versus actual rows and timing, startup/final cost, planning/execution time, trigger timing, `SETTINGS`/`COSTS`/`TIMING`, and recommendation strength.
- Checked database/schema/table, index versus index-only scan terminology where applicable, planner estimates versus actual runtime, session-level configuration, and the `EXPLAIN`/`EXPLAIN ANALYZE` distinction.
- Preserved the source's wording, including its apparent `CONCURRENTLY` locking statement and its `width`/byte example; no source claim was modernized or corrected.
- Preserved all SQL, commands, `psql` prompts, result-set rows, identifiers, literals, configuration output, and query-plan output. No executable or output block was edited.
- Checked the left-boundary result-set continuation and the right-boundary continuation of the `EXPLAIN options` section; no neighbor content was copied.
- No additional edit was needed in `vi/parts/part-051.md` during this retry because the only identified semantic correction is already present.
