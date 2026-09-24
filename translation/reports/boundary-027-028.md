# Boundary Review: part-027 <-> part-028

## Scope

- Wave A boundary only: `part-027` -> `part-028`.
- Compared the final two source pages of `parts/part-027.pdf` with the initial two source pages of `parts/part-028.pdf` (PDF pages 9-10 and 1-2 respectively; printed pages 236-237 and 238-239).
- Checked the translated junction in `vi/parts/part-027.md:371-390` and `vi/parts/part-028.md:1-85` against the core, glossary, boundary, Markdown, SQL/code/output, and table/plan rules.

## Findings

- The source boundary falls inside numbered item 2 of the `INSTEAD OF` rule example and inside one SQL definition. Part 027 ends after `as on INSERT to tags`; part 028 begins with `where NEW.tag ilike 'f%'` and continues the same definition through `DO INSTEAD insert into f_tags(pk,tag,parent)values (NEW.pk,NEW.tag,NEW.parent);`.
- The translation preserves the complete SQL fragment across the junction, including `r_tags2`, `NEW.tag`, `ilike 'f%'`, `DO INSTEAD`, `f_tags`, `NEW.pk`, `NEW.tag`, and `NEW.parent`. No SQL keyword, identifier, value, or casing was translated or modernized.
- Numbered-list continuity is correct. Item 2 begins in part 027, item 3 starts in part 028 after the completed rule definition, and items 4-6 continue in source order. No list item was duplicated, omitted, prematurely closed, or re-owned across the boundary.
- The next `psql` session is complete in part 028: the `insert into tags (tag) values ('Fedora Linux');` command and `INSERT 0 0` output are preserved together. No prompt, query result row, table, `EXPLAIN` plan, figure, or caption is split at this junction.
- Terminology remains continuous for `rule`, `INSERT`, `INSTEAD`, `event`, `tag`, `tags`, and `f_tags`. The prose correctly states that matching records are moved to `f_tags`, consistent with the source code and output.
- Before review, part 027 opened the split SQL code fence without closing it, while part 028 opened a new `text` fence. In a concatenated Markdown package, that caused the part-028 opening fence to be rendered as literal code. The source split requires separate valid file fragments, so the missing closing fence was restored at the end of part 027.
- No missing or duplicated source prose, SQL, prompt, output, or list content was found at the boundary.

## Changes

- Added the missing closing `text` code fence at `vi/parts/part-027.md:390`.
- No source wording or executable content was changed; no other translation file was edited.

## Verification

- Checked `pdftotext -layout` and `pdftotext -raw` extraction for source part 027 page 10 and source part 028 page 1, with the surrounding source pages reviewed for list and paragraph context.
- Checked the translated tail/head against source order, SQL/code fidelity, list numbering, `psql` prompt/output ownership, terminology, and Markdown fence structure.
- Boundary review result: **pass; no unresolved issue**.
