# Semantic Review Report

- Scope: Full `parts/part-061.pdf` (printed pages 568-577) compared with `vi/parts/part-061.md`, including the `part-060` and `part-062` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-061.md:124` | The Docker note used singular `image` and `configuration file`, while the source refers to the book's Docker images and configuration files. | The configuration files are kept under `PGDATA` in the book's Docker images. | Changed both nouns to plural without changing the path or technical meaning. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, notes, lists, knowledge-check answers, references, Discord text, chapter transition, examples, configuration descriptions, SQL, prompts, result output, paths, identifiers, literals, and log lines against the complete 10-page source PDF in paragraph context.
- Checked physical backup restoration, cloned-cluster startup and self-healing, PITR scope and restore-time conditions, WAL archiving/replay and missing-segment behavior, logical-versus-physical backup meaning, database/database-cluster scope, configuration-file roles, `pg_settings`, `pending_restart`, and `SHOW` semantics.
- Checked subject/action/object relationships, conditions, exceptions, negation, cause/effect, recommendation strength, qualifiers, temporal context, PostgreSQL terminology, and the `part-060`/`part-061` and `part-061`/`part-062` boundaries.
- All executable/source blocks are preserved: SQL, shell/configuration snippets, `psql` prompts, result sets, paths, identifiers, literals, and log output were not translated, modernized, repaired, or completed from neighboring parts.
- No replication-specific semantic error, table/result-set fidelity issue, missing content, or unresolved issue was found. The report is the only review artifact added; no neighbor part was edited.
