import _pathsetup  # noqa: F401
import unittest

from headquarters.parsing import (
    extract_fenced_blocks,
    first_paragraph_after_title,
    parse_fenced_key_values,
    parse_loose_key_values,
    parse_markdown_table,
    parse_state_fields,
)


class TestFencedBlocks(unittest.TestCase):
    def test_extracts_multiple_blocks_in_order(self):
        text = "before\n```\nA\n```\nmiddle\n```yaml\nB\n```\nafter"
        blocks = extract_fenced_blocks(text)
        self.assertEqual(len(blocks), 2)
        self.assertIn("A", blocks[0])
        self.assertIn("B", blocks[1])

    def test_no_fence_returns_empty(self):
        self.assertEqual(extract_fenced_blocks("just prose, no fence"), [])


class TestFencedKeyValues(unittest.TestCase):
    def test_single_line_fields(self):
        fields = parse_fenced_key_values("project: discovery-lab\nstatus: ACTIVE\n")
        self.assertEqual(fields["project"], "discovery-lab")
        self.assertEqual(fields["status"], "ACTIVE")

    def test_wrapped_continuation_line_is_appended(self):
        block = "recommendation_id: REC-0001\nsummary: first line\n  second line\n  third line\n"
        fields = parse_fenced_key_values(block)
        self.assertEqual(fields["summary"], "first line second line third line")
        self.assertEqual(fields["recommendation_id"], "REC-0001")

    def test_a_colon_inside_a_continuation_line_does_not_start_a_new_field(self):
        block = "summary: Bug fix: STATUS.yaml did not reflect RUN-0001\n  Suggested action: update the field.\n"
        fields = parse_fenced_key_values(block)
        self.assertEqual(len(fields), 1)
        self.assertIn("Suggested action", fields["summary"])


class TestLooseKeyValues(unittest.TestCase):
    def test_kod_style_padded_colon(self):
        text = "## Runtime\n\nProject Status       : ACTIVE\nArchitecture Status  : FROZEN\n"
        fields = parse_loose_key_values(text)
        self.assertEqual(fields["Project Status"], "ACTIVE")
        self.assertEqual(fields["Architecture Status"], "FROZEN")

    def test_ignores_markdown_links_and_headings(self):
        text = "# Title\n\nSee [here](path.md) for details.\n"
        fields = parse_loose_key_values(text)
        self.assertNotIn("Title", fields)


class TestParseStateFields(unittest.TestCase):
    def test_prefers_fenced_block_when_present(self):
        text = "# State\n\n```yaml\nproject: X\nstatus: ACTIVE\n```\n"
        fields = parse_state_fields(text)
        self.assertEqual(fields["status"], "ACTIVE")

    def test_falls_back_to_loose_parsing_when_no_fence(self):
        text = "# PROJECT STATE\n\n## Runtime\n\nProject Status       : ACTIVE\nKernel Status        : DESIGN\n"
        fields = parse_state_fields(text)
        self.assertEqual(fields["Project Status"], "ACTIVE")

    def test_empty_document_yields_empty_dict(self):
        self.assertEqual(parse_state_fields(""), {})


class TestMarkdownTable(unittest.TestCase):
    def test_parses_headers_and_rows(self):
        text = (
            "| Project | Status |\n"
            "|---|---|\n"
            "| A | ACTIVE |\n"
            "| B | FROZEN |\n"
        )
        headers, rows = parse_markdown_table(text)
        self.assertEqual(headers, ["Project", "Status"])
        self.assertEqual(rows, [["A", "ACTIVE"], ["B", "FROZEN"]])

    def test_no_table_returns_empty(self):
        self.assertEqual(parse_markdown_table("just prose"), ([], []))


class TestFirstParagraph(unittest.TestCase):
    def test_skips_title_and_status_line(self):
        text = "# discovery-lab\n\nStatus: bootstrap\n\nThis repository does X.\n"
        self.assertEqual(first_paragraph_after_title(text), "This repository does X.")

    def test_no_title_returns_none(self):
        self.assertIsNone(first_paragraph_after_title("just prose, no heading"))


if __name__ == "__main__":
    unittest.main()
