import unittest
from pathlib import Path

from scripts.migration_lib import (
    convert_markdown,
    parse_book,
    plan_pages,
    semantic_asset_name,
    toc_major_titles,
)


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "source" / "markdown" / "translated-book.md"


class MigrationStructureTests(unittest.TestCase):
    def test_real_book_has_nineteen_chapters_in_source_order(self):
        chapters = parse_book(BOOK.read_text(encoding="utf-8"))

        self.assertEqual([chapter.number for chapter in chapters], list(range(1, 20)))
        self.assertEqual(chapters[0].title, "1. Giới thiệu về PostgreSQL")
        self.assertEqual(chapters[-1].number, 19)

    def test_long_chapters_are_split_at_semantic_sections(self):
        book_text = BOOK.read_text(encoding="utf-8")
        pages = plan_pages(parse_book(book_text), toc_major_titles(book_text))
        chapter_five = [page for page in pages if page.chapter == 5]
        chapter_four = [page for page in pages if page.chapter == 4]
        chapter_three = [page for page in pages if page.chapter == 3]

        self.assertGreater(len(chapter_five), 1)
        self.assertGreater(len(chapter_four), 1)
        self.assertEqual(len(chapter_three), 1)
        self.assertTrue(all("part-" not in page.page_id for page in pages))
        self.assertTrue(any(page.section_title == "Tìm hiểu về join" for page in chapter_five))

    def test_toc_major_sections_exclude_child_entries(self):
        titles = toc_major_titles(BOOK.read_text(encoding="utf-8"))

        self.assertIn("Kết nối tới cluster", titles[2])
        self.assertNotIn("PostgreSQL processes", titles[2])
        self.assertIn("Quản lý table", titles[4])
        self.assertIn("Tạo và quản lý database", titles[4])
        self.assertNotIn("Tùy chọn `EXISTS`", titles[4])
        self.assertNotIn("Tạo database", titles[4])


class MarkdownConversionTests(unittest.TestCase):
    def test_converts_blocks_without_treating_code_comments_as_headings(self):
        markdown = """# Chapter\n\n## Section\n\n```bash\n# keep this shell comment\npsql --version\n....\n```\n\n> **WARNING:** Keep the command unchanged.\n>\n> ```sql\n> SELECT 1;\n> ```\n\n![Diagram](assets/diagram.png)\n\n[Docs](https://example.test/docs)\n"""

        asciidoc = convert_markdown(markdown, image_names={"diagram.png"})

        self.assertIn("= Chapter", asciidoc)
        self.assertIn("== Section", asciidoc)
        self.assertIn("# keep this shell comment", asciidoc)
        self.assertIn("[source,bash]", asciidoc)
        self.assertIn("\\....", asciidoc)
        self.assertIn("[source,sql]", asciidoc)
        self.assertNotIn("```", asciidoc)
        self.assertIn("[WARNING]", asciidoc)
        self.assertIn("image::diagram.png[Diagram]", asciidoc)
        self.assertIn("https://example.test/docs[Docs]", asciidoc)

    def test_converts_markdown_table_and_nested_list(self):
        markdown = """| Name | Value |\n| --- | --- |\n| `a` | 1 |\n\n- first\n  - nested\n\n4. fourth\n5. fifth\n"""

        asciidoc = convert_markdown(markdown)

        self.assertIn("[cols=\"2*\", options=\"header\"]", asciidoc)
        self.assertIn("|===", asciidoc)
        self.assertIn("| `a` | 1", asciidoc)
        self.assertIn("* first", asciidoc)
        self.assertIn("** nested", asciidoc)
        self.assertIn("[%start=4]", asciidoc)
        self.assertIn(". fourth", asciidoc)

    def test_asset_names_are_semantic(self):
        self.assertEqual(
            semantic_asset_name("part-016-figure-5-1-000.png"),
            "chapter-05-figure-5-1-000.png",
        )
        self.assertNotIn("part-", semantic_asset_name("part-069-figure-18-3-000.jpg"))


if __name__ == "__main__":
    unittest.main()
