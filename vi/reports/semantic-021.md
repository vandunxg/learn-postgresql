# Semantic Review Report

- Scope: Full `parts/part-021.pdf` compared with `vi/parts/part-021.md`, including the `part-020` and `part-022` boundary context.
- Source compared directly: yes
- Reviewer: Semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-021.md:1,178` | `range value` rendered the source's “range of values” as a potentially misleading singular term in the `RANGE BETWEEN` definition. | The frame considers a range of values relative to the value in the current row. | Changed to `một khoảng value`. | Fixed |
| LOW | `vi/parts/part-021.md:5` | The phrase “among other tasks” was omitted from the description of typical `frame_set` uses. | In-depth data analysis and data mining are examples among other tasks. | Restored `cùng nhiều tác vụ khác`. | Fixed |
| LOW | `vi/parts/part-021.md:178-180` | “non-unique values/bunch” was translated literally, obscuring that `RANGE` groups rows with the same ordering value while `ROWS` processes those rows separately. | Duplicate `ORDER BY` values are combined by `RANGE`; `ROWS` includes the same rows but processes them one at a time. | Clarified the repeated-value grouping as `cùng value` / `value trùng nhau`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 3
- Unresolved: 0

## Verification

- Compared all prose, headings, numbered steps, bullets, explanatory tables, figure captions, and boundary-owned content against the complete 10-page source PDF in paragraph context.
- Checked frame-clause conditions, `ROWS` versus `RANGE`, `UNBOUNDED PRECEDING`/`FOLLOWING`, ordering direction, duplicate `ORDER BY` values, frame grouping, and the source's PostgreSQL-specific window-function explanations.
- Confirmed the `part-020` -> `part-021` and `part-021` -> `part-022` boundaries remain continuous and complete.
- SQL, commands, prompts, identifiers, literals, result sets, figure captions, and output formatting were left unchanged.
