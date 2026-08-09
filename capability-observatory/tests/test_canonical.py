import _pathsetup  # noqa: F401
import unittest

from capability_observatory.canonical import (
    canonical_json,
    canonicalize_identity_value,
    sha256_hex,
    utc_now_iso,
)


class CanonicalTests(unittest.TestCase):
    def test_canonical_json_is_deterministic_regardless_of_key_order(self):
        a = canonical_json({"b": 1, "a": 2})
        b = canonical_json({"a": 2, "b": 1})
        self.assertEqual(a, b)

    def test_canonical_json_is_stable_across_repeated_calls(self):
        obj = {"x": [3, 1, 2], "y": "value"}
        self.assertEqual(canonical_json(obj), canonical_json(obj))

    def test_sha256_hex_is_deterministic(self):
        self.assertEqual(sha256_hex("same input"), sha256_hex("same input"))

    def test_sha256_hex_differs_for_different_input(self):
        self.assertNotEqual(sha256_hex("input a"), sha256_hex("input b"))

    def test_canonicalize_identity_value_collapses_whitespace_and_uppercases(self):
        self.assertEqual(canonicalize_identity_value("  Acme   Corp  "), "ACME CORP")

    def test_canonicalize_identity_value_leaves_numbers_untouched(self):
        self.assertEqual(canonicalize_identity_value(42), 42)
        self.assertEqual(canonicalize_identity_value(3.5), 3.5)

    def test_utc_now_iso_ends_with_z(self):
        self.assertTrue(utc_now_iso().endswith("Z"))


if __name__ == "__main__":
    unittest.main()
