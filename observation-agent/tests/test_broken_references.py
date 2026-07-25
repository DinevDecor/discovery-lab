import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from observation_agent.checks.broken_references import check_broken_references
from observation_agent.config import RepoConfig
from observation_agent.models import Confidence


class TestBrokenReferences(unittest.TestCase):
    def test_flags_broken_relative_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("See [missing](does-not-exist.md) for details.")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_broken_references(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].confidence, Confidence.MISMATCH)

    def test_does_not_flag_resolvable_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "target.md").write_text("target content")
            (Path(tmp) / "a.md").write_text("See [target](target.md) for details.")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_broken_references(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(found, [])

    def test_ignores_external_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("See [external](https://example.com/x.md).")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_broken_references(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(found, [])

    def test_resolves_subdirectory_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "sub"
            sub.mkdir()
            (sub / "b.md").write_text("b content")
            (Path(tmp) / "a.md").write_text("See [b](sub/b.md).")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_broken_references(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(found, [])

    def test_line_number_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("line one\nline two\n[missing](x.md)\n")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_broken_references(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].evidence[0].line_number, 3)


if __name__ == "__main__":
    unittest.main()
