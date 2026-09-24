# Semantic Review Report

- Scope: Full `parts/part-052.pdf` (printed pages 478-487) compared with `vi/parts/part-052.md`, including the `part-051` and `part-053` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-052.md:294` | The wording `result set đã được giảm được join` was grammatically ambiguous about which result set is joined. | The reduced result set is then joined with the authors table by a Nested Loop. | Changed to `result set sau khi được giảm sẽ được join`. | Fixed |
| LOW | `vi/parts/part-052.md:351` | `thực thi nhiều nhất` could mean executing the largest number of queries rather than executing most frequently. | Analyze the queries that applications execute most often. | Changed to `được các application của bạn thực thi thường xuyên nhất`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, heading, callout, lists, examples, SQL, `psql` prompts, result-set output, query plans, identifiers, literals, and the final `pg_stat_user_indexes` command against the complete 10-page source PDF in paragraph context.
- Checked `EXPLAIN` option semantics, buffer prefixes and suffixes, WAL/FPI reporting, cache behavior, planner estimates versus actual execution, sequential/index/bitmap scans, `Gather`, `Hash Join`, `Nested Loop`, index maintenance cost, and `pg_stat_user_indexes` usage semantics.
- Preserved the source's apparent inconsistencies: the WAL example prose says “usernames” while its SQL inserts into `posts`; the period prose says two days while the sample uses `CURRENT_DATE - 20`; the first plan output uses `CURRENT_DATE - 2`; and the source calls the joined table “authors” in one explanation. No source claim was modernized or corrected.
- SQL, commands, identifiers, literals, result sets, and query-plan output were not changed. The previously present `Sort Method: external merge` and `Disk: 51192kB` lines remain intact.
- Confirmed the left boundary begins with the `SUMMARY` discussion after the preceding `EXPLAIN` options material and the right boundary ends after the complete `pg_stat_user_indexes` query, before the result table owned by `part-053`.
