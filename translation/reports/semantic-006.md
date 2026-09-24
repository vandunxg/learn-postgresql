# Semantic Review Report

- Scope: Full `parts/part-006.pdf` compared with `vi/parts/part-006.md`, including the list boundary and Chapter 2 continuation
- Source compared directly: yes
- Reviewer: Semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-006.md:99` | Plural source topic was rendered as singular | Exploring configuration files and parameters | `Khám phá các configuration file và parameter` | Fixed |
| LOW | `vi/parts/part-006.md:220` | Docker caveat appeared after the subsequent `pg_ctl status` discussion instead of immediately after the `pg_ctl start` output | The `start`/`stop`/`restart` limitation applies before the explanation of the start output and the follow-up status check | Moved the callout to its source position | Fixed |
| LOW | `vi/parts/part-006.md:258` | `much more problematic` was weakened to `nhiều vấn đề hơn` | Shutting down a cluster can be much more problematic than starting it | `Shutdown một cluster có thể khó xử lý hơn nhiều so với start cluster` | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 3
- Unresolved: 0

All SQL, commands, prompts, output, log lines, identifiers, paths, URLs, and query-plan-like formatting in this part were preserved. No other semantic or PostgreSQL terminology correction was justified by the direct comparison.
