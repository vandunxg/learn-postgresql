# Semantic Review Report

- Scope: Full `parts/part-062.pdf` (10 PDF pages; printed pages 578-587) compared with `vi/parts/part-062.md`, including `part-061` and `part-063` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-062.md:216` | The translation rendered `reserved_connections` as saying that only a special set of users has reserved slots, losing that the parameter indicates which special set of users has them. | `reserved_connections` counts connections established by users with `pg_use_reserved_connection` and indicates the special non-superuser set that has reserved connection slots. | Changed `và chỉ một tập user đặc biệt` to `đồng thời cho biết một tập user đặc biệt`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, qualifiers, configuration recommendations, examples, references, SQL, commands, `psql` prompts, result sets, and `pg_test_fsync` output against the complete 10-page source PDF in paragraph context.
- Checked configuration-file loading and override semantics, `pg_settings`/`pg_file_settings`, configuration contexts, WAL settings, `fsync`, `wal_level`, `synchronous_commit`, memory settings, connection limits, reserved connections, replication settings, vacuum/autovacuum, optimizer, and statistics-collector terminology.
- Preserved source recommendation strength and source anomalies, including the repeated `remote_write` wording, `open_datasysnc`, `maintanance_work_mem`, source parameter names, and chapter references; no source claim was modernized or corrected.
- Preserved all SQL, commands, configuration snippets, `psql` prompts, result-set rows, identifiers, literals, paths, and terminal output. No executable or output block was edited.
- Checked the left boundary after the `SHOW shared_buffers` output and the right boundary after the `track_counts` bullet; no neighbor-owned prose or output was copied, omitted, or duplicated.
