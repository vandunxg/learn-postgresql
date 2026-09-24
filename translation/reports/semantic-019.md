# Semantic Review Report

- Scope: `parts/part-019.pdf` compared with `vi/parts/part-019.md`, including the `part-018` and `part-020` boundary context.
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-019.md:220` | `Ở phía sau` and `nhiều hơn chỉ row hiện tại` were overly literal and awkward. | The window function can access more than the current query-result row behind the scenes. | Changed to `Ở hậu trường` and `có thể truy cập không chỉ row hiện tại`. | fixed |
| LOW | `vi/parts/part-019.md:243` | `connect với user ... đến database` did not clearly express the connection direction and authentication identity. | The statement is executed after connecting to `forumdb` as user `forum`. | Changed to `kết nối tới database forumdb bằng user forum`. | fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, captions, references, and boundary-owned content against the complete 10-page source PDF in paragraph context.
- Checked CTE data movement, recursive CTE behavior, `UNION`, transaction wording, query conditions, PostgreSQL 11/16 materialization claims, window-function semantics, `PARTITION BY`, `WINDOW`, aggregate behavior, and the source's incomplete right-boundary result set.
- SQL, shell commands, `psql` prompts, identifiers, literals, result sets, output formatting, URLs, and code were left unchanged.
- Boundary reports `boundary-018-019.md` and `boundary-019-020.md` were checked for continuity and ownership.
