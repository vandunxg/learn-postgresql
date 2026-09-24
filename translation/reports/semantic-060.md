# Semantic Review Report

- Scope: Full `parts/part-060.pdf` (printed pages 558-567) compared with `vi/parts/part-060.md`, including the `part-059` and `part-061` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose, headings, warning/note callouts, examples, lists, SQL, shell commands, `psql` prompts, result output, configuration, identifiers, literals, paths, and log lines against the complete 10-page source PDF in paragraph context.
- Checked backup automation, `pg_dump`/`pg_dumpall`, catalog/database-cluster scope, `COPY TO`/`COPY FROM`, `WHERE` filtering, external programs, `\\copy`, logical-versus-physical backup distinctions, filesystem-level behavior, WAL self-healing, PostgreSQL-version constraints, `pg_basebackup`, tablespace remapping, replication-client privileges, `pg_verifybackup`, and cloned-cluster startup conditions.
- Checked subject/action/object relationships, conditions, negation, cause/effect, recommendation strength, qualifiers, PostgreSQL terminology, and the continuation of the `pg_restore` and `pg_ctl` output blocks across both boundaries.
- All executable/source blocks are unchanged. SQL, shell commands, configuration snippets, `psql` sessions, output tables, identifiers, literals, paths, and log lines were not translated, modernized, repaired, or completed from neighbor context.
- No edit was made to `vi/parts/part-060.md`; this report is the only semantic-review artifact written.
