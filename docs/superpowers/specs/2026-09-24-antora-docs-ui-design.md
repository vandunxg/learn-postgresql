# Antora Documentation UI Design

**Date:** 2026-09-24
**Status:** Approved for planning
**Scope:** Reusable Antora documentation UI based on the V3 HTML reference

## Goal

Replace the remote Antora default UI bundle with a local, reusable documentation
theme that follows the layout, palette, and reader behavior of
`docs/sample-postgresql-theme-v3.html`.

The production UI must render every AsciiDoc page through Antora's page model.
The sample HTML remains a visual and interaction reference only. Chapter names,
sample prose, sample navigation, sample code, and sample anchors must not be
copied into the production template.

## Decisions

### Architecture

Use a custom local Antora UI bundle with Handlebars templates, CSS, and vanilla
JavaScript. The bundle is Valentus-style and Antora-compatible, but does not
depend on a separate Valentus source repository because none exists in the
current project.

The responsibilities are:

```text
content/
  antora.yml
  modules/ROOT/
    pages/
    images/
    examples/
    partials/
    nav.adoc

ui/
  src/
    layouts/default.hbs
    partials/
    css/
    js/
    helpers/
  ui.yml
  build-ui.sh

playbook/
  antora-playbook.yml
```

`content/` remains content-only. `ui/` contains all reader presentation and
behavior. The playbook points to a locally built UI bundle instead of the
remote `antora-ui-default` artifact.

### Template composition

`default.hbs` is a small composition root. It includes these focused partials:

- `header.hbs`: dynamic site/component identity, search integration point,
  theme toggle, and mobile menu button.
- `sidebar.hbs`: recursive Antora navigation with active page and active
  section state.
- `article.hbs`: semantic page heading, breadcrumbs when available,
  `page.contents`, and page metadata attributes for client-side state.
- `toc.hbs`: page heading TOC from Antora's generated page TOC.
- `pagination.hbs`: dynamic previous/next page cards.
- `reader-tools.hbs`: top progress line, floating progress/back-to-top button,
  and highlight status.

Templates use Antora data such as `site.title`, component/version metadata,
`page.title`, `page.contents`, `page.url`, navigation, TOC, breadcrumbs,
previous, and next. No template branch may depend on a specific chapter name or
filename prefix.

### Rendering and content compatibility

The article renders Asciidoctor output directly. CSS targets standard Antora
and Asciidoctor structures, including headings, paragraphs, inline code,
listing/source blocks, tables, image/figure blocks, lists, quote blocks,
cross-references, footnotes, and admonition blocks.

Source blocks receive a client-side toolbar enhancement without changing their
code text. Tables are wrapped in an overflow container where necessary. The
template does not modify any `.adoc` file to support the layout.

### Reader state

All client-side state is page-scoped and namespaced:

```text
learn-postgresql:theme
learn-postgresql:reading-position:<page-key>
```

The page key comes from the generated page URL or another stable Antora page
identity exposed by the template. It is written to a `data-page-key` attribute
on the page shell.

#### Theme

Theme initialization runs before the visible UI where practical. It reads the
stored preference, then falls back to `prefers-color-scheme`, and sets
`html[data-theme]`. The toggle updates its accessible name and persists the
choice.

#### Reading position

The implementation may save a debounced scroll position under the page-scoped
key. It does not automatically scroll on first load in this phase, avoiding a
surprising navigation jump. The storage boundary leaves room for opt-in
restoration later.

### Progressive enhancements

- Copy buttons use `pre code` text content and show `Copy`, `Copied`, or a
  graceful failure state without throwing an uncaught error.
- TOC and sidebar section activation use `IntersectionObserver` when available.
  Static links remain usable without it.
- The floating reader button updates the top progress line, circular progress,
  tooltip, and ARIA label, and scrolls smoothly to the article top.
- The search field exposes a stable hook for Lunr, Algolia, Pagefind, or an
  Antora search extension, but does not contain sample data or implement a
  search engine in this phase.
- Mobile navigation is a real button with keyboard focus, close behavior, and
  an independent sidebar scroll region.

## Visual system

The visual system follows the reference without copying its sample DOM.

### Tokens

Light mode uses the warm neutral background/surface palette, PostgreSQL blue
accent, muted text, light borders, dark code surface, and pale admonition
surfaces from the reference. Dark mode uses the charcoal background/surface
palette, lighter blue accent/link colors, dark code surface, and compatible
admonition/highlight colors.

Tokens are semantic CSS custom properties in `tokens.css`, including:

```text
background, surface, secondary, text, muted, border
accent, accent-strong, accent-soft, link
code-background, code-text, inline-code-background
note, tip, warning, important, caution
```

The body uses a system fallback equivalent to Source Sans 3. Code uses a system
fallback equivalent to JetBrains Mono. No remote font is required for a usable
page.

### Layout breakpoints

- Desktop at approximately `1024px` and above: sticky header, independently
  scrolling left navigation, fluid article column capped around `840px`, and
  right TOC around `240px`.
- Tablet: retain left navigation and article, hide the right TOC.
- Mobile at approximately `820px` and below: full-width article, sidebar drawer
  closed by default, hamburger menu, and no right TOC.
- The `320px` target must not create page-level horizontal overflow.

Only code blocks and wide tables may scroll horizontally. Headings use a
sticky-header-aware `scroll-margin-top`.

## Accessibility

The output uses semantic `header`, `nav`, `main`, `article`, `aside`, and
`footer` structures. Each page has one primary `h1`; generated heading levels
are not rewritten by the UI.

Icon-only buttons have accessible names. Highlight uses `aria-pressed`, mobile
navigation exposes its state, copy buttons are keyboard reachable, and the
reader control updates its accessible name with the current percentage.
Links, buttons, inputs, tables, and code controls receive visible focus styles
and dark-mode-compatible contrast. Tables retain `thead`, `tbody`, `th`, and
`td` semantics from Asciidoctor output.

## Build and integration

The UI source is packaged as a local Antora UI bundle. The build must be
repeatable without a frontend framework. The bundle contains the Antora UI
configuration, compiled/packaged CSS and JS assets, layouts, partials, helpers,
and any local icons/assets required by the theme.

The playbook is changed to consume the local bundle. The existing content
source configuration and page navigation remain the source of truth. Existing
content is not renamed or rewritten merely to satisfy the UI.

## Validation strategy

Validation is layered:

1. Build the UI bundle and verify the expected bundle files exist.
2. Build the Antora site and verify output is written to `build/site`.
3. Inspect generated pages for dynamic site title, navigation, article content,
   TOC, breadcrumbs where available, and previous/next links.
4. Search the UI source and generated HTML for forbidden sample chapter names,
   sample anchors, and removed user-highlight behavior.
5. Run browser smoke checks at desktop and mobile widths for theme persistence,
   sidebar drawer, TOC activation, copy behavior, and progress/back-to-top.
6. Confirm a JavaScript failure does not prevent reading or normal navigation.
7. Check browser console output for uncaught errors during the smoke flow.

The acceptance target is the requirements document at
`docs/antora-docs-ui-requirements.md`, especially its criteria for dynamic
Antora content, reusable templates, page-scoped reader state, responsive
behavior, accessibility, and successful Antora build.

## Out of scope

This phase does not add login, accounts, synchronization, backend APIs,
comments, shared annotations, AI features, editing, WYSIWYG behavior,
analytics, or an actual search engine.

## Risks and mitigations

- **Antora model differences:** verify the exact navigation, TOC, and
  previous/next shapes against generated output before finalizing helpers.
- **Incomplete content navigation:** do not hide build errors in the UI. Report
  broken xrefs or missing pages separately from template work.
- **Local bundle packaging:** verify the bundle with a real Antora build rather
  than treating a successful archive command as sufficient.
