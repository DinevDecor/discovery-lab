import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from observation_agent.scanner import walk_files


class TestExcludedPaths(unittest.TestCase):
    def test_excludes_the_exact_configured_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "reports").mkdir()
            (base / "reports" / "report.md").write_text("x")
            (base / "keep.md").write_text("x")
            found = walk_files(str(base), excluded_dirs=[], excluded_paths=["reports"])
            names = {p.name for p in found}
            self.assertEqual(names, {"keep.md"})

    def test_excludes_files_nested_inside_the_configured_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "observation-agent" / "reports" / "sub").mkdir(parents=True)
            (base / "observation-agent" / "reports" / "sub" / "deep.md").write_text("x")
            (base / "observation-agent" / "src.py").write_text("x")
            found = walk_files(
                str(base), excluded_dirs=[], excluded_paths=["observation-agent/reports"]
            )
            names = {str(p.relative_to(base)) for p in found}
            self.assertEqual(names, {"observation-agent/src.py"})

    def test_does_not_exclude_a_similarly_named_but_distinct_directory(self):
        # "reports" must not match "reports-extra" via naive string-prefix
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "reports").mkdir()
            (base / "reports" / "a.md").write_text("x")
            (base / "reports-extra").mkdir()
            (base / "reports-extra" / "b.md").write_text("x")
            found = walk_files(str(base), excluded_dirs=[], excluded_paths=["reports"])
            names = {p.name for p in found}
            self.assertEqual(names, {"b.md"})

    def test_no_excluded_paths_behaves_exactly_as_before(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "a.md").write_text("x")
            found_default = walk_files(str(base), excluded_dirs=[])
            found_empty = walk_files(str(base), excluded_dirs=[], excluded_paths=[])
            self.assertEqual({p.name for p in found_default}, {"a.md"})
            self.assertEqual({p.name for p in found_default}, {p.name for p in found_empty})

    def test_excluded_dirs_and_excluded_paths_combine(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / ".git").mkdir()
            (base / ".git" / "x.md").write_text("x")
            (base / "reports").mkdir()
            (base / "reports" / "y.md").write_text("x")
            (base / "z.md").write_text("x")
            found = walk_files(str(base), excluded_dirs=[".git"], excluded_paths=["reports"])
            self.assertEqual({p.name for p in found}, {"z.md"})


if __name__ == "__main__":
    unittest.main()
