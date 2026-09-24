# Semantic Review Report

- Scope: Full `parts/part-043.pdf` (printed pages 388-397) compared with `vi/parts/part-043.md`, including the `part-042` and `part-044` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-043.md:228` | `Trong nội dung trước đó của pg_wal` was a literal and unclear reference. | The paragraph refers to the `pg_wal` file listing shown immediately above. | Changed to `Trong danh sách pg_wal ở trên`. | Fixed |
| MEDIUM | `vi/parts/part-043.md:185-199` | Figures 11.2 and 11.3 contain source text inside the embedded diagrams. | The diagrams label shared buffers, persistent storage, `$PGDATA`, `base`, `pg_wal`, data files/pages, tuples, WAL segments/buffers, and include explanatory text about loading pages and forcing changes into WALs. | Preserved the source diagrams as extracted assets referenced from the Markdown; no image text was invented or altered. | Resolved |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, savepoint explanations, deadlock behavior, `deadlock_timeout`, WAL persistence, shared buffers, WAL segments, crash recovery, captions, SQL, `psql` prompts, result sets, identifiers, literals, shell output, and error messages against the complete 10-page source PDF in paragraph context.
- Rendered the pages containing Figures 11.2 and 11.3 and checked their visible labels and explanatory text. Captions are translated and the source diagrams are preserved through the linked extracted assets.
- Checked savepoint rollback scope, deadlock termination and replay behavior, `COMMIT` durability, WAL segment structure, timeline/LSN/offset explanation, clean versus unclean shutdown, WAL replay, and cluster availability during crash recovery.
- Checked the `part-042` to `part-043` code/result boundary and the `part-043` to `part-044` paragraph boundary; no neighbor prose was copied.
- SQL, commands, prompts, identifiers, literals, output, error messages, and other immutable executable blocks were not edited.
