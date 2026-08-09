import _pathsetup  # noqa: F401
import unittest

from capability_observatory.fingerprint import compute_spec_fingerprint

IDENTITY_FIELDS = ["manufacturer", "mpn", "io_count"]


class FingerprintTests(unittest.TestCase):
    def test_deterministic_for_identical_input(self):
        values = {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16}
        fp1, incomplete1 = compute_spec_fingerprint(IDENTITY_FIELDS, values)
        fp2, incomplete2 = compute_spec_fingerprint(IDENTITY_FIELDS, dict(values))
        self.assertEqual(fp1, fp2)
        self.assertFalse(incomplete1)
        self.assertFalse(incomplete2)

    def test_cosmetic_whitespace_and_case_do_not_change_fingerprint(self):
        values_a = {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16}
        values_b = {"manufacturer": "  acme  ", "mpn": "abc-123", "io_count": 16}
        fp_a, _ = compute_spec_fingerprint(IDENTITY_FIELDS, values_a)
        fp_b, _ = compute_spec_fingerprint(IDENTITY_FIELDS, values_b)
        self.assertEqual(fp_a, fp_b)

    def test_different_mpn_changes_fingerprint(self):
        base = {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16}
        changed = {"manufacturer": "Acme", "mpn": "ABC-124", "io_count": 16}
        fp_base, _ = compute_spec_fingerprint(IDENTITY_FIELDS, base)
        fp_changed, _ = compute_spec_fingerprint(IDENTITY_FIELDS, changed)
        self.assertNotEqual(fp_base, fp_changed)

    def test_different_hard_spec_changes_fingerprint(self):
        base = {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16}
        changed = {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 32}
        fp_base, _ = compute_spec_fingerprint(IDENTITY_FIELDS, base)
        fp_changed, _ = compute_spec_fingerprint(IDENTITY_FIELDS, changed)
        self.assertNotEqual(fp_base, fp_changed)

    def test_missing_identity_field_yields_no_fingerprint_and_incomplete_flag(self):
        values = {"manufacturer": "Acme", "mpn": "ABC-123"}  # io_count missing
        fp, incomplete = compute_spec_fingerprint(IDENTITY_FIELDS, values)
        self.assertIsNone(fp)
        self.assertTrue(incomplete)

    def test_blank_string_identity_field_counts_as_missing(self):
        values = {"manufacturer": "Acme", "mpn": "   ", "io_count": 16}
        fp, incomplete = compute_spec_fingerprint(IDENTITY_FIELDS, values)
        self.assertIsNone(fp)
        self.assertTrue(incomplete)

    def test_no_declared_identity_fields_is_always_incomplete(self):
        fp, incomplete = compute_spec_fingerprint([], {"manufacturer": "Acme"})
        self.assertIsNone(fp)
        self.assertTrue(incomplete)

    def test_extra_undeclared_fields_in_identity_values_do_not_affect_fingerprint(self):
        base = {"manufacturer": "Acme", "mpn": "ABC-123", "io_count": 16}
        with_extra = dict(base, distributor_sku="XYZ-999-ND")
        fp_base, _ = compute_spec_fingerprint(IDENTITY_FIELDS, base)
        fp_extra, _ = compute_spec_fingerprint(IDENTITY_FIELDS, with_extra)
        self.assertEqual(fp_base, fp_extra)


if __name__ == "__main__":
    unittest.main()
