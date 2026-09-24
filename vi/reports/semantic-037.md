# Semantic Review Report

- Scope: Full `parts/part-037.pdf` (printed pages 328-337) compared with `vi/parts/part-037.md`, including the `part-036` and `part-038` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, ACL examples, permission synopses, SQL, `psql` prompts, result sets, identifiers, comments, and error/output text against the complete 10-page source PDF in paragraph context.
- Checked default privileges, owner ACL creation, `PUBLIC` permissions and scope, additive ACL behavior, `GRANT`/`REVOKE` semantics, `WITH GRANT OPTION`, table- and column-level privileges, column privilege precedence, and sequence `USAGE`/`SELECT`/`UPDATE` relationships.
- Checked recommendation strength, conditions, negation, exception behavior, and terminology for roles, objects, tables, columns, routines, functions, procedures, schemas, sequences, ACLs, and privileges.
- Boundary context confirms the opening `perm_test` result-set continuation and the complete closing paragraph before the sequence-permission continuation in part 038.
- SQL, commands, prompts, identifiers, literals, comments, result sets, errors, and output formatting were not edited.
- No edit was made to `vi/parts/part-037.md`; this report is the only review artifact written.
