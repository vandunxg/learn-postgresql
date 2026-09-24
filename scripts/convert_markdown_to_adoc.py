#!/usr/bin/env python3
"""Generate semantic AsciiDoc pages and Antora navigation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.migration_lib import PageSpec, convert_markdown, parse_book, plan_pages, toc_major_titles


def _source_paths(root: Path) -> tuple[Path, Path]:
    new_path = root / "source" / "markdown" / "translated-book.md"
    old_path = root / "vi" / "learn-postgresql-vi.md"
    source = new_path if new_path.exists() else old_path
    image_dir = root / "content" / "modules" / "ROOT" / "images"
    return source, image_dir


def _write_page(output_dir: Path, page_id: str, content: str, image_names: set[str]) -> None:
    path = output_dir / f"{page_id}.adoc"
    path.write_text(convert_markdown(content, image_names), encoding="utf-8")


def _build_nav(pages: list[PageSpec]) -> str:
    lines = ["* Learn PostgreSQL"]
    front = next(page for page in pages if page.chapter is None)
    lines.append(f"** xref:{front.page_id}.adoc[Front matter]")
    for chapter_number in sorted({page.chapter for page in pages if page.chapter is not None}):
        chapter_pages = [page for page in pages if page.chapter == chapter_number]
        chapter_page = next(page for page in chapter_pages if page.section_title is None)
        lines.append(f"** xref:{chapter_page.page_id}.adoc[{chapter_page.title}]")
        for section in (page for page in chapter_pages if page.section_title is not None):
            lines.append(f"*** xref:{section.page_id}.adoc[{section.section_title}]")
    closing = next((page for page in pages if page.page_id == "closing-material"), None)
    if closing:
        lines.append(f"** xref:{closing.page_id}.adoc[Closing material and index]")
    return "\n".join(lines) + "\n"


def _manifest(pages: list[PageSpec], boundary_reports: list[str]) -> dict:
    chapters: dict[int, dict] = {}
    for page in pages:
        if page.chapter is None:
            continue
        entry = chapters.setdefault(page.chapter, {"pages": [], "sections": []})
        entry["pages"].append(page.page_id)
        if page.section_title is not None:
            entry["sections"].append(page.section_title)
    return {
        "chapters": [{"number": number, **chapters[number]} for number in sorted(chapters)],
        "page_count": len(pages),
        "boundary_reports": boundary_reports,
        "unresolved_boundaries": [],
    }


def convert(root: Path) -> dict:
    source, image_dir = _source_paths(root)
    if not source.exists():
        raise FileNotFoundError(f"translated book not found: {source}")
    output_dir = root / "content" / "modules" / "ROOT" / "pages"
    output_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)
    for page_path in output_dir.glob("*.adoc"):
        page_path.unlink()

    text = source.read_text(encoding="utf-8")
    chapters = parse_book(text)
    if [chapter.number for chapter in chapters] != list(range(1, 20)):
        raise ValueError("source book must contain chapters 1 through 19")
    pages = plan_pages(chapters, toc_major_titles(text))
    front_content = "".join(text.splitlines(keepends=True)[: chapters[0].start])
    lines = text.splitlines(keepends=True)
    closing_content = "".join(lines[chapters[-1].end :])
    all_pages = [PageSpec("front-matter", None, "Front matter", None, front_content, 0, chapters[0].start)] + pages
    if closing_content.strip():
        all_pages.append(
            PageSpec(
                "closing-material",
                None,
                "Closing material and index",
                None,
                closing_content,
                chapters[-1].end,
                len(lines),
            )
        )
    image_names = {path.name for path in image_dir.iterdir() if path.is_file()}

    for page in all_pages:
        content = page.content
        if page.page_id == "front-matter":
            # The source starts with a blockquote before its first heading;
            # give the AsciiDoc page a title so the quote remains valid body
            # content instead of being parsed before a document title.
            content = "# Learn PostgreSQL\n\n" + content
        _write_page(output_dir, page.page_id, content, image_names)

    nav_path = root / "content" / "modules" / "ROOT" / "nav.adoc"
    nav_path.parent.mkdir(parents=True, exist_ok=True)
    nav_path.write_text(_build_nav(all_pages), encoding="utf-8")

    report_dir = root / "build" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    boundary_dir = root / "translation" / "reports"
    if not boundary_dir.exists():
        boundary_dir = root / "vi" / "reports"
    boundary_reports = sorted(
        str(path.relative_to(root)) for path in boundary_dir.glob("boundary-*.md")
    )
    manifest = _manifest(all_pages, boundary_reports)
    manifest_path = report_dir / "migration-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    manifest = convert(args.root.resolve())
    print(f"Generated {manifest['page_count']} AsciiDoc pages and nav.adoc")


if __name__ == "__main__":
    main()
