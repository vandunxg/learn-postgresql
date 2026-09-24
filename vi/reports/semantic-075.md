# Semantic Review Report

- Scope: Full `parts/part-075.pdf` (five source pages: printed pages 708-709, the unnumbered promotional page, and two blank pages) compared with `vi/parts/part-075.md`, including the `part-074` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-075.md:34` | `time trong transaction` left the ordinary noun `time` untranslated and was not natural Vietnamese. | The index entry is about time within a transaction. | Changed to `thời gian trong transaction`. | Fixed |
| LOW | `vi/parts/part-075.md:97` | `như phương pháp cứu hộ khi crash` was a literal and awkward rendering of the WAL crash-recovery index entry. | WAL is presented as a recovery method in the event of a crash. | Changed to `như phương pháp khôi phục khi xảy ra crash`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all index entries, nested entries, section transitions, page references, promotional prose, numbered steps, QR-code instruction, and URL against all five source pages in paragraph/list context.
- Checked the `part-074` to `part-075` continuation: the source continues the index at `synchronous replication`, starts `T` on printed page 708, and ends the current content after the promotional numbered list; no next part exists.
- Checked PostgreSQL terminology and distinctions in the index, including synchronous replication, primary/standby server, transaction isolation levels, VACUUM/autovacuum, WAL, WAL-replay, and XID wraparound. No technical meaning or qualifier was changed.
- The source contains no SQL, code, command, result set, log, or query-plan block. The URL `https://packt.link/free-ebook/9781837635641` is preserved exactly.
- Rendered all five source pages: pages 1-2 contain the index, page 3 contains the promotional page and QR code, and pages 4-5 are blank. No source content from the QR image or blank pages was invented in Markdown.
- No unresolved semantic issue remains. Only the two minimal wording corrections in `vi/parts/part-075.md` and this report were written for this review.
