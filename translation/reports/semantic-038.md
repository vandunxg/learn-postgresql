# Semantic Review Report

- Scope: `parts/part-038.pdf` (printed pages 338-347) compared with `vi/parts/part-038.md`, including the `part-037` and `part-039` boundary context
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

- Compared all prose, headings, callouts, lists, examples, policy syntax, ACL explanations, and RLS content against the complete 10-page source PDF in paragraph context.
- Checked sequence `USAGE`/`SELECT`/`UPDATE` permissions, schema `CREATE`/`USAGE`, language and routine `EXECUTE`, database `CONNECT`/`TEMP`/`CREATE`, ownership changes, ACL inspection, and RLS/BYPASSRLS semantics.
- Checked the page-10 backup callout ordering and the split `CREATE POLICY` syntax at the `part-038` -> `part-039` boundary.
- Preserved source inconsistencies such as the query filtering `relname = 'users'` while the following prose refers to table `categories`; no unsupported correction was made.
- SQL, function definitions, commands, `psql` prompts, identifiers, literals, error messages, ACL output, and the partial policy syntax were not edited.
- No edit was made to `vi/parts/part-038.md`; this report is the only review artifact written.
