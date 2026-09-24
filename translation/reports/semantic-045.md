# Semantic Review Report

- Scope: Full `parts/part-045.pdf` (printed pages 408-417) compared with `vi/parts/part-045.md`, including the `part-044` and `part-046` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| MEDIUM | `vi/parts/part-045.md:160` | The final analogy said `PGXN đối với Perl`, reversing the subject of the analogy. | PGXN is to PostgreSQL what CPAN is to Perl, CTAN is to LaTeX, and PEAR is to PHP. | Changed the phrase to `PGXN đối với PostgreSQL cũng giống như CPAN đối với Perl`. | Fixed |
| LOW | `vi/parts/part-045.md:97` | The knowledge-check heading used the plural pronoun `chúng` for the singular collective term `WAL`. | The source asks about WALs; the answer and surrounding prose use `WAL` as the collective PostgreSQL log term. | Changed `chúng lại quan trọng` to `nó quan trọng`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 1
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, callouts, figure captions, examples, references, Discord material, and the Chapter 12 opening against the complete 10-page source PDF in paragraph context.
- Checked VACUUM versus VACUUM FULL storage effects, plain VACUUM deallocation exception, autovacuum worker behavior, threshold and scale-factor conditions, cost-limit suspension, ANALYZE statistics, xid wraparound, MVCC snapshots, WAL/checkpoint relationships, and transaction-isolation qualifiers.
- Checked the extension and PGXN explanations, cluster/database scope, third-party extension stability qualifier, package spelling, source typo `postgrsql-contrib`, and the final PGXN analogy.
- SQL, `psql` prompts, result output, configuration parameters, identifiers, literals, URLs, captions, and technical names were not altered.
- Checked the `part-044` to `part-045` and `part-045` to `part-046` boundaries; no neighbor-owned prose was copied or omitted.
