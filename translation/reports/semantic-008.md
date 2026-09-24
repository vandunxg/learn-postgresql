# Semantic Review Report

- Scope: Full `part-008` (`parts/part-008.pdf`, local pages 1-10) versus `vi/parts/part-008.md`, including left/right boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `No pg_hba.conf entry` section; source local p. 4 | The Docker/testing caveat was placed after the refusal example and its remediation instead of before the example. | The source gives the chapter-specific Docker caveat first, then presents the example and explains the general configuration problem. | Moved the existing caveat paragraph before the example; no wording or technical block was changed. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0
