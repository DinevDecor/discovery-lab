import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from observation_agent.checks.status_history_consistency import (
    check_status_history_consistency,
)
from observation_agent.config import RepoConfig
from observation_agent.models import Confidence


class TestStatusHistoryConsistency(unittest.TestCase):
    def test_flags_mismatched_run_count(self):
        # Reproduces the exact real defect this session found and fixed
        # by hand in AG-001 (STRATEGIC-001).
        with tempfile.TemporaryDirectory() as tmp:
            role_dir = Path(tmp) / "employees" / "AG-001"
            role_dir.mkdir(parents=True)
            (role_dir / "STATUS.yaml").write_text("runs_completed: 0\nlast_run: null\n")
            (role_dir / "HISTORY.md").write_text(
                "# History\n\n## 2026-07-24 — RUN-0001\n\nFirst real run executed.\n"
            )
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_status_history_consistency(repo, excluded_dirs=[".git"])
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)
            self.assertEqual(len(found[0].evidence), 2)

    def test_no_finding_when_counts_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            role_dir = Path(tmp) / "employees" / "AG-002"
            role_dir.mkdir(parents=True)
            (role_dir / "STATUS.yaml").write_text("runs_completed: 1\n")
            (role_dir / "HISTORY.md").write_text("## 2026-07-24 — RUN-0001\n\nDone.\n")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_status_history_consistency(repo, excluded_dirs=[".git"])
            self.assertEqual(found, [])

    def test_no_finding_when_no_history_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            role_dir = Path(tmp) / "employees" / "AG-003"
            role_dir.mkdir(parents=True)
            (role_dir / "STATUS.yaml").write_text("runs_completed: 0\n")
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_status_history_consistency(repo, excluded_dirs=[".git"])
            self.assertEqual(found, [])

    def test_bugfix_entry_mentioning_run_id_in_prose_is_not_double_counted(self):
        # Real false positive found running this check against the live
        # AG-001 role: a bug-fix HISTORY.md entry whose heading mentions
        # "RUN-0001" in explanatory prose (not as the heading's primary
        # subject) must not be counted as a second run entry.
        with tempfile.TemporaryDirectory() as tmp:
            role_dir = Path(tmp) / "employees" / "AG-001"
            role_dir.mkdir(parents=True)
            (role_dir / "STATUS.yaml").write_text("runs_completed: 1\n")
            (role_dir / "HISTORY.md").write_text(
                "# History\n\n"
                "## 2026-07-24 — Role created\n\n...\n\n"
                "## 2026-07-24 — RUN-0001\n\nFirst real run executed.\n\n"
                "## 2026-07-25 — Bug fix: `STATUS.yaml` did not reflect `RUN-0001`\n\n"
                "Corrected runs_completed to 1.\n"
            )
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_status_history_consistency(repo, excluded_dirs=[".git"])
            self.assertEqual(found, [])

    def test_non_run_prefixed_and_bundled_headings_undercount_as_insufficient_evidence(self):
        # Real undercount found running this check against the live
        # AG-002 role: run identifiers that don't use a literal "RUN-N"
        # primary subject (e.g. "MIRROR-VERIFY-0001") or that bundle
        # several run IDs into one heading (e.g. "STRESS-RUN-0003,
        # -0004, -0005") are not fully counted. This is a known,
        # documented limitation, not a crash or a false MISMATCH claim
        # — it must surface as INSUFFICIENT_EVIDENCE for human review.
        with tempfile.TemporaryDirectory() as tmp:
            role_dir = Path(tmp) / "employees" / "AG-002"
            role_dir.mkdir(parents=True)
            (role_dir / "STATUS.yaml").write_text("runs_completed: 3\n")
            (role_dir / "HISTORY.md").write_text(
                "# History\n\n"
                "## 2026-07-24 — PILOT-RUN-0001\n\n...\n\n"
                "## 2026-07-24 — MIRROR-VERIFY-0001 (pipeline verification)\n\n...\n\n"
                "## 2026-07-24 — STRESS-RUN-0003, -0004, -0005\n\n...\n"
            )
            repo = RepoConfig(name="fixture", path=tmp, state_file_candidates=[])
            found = check_status_history_consistency(repo, excluded_dirs=[".git"])
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)


if __name__ == "__main__":
    unittest.main()
