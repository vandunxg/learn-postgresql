# Semantic Review Report

- Scope: Full `parts/part-041.pdf` (printed pages 368-377) compared with `vi/parts/part-041.md`, including the `part-040` and `part-042` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-041.md:34` | `source time-continuous` was a literal and awkward rendering. | Use a continuously changing time source while a transaction is running. | Changed to `nguồn thời gian liên tục`. | Fixed |
| LOW | `vi/parts/part-041.md:86` | `xid cao hơn hẳn phải được tạo` was awkward and did not cleanly express the source's necessity. | A tuple with a higher xid must have been created after one with a lower creation xid. | Changed to `xid cao hơn chắc chắn được tạo`. | Fixed |
| LOW | `vi/parts/part-041.md:164` | `Lock là một cơ chế nặng` was too literal for the source's costly/heavy mechanism meaning. | Locks impose a significant concurrency cost and make transactions wait to acquire them. | Changed to `Lock là một cơ chế tốn kém`. | Fixed |
| LOW | `vi/parts/part-041.md:166` | `operating filesystem` was an unnatural rendering of the filesystem context. | The comparison is with copy-on-write in operating-system filesystems such as ZFS. | Changed to `filesystem của hệ điều hành`. | Fixed |
| LOW | `vi/parts/part-041.md:255` | `hoàn tất COMMIT công việc` was unnecessarily literal. | Transaction 4928 commits its work before later transactions see the consolidated data. | Changed to `COMMIT công việc của mình`. | Fixed |
| MEDIUM | `vi/parts/part-041.md:172` | Figure 11.1 was missing from the Markdown; only its translated caption remained. | The source diagram shows the `tags` table before and after `UPDATE`, including the invalidated old tuple and inserted new tuple. | Extracted the embedded source image to `vi/assets/part-041-figure-11-1-000.jpg` and linked it from the translation. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 1
- LOW fixed: 5
- Unresolved: 0

## Verification

- Compared all prose, headings, callout, figure caption, SQL, `psql` prompts, result sets, identifiers, literals, and comments against the complete 10-page source PDF in paragraph context.
- Checked transaction time semantics, xid modulo/wraparound, tuple freezing, virtual versus real xid assignment, `txid_current_if_assigned()`, MVCC versioning, snapshots, visibility, concurrent sessions, and lock behavior.
- Checked PostgreSQL terminology and technical relationships for transaction, xid, xmin, tuple, snapshot, MVCC, lock, session, and database service.
- SQL, commands, prompts, identifiers, literals, result sets, and output formatting were preserved and not edited.
- Checked the `part-040` -> `part-041` opening and `part-041` -> `part-042` closing boundaries; no neighbor prose or code was copied.
