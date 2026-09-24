# Naturalize Vietnamese Translation Design

## Goal

Rà soát và viết lại toàn bộ bản dịch trong `content/modules/ROOT/pages/*.adoc` để văn phong tự nhiên, mạch lạc và phù hợp với developer Việt Nam. Bản dịch phải ưu tiên dịch ý, giữ nguyên technical meaning và dùng English technical/domain terms khi chúng giúp ngữ cảnh rõ hơn.

## Scope

- Review and edit exactly the 173 `.adoc` files under `content/modules/ROOT/pages/`.
- Do not edit `nav.adoc`, files under `translation/`, source files, generated site output, code, SQL, commands, identifiers, API names, file paths, URLs, anchors, or assets.
- Review all prose, headings, captions, table text, callouts, and list text that are part of the translated book.

## Translation contract

- Rewrite word-by-word, stiff, or awkward Vietnamese into natural Vietnamese rather than preserving English word order.
- Keep English technical/domain terms when that is the idiomatic choice for Vietnamese engineers, including terms such as `system`, `backend`, `frontend`, `module`, `request`, `response`, `order`, `approval`, `inventory`, `procurement`, `finance`, `fulfillment`, `downstream`, `async`, `message`, `task`, `transaction`, `query`, `index`, `cache`, `lock`, `thread`, and `API`.
- Translate ordinary words when Vietnamese is clearer and does not reduce technical precision.
- Decide terminology by context, not by blindly applying a fixed glossary; still maintain consistency across chapters.
- Do not add, remove, modernize, or reinterpret technical content.
- Preserve AsciiDoc structure, table shape, code blocks, inline code, image references, links, anchors, and formatting.

## Parallel workflow

The 173 files are processed in six waves, with at most 30 parallel agents per wave. Each agent owns exactly one `.adoc` file and may edit only that file. Agents must read the translation style instructions and glossary, inspect nearby chapter context when needed, and perform the naturalization directly in the assigned file. Files are partitioned before each wave so no two agents edit the same file.

Each agent checks its file for:

- literal English word order and machine-translation residue;
- unnecessarily Việt-hóa technical terms or unnatural English mixing;
- inconsistent terminology within the file;
- changed meaning, recommendation strength, negation, conditions, or examples;
- accidental changes to code, SQL, commands, identifiers, paths, links, anchors, tables, and AsciiDoc delimiters.

## Consolidation and final review

After all waves complete:

1. Compare the changed files against their pre-review versions and identify structural or technical changes.
2. Run a terminology consistency pass across chapter titles, recurring PostgreSQL concepts, and repeated instructional phrases.
3. Run a machine-translation residue pass for remaining stiff sentence patterns, excessive English interpolation, and forced Vietnamese technical translations.
4. Repair only confirmed issues while preserving the source meaning and file structure.
5. Validate that all 173 target files remain present and non-empty, code/SQL regions are unchanged, and no unrelated files were modified.
6. Run the repository's available AsciiDoc/site build checks.

## Acceptance criteria

- Every target `.adoc` file has been reviewed and remains valid AsciiDoc.
- No code block, SQL, command, identifier, API name, path, link target, anchor, image reference, table structure, or technical claim is changed unintentionally.
- Prose reads as technical Vietnamese written by a Vietnamese engineer, with English technical terms used intentionally rather than mechanically.
- Terminology is coherent across chapters without forcing a glossary-only translation.
- No known word-by-word or machine-like sentence remains after the final pass.
- Only intended content files and the design/implementation artifacts are changed.
