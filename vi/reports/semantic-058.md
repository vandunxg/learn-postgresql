# Semantic Review Report

- Scope: Full `parts/part-058.pdf` (printed pages 538-547) compared with `vi/parts/part-058.md`, including the `part-057` and `part-059` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-058.md:11-13` | The tool-version and backup-validity callouts appeared before the local/remote command paragraph and the subsection-introduction paragraph, instead of in the source order. | The source presents local/remote operation, subsection scope, tool-version compatibility, then backup validity. | Restored the two callouts to their source position. | Fixed |
| LOW | `vi/parts/part-058.md:176` | The dependency-order note appeared before the `CREATE DATABASE` warning, while the source places it after that warning. | `pg_dump` determines dump order and dependency restoration order after explaining that plain output does not create a database. | Moved the note after the `CREATE DATABASE` discussion. | Fixed |
| LOW | `vi/parts/part-058.md:21` | The plain-text format description was overly literal and awkwardly phrased. | The backup consists of reproducible SQL statements represented as text SQL. | Rephrased the sentence without changing the technical meaning. | Fixed |
| LOW | `vi/parts/part-058.md:143` | The verbose-output description repeated the idea that the backup is performing an action while it is performing it. | `pg_dump -v` prints the backup operations while they run. | Rephrased as "các thao tác backup đang thực hiện." | Fixed |
| LOW | `vi/parts/part-058.md:248` | The `search_path` restart instruction used an awkward literal phrase. | Restarting the connection restores a normally configured `search_path`. | Rephrased with the same subject and effect. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 5
- Unresolved: 0

## Verification

- Compared all prose, headings, callouts, lists, examples, SQL, shell commands, `psql` prompts, result sets, identifiers, literals, and command output against the complete 10-page source PDF in paragraph context.
- Checked subject/action/object, conditions, exceptions, negation, cause/effect, comparison, recommendation strength, qualifiers, temporal/version context, and technical relationships.
- Checked backup and restore permissions, `pg_dump`/`pg_dumpall`/`pg_restore` scope, format distinctions, `search_path`, `COPY` versus `INSERT`, `--create`, `-s`/`-a`, restore ordering, and local/remote behavior.
- Preserved source anomalies and terminology, including the `--insert`/`--inserts` wording, `backup_forumd.sql` filename spelling in prose, `forumdb_test` prompt, and source PostgreSQL version context; no modernization or source correction was applied.
- SQL, commands, prompts, table definitions, output tables, result-set rows, identifiers, literals, and configuration values were not edited. No query plan appears in this part.
- Checked both part boundaries. Part 058 begins and ends at complete prose boundaries, with no duplicated or missing content.
