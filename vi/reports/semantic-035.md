# Semantic Review Report

- Scope: Full `parts/part-035.pdf` (10 pages, printed pages 308-317) compared with `vi/parts/part-035.md`, including `part-034` and `part-036` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-035.md:316` | `có các privilege một cách trong suốt` was a literal and unclear rendering of transparent privilege inheritance. | A member role receives the group privileges automatically/dynamically, without needing to explicitly become the group role. | Changed to `sẽ tự động có các privilege`. | Fixed |
| LOW | `vi/parts/part-035.md:363` | `GRANT role này cho role kia` left the grantor/recipient mapping ambiguous in the explanation of the two `GRANT` statements. | `forum_admins` is granted to `enrico`, and `forum_stats` is granted to `luca`. | Named both source and recipient roles explicitly. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, headings, bullets, role-property explanations, examples, SQL blocks, prompts, result sets, identifiers, URL, and the complete ending paragraph against the full 10-page source PDF in paragraph context.
- Checked role versus user/group terminology, cluster/database scope, `CREATEROLE`/`CREATEDB`, `SUPERUSER`, `REPLICATION`, RLS and `BYPASSRLS`, `ALTER ROLE` restrictions, role renaming, `SESSION_USER`/`CURRENT_USER`, per-role configuration, `pg_authid`/`pg_roles`/`pg_auth_members`, and `INHERIT`/`WITH INHERIT` behavior.
- SQL, shell commands, `psql` meta-commands, prompts, result sets, catalog names, identifiers, literals, password/hash samples, and output formatting were not edited.
- Existing boundary reviews confirm clean ownership and continuity at both `part-034` -> `part-035` and `part-035` -> `part-036`; no neighbor files were changed.
