# Semantic Review Report

- Scope: `parts/part-030.pdf` (printed pages 258-267) compared with `vi/parts/part-030.md`, including the `part-029` and `part-031` boundary context.
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

- Compared all prose, headings, lists, examples, event-trigger explanations, and the `Summary` paragraph against the complete 10-page source PDF in paragraph context.
- Checked trigger-event conditions, `TG_OP`, `NEW`/`OLD`, `BEFORE`/`AFTER` behavior, DML versus DDL event triggers, command tags, object types, event-trigger scope, superuser requirements, exception behavior, and recommendation strength.
- Preserved source wording and inconsistencies such as the prose references to `a_tags`/`b_tags` and `pg_event_trigger_commands()`; no unsupported correction was made.
- SQL, PL/pgSQL, shell commands, `psql` prompts, identifiers, literals, result sets, errors, event-trigger syntax, and output formatting were not edited.
- Boundary context confirms the opening continuation from the trigger examples and the ending `Summary` paragraph before the part-031 summary and knowledge-check material.
- No edit was made to `vi/parts/part-030.md`; this report is the only review artifact written.
