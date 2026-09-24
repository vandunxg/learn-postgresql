# Semantic Review Report

- Scope: Full `parts/part-057.pdf` (PDF pages 1-10; printed pages 528-533 and 535-537, with PDF page 7 blank) compared with `vi/parts/part-057.md`, including the `part-056` and `part-058` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-057.md:93` | The prose said `GRANT các action đó`, which could imply that PostgreSQL grants actions rather than privileges. | The source says to grant the permissions corresponding to the actions that should be audited. | Changed to `GRANT các permission tương ứng cho role`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, knowledge-check answers, references, Discord information, chapter transition, backup examples, and both part boundaries against the complete source PDF in paragraph context.
- Checked PgAudit session and role auditing semantics, `READ`/`WRITE` categories, role permissions, audit counters, dynamic SQL logging, `pgaudit.log`, `pgaudit.role`, and the distinction between logging and auditing.
- Checked logical versus physical backup meaning, snapshot consistency, concurrent activity, file-level `PGDATA` copying, WAL replay, PITR, PostgreSQL major-version and operating-system constraints, and logical-backup tool coverage.
- All SQL, commands, `psql` prompts, comments, log lines, result output, identifiers, literals, URLs, configuration values, and executable blocks were preserved. Lists and examples were retained.
- The only translation edit was the permission terminology recorded above; no source-level technical claim was modernized or corrected. No boundary prose was copied from neighboring parts.
