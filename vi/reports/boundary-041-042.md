# Boundary Report

- Left part: `part-041`
- Right part: `part-042`
- Source checked: yes; compared the final two PDF pages of `parts/part-041.pdf` (PDF pages 9-10, printed pages 376-377) with the initial two PDF pages of `parts/part-042.pdf` (PDF pages 1-2, printed pages 378-379), using layout/raw extraction and rendered-page checks.
- Translation checked: yes; checked the junction at `vi/parts/part-041.md:277-292` and `vi/parts/part-042.md:1-38`.
- Sentence continuity: pass; part 041 ends with the complete introductory sentence and session-1 `UPDATE 6` fragment, and part 042 begins with the source's complete "In the meantime" sentence without duplication or invented closure.
- Paragraph continuity: pass; the explanation before session 1, the session-2 explanation, and the post-session MVCC paragraph remain in source order and ownership.
- SQL/code continuity: pass; the split `psql` example preserves `BEGIN`, `SELECT`, `UPDATE tags SET tag = upper( tag );`, `UPDATE 6`, the session-2 `UPDATE`, `-- LOCKED!!!!`, and the later `COMMIT`/unblock output. Prompts, identifiers, literals, comments, and output are unchanged. Each part has a valid separate `text` fence.
- Table/result continuity: pass; no standalone table or result set is cut at this junction. The query result inside the session fragments is complete and unchanged on each side.
- Query plan continuity: n-a; no `EXPLAIN` or query-plan output occurs at the boundary.
- List continuity: n-a; no list crosses the boundary.
- Terminology continuity: pass; `transaction`, `MVCC`, `lock`, `snapshot`, `tuple`, `VACUUM`, `autovacuum`, and `storage` remain consistent with the source and glossary baseline.
- Missing/duplicate content: none; no source prose, SQL, prompt, output, caption, or figure content is missing or duplicated at the junction. No figure/caption continuation occurs here.
- Changes made: none to `vi/parts/part-041.md` or `vi/parts/part-042.md`; the boundary report is the only review file added.
- Unresolved issues: none for this boundary.
