# Semantic Review Report

- Scope: Full `parts/part-039.pdf` (printed pages 348-357) compared with `vi/parts/part-039.md`, including the `part-038` and `part-040` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-039.md:17` | `match chính user` was awkward and overly literal. | The condition matches the users themselves against a `SELECT` statement. | Changed to `đối chiếu user`. | Fixed |
| LOW | `vi/parts/part-039.md:168` | `đưa password mới vào` was a literal rendering in the `ALTER ROLE` context. | Issue `ALTER ROLE` statements to set a new password for every defined role. | Changed to `thiết lập password mới`. | Fixed |
| LOW | `vi/parts/part-039.md:316` | `theo dõi QR code` was not the natural action for the source's QR-code instruction. | Follow the QR code below to join the book's Discord community. | Changed to `quét QR code`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 3
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, policy explanations, RLS conditions, examples, password-encryption discussion, SSL behavior, summary, knowledge check, references, and Discord section against the complete 10-page source PDF in paragraph context.
- Checked policy `USING`/`WITH CHECK` semantics, RLS enable/disable scope, permissive versus restrictive policy combination, `CURRENT_ROLE`, password reset requirements, `sslmode` conditions, `host` versus `hostssl`, and the source's `sslmode=require` example under the `sslmode=disable` discussion.
- Verified that all SQL, configuration snippets, `psql` prompts, terminal output, query plan, identifiers, literals, error messages, and URLs remain unchanged. The source's apparent SSL example inconsistency was preserved rather than corrected.
- Checked the `part-038` -> `part-039` code-fragment boundary and the `part-039` -> `part-040` chapter boundary; no neighbor prose was copied.
- Fresh whitespace and Markdown checks found no trailing whitespace and 32 balanced fence markers. No unresolved semantic issue remains.
