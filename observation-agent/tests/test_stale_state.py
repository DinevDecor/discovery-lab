import _pathsetup  # noqa: F401
import os
import tempfile
import time
import unittest
from pathlib import Path

from observation_agent.checks.stale_state import check_stale_state
from observation_agent.config import RepoConfig
from observation_agent.models import Confidence


class TestStaleState(unittest.TestCase):
    def test_flags_state_file_older_than_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "STATE.md"
            state.write_text("updated_at: 2020-01-01\n")
            other = Path(tmp) / "other.md"
            other.write_text("recent content")
            # Force other.md's mtime to be clearly newer than the declared date.
            recent = time.time()
            os.utime(other, (recent, recent))

            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=["STATE.md"])
            found = check_stale_state(repo, excluded_dirs=[".git"], threshold_days=3)
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)

    def test_no_finding_when_no_date_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "STATE.md").write_text("no date field here")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=["STATE.md"])
            found = check_stale_state(repo, excluded_dirs=[".git"], threshold_days=3)
            self.assertEqual(found, [])

    def test_no_finding_when_within_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            today = time.strftime("%Y-%m-%d")
            (Path(tmp) / "STATE.md").write_text(f"updated_at: {today}\n")
            (Path(tmp) / "other.md").write_text("content")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=["STATE.md"])
            found = check_stale_state(repo, excluded_dirs=[".git"], threshold_days=3)
            self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
