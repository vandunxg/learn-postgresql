# Semantic Review Report

- Scope: Full `parts/part-048.pdf` (printed pages 438-447) compared with `vi/parts/part-048.md`, including the `part-047` and `part-049` boundary context
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| MEDIUM | `vi/parts/part-048.md:32` | `CREATE EXTENSION` was described as a `function`, which is a misleading SQL/PostgreSQL concept and inconsistent with the source's surrounding use of `statement`. | The paragraph refers to explicitly executing the `CREATE EXTENSION` statement in another database. | Changed `function` to `statement`. | Fixed |
| LOW | `vi/parts/part-048.md:92` | `bằng cách chuyển vào folder đó` was an awkward literal rendering of entering the extension directory. | Enter the `/src/tagext` folder in the Docker image before installing the extension. | Changed to `bằng cách vào folder đó`. | Fixed |
| LOW | `vi/parts/part-048.md:360` | `theo dõi QR code` described the wrong action for joining Discord. | Follow the QR code below, meaning scan it to join the community. | Changed to `quét QR code bên dưới`. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 1
- LOW fixed: 2
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, callouts, examples, summary, knowledge review, references, and the Discord section against the complete 10-page source PDF in paragraph context.
- Checked extension installation/removal scope, database versus cluster effects, PGXN/manual uninstall behavior, control-file semantics, PGXS/Makefile behavior, extension upgrade flow, and version/argument relationships.
- Checked PostgreSQL terminology, SQL statement/function distinctions, conditions, recommendation strength, and the `part-047` to `part-048` and `part-048` to `part-049` boundaries.
- SQL, PL/pgSQL, commands, `psql` prompts, result sets, identifiers, literals, output, error messages, file paths, and URLs were not edited.
