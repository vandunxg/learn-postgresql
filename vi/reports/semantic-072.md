# Semantic Review Report

- Scope: Full `parts/part-072.pdf` (printed pages 678-687) compared with `vi/parts/part-072.md`, including the `part-071` and `part-073` boundary context
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

- Compared all prose, headings, examples, SQL, shell commands, `psql` sessions, result output, logs, configuration references, identifiers, literals, and URLs against the complete 10-page source PDF in paragraph context.
- Checked pgBackRest full, differential, and incremental backup relationships; retention behavior and linked-backup expiration; WAL/archive descriptions; PITR recovery ordering; recovery target semantics; read-only recovery state; promotion; and restored table/data state.
- Checked the MySQL/MariaDB-to-PostgreSQL pgloader walkthrough, including source/destination database and server relationships, generated schema ownership, role creation, schema/table permissions, and the boundary continuation into part 073.
- Checked subject/action/object relationships, conditions, negation, cause/effect, recommendation strength, qualifiers, PostgreSQL terminology, and both part boundaries.
- The source’s internally inconsistent statement that the restored database state was from `2020-05-30 16:23:38` was preserved in the translation; it is source content, not a translation defect.
- All executable/source blocks and output are unchanged. SQL, shell commands, `psql` prompts, result tables, logs, identifiers, literals, URLs, and source-level anomalies were not translated, modernized, repaired, or completed from neighbor context.
- No edit was made to `vi/parts/part-072.md`; this report is the only semantic-review artifact written.
