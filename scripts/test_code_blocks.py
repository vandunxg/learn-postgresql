import unittest

from scripts.format_code_blocks import format_sql, transform_text


class CodeBlockFormattingTests(unittest.TestCase):
    def test_sql_formatter_puts_columns_and_clauses_on_readable_lines(self):
        source = "select pk,username,gecos,email from users order by\nusername;"

        formatted = format_sql(source)

        self.assertEqual(
            formatted,
            """SELECT
    pk,
    username,
    gecos,
    email
FROM users
ORDER BY username;""",
        )
        self.assertFalse(any(line.endswith(" ") for line in formatted.splitlines()))

    def test_sql_formatter_keeps_insert_values_readable(self):
        source = "insert into categories (title,description) values ('C\nLanguage', 'Languages'), ('Python Language','Languages');"

        self.assertEqual(
            format_sql(source),
            """INSERT INTO categories (title, description)
VALUES
    ('C Language', 'Languages'),
    ('Python Language', 'Languages');""",
        )

    def test_sql_formatter_preserves_multiline_definition_examples(self):
        source = """CREATE FUNCTION function_name(p1 type, p2 type,p3 type)
    RETURNS type AS
BEGIN
    -- function logic
END;
LANGUAGE language_name"""

        formatted = format_sql(source)

        self.assertIn("CREATE FUNCTION function_name(p1 type, p2 type, p3 type)", formatted)
        self.assertIn("\n    RETURNS type AS\n", formatted)
        self.assertIn("\nBEGIN\n", formatted)

    def test_sql_formatter_removes_trailing_spaces_after_line_breaking_commas(self):
        formatted = format_sql("CREATE TABLE users (\n    id integer,\n    name text\n);")

        self.assertEqual(formatted.splitlines()[1], "    id integer,")

    def test_sql_formatter_normalizes_excessive_statement_indentation(self):
        formatted = format_sql("CREATE TABLE users (\n         id integer,\n         name text\n         );")

        self.assertEqual(
            formatted,
            """CREATE TABLE users (
    id integer,
    name text
);""",
        )

    def test_sql_formatter_formats_query_statements_after_other_statements(self):
        source = """CREATE TEMP TABLE new_data AS SELECT * FROM categories LIMIT 0;
INSERT INTO new_data (pk,title) VALUES (1,'Database'), (2,'Unix');
SELECT * FROM new_data;"""

        formatted = format_sql(source)

        self.assertIn(
            "INSERT INTO new_data (pk, title)\nVALUES\n    (1, 'Database'),\n    (2, 'Unix');",
            formatted,
        )
        self.assertIn("SELECT *\nFROM new_data;", formatted)

    def test_sql_formatter_repairs_collapsed_function_definition_examples(self):
        source = "CREATE FUNCTION function_name(p1 type) RETURNS type AS BEGIN -- function logic\nEND;\nLANGUAGE language_name"

        formatted = format_sql(source)

        self.assertIn("\n    RETURNS type AS\nBEGIN\n    -- function logic\nEND;", formatted)

    def test_psql_transcript_keeps_original_and_adds_sql_and_output_views(self):
        source = """Intro

[source,text]
....
forumdb=> SELECT id, name FROM users;
 id | name
----+------
  1 | Ada
(1 row)
....

Next
"""

        formatted = transform_text(source)

        self.assertIn('[source,console,role="transcript"]', formatted)
        self.assertIn(
            ".SQL\n[source,sql]\n....\nSELECT\n    id,\n    name\nFROM users;\n....",
            formatted,
        )
        self.assertIn(
            ".Output\n[source,output]\n....\n id | name\n----+------\n  1 | Ada\n(1 row)\n....",
            formatted,
        )
        self.assertEqual(formatted.count("forumdb=> SELECT id, name FROM users;"), 1)
        self.assertEqual(formatted.count(" id | name"), 2)
        self.assertEqual(transform_text(formatted), formatted)

    def test_shell_transcript_adds_command_and_output_views(self):
        source = """[source,text]
....
$ psql -d forumdb
You are now connected.
$ \\dt
 public | users | table
....
"""

        formatted = transform_text(source)

        self.assertIn('[source,console,role="transcript"]', formatted)
        self.assertIn(
            ".Command\n[source,bash]\n....\npsql -d forumdb\n\\dt\n....",
            formatted,
        )
        self.assertIn(
            ".Output\n[source,output]\n....\nYou are now connected.\n public | users | table\n....",
            formatted,
        )

    def test_mixed_shell_and_psql_transcript_gets_both_command_views(self):
        source = """[source,text]
....
$ psql -d forumdb
psql (16.0)
forumdb=> SELECT 1;
 ?column?
----------
        1
(1 row)
....
"""

        formatted = transform_text(source)

        self.assertIn(".Command\n[source,bash]\n....\npsql -d forumdb\n....", formatted)
        self.assertIn(".SQL\n[source,sql]\n....\nSELECT 1;\n....", formatted)
        self.assertIn(
            ".Output\n[source,output]\n....\npsql (16.0)\n ?column?\n----------\n        1\n(1 row)\n....",
            formatted,
        )

    def test_inline_psql_output_header_moves_to_output_view(self):
        source = """[source,text]
....
$ psql -l                                      List of databases
 Name | Owner
------+--------
 foo  | postgres
....
"""

        formatted = transform_text(source)

        self.assertIn(".Command\n[source,bash]\n....\npsql -l\n....", formatted)
        self.assertIn(
            ".Output\n[source,output]\n....\nList of databases\n Name | Owner\n------+--------\n foo  | postgres\n....",
            formatted,
        )

    def test_plain_sql_gets_sql_language_without_duplicate_blocks(self):
        source = """[source,text]
....
SELECT id, name
FROM users
WHERE active = true;
....
"""

        formatted = transform_text(source)

        self.assertIn("[source,sql]", formatted)
        self.assertNotIn(".SQL\n[source,sql]", formatted)
        self.assertIn("SELECT\n    id,\n    name\nFROM users\nWHERE active = TRUE;", formatted)

    def test_output_only_block_gets_output_language(self):
        source = """[source,text]
....
 id | name
----+------
  1 | Ada
(1 row)
....
"""

        formatted = transform_text(source)

        self.assertIn("[source,output]", formatted)
        self.assertNotIn('[source,console,role="transcript"]', formatted)
        self.assertEqual(formatted.count(" id | name"), 1)

    def test_explicit_sql_output_block_gets_output_language(self):
        source = """[source,sql]
....
QUERY PLAN
----------
Seq Scan on users
....
"""

        formatted = transform_text(source)

        self.assertIn("[source,output]", formatted)
        self.assertNotIn("[source,sql]", formatted)


if __name__ == "__main__":
    unittest.main()
