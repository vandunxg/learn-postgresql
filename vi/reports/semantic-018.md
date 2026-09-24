# Semantic Review Report

- Scope: `parts/part-018.pdf` (printed pages 138-147) compared with `vi/parts/part-018.md`, including the `part-017` and `part-019` boundary context.
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose in the complete 10-page source part in paragraph context, including the UPSERT, `RETURNING`, multi-row `UPDATE`, `MERGE`, and CTE sections.
- Checked PostgreSQL terminology and meaning for primary keys, unique/exclusion constraints, `ON CONFLICT`, `RETURNING`, `GENERATED ALWAYS`, `MERGE`, CTE lifetime, inline views, and `MATERIALIZED`/`NOT MATERIALIZED` behavior.
- Preserved the source inconsistency between the prose reference to `j_posts_add` and the SQL/output using `j_posts_tags`; no unsupported correction was made.
- SQL, commands, prompts, identifiers, literals, result sets, errors, and output formatting were not edited.
- Boundary context confirms the opening `\d j_posts_tags` output and list continuation, as well as the ending `t_posts` result set and continuation into part 019, without omission or duplication.
- No edit was required in `vi/parts/part-018.md`; this report is the only file added by the semantic review.
