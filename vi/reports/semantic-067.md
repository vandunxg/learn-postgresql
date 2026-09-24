# Semantic Review Report

- Scope: Full `parts/part-067.pdf` (PDF pages 1-10; printed pages 628-629 and 631-637) compared with `vi/parts/part-067.md`, including the `part-066` and `part-068` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-067.md:87` | The sentence structure made the relationship between pre-native systems and their trigger-based implementation less explicit. | The first method was implemented by systems designed before native logical replication and based on triggers. | Rephrased to state explicitly that the systems were trigger-based and predated native logical replication. | Fixed |
| LOW | `vi/parts/part-067.md:149` | `replication permission` was singular although the source says `replication permissions`. | A database user needs replication permissions for logical replication. | Changed to `replication permissions`. | Fixed |
| LOW | `vi/parts/part-067.md:116` | The heading was a literal mixed-language rendering of “Logical replication environment settings.” | The section describes setting up the logical replication environment. | Changed to `Thiết lập môi trường logical replication`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 3
- Unresolved: 0

## Verification

- Compared all prose, headings, notes, lists, references, examples, figure captions, knowledge-check answers, and both part boundaries against the complete 10-page source PDF in paragraph context.
- Checked replication and backup-related meaning, including physical versus logical replication, synchronous/asynchronous/cascading conditions, `pg_basebackup`, replica promotion, `REPLICA IDENTITY`, WAL and logical decoding, publication/subscription roles, version compatibility, DML/DDL scope, bloat behavior, and hot upgrade.
- Checked subject/action/object relationships, conditions, exceptions, negation, cause/effect, comparisons, recommendation strength, qualifiers, temporal/version context, and PostgreSQL terminology.
- All SQL, shell commands, configuration snippets, `psql` prompts, terminal output, URLs, identifiers, literals, paths, and source-level anomalies were preserved. No executable or output block was edited.
- No missing, duplicated, or hallucinated content was found. The current part ends inside the numbered configuration list as documented; no neighbor prose was copied.
