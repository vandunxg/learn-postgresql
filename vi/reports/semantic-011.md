# Semantic Review Report

- Scope: `parts/part-011.pdf` compared with `vi/parts/part-011.md`, including the `part-010` and `part-012` boundary context.
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-011.md:209` | The `$user` schema lookup was rendered as searching a schema name “in the user table,” which obscures the search-path behavior. | With the default `$user,public`, PostgreSQL first searches the schema whose name matches the current user, then `public`; the following `forum` example confirms this mapping. | Changed to `schema có tên trùng với user hiện tại`. | fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Reviewed all prose in the complete 10-page source part against the translation in paragraph context.
- Checked the chapter transition, database/schema and user/role terminology, `$user,public` search-path behavior, template database flow, and the `part-010`/`part-012` boundaries.
- SQL, commands, `psql` prompts, identifiers, literals, result sets, errors, notices, and output formatting were left unchanged.
