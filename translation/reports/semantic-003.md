# Semantic Review Report

- Scope: `part-003`, all 10 local PDF pages, including the table of contents and Preface
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| MEDIUM | `vi/parts/part-003.md:159` | “hệ thống quản lý database” was literal and unnatural for DBMS. | PostgreSQL is an object-relational Database Management System. | Changed to “hệ quản trị database”. | Fixed |
| MEDIUM | `vi/parts/part-003.md:183` | “query có các row RETURNING” obscured the role of `RETURNING`. | The queries use `RETURNING` to return rows. | Changed to “query sử dụng RETURNING để trả về các row”. | Fixed |
| MEDIUM | `vi/parts/part-003.md:201` | “các chính sách quy định dữ liệu” was awkward. | Auditing can help comply with data regulation policies, such as GDPR. | Changed to “các chính sách về quy định dữ liệu”. | Fixed |
| HIGH | `vi/parts/part-003.md:207` | “giữ nhiều instance đồng bộ” omitted “up” from “up and in sync”. | Replication keeps several instances running and synchronized with one master node. | Changed to “giữ nhiều instance hoạt động và đồng bộ”. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 1
- MEDIUM fixed: 3
- LOW fixed: 0
- Unresolved: 0

## Checks

- Table of contents entries, chapter summaries, Preface paragraphs, lists, and the software/OS table remain in source order with no detected omission or duplication.
- No source condition, negation, exception, recommendation qualifier, or version context was changed.
- PostgreSQL terminology was checked for database/database cluster, schema, role/user, session/connection, MVCC/WAL/checkpoint, replication, and related terms.
- No SQL, code, command, output, log, query result, or query plan occurs in this part.
- The boundary is clean: part-003 ends after the color-images URL, before `Conventions used` in part-004; no sentence, paragraph, list, table, or executable block crosses it.
