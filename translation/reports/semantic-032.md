# Semantic Review Report

- Scope: Full `parts/part-032.pdf` (printed pages 278-287) compared with `vi/parts/part-032.md`, including the `part-031` and `part-033` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-032.md:124` | The source's plural `child tables` was rendered as singular `child table`. | Inheritance propagates operations from the parent table to all child tables. | Changed to `các child table`. | Fixed |
| LOW | `vi/parts/part-032.md:128` | Literal `delete table` is ambiguous with PostgreSQL's row-level `DELETE` operation, while the source's concrete command is `drop table`. | The prose introduces removing a table, then gives the `DROP TABLE` statement. | Changed the generic prose to `xóa table` and retained `drop` for the SQL action. | Fixed |
| LOW | `vi/parts/part-032.md:193` | `procedure partition` could be mistaken for a PostgreSQL `PROCEDURE` object and is unnatural Vietnamese. | The generic partitioning procedure/process is complete. | Changed to `quy trình partition`. | Fixed |
| LOW | `vi/parts/part-032.md:304` | `partition bằng list` is less precise and less natural than the source's list-partitioning meaning. | The partitions were successfully created using list partitioning. | Changed to `partition theo list`. | Fixed |
| LOW | `vi/parts/part-032.md:358` | `có ... mà không phức tạp` is awkward and weakens the source's statement that the parent and child tables were obtained without complexity; the propagated indexes were also rendered with singular `child table`. | The example creates the parent and all child tables simply, and `CREATE INDEX` is automatically propagated to the child tables. | Changed to `đã tạo được ... một cách đơn giản` and `các child table`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 5
- Unresolved: 0

## Verification

- Compared all 10 pages of the source PDF directly against the translation in paragraph/context order, covering inheritance, `SELECT`/`ONLY`, `UPDATE`/`DELETE` propagation, table dropping, declarative partitioning, list partitioning, range partitioning, conditions, and recommendation strength.
- Checked the opening continuation of the `\d table_b` output against `part-031` and the ending `part_tags_date_02_2023` result-set continuation against `part-033`; no prose, list, output row, or boundary content was missing or duplicated.
- SQL, DDL/DML, `psql` commands and prompts, identifiers, literals, dates, result sets, and output formatting were not edited.
- Only `vi/parts/part-032.md` and this `semantic-032` report were touched for this review.
