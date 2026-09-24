# Semantic Review Report

- Scope: `parts/part-023.pdf` (printed pages 188-197) compared with `vi/parts/part-023.md`, including the `part-022` and `part-024` boundary context.
- Source compared directly: yes
- Reviewer: Semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-023.md:35,88,143,166,181` | The generic character-data-type category was rendered as `char`, which could be read as the specific fixed-length `char(n)` type. | The section covers character types generally, including `char(n)`, `varchar(n)`, and `text`. | Changed these references to `data type ký tự`. | Fixed |
| LOW | `vi/parts/part-023.md:179` | The literal wording around `substring` did not clearly state that `from` supplies the starting position and the length is `n` characters. | `substring` takes a substring starting at the position specified by `from` for `n` characters. | Clarified the start position and length relationship. | Fixed |
| LOW | `vi/parts/part-023.md:185` | `hour` was retained as an awkward noun and the time-zone alternatives were grammatically ambiguous. | PostgreSQL manages time with and without time-zone settings. | Changed this to `quản lý thời gian với cả thiết lập có time zone và không có time zone`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 3
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, quotations, references, examples, and boundary-owned content against the complete 10-page source PDF in paragraph context.
- Checked numeric precision/scale, character types, `char(n)` padding, `varchar(n)` limits, `text`, `substring`, date parsing/formatting, `DateStyle`, `CURRENT_TIMESTAMP`, timestamp variants, and session time-zone behavior.
- Preserved the source's prose/code identifier inconsistencies (`create_on_t`/`created_on_t` and `created_on_nt`/`create_on_nt`) rather than introducing unsupported corrections.
- SQL, commands, prompts, identifiers, literals, result sets, error output, URLs, and executable block formatting were left unchanged.
- Boundary context confirms the numeric-precision opening and the NoSQL-section continuation without omission or duplication.
