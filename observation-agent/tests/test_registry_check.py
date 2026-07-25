import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from observation_agent.checks.registry_check import check_registry_entries
from observation_agent.config import RepoConfig
from observation_agent.models import Confidence


class TestRegistryCheck(unittest.TestCase):
    def test_flags_uncited_active_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "REGISTRY.md").write_text(
                "| Project | Status |\n"
                "|---|---|\n"
                "| Widget System | ACTIVE / DISCOVERY |\n"
            )
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_registry_entries(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)

    def test_does_not_flag_cited_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "note.md").write_text("evidence")
            (Path(tmp) / "REGISTRY.md").write_text(
                "| Project | Status |\n"
                "|---|---|\n"
                "| Widget System | [ACTIVE](note.md) |\n"
            )
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_registry_entries(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(found, [])

    def test_no_finding_without_status_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "notes.md").write_text("Just prose, ACTIVE mentioned in passing.")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_registry_entries(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            self.assertEqual(found, [])

    def test_never_returns_mismatch_confidence(self):
        # Structural policy: this check can never claim a confirmed
        # contradiction, only surface a candidate for review.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "REGISTRY.md").write_text(
                "| Project | Status |\n|---|---|\n| X | ACTIVE |\n"
            )
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_registry_entries(repo, excluded_dirs=[".git"], markdown_extensions=[".md"])
            for obs in found:
                self.assertNotEqual(obs.confidence, Confidence.MISMATCH)


if __name__ == "__main__":
    unittest.main()
