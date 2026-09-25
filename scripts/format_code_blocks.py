#!/usr/bin/env python3
"""Improve AsciiDoc source-block readability without changing source content."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


SOURCE_BLOCK = re.compile(
    r"(?ms)^(?P<attrs>\[source[^\n]*\])\n"
    r"^\.\.\.\.\n(?P<body>.*?)^\.\.\.\.\n"
)
DERIVED_BLOCK = re.compile(
    r"(?ms)^\.(?:SQL|Command|Output)\n\[source[^\n]*\]\n"
    r"^\.\.\.\.\n.*?^\.\.\.\.\n"
)
PSQL_PROMPT = re.compile(r"^\s*[\w.-]+(?:=\*>|=>|->|=#|-#)\s?(?P<command>.*)$", re.M)
SHELL_PROMPT = re.compile(
    r"^\s*(?:(?:[\w.-]+@[\w.-]+(?::[^$]*)?)?\$|#|%)\s?(?P<command>.*)$",
    re.M,
)
SQL_START = re.compile(
    r"^(?:SELECT|WITH|INSERT|UPDATE|DELETE|MERGE|CREATE|ALTER|DROP|GRANT|REVOKE|"
    r"BEGIN|COMMIT|ROLLBACK|SET|COPY|VACUUM|ANALYZE|EXPLAIN|DO)\b",
    re.I,
)
SQL_KEYWORDS = (
    "ADD",
    "ALL",
    "AND",
    "ALTER",
    "AS",
    "ASC",
    "BEGIN",
    "BY",
    "CASE",
    "CASCADE",
    "CHECK",
    "COLUMN",
    "COMMIT",
    "CONFLICT",
    "CONSTRAINT",
    "CREATE",
    "CURRENT",
    "DATABASE",
    "DEFAULT",
    "DELETE",
    "DESC",
    "DISTINCT",
    "DO",
    "DROP",
    "ELSE",
    "END",
    "EXCEPT",
    "EXISTS",
    "EXPLAIN",
    "FETCH",
    "FOR",
    "FROM",
    "FUNCTION",
    "GROUP",
    "GRANT",
    "HAVING",
    "IN",
    "INSERT",
    "INTERSECT",
    "INTO",
    "INDEX",
    "IS",
    "KEY",
    "JOIN",
    "LANGUAGE",
    "LIMIT",
    "MATERIALIZED",
    "MERGE",
    "NOT",
    "NULL",
    "OFFSET",
    "ON",
    "OR",
    "ORDER",
    "OVER",
    "PARTITION",
    "PRIMARY",
    "REFERENCES",
    "REPLACE",
    "RETURNING",
    "REVOKE",
    "ROLLBACK",
    "SELECT",
    "SET",
    "TABLE",
    "TEMP",
    "THEN",
    "TRUE",
    "UNION",
    "UNIQUE",
    "UPDATE",
    "USING",
    "VALUES",
    "WHEN",
    "WHERE",
    "VIEW",
    "WITH",
    "FALSE",
)
SQL_CLAUSES = (
    "ON CONFLICT",
    "ORDER BY",
    "GROUP BY",
    "UNION ALL",
    "FOR UPDATE",
    "RETURNING",
    "FROM",
    "WHERE",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "FETCH",
    "UNION",
    "INTERSECT",
    "EXCEPT",
)
OUTPUT_MARKER = re.compile(
    r"(?m)^\s*(?:\(\d+ rows?\)|ERROR:|WARNING:|NOTICE:|DETAIL:|HINT:|"
    r"QUERY PLAN|LOG:|[-+]{3,}.*[-+])\s*$",
    re.I,
)


def _attributes(attrs: str) -> tuple[str | None, bool]:
    values = attrs[1:-1].split(",")
    if not values or values[0] != "source":
        return None, False
    language = None
    for value in values[1:]:
        if "=" not in value and language is None:
            language = value.strip().lower()
    return language, any(value.strip().startswith("role=") for value in values[1:])


def _with_language(attrs: str, language: str, role: str | None = None) -> str:
    values = attrs[1:-1].split(",")
    if len(values) == 1:
        values.append(language)
    else:
        language_index = next(
            (index for index, value in enumerate(values[1:], start=1) if "=" not in value),
            None,
        )
        if language_index is None:
            values.insert(1, language)
        else:
            values[language_index] = language
    if role and not any(value.strip().startswith("role=") for value in values[1:]):
        values.append(f'role="{role}"')
    return "[" + ",".join(values) + "]"


def _trim_lines(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def _body(lines: list[str]) -> str:
    return "\n".join(_trim_lines(lines)) + "\n"


def _protect_sql(text: str) -> tuple[str, list[str]]:
    """Hide literals and comments while SQL structure is being reformatted."""

    protected: list[str] = []
    masked: list[str] = []
    index = 0

    def add(value: str) -> None:
        token = f"__SQL_PROTECTED_{len(protected)}__"
        protected.append(value)
        masked.append(token)

    while index < len(text):
        if text.startswith("--", index):
            end = text.find("\n", index)
            if end == -1:
                add(text[index:])
                break
            add(text[index : end + 1])
            index = end + 1
            continue

        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            end = len(text) if end == -1 else end + 2
            add(text[index:end])
            index = end
            continue

        dollar_quote = re.match(r"\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$", text[index:])
        if dollar_quote:
            delimiter = dollar_quote.group(0)
            end = text.find(delimiter, index + len(delimiter))
            end = len(text) if end == -1 else end + len(delimiter)
            add(text[index:end])
            index = end
            continue

        if text[index] in {"'", '"'}:
            quote = text[index]
            start = index
            index += 1
            while index < len(text):
                if text[index] == "\\" and quote == "'":
                    index += 2
                    continue
                if text[index] == quote:
                    if index + 1 < len(text) and text[index + 1] == quote:
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            value = text[start:index]
            if quote == "'":
                value = re.sub(r"[ \t]*\r?\n[ \t]*", " ", value)
            add(value)
            continue

        masked.append(text[index])
        index += 1

    return "".join(masked), protected


def _restore_sql(text: str, protected: list[str]) -> str:
    for index, value in enumerate(protected):
        text = text.replace(f"__SQL_PROTECTED_{index}__", value)
    return text


def _normalize_sql(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*,\s*", ", ", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s*;\s*", ";", text)
    text = re.sub(r"(?<![<>=!])\s*=\s*(?![=>])", " = ", text)
    text = re.sub(r"\bVALUES\s*\(", "VALUES (", text, flags=re.I)
    text = re.sub(r"\b(INTO\s+[^\s(]+)\s*\(", r"\1 (", text, flags=re.I)

    for keyword in sorted(SQL_KEYWORDS, key=len, reverse=True):
        text = re.sub(
            rf"(?<![\w$]){keyword}(?![\w$])",
            keyword,
            text,
            flags=re.I,
        )
    return text.rstrip()


def _paren_depth(text: str, index: int) -> int:
    return text[:index].count("(") - text[:index].count(")")


def _find_top_level_keyword(text: str, keyword: str, start: int = 0) -> int | None:
    escaped_keyword = re.escape(keyword).replace(r"\ ", r"\s+")
    pattern = re.compile(rf"(?<![\w$]){escaped_keyword}(?![\w$])")
    for match in pattern.finditer(text, start):
        if _paren_depth(text, match.start()) == 0:
            return match.start()
    return None


def _split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    for index, character in enumerate(text):
        if character == "(":
            depth += 1
        elif character == ")":
            depth = max(0, depth - 1)
        elif character == delimiter and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return [part for part in parts if part]


def _format_clause_tail(text: str) -> str:
    text = text.strip()
    positions = [
        (position, keyword)
        for keyword in SQL_CLAUSES
        if (position := _find_top_level_keyword(text, keyword)) is not None
    ]
    positions.sort()
    if not positions:
        return text

    lines: list[str] = []
    first_position = positions[0][0]
    if first_position:
        lines.append(text[:first_position].strip())
    for index, (position, keyword) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        clause = text[position:end].strip()
        if keyword in {"ORDER BY", "GROUP BY"} and "," in clause:
            keyword_match = re.match(r"^(ORDER BY|GROUP BY)\s+(.*)$", clause)
            if keyword_match:
                values = keyword_match.group(2)
                items = _split_top_level(values)
                if len(items) > 1:
                    lines.append(keyword_match.group(1))
                    lines.extend(
                        f"    {item}{',' if item != items[-1] else ''}" for item in items
                    )
                    continue
        lines.append(clause)
    return "\n".join(line for line in lines if line)


def _format_select(statement: str) -> str:
    select_position = _find_top_level_keyword(statement, "SELECT")
    if select_position is None:
        return statement
    select_end = select_position + len("SELECT")
    from_position = _find_top_level_keyword(statement, "FROM", select_end)
    if from_position is None:
        return statement

    prefix = statement[:select_position].strip()
    expressions = statement[select_end:from_position].strip()
    tail = _format_clause_tail(statement[from_position:])
    columns = _split_top_level(expressions)
    select_line = f"{prefix + ' ' if prefix else ''}SELECT"
    if len(columns) == 1:
        select_line += f" {columns[0]}"
        return "\n".join((select_line, tail))
    return "\n".join((select_line, *(f"    {column}{',' if column != columns[-1] else ''}" for column in columns), tail))


def _format_insert(statement: str) -> str:
    values_position = _find_top_level_keyword(statement, "VALUES")
    if values_position is None:
        return statement

    prefix = statement[:values_position].strip()
    values = statement[values_position + len("VALUES") :].strip()
    tail_positions = [
        position
        for keyword in ("ON CONFLICT", "RETURNING")
        if (position := _find_top_level_keyword(values, keyword)) is not None
    ]
    values_end = min(tail_positions) if tail_positions else len(values)
    values_part = values[:values_end].strip()
    tail = _format_clause_tail(values[values_end:]) if values_end < len(values) else ""
    value_rows = _split_top_level(values_part)
    if len(value_rows) == 1:
        lines = [f"{prefix}\nVALUES {value_rows[0]}"]
    else:
        lines = [prefix, "VALUES"]
        lines.extend(
            f"    {row}{',' if row != value_rows[-1] else ''}" for row in value_rows
        )
    if tail:
        lines.append(tail)
    return "\n".join(lines)


def _format_update(statement: str) -> str:
    set_position = _find_top_level_keyword(statement, "SET")
    if set_position is None:
        return statement
    prefix = statement[:set_position].strip()
    assignments = statement[set_position + len("SET") :].strip()
    tail_positions = [
        position
        for keyword in ("WHERE", "RETURNING")
        if (position := _find_top_level_keyword(assignments, keyword)) is not None
    ]
    assignments_end = min(tail_positions) if tail_positions else len(assignments)
    assignment_text = assignments[:assignments_end].strip()
    tail = _format_clause_tail(assignments[assignments_end:]) if assignments_end < len(assignments) else ""
    lines = [prefix, "SET"]
    items = _split_top_level(assignment_text)
    lines.extend(f"    {item}{',' if item != items[-1] else ''}" for item in items)
    if tail:
        lines.append(tail)
    return "\n".join(lines)


def _split_statements(text: str) -> list[tuple[str, bool]]:
    statements: list[tuple[str, bool]] = []
    start = 0
    for index, character in enumerate(text):
        if character == ";":
            statements.append((text[start:index].strip(), True))
            start = index + 1
    remainder = text[start:].strip()
    if remainder:
        statements.append((remainder, False))
    return statements


def _preserve_sql_lines(text: str) -> str:
    lines = []
    for line in text.splitlines():
        prefix = re.match(r"^\s*", line).group(0)
        normalized = _normalize_sql(line)
        if normalized:
            lines.append(prefix + normalized)
    if len(lines) > 1:
        indents = [len(line) - len(line.lstrip()) for line in lines[1:] if line.strip()]
        shift = max(0, min(indents, default=0) - 4)
        if shift:
            normalized_lines = [lines[0]]
            for line in lines[1:]:
                content = line.lstrip()
                if content.startswith((")", "]")):
                    normalized_lines.append(content)
                else:
                    normalized_lines.append(line[: max(0, len(line) - len(content) - shift)] + content)
            lines = normalized_lines
    result = "\n".join(lines)
    if re.match(r"^CREATE(?: OR REPLACE)? FUNCTION\b", result, re.I):
        result = re.sub(r"\s+(RETURNS\b)", r"\n    \1", result, count=1, flags=re.I)
        result = re.sub(r"\s+AS\s+BEGIN\b", " AS\nBEGIN", result, count=1, flags=re.I)
        result = re.sub(
            r"(BEGIN)\s+(__SQL_PROTECTED_\d+__)",
            r"\1\n    \2",
            result,
            count=1,
        )
    return result


def format_sql(text: str) -> str:
    """Format common SQL statements while keeping literals and code bodies intact."""

    masked, protected = _protect_sql(text)
    formatted: list[str] = []
    for raw_statement, terminated in _split_statements(masked):
        statement = _normalize_sql(raw_statement)
        if not statement:
            continue
        if statement.startswith("\\"):
            rendered = statement
        elif re.match(r"^(?:EXPLAIN\s+)?SELECT\b", statement):
            rendered = _format_select(statement)
        elif statement.startswith("INSERT"):
            rendered = _format_insert(statement)
        elif statement.startswith("UPDATE"):
            rendered = _format_update(statement)
        else:
            rendered = _preserve_sql_lines(raw_statement)
        formatted.append(rendered + (";" if terminated else ""))
    return _restore_sql("\n".join(formatted), protected).strip()


def _is_complete_sql(lines: list[str]) -> bool:
    if not lines:
        return False
    last = lines[-1].strip()
    return (
        last.startswith("\\")
        or bool(re.search(r";\s*(?:<ENTER>\s*)?(?:--.*)?$", last, re.I))
        or bool(re.search(r"\\(?:g|q)\b", last, re.I))
    )


def _split_inline_psql_output(command: str) -> tuple[str, str | None]:
    match = re.match(r"^(?P<command>.*?\bpsql\b.*?\S)\s{2,}(?P<output>List of databases)\s*$", command)
    if match:
        return match.group("command"), match.group("output")
    return command, None


def _split_transcript(text: str, kind: str) -> tuple[dict[str, str], str]:
    commands = {"psql": [], "shell": []}
    output: list[str] = []
    pending: list[str] = []
    active: list[str] = []
    active_kind: str | None = None
    in_output = False

    def prompt_for(line: str) -> tuple[str, str] | None:
        psql = PSQL_PROMPT.match(line)
        if psql:
            return "psql", psql.group("command")
        shell = SHELL_PROMPT.match(line)
        if shell:
            return "shell", shell.group("command")
        return None

    def flush_active() -> None:
        nonlocal active, active_kind
        if active and active_kind:
            commands[active_kind].extend(active)
        active = []
        active_kind = None

    for line in text.splitlines():
        prompt = prompt_for(line)
        if prompt:
            flush_active()
            prompt_kind, command = prompt
            if pending:
                if _detect_language("\n".join(pending)) == "output":
                    output.extend(pending)
                else:
                    commands[prompt_kind].extend(pending)
                pending = []
            if command.strip():
                inline_output = None
                if prompt_kind == "shell":
                    command, inline_output = _split_inline_psql_output(command)
                active_kind = prompt_kind
                active = [command]
                in_output = prompt_kind == "shell" or _is_complete_sql(active)
                if inline_output:
                    output.append(inline_output)
            else:
                in_output = False
            continue

        if not active_kind:
            pending.append(line)
        elif in_output:
            output.append(line)
        else:
            active.append(line)
            in_output = _is_complete_sql(active)

    flush_active()
    if pending:
        commands[kind if kind in commands else "shell"].extend(pending)

    command_text = {
        name: _body(values) for name, values in commands.items() if _trim_lines(values)
    }
    return command_text, _body(output) if _trim_lines(output) else ""


def _detect_transcript(text: str) -> str | None:
    has_psql = bool(PSQL_PROMPT.search(text))
    has_shell = bool(SHELL_PROMPT.search(text))
    if has_psql and has_shell:
        return "mixed"
    if has_psql:
        return "psql"
    if has_shell:
        return "shell"
    return None


def _detect_language(text: str) -> str | None:
    meaningful = [line.strip() for line in text.splitlines() if line.strip()]
    if not meaningful:
        return None
    first = next((line for line in meaningful if not line.startswith(("--", "#"))), meaningful[0])
    if SQL_START.match(first) and (";" in text or len(meaningful) > 1):
        return "sql"
    if any(line.startswith(("$ ", "# ", "#!/")) for line in meaningful):
        return "bash"
    if OUTPUT_MARKER.search(text):
        return "output"
    return None


def _derived(title: str, language: str, body: str) -> str:
    if language == "sql":
        body = format_sql(body)
    body = body.rstrip("\n") + "\n"
    return f"\n.{title}\n[source,{language}]\n....\n{body}....\n"


def _previous_title(match: re.Match[str]) -> str | None:
    prefix = match.string[: match.start()].rstrip("\n")
    if not prefix:
        return None
    line = prefix.splitlines()[-1].strip()
    return line if line in {".SQL", ".Command", ".Output"} else None


def _transform_block(match: re.Match[str]) -> str:
    attrs = match.group("attrs")
    body = match.group("body")
    language, has_role = _attributes(attrs)
    if has_role or language == "output":
        return match.group(0)

    title = _previous_title(match)
    if title in {".SQL", ".Command", ".Output"}:
        return match.group(0)

    transcript = _detect_transcript(body)
    if transcript:
        commands, output = _split_transcript(body, transcript)
        original_attrs = _with_language(attrs, "console", role="transcript")
        original = original_attrs + match.group(0)[len(attrs) :]
        derived = []
        if transcript == "psql" and commands.get("psql"):
            derived.append(_derived("SQL", "sql", commands["psql"]))
        elif transcript == "shell" and commands.get("shell"):
            derived.append(_derived("Command", "bash", commands["shell"]))
        elif transcript == "mixed":
            if commands.get("shell"):
                derived.append(_derived("Command", "bash", commands["shell"]))
            if commands.get("psql"):
                derived.append(_derived("SQL", "sql", commands["psql"]))
        if output:
            derived.append(_derived("Output", "output", output))
        return original + "".join(derived)

    if language in (None, "text"):
        detected = _detect_language(body)
        if detected:
            if detected == "sql":
                formatted_body = format_sql(body)
                return f"{_with_language(attrs, detected)}\n....\n{formatted_body}\n....\n"
            return _with_language(attrs, detected) + match.group(0)[len(attrs) :]
    if language in {"bash", "sh", "sql"} and _detect_language(body) == "output":
        return _with_language(attrs, "output") + match.group(0)[len(attrs) :]
    if language == "sql":
        formatted_body = format_sql(body)
        return f"{attrs}\n....\n{formatted_body}\n....\n"
    return match.group(0)


def transform_text(text: str) -> str:
    """Return deterministic formatting changes for one AsciiDoc document."""

    return _normalize_eof(_collapse_blank_lines(SOURCE_BLOCK.sub(_transform_block, text)))


def _collapse_blank_lines(text: str) -> str:
    chunks = []
    cursor = 0
    for match in SOURCE_BLOCK.finditer(text):
        chunks.append(re.sub(r"\n{3,}", "\n\n", text[cursor : match.start()]))
        chunks.append(match.group(0))
        cursor = match.end()
    chunks.append(re.sub(r"\n{3,}", "\n\n", text[cursor:]))
    return "".join(chunks)


def reset_text(text: str) -> str:
    """Remove formatter-derived views and restore the original source tag."""

    text = DERIVED_BLOCK.sub("", text)
    text = text.replace('[source,console,role="transcript"]', "[source,text]")
    text = text.replace("[source,output]", "[source,text]")
    return _normalize_eof(_collapse_blank_lines(text))


def _normalize_eof(text: str) -> str:
    return text.rstrip("\n") + "\n"


def _pages(root: Path) -> list[Path]:
    return sorted(root.rglob("*.adoc"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("content/modules/ROOT/pages"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write formatting changes")
    mode.add_argument("--check", action="store_true", help="fail when formatting changes are needed")
    parser.add_argument("--reset", action="store_true", help="remove formatter-derived views")
    args = parser.parse_args()

    changed = []
    for path in _pages(args.root):
        original = path.read_text(encoding="utf-8")
        formatted = reset_text(original) if args.reset else transform_text(original)
        if formatted != original:
            changed.append(path)
            if args.write:
                path.write_text(formatted, encoding="utf-8")

    if args.write:
        print(f"Formatted {len(changed)} AsciiDoc pages")
        return 0
    if changed:
        print("Pages needing code-block formatting:")
        print("\n".join(str(path) for path in changed))
        return 1
    print("Code-block formatting is up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
