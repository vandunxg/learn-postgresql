# Semantic Review Report

- Scope: Full `parts/part-034.pdf` (printed pages 298-308; page 307 is blank) compared with `vi/parts/part-034.md`, including the `part-033` and `part-035` boundary context.
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-034.md:295` | `truy cập QR code` was an unnatural rendering of the instruction to follow the QR code to join the Discord community. | The reader should use the QR code to join the community. | Changed to `quét QR code`. | Fixed |
| LOW | `vi/parts/part-034.md:301` | `group user` did not clearly express the source's explicit group-of-users meaning. | A PostgreSQL role can be both an individual user and a group of users. | Changed to `một group gồm nhiều user`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, examples, references, the Discord notice, and the Chapter 10 introduction against the complete source PDF in paragraph context.
- Checked partitioning, child-table/default-partition behavior, partition pruning, `constraint_exclusion`, `UNION ALL`, declarative partitioning, tablespaces, role/user terminology, ACL, RLS, privileges, and recommendation strength.
- Preserved the source's SQL, commands, `psql` prompts, query plans, result sets, identifiers, literals, URLs, and source inconsistencies; no executable or output block was edited.
- Checked the `part-033` -> `part-034` result-set boundary and the `part-034` -> `part-035` Chapter 10 boundary.
