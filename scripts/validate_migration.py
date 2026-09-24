#!/usr/bin/env python3
"""Validate the semantic migration without requiring Antora or Node.js."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.migration_lib import parse_book, plan_pages, toc_major_titles


def _paths(root: Path) -> tuple[Path, Path, Path]:
    source = root / "source" / "markdown" / "translated-book.md"
    if not source.exists():
        source = root / "vi" / "learn-postgresql-vi.md"
    parts = root / "source" / "markdown" / "translated-parts"
    if not parts.exists():
        parts = root / "vi" / "parts"
    reports = root / "translation" / "reports"
    if not reports.exists():
        reports = root / "vi" / "reports"
    return source, parts, reports


def _balanced(text: str, marker: str) -> bool:
    return sum(1 for line in text.splitlines() if line.strip() == marker) % 2 == 0


def validate(root: Path) -> list[str]:
    source, parts, reports = _paths(root)
    errors: list[str] = []
    if not source.exists():
        errors.append(f"missing translated book: {source}")
        return errors
    if not (root / "source" / "pdf" / "original.pdf").exists() and not (root / "027652113.pdf").exists():
        errors.append("missing original PDF")
    if len(list(parts.glob("part-*.md"))) != 75:
        errors.append("expected 75 translated Markdown parts")
    if len(list((root / "source" / "pdf" / "parts").glob("part-*.pdf"))) not in (0, 75):
        errors.append("expected 75 PDF parts when archive has been migrated")
    if len(list(reports.glob("boundary-*.md"))) != 74:
        errors.append("expected 74 boundary reports")

    chapters = parse_book(source.read_text(encoding="utf-8"))
    if [chapter.number for chapter in chapters] != list(range(1, 20)):
        errors.append("chapter inventory is not exactly 1 through 19")

    pages_dir = root / "content" / "modules" / "ROOT" / "pages"
    nav_path = root / "content" / "modules" / "ROOT" / "nav.adoc"
    manifest_path = root / "build" / "reports" / "migration-manifest.json"
    if not pages_dir.exists():
        errors.append("missing generated pages directory")
        return errors
    if not nav_path.exists():
        errors.append("missing nav.adoc")
    if not manifest_path.exists():
        errors.append("missing migration manifest")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_pages = len(plan_pages(chapters, toc_major_titles(source.read_text(encoding="utf-8")))) + 2
        if manifest.get("page_count") != expected_pages:
            errors.append("manifest page count does not match semantic page plan")
        expected_boundaries = sorted(
            str(path.relative_to(root)) for path in reports.glob("boundary-*.md")
        )
        if manifest.get("boundary_reports") != expected_boundaries:
            errors.append("manifest boundary report inventory is incomplete")

    expected_page_ids = {"front-matter", "closing-material"}
    expected_page_ids.update(
        page.page_id for page in plan_pages(chapters, toc_major_titles(source.read_text(encoding="utf-8")))
    )
    actual_page_ids = {path.stem for path in pages_dir.glob("*.adoc")}
    if actual_page_ids != expected_page_ids:
        errors.append("generated page inventory does not match semantic page plan")
    for page_id in sorted(expected_page_ids):
        page_path = pages_dir / f"{page_id}.adoc"
        if not page_path.exists():
            continue
        first_content = next(
            (line for line in page_path.read_text(encoding="utf-8").splitlines() if line.strip()),
            "",
        )
        if not first_content.startswith("= "):
            errors.append(f"page has no AsciiDoc document title: {page_path.name}")

    adoc_files = list(pages_dir.glob("*.adoc"))
    for path in adoc_files:
        text = path.read_text(encoding="utf-8")
        if not _balanced(text, "...."):
            errors.append(f"unbalanced listing block: {path.name}")
        if not _balanced(text, "|==="):
            errors.append(f"unbalanced table block: {path.name}")
        if not _balanced(text, "____"):
            errors.append(f"unbalanced quote block: {path.name}")
        if "```" in text or "~~~" in text:
            errors.append(f"Markdown fence remains: {path.name}")

    image_dir = root / "content" / "modules" / "ROOT" / "images"
    image_names = {path.name for path in image_dir.glob("*") if path.is_file()}
    for path in adoc_files:
        for image_name in re.findall(r"image::([^\[]+)\[", path.read_text(encoding="utf-8")):
            if image_name not in image_names:
                errors.append(f"missing image {image_name} referenced by {path.name}")

    if nav_path.exists():
        nav = nav_path.read_text(encoding="utf-8")
        if re.search(r"part-\d{3}", nav, re.I):
            errors.append("part-xxx identifier appears in nav.adoc")
        if nav.count("xref:chapter-") < 19:
            errors.append("nav.adoc does not contain all 19 chapters")

    report_path = root / "build" / "reports" / "migration-validation.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if not errors else "FAIL"
    report = ["# Migration Validation", "", f"Status: **{status}**", ""]
    report.append("## Checks")
    report.extend(f"- {error}" for error in errors)
    if not errors:
        report.append("- 75 translated Markdown parts present")
        report.append("- 74 boundary reports present")
        report.append("- 19 chapters and semantic pages validated")
        report.append("- AsciiDoc block and asset checks passed")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return errors


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("Migration validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
