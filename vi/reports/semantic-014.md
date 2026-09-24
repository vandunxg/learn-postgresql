# Semantic Review Report

- Scope: `parts/part-014.pdf`, all 10 local PDF pages, compared with `vi/parts/part-014.md`
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| MEDIUM | `vi/parts/part-014.md:78,105,143` | Three immutable result-set separators had one fewer hyphen than the PDF output. | The source output uses `----+-------+-------------`. | Restored the missing hyphen in each separator. | Fixed |
| MEDIUM | `vi/parts/part-014.md:320` | `function SELECT` could incorrectly present `SELECT` as a function. | PostgreSQL can execute a `SELECT` statement without a `FROM` clause. | Changed to `câu lệnh SELECT`. | Fixed |
| LOW | `vi/parts/part-014.md:246` | `điều kiện bằng nhau` was a literal rendering of the SQL equality condition. | The paragraph introduces filtering with an equality condition. | Changed to `điều kiện so sánh bằng`. | Fixed |
| LOW | `vi/parts/part-014.md:286` | `string không đầy đủ` could imply an incomplete string rather than a substring. | The `LIKE '%discuss%'` example searches for the partial string `discuss`. | Changed to `chuỗi con \`discuss\``. | Fixed |
| LOW | `vi/parts/part-014.md:334` | `function` was misleading in the conclusion to the `LIKE` subsection. | The section presents ways to use the `LIKE` operator, not SQL functions. | Changed to `mọi cách sử dụng operator \`like\``. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 2
- LOW fixed: 3
- Unresolved: 0

## Checks

- Reviewed all prose, headings, lists, warnings, references, examples, result sets, and the Discord invitation across the complete 10-page PDF.
- No omission, duplication, condition/negation error, recommendation-strength change, or boundary ownership issue was found.
- Checked `UPDATE`, `DELETE`, `TRUNCATE`, `NULL`/`IS NULL`, `LIKE`, wildcard matching, case sensitivity, and the `upper` example in paragraph context.
- SQL, commands, prompts, identifiers, literals, notices, result values, and output layout were left unchanged except for restoring the three source-faithful separators above.
- The start follows the preceding temporary-table example; the end remains before part-015's `Using ilike` subsection.
