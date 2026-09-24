# Semantic Review Report

- Scope: `parts/part-027.pdf` (printed pages 228-237) compared with `vi/parts/part-027.md`, including the `part-026` and `part-028` boundary context.
- Source compared directly: yes
- Reviewer: Semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-027.md:192` | The Discord paragraph omitted the invitation to ask questions to the author and added the broader, unsupported activity `trao đổi`. | The community lets readers share feedback, ask the author questions, and learn about new releases. | Restored `đặt câu hỏi cho tác giả` and removed the unsupported addition. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, references, and boundary-owned content against the complete 10-page source PDF in paragraph context.
- Checked exception handling, `SQLSTATE`/`SQLERRM`, `security definer`, permissions, server-side programming summary, event/rule/trigger relationships, `OLD`/`NEW`, rule timing, and the source's inconsistent `a_tag`/`O_tags` example without correcting the source.
- Confirmed the intentionally incomplete `r_tags2` SQL block remains owned by this part and unchanged; its continuation belongs to part 028.
- SQL, commands, prompts, identifiers, URLs, result sets, errors, and output formatting were left unchanged.
