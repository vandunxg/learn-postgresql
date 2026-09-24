# Semantic Review Report

- Scope: Full `parts/part-001.pdf` compared with `vi/parts/part-001.md`, including front matter and table of contents
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | TOC, Chapter 2, template databases | Plural source heading rendered as singular | The template databases | `Các template database` | Fixed |
| LOW | TOC, PGDATA directory | Plural source heading rendered as singular | Objects in the PGDATA directory | `Các object trong thư mục PGDATA` | Fixed |
| LOW | TOC, Tablespaces | Plural source heading rendered as singular | Tablespaces | `Các tablespace` | Fixed |
| LOW | TOC, `search_path` | Vietnamese modifier order was unnatural | The `search_path` variable | `Biến search_path` | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 4
- Unresolved: 0

The source contains no SQL, code, command, output, log, or query-plan blocks in this part. No other semantic changes were justified by the direct comparison.
