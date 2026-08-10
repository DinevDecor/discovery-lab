import _pathsetup  # noqa: F401
import unittest

from business_candidate_analyst.config import load_rearchitecture_thresholds
from business_candidate_analyst.rearchitecture.taxonomy import (
    best_constraint_category, enabler_hits, is_ai_only, still_binding_hits, weakening_hits,
    UNCLASSIFIED_CONSTRAINT,
)


class TaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_rearchitecture_thresholds()

    def test_unclassified_when_nothing_matches(self):
        cat, legacy, reason = best_constraint_category("a giraffe crosses the savanna", self.cfg)
        self.assertEqual(cat, UNCLASSIFIED_CONSTRAINT)

    def test_buffer_inventory_pattern(self):
        cat, legacy, reason = best_constraint_category(
            "warehouse inventory kept because supplier delivery was slow and unreliable", self.cfg)
        self.assertEqual(cat, "buffer_inventory")
        self.assertIn("warehouse", legacy)

    def test_physical_presence_requires_specific_phrase_not_bare_branch(self):
        """Regression: bare 'branch' collided with git/code 'branch' language
        in the real corpus (a SAT-solver optimization post was misclassified
        physical_presence via 'branch and bound'). The taxonomy now requires
        'branch network'/'branch office'/'bank branch'."""
        cat, _, _ = best_constraint_category("we optimized the branch and bound search", self.cfg)
        self.assertNotEqual(cat, "physical_presence")
        cat2, legacy2, _ = best_constraint_category(
            "customers had to visit a branch office to open an account", self.cfg)
        self.assertEqual(cat2, "physical_presence")

    def test_intermediation_trust_does_not_fire_on_bare_agent(self):
        """Regression: bare 'agent' collided with 'AI agent' everywhere in
        the real corpus, false-positiving dozens of unrelated dev-tool
        observations into intermediation_trust."""
        cat, _, _ = best_constraint_category(
            "managing multiple AI coding agents simultaneously in a terminal", self.cfg)
        self.assertNotEqual(cat, "intermediation_trust")

    def test_enabler_ai_is_one_bucket_among_many(self):
        hits = enabler_hits("this could now be done with AI instead of manual review", self.cfg)
        self.assertIn("ai", hits)
        self.assertGreaterEqual(len(self.cfg["enabler_taxonomy"]), 10, "AI must be one of many enabler buckets")

    def test_is_ai_only(self):
        self.assertTrue(is_ai_only({"ai": {"ai"}}))
        self.assertFalse(is_ai_only({"ai": {"ai"}, "gps_location": {"gps"}}))
        self.assertFalse(is_ai_only({}))

    def test_still_binding_language_detected_separately_from_weakening(self):
        text = "the batteries everyone suggests aren't free"
        self.assertTrue(still_binding_hits(text, self.cfg))
        self.assertFalse(weakening_hits(text, self.cfg))

    def test_weakening_language_requires_explicit_change_words(self):
        text = "prices have fallen and adoption is now possible"
        self.assertTrue(weakening_hits(text, self.cfg))


if __name__ == "__main__":
    unittest.main()
