# Semantic Review Report

- Scope: Full `parts/part-065.pdf` (printed pages 608-617) compared with `vi/parts/part-065.md`, including the `part-064` and `part-066` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| MEDIUM | `vi/parts/part-065.md:281` | The translation said the primary server was ready to connect to the replica, reversing the source's passive relationship. | The primary server is ready for the replica server to connect to it; the replica is ready to receive information from the primary. | Rephrased as `sẵn sàng để replica server kết nối tới`. | Fixed |
| LOW | Figures 17.1-17.3, between `vi/parts/part-065.md:167-183` | The source diagrams contain visible labels (`PostgreSQL`, `Primary`, `Replica`, and `WAL`). | The figures visually show the primary/replica direction, PITR/WAL flow, and the WAL channel. | Preserved the source diagrams as extracted assets referenced from the Markdown; no labels were invented or redrawn. | Resolved |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 1
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, figure captions, examples, SQL, shell commands, `psql` prompts, result output, configuration, identifiers, literals, paths, and log lines against the complete 10-page source PDF in paragraph context.
- Checked replication direction, primary/replica roles, asynchronous versus synchronous behavior, WAL and checkpoint claims, `wal_level`, `wal_keep_segments`, replication slots, `pg_basebackup`, recovery state, conditions, qualifiers, and the `pg_basebackup` option-list continuation into part 066.
- All executable/source blocks are unchanged. SQL, shell commands, configuration snippets, `psql` sessions, terminal output, identifiers, literals, paths, and URLs were not translated, modernized, repaired, or completed from neighbor context.
- No neighbor prose or list item was copied into part 065. The only translation edit was the corrected passive connection relationship.
