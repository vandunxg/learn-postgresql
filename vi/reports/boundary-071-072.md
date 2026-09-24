# Boundary Review: part-071 <-> part-072

- Wave: `A`
- Scope: `part-071` final source/translation pages and `part-072` initial source/translation pages only.
- Source checked: `parts/part-071.pdf` printed page 677 (PDF page 10) and `parts/part-072.pdf` printed page 678 (PDF page 1), using parsed PDF text, `pdftotext -layout`, and rendered-page checks.
- Translation checked: `vi/parts/part-071.md:309-314` and `vi/parts/part-072.md:1-7`.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- The source boundary is inside one `pgbackrest` terminal-output block. Part 071 ends after `postgres@pgbackrest:~$ pgbackrest --stanza=pg1 check`; part 072 continues with `[....]` and `completed successfully (2868ms)`.
- The following prose is a complete new paragraph: "If everything is OK, we will receive a completed successfully message (as seen above); now we are ready to manage continuous backup." Its Vietnamese translation follows the output without duplication or omission and proceeds to the `Managing base backups` section.
- The translation preserves the command, output, prompt, literal completion message, and source ownership. No sentence, list, table/result set, `psql` session, query plan, figure, or caption crosses this boundary.
- Before review, part 072 incorrectly opened a second fenced block while part 071's fence was still open. On concatenation, that opening fence would render as literal output inside the existing block. The established split-code convention keeps a continuation fragment directly inside the preceding fence.
- Terminology is continuous for `pgbackrest`, stanza, continuous backup, base backup, full backup, differential backup, and incremental backup.

## Changes

- Removed only the redundant opening fenced-block marker at the start of `vi/parts/part-072.md`; the existing fence in part 071 now encloses the complete cross-part terminal-output fragment and closes at the end of the part-072 fragment.
- No source content, translation wording, or ownership was otherwise changed.

## Verification

- Compared source layout/raw extraction and rendered pages at printed pages 677-678.
- Rechecked the translation junction for code-fence continuity, prompt/output fidelity, prose continuity, terminology, duplication, and omissions after the correction.
- Boundary review result: **pass after minimal correction; no unresolved issue**.
