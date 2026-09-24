# Semantic Review Report

- Scope: Full `parts/part-073.pdf` (printed pages 688-697) compared with `vi/parts/part-073.md`, including the `part-072` and `part-074` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-073.md:28,30` | The knowledge-check wording omitted the `like` operator from the `where` condition. | The question and answer concern a condition like `foo%`, specifically a `LIKE` pattern. | Added `like` to both prose lines. | Fixed |
| LOW | `vi/parts/part-073.md:38` | `Với retention` was a literal and awkward rendering of the source qualifier `Given retention`. | PITR can restore to any past point within the available retention period. | Changed to `Trong phạm vi retention`. | Fixed |
| LOW | `vi/parts/part-073.md:51-52` | The reference labels used singular `foreign data wrapper` although the source names the `foreign data wrappers` wiki and documentation. | Both references cover the foreign data wrappers documentation. | Changed both labels to `foreign data wrappers`. | Fixed |
| LOW | `vi/parts/part-073.md:64` | `books and videos` was narrowed to `eBook và video`. | The Packt library offers access to more than 7,000 books and videos. | Changed to `sách và video`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 4
- Unresolved: 0

## Verification

- Compared all prose, headings, knowledge-check items, references, Discord notice, promotional pages, book descriptions, author notice, share-your-thoughts notice, and index entries against the complete 10-page source PDF in paragraph context.
- Checked subject/action/object relationships, conditions, qualifiers, cause/effect, technical terminology, and the source's asynchronous physical-replication and asynchronous-replication index entries. No logical-replication workflow or physical/logical comparison prose occurs in this part.
- Checked the `part-072` opening boundary and `part-074` index continuation. The intentionally blank fifth PDF page and the `LEAD 164` right boundary were preserved without importing neighbor content.
- The `psql` session, SQL statements, result sets, identifiers, literals, URLs, and all other executable/source blocks remain unchanged. No captions or diagrams occur in this part.
- No unresolved semantic issue remains. Only the four minimal prose corrections listed above and this report were written for this review.
