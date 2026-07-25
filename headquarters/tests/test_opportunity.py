import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from headquarters.collector import Collected, ObservationAgentSnapshot, RepoSnapshot
from headquarters.config import ArtifactRef, HeadquartersConfig, RepoConfig
from headquarters.models import Confidence
from headquarters.opportunity import (
    changelog_size_signal,
    registry_consolidation,
    shared_safety_pattern,
)


def _repo(name, path, changelog_lines=None) -> RepoSnapshot:
    return RepoSnapshot(name=name, path=path, state_fields={}, state_file_path=None, purpose=None, adr_files=[], changelog_lines=changelog_lines)


def _collected(repos) -> Collected:
    return Collected(repos, [], [], [], {}, ObservationAgentSnapshot(None, None, {}, [], [], []), False, [])


class TestSharedSafetyPattern(unittest.TestCase):
    def test_flags_when_both_safety_files_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "observation-agent" / "tests").mkdir(parents=True)
            (base / "headquarters" / "tests").mkdir(parents=True)
            (base / "observation-agent" / "tests" / "test_safety.py").write_text("x")
            (base / "headquarters" / "tests" / "test_safety.py").write_text("x")

            config = HeadquartersConfig(
                repos=[RepoConfig("discovery-lab", str(base), None, None, None, None)],
                project_registry=ArtifactRef("discovery-lab", "x"),
                recommendation_ledger=ArtifactRef("discovery-lab", "x"),
                observation_agent_reports_dir=ArtifactRef("discovery-lab", "x"),
                governance_doc=ArtifactRef("discovery-lab", "x"),
                proposals_dir=ArtifactRef("discovery-lab", "x"),
                decision_backlog_threshold_days=3,
                stale_adr_threshold_days=30,
            )
            findings = shared_safety_pattern(config)
            self.assertEqual(len(findings), 1)
            self.assertTrue(findings[0].is_opportunity)
            self.assertEqual(findings[0].confidence, Confidence.INSUFFICIENT_EVIDENCE)

    def test_no_finding_when_only_one_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "observation-agent" / "tests").mkdir(parents=True)
            (base / "observation-agent" / "tests" / "test_safety.py").write_text("x")
            config = HeadquartersConfig(
                repos=[RepoConfig("discovery-lab", str(base), None, None, None, None)],
                project_registry=ArtifactRef("discovery-lab", "x"),
                recommendation_ledger=ArtifactRef("discovery-lab", "x"),
                observation_agent_reports_dir=ArtifactRef("discovery-lab", "x"),
                governance_doc=ArtifactRef("discovery-lab", "x"),
                proposals_dir=ArtifactRef("discovery-lab", "x"),
                decision_backlog_threshold_days=3,
                stale_adr_threshold_days=30,
            )
            self.assertEqual(shared_safety_pattern(config), [])


class TestRegistryConsolidation(unittest.TestCase):
    def test_flags_repo_with_two_or_more_known_registries(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "Knowledge").mkdir()
            (base / "Knowledge" / "PRINCIPLE_REGISTRY.md").write_text("x")
            (base / "Knowledge" / "IDEA_REGISTRY.md").write_text("x")
            repos = {"kod": _repo("kod", str(base))}
            findings = registry_consolidation(_collected(repos))
            self.assertEqual(len(findings), 1)
            self.assertTrue(findings[0].is_opportunity)

    def test_no_finding_when_files_absent(self):
        repos = {"kod": _repo("kod", "/nonexistent")}
        self.assertEqual(registry_consolidation(_collected(repos)), [])


class TestChangelogSizeSignal(unittest.TestCase):
    def test_flags_large_changelog(self):
        repos = {"discovery-lab": _repo("discovery-lab", "/x", changelog_lines=2000)}
        findings = changelog_size_signal(_collected(repos))
        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].is_opportunity)

    def test_no_finding_under_threshold(self):
        repos = {"discovery-lab": _repo("discovery-lab", "/x", changelog_lines=50)}
        self.assertEqual(changelog_size_signal(_collected(repos)), [])


if __name__ == "__main__":
    unittest.main()
