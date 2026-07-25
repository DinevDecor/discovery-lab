import _pathsetup  # noqa: F401
import tempfile
import unittest
from pathlib import Path

from headquarters.collector import Collected, ObservationAgentSnapshot, RepoSnapshot
from headquarters.config import ArtifactRef, HeadquartersConfig, RepoConfig
from headquarters.models import Confidence
from headquarters.opportunity import (
    changelog_size_signal,
    discover_registry_files,
    discover_safety_scanners,
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


class TestGenericDiscoveryExtensibility(unittest.TestCase):
    """Robustness Requirement: a brand-new repository with its own,
    previously-unseen registry naming convention or tool layout must
    be picked up with zero code changes — only a config.json entry.
    These tests use a repo/file-naming scheme that appears nowhere in
    this module's source, to prove the discovery is genuinely generic
    rather than re-matching a hard-coded list under a different name."""

    def test_discovers_a_never_before_seen_registry_naming_scheme(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "config" / "catalog").mkdir(parents=True)
            (base / "config" / "catalog" / "WIDGET_REGISTRY.md").write_text("x")
            (base / "config" / "catalog" / "GADGET_registry.md").write_text("x")
            found = discover_registry_files(base)
            self.assertEqual(len(found), 2)

    def test_ignores_excluded_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "node_modules").mkdir()
            (base / "node_modules" / "vendor_registry.md").write_text("x")
            found = discover_registry_files(base)
            self.assertEqual(found, [])

    def test_respects_the_depth_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            deep = base / "a" / "b" / "c" / "d" / "e" / "f"
            deep.mkdir(parents=True)
            (deep / "TOO_DEEP_REGISTRY.md").write_text("x")
            found = discover_registry_files(base)
            self.assertEqual(found, [])

    def test_registry_consolidation_works_for_a_repo_never_named_in_this_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "docs").mkdir()
            (base / "docs" / "SPROCKET_REGISTRY.md").write_text("x")
            (base / "docs" / "COG_REGISTRY.md").write_text("x")
            repos = {"a-brand-new-repo-name": _repo("a-brand-new-repo-name", str(base))}
            findings = registry_consolidation(_collected(repos))
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].affected, ["a-brand-new-repo-name"])

    def test_discovers_safety_scanner_under_a_tool_name_never_seen_before(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "brand-new-tool-a" / "tests").mkdir(parents=True)
            (base / "brand-new-tool-a" / "tests" / "test_safety.py").write_text("x")
            (base / "brand-new-tool-b" / "tests").mkdir(parents=True)
            (base / "brand-new-tool-b" / "tests" / "test_safety.py").write_text("x")
            config = HeadquartersConfig(
                repos=[RepoConfig("r", str(base), None, None, None, None)],
                project_registry=ArtifactRef("r", "x"),
                recommendation_ledger=ArtifactRef("r", "x"),
                observation_agent_reports_dir=ArtifactRef("r", "x"),
                governance_doc=ArtifactRef("r", "x"),
                proposals_dir=ArtifactRef("r", "x"),
                decision_backlog_threshold_days=3,
                stale_adr_threshold_days=30,
            )
            self.assertEqual(len(discover_safety_scanners(config)), 2)
            findings = shared_safety_pattern(config)
            self.assertEqual(len(findings), 1)


if __name__ == "__main__":
    unittest.main()
