# Boundary Review: part-072 <-> part-073

- Wave: `B`
- Scope: `part-072` final source/translation page and `part-073` initial source/translation page only.
- Source checked: `parts/part-072.pdf` PDF page 10 (printed page 687) and `parts/part-073.pdf` PDF page 1 (printed page 688), using fresh `pdftotext -layout` extraction.
- Translation checked: `vi/parts/part-072.md:363-460` and `vi/parts/part-073.md:1-20`.
- Instructions checked: `00-core-rules.md`, `02-postgresql-glossary.md`, `04-boundary-context.md`, `05-markdown-preservation.md`, `06-sql-code-output-fidelity.md`, and `07-table-diagram-query-plan.md`.

## Findings

- **Continuity:** The source boundary is between a completed `psql` session and a new paragraph. Part 072 ends the migration session with `forumdb=# \q`; part 073 begins, “Now we can access the postgresql database forumdb using a user called forumdb,” followed by a new `psql -U forumdb forumdb` session. The Vietnamese translation preserves this separation and meaning.
- **Ownership:** Part 072 contains the complete migration output, verification queries, permission grants, and terminating `\q`. Part 073 contains the next user-access query results, summary, and subsequent book matter. No neighbor content is copied across the boundary.
- **Constructs:** No sentence, prose paragraph, list, table/result set, SQL/code block, `psql` session, query plan, figure, or caption crosses the boundary. The code fence in part 072 closes after `forumdb=# \q`; part 073 opens its own code fence for the new session.
- **Fidelity:** The translation preserves the prompts, commands, query results, row counts, identifiers, permissions, URLs, and source executable text at both edges. The source's `ppostgres@pg-destination:~$` spelling in the pgloader block is retained rather than silently corrected.
- **Terminology:** `forumdb`, `postgresql`, `pgloader`, `psql`, `schema`, `table`, `role`, `PITR`, and related PostgreSQL terms remain continuous and technically recognizable. No glossary or casing issue occurs at the boundary.
- **Missing/duplicate content:** None found.

## Result

Boundary passes. No edits were made to either assigned translation part.
