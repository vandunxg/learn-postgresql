# Semantic Review: part-004

- Source: `parts/part-004.pdf`, all 10 local pages
- Translation: `vi/parts/part-004.md`
- Method: paragraph-by-paragraph comparison with layout-preserving PDF extraction and surrounding boundary context

## Corrections

- `vi/parts/part-004.md:5`: changed `database table` to `table trong database` so “database table names” is represented naturally without changing the technical meaning.
- `vi/parts/part-004.md:183`: changed `community user của nó` to `cộng đồng người dùng của nó`; the source means PostgreSQL’s community of users.
- `vi/parts/part-004.md:189`: translated `mnemonic name` as `tên gợi nhớ`; this is ordinary explanatory prose, not a PostgreSQL identifier or immutable technical token.

## Verification

- No mistranslation was found in the ACID explanation, PostgreSQL history, version/release policy, PostgreSQL 15 personal-schema note, or cluster/database/schema/user terminology.
- The PostgreSQL 15 schema paragraph is in the same position as the source PDF, before the paragraph defining users; no reordering was needed.
- SQL, shell command, Git output, identifiers, URLs, and literal values were left unchanged.
- No unresolved semantic, nuance, terminology, or context issue remains in part 004.
