# Semantic Review Report

- Scope: Full `parts/part-066.pdf` (PDF pages 1-10, printed pages 618-627) compared with `vi/parts/part-066.md`, including the `part-065` and `part-067` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-066.md:183` | Source says `standby servers` in the synchronous-status explanation, but the translation used singular `standby server`. | The `sync_state=sync` result describes synchronous replication for the standby-server set. | Changed to `các standby server`. | Fixed |
| MEDIUM | `vi/parts/part-066.md:189` | Figure 17.4 contains source topology labels and links inside the diagram. | The source diagram shows `Primary`, `First Replica`, and `Second Replica`, with links forming the cascading-replication topology. | Preserved the source diagram as an extracted asset referenced from the Markdown; no topology was inferred or redrawn. | Resolved |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, numbered steps, lists, figure caption, examples, configuration explanations, SQL, shell commands, `psql` prompts, result sets, identifiers, literals, paths, and PostgreSQL log/error lines against the complete source PDF in paragraph context.
- Checked subject/action/object, conditions, negation, cause/effect, comparison, recommendation strength, qualifiers, temporal/version context, and the physical-replication relationships across asynchronous, synchronous, cascading, delayed, and promoted-replica workflows.
- Checked `primary`/`standby` roles, physical replication, replication slots, `pg_stat_replication`, LSN alignment, `synchronous_commit`, `synchronous_standby_names`, `recovery_min_apply_delay`, promotion, timeline change, WAL loss, and the chapter-summary transition. Source-level technical claims and anomalies were preserved rather than modernized.
- Rendered the page containing Figure 17.4 and confirmed its visible `Primary`, `First Replica`, and `Second Replica` labels and cascading topology. The source diagram is preserved through the linked extracted asset; no labels were reconstructed or hallucinated.
- All executable/source blocks are unchanged. SQL, shell commands, configuration snippets, `psql` sessions, result tables, identifiers, literals, paths, URLs, and log lines were not translated, modernized, repaired, or completed from neighbor context.
- Checked the `part-065` list continuation and the `part-066` to `part-067` chapter boundary; no neighbor prose, code, output, or knowledge-check content was copied.
- Only the number-agreement correction listed above and this report were written for this review.
