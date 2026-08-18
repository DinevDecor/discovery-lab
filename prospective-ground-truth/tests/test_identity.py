import _pathsetup  # noqa: F401
import unittest

from prospective_ground_truth.identity import make_prospective_case_id, make_resolution_id


class ProspectiveCaseIdTests(unittest.TestCase):
    def test_same_inputs_produce_same_id(self):
        a = make_prospective_case_id("permits", "Will X be approved?", "2026-08-01")
        b = make_prospective_case_id("permits", "Will X be approved?", "2026-08-01")
        self.assertEqual(a, b)

    def test_different_proposition_produces_different_id(self):
        a = make_prospective_case_id("permits", "Will X be approved?", "2026-08-01")
        b = make_prospective_case_id("permits", "Will Y be approved?", "2026-08-01")
        self.assertNotEqual(a, b)

    def test_different_t0_cutoff_produces_different_id(self):
        a = make_prospective_case_id("permits", "Will X be approved?", "2026-08-01")
        b = make_prospective_case_id("permits", "Will X be approved?", "2026-08-02")
        self.assertNotEqual(a, b)

    def test_id_has_stable_prefix(self):
        self.assertTrue(make_prospective_case_id("d", "p", "2026-08-01").startswith("pgt-case:"))


class ResolutionIdTests(unittest.TestCase):
    def test_same_inputs_produce_same_id(self):
        a = make_resolution_id("pgt-case:abc", "POSITIVE", "2026-09-01")
        b = make_resolution_id("pgt-case:abc", "POSITIVE", "2026-09-01")
        self.assertEqual(a, b)

    def test_different_outcome_produces_different_id(self):
        a = make_resolution_id("pgt-case:abc", "POSITIVE", "2026-09-01")
        b = make_resolution_id("pgt-case:abc", "NEGATIVE", "2026-09-01")
        self.assertNotEqual(a, b)

    def test_id_has_stable_prefix(self):
        self.assertTrue(make_resolution_id("pgt-case:abc", "POSITIVE", "2026-09-01").startswith("pgt-resolution:"))


if __name__ == "__main__":
    unittest.main()
