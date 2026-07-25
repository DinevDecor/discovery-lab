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


class TestSelfReferentialFeedbackLoop(unittest.TestCase):
    """Regression test for the real defect found in EXEC-005's
    Operational Validation (INV-0004): a prior run's own report,
    written into the tool's own reports/ directory inside the
    observed repo, quotes a flagged citation verbatim — which the
    *next* run then rediscovers as new repository content, compounding
    across repeated local runs. Reproduced here with the exact shape
    (a report file quoting a `[text](path)`-style citation), proving
    both that the bug is real without the fix, and that
    `excluded_paths` resolves it."""

    def _fixture_with_self_quoting_report(self, tmp: str) -> None:
        reports_dir = Path(tmp) / "observation-agent" / "reports"
        reports_dir.mkdir(parents=True)
        (reports_dir / "observation-report-prior.md").write_text(
            "## New Observations\n\n"
            "### Broken reference in some/file.md: [text](path)\n\n"
            "- Evidence: some/file.md:14 — \"Markdown [text](path) links\"\n"
        )

    def test_without_exclusion_the_own_report_is_rediscovered_as_new_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._fixture_with_self_quoting_report(tmp)
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_broken_references(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertGreater(len(found), 0, "expected the bug to reproduce without excluded_paths")

    def test_with_exclusion_the_own_reports_directory_is_never_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._fixture_with_self_quoting_report(tmp)
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_broken_references(
                repo,
                excluded_dirs=[".git"],
                markdown_extensions=[".md"],
                excluded_paths=["observation-agent/reports"],
            )
            self.assertEqual(found, [])

    def test_repeated_runs_over_the_same_growing_reports_directory_stay_stable(self):
        """Simulates two consecutive local runs: the second run's
        reports/ directory contains the first run's own output.
        With excluded_paths configured, the second run must not find
        anything new attributable to the first run's report."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            reports_dir = Path(tmp) / "observation-agent" / "reports"
            reports_dir.mkdir(parents=True)

            run1 = check_broken_references(
                repo, excluded_dirs=[".git"], markdown_extensions=[".md"],
                excluded_paths=["observation-agent/reports"],
            )
            (reports_dir / "observation-report-run1.md").write_text(
                "### Broken reference: [text](path)\n"
            )

            run2 = check_broken_references(
                repo, excluded_dirs=[".git"], markdown_extensions=[".md"],
                excluded_paths=["observation-agent/reports"],
            )
            self.assertEqual(run1, [])
            self.assertEqual(run2, [])


if __name__ == "__main__":
    unittest.main()
