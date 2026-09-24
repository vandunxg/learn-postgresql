"""Small, dependency-free helpers for the Markdown to AsciiDoc migration."""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
import unicodedata


CHAPTER_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CHAPTER_TITLE = re.compile(r"^(?:Chương\s+)?(\d{1,2})(?:[.)]|\s+)(.*)$", re.I)
SPECIAL_CHAPTER_TITLES = {"Làm quen với cluster của bạn": 2}
CLOSING_HEADINGS = {
    "packt.com",
    "Những cuốn sách khác bạn có thể thích",
    "Chỉ mục",
}
FENCE = re.compile(r"^\s*(`{3,}|~{3,})([^`]*)\s*$")
TABLE_SEPARATOR = re.compile(
    r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?\s*$"
)
ADMONITION = re.compile(r"^\*\*(WARNING|NOTE|TIP|IMPORTANT|CAUTION):\*\*\s*(.*)$", re.I)
ASSET_CHAPTER = {
    "016": "05",
    "017": "05",
    "019": "06",
    "021": "06",
    "034": "10",
    "039": "10",
    "041": "11",
    "043": "11",
    "044": "11",
    "045": "11",
    "047": "12",
    "049": "13",
    "056": "14",
    "057": "14",
    "061": "15",
    "063": "16",
    "064": "16",
    "065": "17",
    "066": "17",
    "067": "18",
    "069": "18",
}


@dataclass
class Section:
    title: str
    level: int
    start: int
    end: int


@dataclass
class Chapter:
    number: int
    title: str
    level: int
    start: int
    end: int
    lines: list[str]
    sections: list[Section]


@dataclass
class PageSpec:
    page_id: str
    chapter: int | None
    title: str
    section_title: str | None
    content: str
    source_start: int
    source_end: int


def _headings(text: str) -> list[tuple[int, str, int]]:
    lines = text.splitlines(keepends=True)
    result: list[tuple[int, str, int]] = []
    in_fence = False
    fence_char = ""
    for index, line in enumerate(lines):
        fence = FENCE.match(line.rstrip("\n"))
        if fence:
            marker = fence.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_char = marker
            elif marker == fence_char:
                in_fence = False
            continue
        if not in_fence:
            heading = CHAPTER_HEADING.match(line.rstrip("\n"))
            if heading:
                result.append((len(heading.group(1)), heading.group(2), index))
    return result


def parse_book(text: str) -> list[Chapter]:
    """Return numbered chapters while ignoring headings inside code fences."""

    lines = text.splitlines(keepends=True)
    chapter_headers: list[tuple[int, str, int]] = []
    for level, title, index in _headings(text):
        match = CHAPTER_TITLE.match(title)
        if match and 1 <= int(match.group(1)) <= 19:
            chapter_headers.append((level, title, index))
        elif title in SPECIAL_CHAPTER_TITLES:
            chapter_headers.append((level, f"2. {title}", index))

    chapters: list[Chapter] = []
    for position, (level, title, start) in enumerate(chapter_headers):
        end = chapter_headers[position + 1][2] if position + 1 < len(chapter_headers) else len(lines)
        if position + 1 == len(chapter_headers):
            closing = [
                heading_index
                for _, heading_title, heading_index in _headings("".join(lines[start:end]))
                if heading_index > 0 and heading_title in CLOSING_HEADINGS
            ]
            if closing:
                end = start + min(closing)
        sections: list[Section] = []
        for section_level, section_title, section_start in _headings("".join(lines[start:end])):
            absolute = start + section_start
            if absolute == start:
                continue
            if section_level < level:
                continue
            sections.append(Section(section_title, section_level, absolute, end))
        for index, section in enumerate(sections):
            section.end = sections[index + 1].start if index + 1 < len(sections) else end
        number = int(CHAPTER_TITLE.match(title).group(1))
        chapters.append(Chapter(number, title, level, start, end, lines[start:end], sections))
    return chapters


def toc_major_titles(text: str) -> dict[int, list[str]]:
    """Extract first-level chapter sections from the source table of contents."""

    records: dict[int, list[tuple[int, str]]] = {}
    current: int | None = None
    in_toc = False
    for line in text.splitlines():
        if line.strip() == "# Mục lục":
            in_toc = True
            continue
        if in_toc and line.strip() == "# Lời nói đầu":
            break
        if not in_toc:
            continue
        chapter_heading = re.match(r"^#{1,6}\s+Chương\s+(\d+)", line)
        value = re.sub(r"^\s*-\s*", "", line).replace("**", "").strip()
        chapter_bullet = re.match(r"^Chương\s+(\d+)", value)
        if chapter_heading:
            current = int(chapter_heading.group(1))
            records.setdefault(current, [])
            continue
        if chapter_bullet:
            current = int(chapter_bullet.group(1))
            records.setdefault(current, [])
            continue
        if current is None or not line.lstrip().startswith("-"):
            continue
        title = re.sub(r"\s+[•—]\s+[0-9x].*$", "", value).strip()
        if title:
            records[current].append((len(line) - len(line.lstrip()), title))

    result: dict[int, list[str]] = {}
    for chapter, chapter_records in records.items():
        has_zero = any(indent == 0 for indent, _ in chapter_records)
        first_zero = next(
            (index for index, (indent, _) in enumerate(chapter_records) if indent == 0),
            len(chapter_records),
        )
        if not has_zero:
            result[chapter] = [title for indent, title in chapter_records if indent <= 2]
        else:
            result[chapter] = [
                title
                for index, (indent, title) in enumerate(chapter_records)
                if indent == 0 or (indent == 2 and index < first_zero)
            ]
    return result


def _slug(value: str) -> str:
    value = value.replace("Đ", "D").replace("đ", "d")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "section"


def semantic_asset_name(name: str) -> str:
    """Replace legacy chunk prefixes in publishable asset names."""

    match = re.match(r"part-(\d{3})-(.+)$", name)
    if not match or match.group(1) not in ASSET_CHAPTER:
        return name
    return f"chapter-{ASSET_CHAPTER[match.group(1)]}-{match.group(2)}"


LONG_CHAPTER_LINE_THRESHOLD = 650


def _same_section_title(source_title: str, toc_title: str) -> bool:
    def normalize(value: str) -> str:
        value = value.lower().replace("của bạn", "").strip()
        value = re.sub(r"[^\w]+|_", " ", value, flags=re.UNICODE)
        value = re.sub(r"\s+", " ", value).strip()
        return re.sub(r"\b([a-z0-9_]+)s\b", r"\1", value)

    source = normalize(source_title)
    toc = normalize(toc_title)
    aliases = {
        "yêu cầu kỹ thuật": {"technical requirement", "technical requirements"},
        "giới thiệu về user và group": {"introduction to users and groups"},
        "quản lý role": {"managing roles"},
        "quản lý incoming connection ở cấp role": {"quản lý connection đến ở role level"},
        "khám phá cte": {"tìm hiểu cte"},
        "sử dụng các statement window function nâng cao": {
            "sử dụng advanced statement window function"
        },
        "khám phá functions và languages": {"khám phá function và language"},
        "các khái niệm cơ bản": {"concept cơ bản"},
        "khám phá declarative partitioning": {"exploring declarative partitioning"},
        "tìm hiểu roles": {"tìm hiểu về role"},
        "ssl connections": {"kết nối ssl"},
        "backup song song": {"parallel backups"},
        "tìm hiểu physical backup": {"khám phá physical backup"},
        "các khái niệm cơ bản phía sau pitr": {"các khái niệm cơ bản đằng sau pitr"},
        "monitoring cluster": {"monitoring the cluster"},
        "statistics nâng cao với extension pg stat statements": {
            "thống kê nâng cao với extension pg stat statements"
        },
        "tìm hiểu các khái niệm replication cơ bản": {
            "khám phá các khái niệm cơ bản về replication"
        },
        "tìm hiểu các khái niệm cơ bản của logical replication": {
            "tìm hiểu các concept cơ bản của logical replication"
        },
        "tìm hiểu thiết lập logical replication và các tính năng logical replication mới trên postgresql 16": {
            "khám phá một logical replication setup và các feature logical replication mới trên postgresql 16"
        },
        "tìm hiểu extension pg trgm": {"khám phá extension pg trgm"},
        "statement explain": {"the explain statement"},
        "statistics nâng cao với extension pg stat statement": {
            "thống kê nâng cao với extension pg stat statement"
        },
        "sử dụng foreign data wrapper và extension postgres fdw": {
            "sử dụng foreign data wrappers và extension postgres fdw"
        },
        "di chuyển từ mysql mariadb sang postgresql bằng pgloader": {
            "migrate từ mysql mariadb sang postgresql bằng pgloader"
        },
        "tóm tắt": {"tổng kết"},
    }
    normalized_aliases = {
        normalize(key): values for key, values in aliases.items()
    }
    if any(normalize(alias) == source for alias in normalized_aliases.get(toc, set())):
        return True
    if toc == normalize("Tìm hiểu extension pg_trgm") and source.startswith("khám phá extension pg trgm"):
        return True
    if toc == normalize("Statistics nâng cao với extension pg_stat_statements") and source.startswith(
        "thống kê nâng cao với pg stat statement"
    ):
        return True
    return source == toc or source.startswith(toc) or toc.startswith(source)


def plan_pages(
    chapters: list[Chapter], major_titles: dict[int, list[str]] | None = None
) -> list[PageSpec]:
    """Build stable page IDs from chapter and real section headings."""

    pages: list[PageSpec] = []
    for chapter in chapters:
        chapter_id = f"chapter-{chapter.number:02d}"
        if major_titles and chapter.number in major_titles:
            major_sections = []
            next_section = 0
            for title in major_titles[chapter.number]:
                match_index = next(
                    (
                        index
                        for index, section in enumerate(chapter.sections[next_section:], next_section)
                        if _same_section_title(section.title, title)
                    ),
                    None,
                )
                if match_index is not None:
                    major_sections.append(chapter.sections[match_index])
                    next_section = match_index + 1
        else:
            major_sections = [
                section
                for section in chapter.sections
                if section.level in (chapter.level, chapter.level + 1)
            ]
        if len(chapter.lines) <= LONG_CHAPTER_LINE_THRESHOLD or not major_sections:
            pages.append(
                PageSpec(chapter_id, chapter.number, chapter.title, None, "".join(chapter.lines), chapter.start, chapter.end)
            )
            continue

        first_section = major_sections[0].start - chapter.start
        pages.append(
            PageSpec(
                chapter_id,
                chapter.number,
                chapter.title,
                None,
                "".join(chapter.lines[:first_section]),
                chapter.start,
                major_sections[0].start,
            )
        )
        seen: dict[str, int] = {}
        for index, section in enumerate(major_sections):
            slug = _slug(section.title)
            seen[slug] = seen.get(slug, 0) + 1
            suffix = f"-{seen[slug]}" if seen[slug] > 1 else ""
            section_end = major_sections[index + 1].start if index + 1 < len(major_sections) else chapter.end
            pages.append(
                PageSpec(
                    f"{chapter_id}-{slug}{suffix}",
                    chapter.number,
                    section.title,
                    section.title,
                    "".join(chapter.lines[section.start - chapter.start : section_end - chapter.start]),
                    section.start,
                    section_end,
                )
            )
    return pages


def _strip_table_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    return [cell.strip() for cell in value.split("|")]


def _convert_inline(text: str, image_names: set[str] | None) -> str:
    def image_replacement(match: re.Match[str]) -> str:
        alt, target = match.group(1), match.group(2)
        name = semantic_asset_name(Path(target).name)
        return f"image::{name}[{alt}]"

    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", image_replacement, text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\2[\1]", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"*\1*", text)
    return text


def _append_quote_content(output: list[str], values: list[str], image_names: set[str] | None) -> None:
    inner_fence = False
    inner_char = ""
    for value in values:
        fence = FENCE.match(value)
        if fence:
            marker = fence.group(1)[0]
            if not inner_fence:
                inner_fence = True
                inner_char = marker
                language = fence.group(2).strip()
                output.append(f"[source,{language}]" if language else "[source]")
                output.append("....")
            elif marker == inner_char:
                inner_fence = False
                output.append("....")
            else:
                output.append(value)
        elif inner_fence:
            output.append("\\" + value if value.strip() == "...." else value)
        else:
            output.append(_convert_inline(value, image_names))


def convert_markdown(markdown: str, image_names: set[str] | None = None) -> str:
    """Convert the supported Markdown constructs without touching code text."""

    lines = markdown.splitlines()
    output: list[str] = []
    in_fence = False
    fence_char = ""
    first_heading_level: int | None = None
    last_order_depth: int | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_char = marker
                language = fence.group(2).strip()
                output.append(f"[source,{language}]" if language else "[source]")
                output.append("....")
            elif marker == fence_char:
                in_fence = False
                output.append("....")
            else:
                output.append(line)
            index += 1
            continue

        if in_fence:
            output.append("\\" + line if line.strip() == "...." else line)
            index += 1
            continue

        heading = CHAPTER_HEADING.match(line)
        if heading:
            last_order_depth = None
            level = len(heading.group(1))
            if first_heading_level is None:
                first_heading_level = level
                asciidoc_level = 1
            elif level == first_heading_level:
                # A page may contain several source-level headings (for
                # example front matter); only the first one may be a document
                # title in AsciiDoc.
                asciidoc_level = 2
            else:
                asciidoc_level = max(2, level - first_heading_level + 1)
            output.append("=" * asciidoc_level + " " + _convert_inline(heading.group(2), image_names))
            index += 1
            continue

        if index + 1 < len(lines) and "|" in line and TABLE_SEPARATOR.match(lines[index + 1]):
            last_order_depth = None
            header = _strip_table_row(line)
            output.append(f"[cols=\"{len(header)}*\", options=\"header\"]")
            output.append("|===")
            output.append(" ".join("| " + _convert_inline(cell, image_names) for cell in header))
            index += 2
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                output.append(
                    " ".join("| " + _convert_inline(cell, image_names) for cell in _strip_table_row(lines[index]))
                )
                index += 1
            output.append("|===")
            continue

        if line.lstrip().startswith(">"):
            last_order_depth = None
            quote_lines: list[str] = []
            while index < len(lines) and (lines[index].lstrip().startswith(">") or not lines[index].strip()):
                current = lines[index]
                if current.lstrip().startswith(">"):
                    quote_lines.append(re.sub(r"^\s*>\s?", "", current))
                else:
                    quote_lines.append("")
                index += 1
            label = ADMONITION.match(quote_lines[0]) if quote_lines else None
            if label:
                output.append(f"[{label.group(1).upper()}]")
                output.append("====")
                quote_content = [label.group(2), *quote_lines[1:]]
                _append_quote_content(output, quote_content, image_names)
                output.append("====")
            else:
                output.append("[quote]")
                output.append("____")
                _append_quote_content(output, quote_lines, image_names)
                output.append("____")
            continue

        list_match = re.match(r"^(\s*)([-*])\s+(.*)$", line)
        if list_match:
            last_order_depth = None
            depth = len(list_match.group(1)) // 2
            output.append("*" * (depth + 1) + " " + _convert_inline(list_match.group(3), image_names))
            index += 1
            continue

        ordered_match = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if ordered_match:
            depth = len(ordered_match.group(1)) // 2
            number = int(ordered_match.group(2))
            if last_order_depth != depth and number != 1:
                output.append(f"[%start={number}]")
            output.append("." * (depth + 1) + " " + _convert_inline(ordered_match.group(3), image_names))
            last_order_depth = depth
            index += 1
            continue

        if line.strip():
            last_order_depth = None
        output.append(_convert_inline(line, image_names))
        index += 1

    return "\n".join(output).rstrip() + "\n"
