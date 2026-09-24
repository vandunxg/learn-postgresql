# Semantic Review Report

- Scope: Full `parts/part-068.pdf` (printed pages 638-647) compared with `vi/parts/part-068.md`, including the `part-067` and `part-069` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-068.md:243` | `access write operation` was a literal rendering of the source's action and was less precise in Vietnamese. | Logical replication permits performing write operations on the replica server. | Changed to `thực hiện write operation`. | Fixed |
| LOW | `vi/parts/part-068.md:395` | `có tác dụng gây ra message` was awkward and obscured that the replica error causes the primary server to record the shown message. | The duplicate-key error on the replica causes the illustrated message on the primary server. | Rephrased as `khiến primary server ghi lại message được minh họa ở đây`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, headings, numbered setup steps, note, examples, SQL, shell commands, `psql` prompts, result output, catalog output, configuration, identifiers, literals, URLs, paths, and log lines against the complete 10-page source PDF in paragraph context.
- Checked subject/action/object, conditions, exceptions, negation, cause/effect, comparison, recommendation strength, qualifiers, temporal/version context, and logical-replication technical relationships.
- Checked primary/replica roles, publication/subscription setup, `pg_hba.conf`, replication workers, `pg_stat_replication`, catalog scope, DML-versus-DDL behavior, duplicate-key failure, worker shutdown, and recovery procedure.
- All executable/source blocks are unchanged. SQL, shell commands, configuration snippets, `psql` sessions, output tables, catalog output, identifiers, literals, paths, URLs, and log lines were not translated, modernized, repaired, or completed from neighbor context.
- Checked the continued numbered list at the left boundary and the incomplete `DROP SUBSCRIPTION` output block at the right boundary. No neighbor prose or code/output was copied.
- Only the two prose edits listed above were made to `vi/parts/part-068.md`.
