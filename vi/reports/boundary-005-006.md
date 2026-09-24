# Boundary Report

- Left part: `part-005`
- Right part: `part-006`
- Source checked: yes
- Translation checked: yes
- Sentence continuity: pass
- Paragraph continuity: pass
- SQL/code continuity: pass
- Table/result continuity: n-a
- Query plan continuity: n-a
- List continuity: pass
- Terminology continuity: pass
- Missing/duplicate content: none
- Changes made: none; the junction already matches the source and no edit was justified.
- Unresolved issues: none

## Findings

- The source ends part 005 on local PDF page 10 (printed page 17) after numbered item 2, including the complete `md5sum --check` command and output `postgresql-16.0.tar.bz2: OK`.
- The source begins part 006 on local PDF page 1 (printed page 18) with numbered item 3. The translation preserves this ownership: `vi/parts/part-005.md` ends at item 2 and `vi/parts/part-006.md` begins at item 3.
- The item-2 code fence closes at the end of part 005 and item 3 opens a new code fence in part 006. Commands, output, paths, identifiers, and version values are preserved without duplication or omission.
- No SQL, `psql` session, query result, `EXPLAIN` plan, table, diagram, or caption crosses this boundary.
- `tarball`, `compilation`, `archive`, `systemd(1)`, `configure`, `database directory`, and `initdb` remain technically consistent across the junction.

## Verification

- Reviewed the source last two pages and translation tail for part 005, and source first two pages and translation head for part 006.
- Confirmed translation lines `part-005.md:249-254` and `part-006.md:1-10` preserve the source list continuation.
- Confirmed metadata records `ends_inside_list: yes` for part 005 and `begins_inside_list: yes` for part 006, with no sentence or code continuation claimed.
