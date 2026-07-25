"""Trust classification (EXEC-008 required test category): every
source in the real, committed config/source-registry.json must
declare a value from the closed TrustLevel vocabulary - never blank,
never a typo that would silently be treated as UNKNOWN."""

import _pathsetup  # noqa: F401
import unittest
from pathlib import Path

from reality_sensor.config import load_relevance_gate, load_source_registry
from reality_sensor.models import Category, Project, TrustLevel

_PKG_ROOT = Path(__file__).resolve().parents[1]
_SOURCE_REGISTRY_PATH = _PKG_ROOT / "config" / "source-registry.json"
_RELEVANCE_GATE_PATH = _PKG_ROOT / "config" / "relevance-gate.json"


class TestSourceRegistryTrustClassification(unittest.TestCase):
    def test_every_committed_source_has_a_valid_trust_level(self):
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        self.assertGreater(len(registry.sources), 0)
        for s in registry.sources:
            self.assertIn(
                s.trust_level, TrustLevel.ALL,
                f"{s.name} declares trust_level {s.trust_level!r}, not in {TrustLevel.ALL}",
            )

    def test_every_committed_source_has_a_valid_category(self):
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        for s in registry.sources:
            self.assertIn(s.category, Category.ALL)

    def test_no_community_trust_sources_in_the_fixed_initial_list(self):
        # Not a hard rule, but worth a documented assertion: EXEC-008's
        # own named source examples (OpenAI, Anthropic, GitHub, arXiv...)
        # are all PRIMARY/OFFICIAL/RESEARCH by nature.
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        self.assertTrue(all(s.trust_level != TrustLevel.COMMUNITY for s in registry.sources))

    def test_search_budget_is_fixed_and_positive(self):
        registry = load_source_registry(_SOURCE_REGISTRY_PATH)
        self.assertGreater(registry.search_budget, 0)


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
