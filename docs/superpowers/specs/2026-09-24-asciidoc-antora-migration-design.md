# Learn PostgreSQL AsciiDoc and Antora Migration Design

## Goal

Reorganize the existing translated Learn PostgreSQL repository into an
AsciiDoc and Antora project without changing or deleting the original PDFs or
translated Markdown. The published structure must follow the book's semantic
content, not the 75 translation chunks.

## Source and Archive Policy

- Move `027652113.pdf` to `source/pdf/original.pdf` and preserve all 75 PDF
  chunks under `source/pdf/parts/`.
- Move the 75 translated Markdown chunks to
  `source/markdown/translated-parts/` without changing their contents.
- Preserve the merged Markdown book as `source/markdown/translated-book.md`.
- Move translation instructions, prompts, schemas, metadata, reports,
  glossary, and progress files under `translation/` without content changes.
- Preserve existing image assets in the Antora component image directory.
- Keep the existing ZIP as a build/archive artifact if it is retained during
  the migration.

All source/archive files remain available for comparison and are never used
as an excuse to rewrite technical content.

## Semantic Book Model

The source table of contents defines 19 chapters but does not define separate
book-level Part headings. The navigation therefore uses one book Part named
`Learn PostgreSQL`, containing the 19 source chapters in source order. No new
thematic Parts are invented.

The published content keeps:

- front matter and preface;
- the 19 chapters;
- the book's closing material and index;
- source-defined headings, lists, examples, tables, figures, references, and
  Discord/promotional material where present.

Short chapters are one AsciiDoc page. Long chapters are split only at real
major-section headings identified from the TOC, headings, metadata, and all 74
boundary reports. A split page receives a stable semantic slug; no publish
page, navigation entry, or xref contains a `part-xxx` identifier.

## Conversion Rules

The converter reads the merged Markdown in natural source order while tracking
fenced-code state.

- Markdown document/chapter headings become AsciiDoc page titles and section
  headings with equivalent hierarchy.
- Hash-prefixed lines inside fenced code remain code, not headings.
- Ordered and unordered lists retain nesting and continuation.
- Markdown tables become AsciiDoc tables while retaining columns, rows, cell
  values, and technical output exactly.
- Fenced code becomes AsciiDoc listing blocks with the source language where
  known; SQL, shell, `psql`, terminal output, and query plans remain literal
  technical content.
- Inline code, emphasis, URLs, and link labels retain their meaning.
- Existing images become `image::` macros and are resolved from the component
  image directory. Missing image assets are reported rather than invented.
- Blockquotes remain blockquotes. Explicit `WARNING`, `NOTE`, or `TIP` labels
  become the corresponding AsciiDoc admonition without changing body text.
- Stable anchors are generated for semantic chapter and section targets when
  needed by internal links; external URLs remain unchanged.
- Conversion is syntax-only. It does not retranslate, modernize, correct, or
  otherwise editorialize technical prose, SQL, commands, output, or diagrams.

The converter writes a manifest containing source heading ranges, publish page
names, and source part references. The manifest supports later audits without
making chunk names part of the public URL model.

## Repository and Antora Layout

```text
source/
  pdf/original.pdf
  pdf/parts/
  markdown/translated-book.md
  markdown/translated-parts/
translation/
  instructions/
  prompts/
  schemas/
  metadata/
  reports/
  GLOSSARY.md
  PROGRESS.md
content/
  antora.yml
  modules/ROOT/pages/
  modules/ROOT/images/
  modules/ROOT/examples/
  modules/ROOT/partials/
  modules/ROOT/nav.adoc
playbook/
  antora-playbook.yml
scripts/
build/
ui/
```

`content/antora.yml` defines one component and version. The playbook reads the
local component from `content/`, writes the generated site to `build/site`,
and does not configure a custom UI bundle. `ui/README.md` is only a placeholder
for a future Valentus theme; no CSS, JavaScript, HTML template, or theme code
is included in this migration.

## Navigation

`content/modules/ROOT/nav.adoc` has this semantic shape:

```text
* Learn PostgreSQL
** Front matter
** Chapter 1 ...
*** Major section
** Chapter 2 ...
*** Major section
...
** Chapter 19 ...
** Closing material and index
```

The actual entries use stable page IDs and anchors derived from book headings,
not PDF chunk names. Sections that stay within a single page use xref anchors;
sections split into pages use page-level xrefs.

## Validation

The migration provides static validation and an optional Antora build.

Static checks include:

- exactly 75 source PDF chunks and 75 translated Markdown chunks;
- all original archive paths exist after migration;
- chapter and section counts match the source TOC/heading inventory;
- all 74 boundary reports are accounted for in the conversion audit;
- no duplicate or missing chapter/section transition;
- balanced AsciiDoc source blocks and no code/table boundary loss;
- all referenced images and links resolve where assets are available;
- no `part-xxx` appears in navigation or generated page IDs;
- generated manifest and reports identify unresolved semantic boundaries rather
  than guessing.

If Node.js and Antora are available, `scripts/build-antora.sh` runs the local
playbook and verifies that `build/site` is generated. Environment failures are
reported separately from content validation failures.

## Risks and Explicit Non-Goals

- Extracted image-only labels are not redrawn or inferred.
- Source promotional pages and index material are not silently discarded.
- No frontend design, theme integration, or UI asset implementation is part of
  this phase.
- A boundary that cannot be resolved from the merged Markdown and reports is
  recorded in the migration report and left visibly flagged; it is never
  resolved by inventing structure.
