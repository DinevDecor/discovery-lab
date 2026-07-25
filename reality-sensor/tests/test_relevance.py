import _pathsetup  # noqa: F401
import unittest

from reality_sensor.config import RelevanceGateConfig, RelevanceRule
from reality_sensor.models import Project
from reality_sensor.relevance import gate

_CONFIG = RelevanceGateConfig(
    rules=[
        RelevanceRule(project=Project.DISCOVERY_LAB, keywords=["mcp", "agent sdk"]),
        RelevanceRule(project=Project.TRUST_ENGINE, keywords=["calibration", "audit"]),
    ]
)


class TestRelevanceGate(unittest.TestCase):
    def test_matches_a_single_project(self):
        self.assertEqual(
            gate("New Agent SDK release with better tool use", _CONFIG),
            [Project.DISCOVERY_LAB],
        )

    def test_matches_multiple_projects(self):
        result = gate("A calibration and MCP update", _CONFIG)
        self.assertEqual(set(result), {Project.TRUST_ENGINE, Project.DISCOVERY_LAB})

    def test_no_match_falls_back_to_watch_not_forced_relevance(self):
        self.assertEqual(gate("A new font rendering library", _CONFIG), [Project.WATCH])

    def test_case_insensitive(self):
        self.assertEqual(gate("MCP SPEC UPDATED", _CONFIG), [Project.DISCOVERY_LAB])


if __name__ == "__main__":
    unittest.main()
