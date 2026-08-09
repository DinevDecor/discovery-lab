import os, sys, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,"src"))
from ca_agents.sensor import cap_confidence_for_source, _SOLUTION_SIGNAL_CONFIDENCE_CAP


class TestConfidenceCap(unittest.TestCase):
    def test_product_hunt_high_confidence_is_capped(self):
        self.assertEqual(cap_confidence_for_source("product_hunt", 0.95), _SOLUTION_SIGNAL_CONFIDENCE_CAP)

    def test_product_hunt_low_confidence_not_raised(self):
        self.assertEqual(cap_confidence_for_source("product_hunt", 0.2), 0.2)

    def test_other_sources_unaffected(self):
        self.assertEqual(cap_confidence_for_source("hacker_news", 0.95), 0.95)
        self.assertEqual(cap_confidence_for_source("discourse:python", 0.95), 0.95)


if __name__ == "__main__":
    unittest.main()
