import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from observation_agent.checks.orphan_files import check_orphan_files
from observation_agent.config import RepoConfig
from observation_agent.models import Confidence


class TestOrphanFiles(unittest.TestCase):
    def test_flags_zero_byte_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "empty.md").write_text("")
            (Path(tmp) / "real.md").write_text("content")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_orphan_files(repo, excluded_dirs=[".git"])
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].confidence, Confidence.MISMATCH)
            self.assertIn("empty.md", found[0].event)

    def test_no_finding_when_no_empty_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "real.md").write_text("content")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_orphan_files(repo, excluded_dirs=[".git"])
            self.assertEqual(found, [])

    def test_every_observation_carries_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "empty.md").write_text("")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_orphan_files(repo, excluded_dirs=[".git"])
            for obs in found:
                self.assertTrue(obs.evidence, "every Observation must carry Evidence")


if __name__ == "__main__":
    unittest.main()
