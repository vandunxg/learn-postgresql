# Semantic Review Report

- Scope: Full `parts/part-059.pdf` (printed pages 548-557) compared with `vi/parts/part-059.md`, including the `part-058` and `part-060` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| HIGH | `vi/parts/part-059.md:4,10` | The two opening `pg_dump` commands used `forum.users_pk_seq`, changing the executable sequence identifier from the source's `forum.user_pk_seq`. | The source prose names the sequence `users_pk_seq`, but both source commands use the distinct singular identifier `forum.user_pk_seq`; executable content must preserve that source-level inconsistency. | Restored `forum.user_pk_seq` in both commands. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 1
- MEDIUM fixed: 0
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, examples, SQL, shell commands, `pg_restore`/`pg_dumpall` invocations, prompts, output, TOC entries, role definitions, identifiers, literals, and the incomplete right-boundary output block against the complete 10-page source PDF in paragraph context.
- Checked backup scope filters, compression levels, plain/custom/directory/tar formats, selective restore, whole-cluster backup, `--globals-only`, parallel backup/restore behavior, connection counts, lock/deadlock qualifiers, and CPU-core guidance.
- Checked backup/restore, cluster, role, tablespace, replication slot, connection, lock, and parallelism terminology, plus subject/action/object relationships, conditions, negation, cause/effect, recommendation strength, and qualifiers.
- Preserved the source's apparent identifier inconsistency (`users_pk_seq` in prose versus `forum.user_pk_seq` in the two commands) rather than correcting the source from PostgreSQL knowledge.
- The SQL, commands, prompts, terminal output, TOC lines, identifiers, literals, and query-related output were not translated or modernized; only the two corrupted command identifiers were corrected.
- Checked the `part-058` to `part-059` ownership boundary and the `part-059` to `part-060` continuation inside the `pg_restore` output block. No neighbor prose or output was copied.
