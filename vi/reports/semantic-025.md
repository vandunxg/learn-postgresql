# Semantic Review Report

- Scope: `parts/part-025.pdf` (printed pages 208-217) compared with `vi/parts/part-025.md`, including the `part-024` and `part-026` boundary context.
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| LOW | `vi/parts/part-025.md:219` | The translation said the `language` statement specifies PostgreSQL “where the function is written,” which obscured that it identifies the language used to write the function. | The `language` statement identifies the programming language in which the function is written, as shown by `language 'plpgsql';`. | Changed the sentence to state that `language` specifies the language used by the function. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 0
- LOW fixed: 1
- Unresolved: 0

## Verification

- Compared all prose in the complete 10-page source part against the translation in paragraph context, including the surrounding examples and the numbered explanation of the PL/pgSQL function body.
- Checked SQL functions returning `setof` and table results, polymorphic functions, PL/pgSQL terminology, alias and positional parameters, `IN`/`OUT`/`INOUT` behavior, function volatility categories, and the `now()` transaction example.
- Checked subject/action/object, conditions, qualifiers, technical relationships, headings, numbered and bulleted lists, and terminology consistency.
- SQL, commands, `psql` prompts, identifiers, literals, URLs, result sets, output formatting, and the incomplete `now()` output were left unchanged.
- Boundary reports `boundary-024-025.md` and `boundary-025-026.md` were checked for continuity, ownership, and the continued `psql` result/list structure.
- Only the identified prose sentence in `vi/parts/part-025.md` was edited; no neighboring part was changed.
