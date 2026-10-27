"""README.md and README.ko.md must say the same thing.

The Korean README is a full translation, not a summary. Translation cannot be checked
mechanically, but drift can: the two files must have the same section structure, the same
tables with the same number of rows, and byte-identical code blocks (commands, transcripts
and file trees are not translated). A section added to one and not the other fails here.

    python3 -m unittest tests.test_readme -v
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EN = REPO / "README.md"
KO = REPO / "README.ko.md"


def code_blocks(text):
    return re.findall(r"^```[^\n]*\n(.*?)^```", text, re.S | re.M)


def prose(text):
    return re.sub(r"^```[^\n]*\n.*?^```", "", text, flags=re.S | re.M)


def heading_levels(text):
    return [len(m.group(1)) for m in re.finditer(r"^(#{1,6}) ", prose(text), re.M)]


def table_shapes(text):
    shapes, rows = [], 0
    for line in prose(text).splitlines():
        if line.startswith("|"):
            rows += 1
        elif rows:
            shapes.append(rows)
            rows = 0
    if rows:
        shapes.append(rows)
    return shapes


def list_items(text):
    return len(re.findall(r"^\s*(?:[-*]|\d+\.) ", prose(text), re.M))


def anchors(text):
    return re.findall(r"\]\(#([^)]+)\)", text)


def slug(heading):
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


class TestReadmeParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.en = EN.read_text()
        cls.ko = KO.read_text()

    def test_same_section_structure(self):
        self.assertEqual(heading_levels(self.en), heading_levels(self.ko))

    def test_same_tables(self):
        self.assertEqual(table_shapes(self.en), table_shapes(self.ko))

    def test_same_list_items(self):
        self.assertEqual(list_items(self.en), list_items(self.ko))

    def test_identical_code_blocks(self):
        self.assertEqual(code_blocks(self.en), code_blocks(self.ko))

    def test_cross_links(self):
        self.assertIn("(README.ko.md)", self.en)
        self.assertIn("(README.md)", self.ko)

    def test_table_of_contents_anchors_resolve(self):
        for name, text in (("README.md", self.en), ("README.ko.md", self.ko)):
            slugs = {slug(m.group(1)) for m in re.finditer(r"^#{1,6} (.+)$", prose(text), re.M)}
            for a in anchors(text):
                self.assertIn(a, slugs, f"{name}: link #{a} matches no heading")


if __name__ == "__main__":
    unittest.main()
