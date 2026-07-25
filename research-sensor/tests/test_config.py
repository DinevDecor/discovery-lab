"""Source validation / trust classification against the real,
committed config/source-registry.json - every source must declare a
value from the closed SourceTrust vocabulary."""

import _pathsetup  # noqa: F401
import unittest
from pathlib import Path

from research_sensor.config import load_relevance_gate, load_source_registry
from research_sensor.models import Project, SourceTrust

_PKG_ROOT = Path(__file__).resolve().parents[1]
_SOURCE_REGISTRY_PATH = _PKG_ROOT / "config" / "source-registry.json"
_RELEVANCE_GATE_PATH = _PKG_ROOT / "config" / "relevance-gate.json"


class TestSourceRegistryTrustClassification(unittest.TestCase):
    def test_every_committed_source_has_a_valid_source_trust(self):
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        self.assertGreater(len(registry.sources), 0)
        for s in registry.sources:
            self.assertIn(s.source_trust, SourceTrust.ALL)

    def test_primary_sources_include_the_named_venues(self):
        # EXEC-010's own Priority order names arXiv, OpenReview, Nature,
        # Science, ACL, NeurIPS, ICML, ICLR as PRIMARY.
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        primary_names = {s.name for s in registry.sources if s.source_trust == SourceTrust.PRIMARY}
        for expected in ("arXiv", "OpenReview", "Nature", "Science", "ACL", "NeurIPS", "ICML", "ICLR"):
            self.assertTrue(
                any(expected in name for name in primary_names),
                f"no PRIMARY source name contains {expected!r}",
            )

    def test_community_sources_exist_and_are_marked_community(self):
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        community = [s for s in registry.sources if s.source_trust == SourceTrust.COMMUNITY]
        self.assertGreater(len(community), 0)

    def test_processing_budget_and_window_are_fixed_and_positive(self):
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        self.assertGreater(registry.processing_budget, 0)
        self.assertEqual(registry.window_days, 30)  # EXEC-010: "Last 30 days"


class TestRelevanceGateConfig(unittest.TestCase):
    def test_every_rule_names_an_allowed_project(self):
        config = load_relevance_gate(_RELEVANCE_GATE_PATH)
        self.assertGreater(len(config.rules), 0)
        for rule in config.rules:
            self.assertIn(rule.project, Project.NAMED)

    def test_every_project_has_at_least_one_rule(self):
        config = load_relevance_gate(_RELEVANCE_GATE_PATH)
        covered = {rule.project for rule in config.rules}
        self.assertEqual(covered, set(Project.NAMED))


if __name__ == "__main__":
    unittest.main()
