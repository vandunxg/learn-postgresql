# Semantic Review Report

- Scope: Full `parts/part-046.pdf` (printed pages 418-427) compared with `vi/parts/part-046.md`, including the `part-045` and `part-047` boundary context.
- Source compared directly: yes
- Reviewer: OpenCode semantic reviewer

## Findings

| Severity | Location | Issue | Source meaning | Fix | Status |
| --- | --- | --- | --- | --- | --- |
| MEDIUM | `vi/parts/part-046.md:40` | “path tới extension script path” was tautological and obscured the `directory` directive's meaning. | The directive specifies the path where the extension script is located. | Changed to “path tới nơi chứa script của extension”. | Fixed |
| MEDIUM | `vi/parts/part-046.md:89` | “command fail một cách êm thấm” was overly literal and unnatural. | `IF NOT EXISTS` handles an already-installed extension without raising an error, as clarified by the following sentence. | Changed to “command xử lý êm thấm”. | Fixed |
| MEDIUM | `vi/parts/part-046.md:100` | “cài đặt bằng database administrator” used the wrong Vietnamese preposition for the installer. | The PL/Perl extension must be installed by the database administrator. | Changed to “cài đặt bởi database administrator”. | Fixed |

## Summary

- CRITICAL fixed: 0
- HIGH fixed: 0
- MEDIUM fixed: 3
- LOW fixed: 0
- Unresolved: 0

## Verification

- Compared all prose, headings, lists, callouts, examples, and paragraph context against the complete 10-page source PDF using fresh layout and raw text extraction.
- Checked conditions, negation, recommendation strength, version context, database/cluster and schema relationships, extension lifecycle, control/script files, `CREATE EXTENSION`, `ALTER EXTENSION`, `DROP EXTENSION`, and `CASCADE`/`RESTRICT` behavior.
- Confirmed the opening PGXN paragraph and closing `get_max()` explanation remain correctly owned by the neighboring parts; no boundary content was added or omitted.
- Confirmed SQL, shell commands, `psql` prompts, identifiers, literals, result sets, notices, errors, and output blocks were not edited.
