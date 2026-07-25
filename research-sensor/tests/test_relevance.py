import _pathsetup  # noqa: F401
import unittest

from research_sensor.config import RelevanceGateConfig, RelevanceRule
from research_sensor.models import Project
from research_sensor.relevance import gate

_CONFIG = RelevanceGateConfig(
    rules=[
        RelevanceRule(project=Project.GENERATIVE_DISCOVERY_ENGINE, keywords=["hypothesis generation"]),
        RelevanceRule(project=Project.TRUST_ENGINE, keywords=["reproducibility", "falsification"]),
    ]
)


class TestRelevanceGate(unittest.TestCase):
    def test_matches_a_single_project(self):
        self.assertEqual(
            gate("A new automated hypothesis generation method", _CONFIG),
            [Project.GENERATIVE_DISCOVERY_ENGINE],
        )

    def test_matches_multiple_projects(self):
        result = gate("Reproducibility and falsification in hypothesis generation pipelines", _CONFIG)
        self.assertEqual(set(result), {Project.TRUST_ENGINE, Project.GENERATIVE_DISCOVERY_ENGINE})

    def test_no_match_falls_back_to_watch_class(self):
        # "WATCH classification" required test category
        self.assertEqual(gate("A new dataset of cat photos", _CONFIG), [Project.WATCH])

    def test_case_insensitive(self):
        self.assertEqual(
            gate("HYPOTHESIS GENERATION at scale", _CONFIG), [Project.GENERATIVE_DISCOVERY_ENGINE]
        )


if __name__ == "__main__":
    unittest.main()
