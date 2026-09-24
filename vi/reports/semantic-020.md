# Semantic Review Report

- Scope: Full `parts/part-020.pdf` compared with `vi/parts/part-020.md`, including the `part-019` and `part-021` boundary context
- Source compared directly: yes
- Reviewer: Semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-020.md:229` | The LAG definition rendered “offset rows before” as an ambiguous “offset row before.” | The target row is a number of rows before the current row, where the number is given by `offset`. | Clarified the relative row position. | Fixed |
| LOW | `vi/parts/part-020.md:263` | The LEAD definition had the same ambiguity for the rows after the current row. | The target row is a number of rows after the current row, where the number is given by `offset`. | Clarified the relative row position. | Fixed |
| LOW | `vi/parts/part-020.md:280` | “offset bắt đầu từ phía dưới” was a literal rendering that obscured the direction of LEAD’s offset. | LEAD looks toward rows below/later in the ordered partition. | Changed to `offset được tính từ các row bên dưới`. | Fixed |
| LOW | `vi/parts/part-020.md:301` | The comparison omitted the explicit value being compared with the current row. | CUME_DIST counts partition rows whose values are less than or equal to the value of the current row and its peers. | Added `giá trị của` before `row hiện tại`. | Fixed |
| LOW | `vi/parts/part-020.md:360` | “line” was retained where the source refers to table rows. | LAG and LEAD can compare different rows of a table. | Changed `line` to `row`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 5
- Unresolved: 0

## Verification

- Reviewed all prose in the complete 10-page source part against the translation in paragraph context.
- Checked window-frame terminology, ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, CUME_DIST, NTILE, partition/frame relationships, comparison direction, and recommendation strength.
- Checked the `part-019` -> `part-020` result-set boundary and the `part-020` -> `part-021` list/section boundary.
- SQL, commands, prompts, identifiers, URLs, result sets, quotations, and output formatting were left unchanged.
