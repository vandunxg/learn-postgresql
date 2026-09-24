# Boundary Report: part-014 <-> part-015

- Wave: B
- Scope: Only the 014 -> 015 junction
- Source authority: `parts/part-014.pdf` printed pages 106-107 and `parts/part-015.pdf` printed page 108
- Translation files: `vi/parts/part-014.md`, `vi/parts/part-015.md`

## Boundary Evidence

- Source part 014 ends with the complete `like` subsection and the sentence stating that all functions usable with the `like` operator have been covered.
- Source part 015 begins with the new `Using ilike` heading, its complete case-insensitive `ilike` explanation, and the complete query result.
- Translation part 014 preserves the closing `like` explanation at `vi/parts/part-014.md:322-334`.
- Translation part 015 begins with the matching `ilike` heading and explanation at `vi/parts/part-015.md:1-16`, preserving the query, prompts, output, and `(2 rows)`.

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Sentence/paragraph continuation | PASS | Part 014 ends with a complete sentence and part 015 starts a new subsection; neither side fabricates a continuation or closure. |
| List/table continuation | PASS | No list or table crosses the junction. |
| SQL/code block continuation | PASS | The final `upper(description) like` query and output are complete in part 014; the separate `ilike` query and output are complete in part 015. |
| `psql` session continuation | PASS | The prompts and session state are preserved within each complete code block; no prompt is missing at the boundary. |
| Query result continuation | PASS | Part 014's final `(2 rows)` and part 015's `(2 rows)` belong to separate complete queries. |
| `EXPLAIN` plan tree continuation | N/A | No `EXPLAIN` or query-plan output occurs at this boundary. |
| Caption/figure continuation | N/A | No caption or figure crosses this boundary. |
| Terminology continuity | PASS | `like`, `ilike`, `operator`, `query`, `function`, `record`, and `description` are used consistently across the junction and preserve the source's technical terms. |
| Duplicated or missing text | PASS | No prose, heading, SQL, prompt, output, or result row is duplicated or omitted across the junction. |
| Source ownership | PASS | Part 014 retains its complete `like` subsection; part 015 owns the complete `ilike` subsection. |

## Fixes

- No boundary fix required.
- No preference rewrite made.

## Unresolved Issues

- None at the assigned 014 -> 015 boundary.
