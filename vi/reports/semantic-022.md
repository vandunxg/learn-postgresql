# Semantic Review Report

- Scope: `parts/part-022.pdf` (printed pages 178-187) compared with `vi/parts/part-022.md`, including the `part-021` and `part-023` boundary context
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-022.md:63` | `Có thể có value đầu tiên` was a literal rendering that did not clearly express retrieving the first value with `first_value()`. | The question asks whether the first value in a partition can be obtained. | Changed to `Có thể lấy value đầu tiên`. | Fixed |
| LOW | `vi/parts/part-022.md:116` | `character` was retained as an awkward untranslated noun in the explanation of `upper`. | The function converts every character in a string to uppercase. | Changed `character` to `ký tự` and clarified the phrase with `trong`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, tables, examples, references, and review questions against the complete 10-page source PDF in paragraph context.
- Checked window-frame semantics, aggregate behavior, `ROW_NUMBER()`, `FIRST_VALUE()`, `RANK`, `DENSE_RANK()`, `LAG()`, `LEAD()`, `CUME_DIST()`, `NTILE()`, Boolean NULL handling, numeric precision/scale, casting, rounding, and error conditions.
- Checked the `part-021` -> `part-022` RANGE/ROWS boundary and the `part-022` -> `part-023` numeric-precision boundary.
- SQL, commands, prompts, identifiers, literals, result sets, error output, URLs, and code formatting were left unchanged.
