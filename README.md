# Learn PostgreSQL Vietnamese Antora Project

This repository publishes the existing Vietnamese translation of *Learn
PostgreSQL* as an AsciiDoc/Antora site. The translated PDF chunks and Markdown
remain in `source/` as immutable source/archive material.

## Layout

- `source/`: original PDF and translated Markdown archive.
- `translation/`: translation instructions, metadata, reports, glossary, and progress.
- `content/`: Antora component, semantic pages, images, and navigation.
- `playbook/`: local Antora playbook.
- `scripts/`: conversion, validation, and build tooling.
- `build/`: generated site, reports, and archive artifacts.
- `ui/`: empty placeholder for a future Valentus theme.

## Commands

```bash
python3 scripts/convert_markdown_to_adoc.py
python3 scripts/validate_migration.py
scripts/build-antora.sh
```

The publish hierarchy uses one book-level Part, `Learn PostgreSQL`, followed by
the 19 chapters and their semantic sections. It does not use the old
`part-xxx` chunk names in navigation or URLs.
