import _pathsetup  # noqa: F401
import unittest

from x_signal_probe.audit_models import (
    RUBRIC_ABCD_VALUES,
    RUBRIC_E_VALUES,
    AuditSampleEntry,
    unavailable_verdict,
)


def _sample_entry():
    return AuditSampleEntry(
        post_id="123",
        query_family="unexpected_cost_bill",
        query_id="q01",
        canonical_url="https://x.com/i/status/123",
        created_at="2026-08-18T00:00:00Z",
        retrieved_at="2026-08-18T01:00:00Z",
    )


class RubricValueTests(unittest.TestCase):
    def test_abcd_allows_unclear(self):
        self.assertIn("UNCLEAR", RUBRIC_ABCD_VALUES)

    def test_e_does_not_allow_unclear(self):
        self.assertNotIn("UNCLEAR", RUBRIC_E_VALUES)

    def test_both_allow_unavailable(self):
        self.assertIn("UNAVAILABLE", RUBRIC_ABCD_VALUES)
        self.assertIn("UNAVAILABLE", RUBRIC_E_VALUES)


class UnavailableVerdictTests(unittest.TestCase):
    def test_every_rubric_field_set_to_unavailable(self):
        v = unavailable_verdict(_sample_entry(), "AUDIT-1", "run-1", "0.1", "2026-08-18T02:00:00Z")
        self.assertEqual(v.availability, "UNAVAILABLE")
        self.assertEqual(v.a_genuine_problem_report, "UNAVAILABLE")
        self.assertEqual(v.b_operational_economic_consequence, "UNAVAILABLE")
        self.assertEqual(v.c_noise, "UNAVAILABLE")
        self.assertEqual(v.d_incremental_vs_discovery_lab, "UNAVAILABLE")
        self.assertEqual(v.e_corroboration_worthy, "UNAVAILABLE")

    def test_preserves_post_identity_fields(self):
        entry = _sample_entry()
        v = unavailable_verdict(entry, "AUDIT-1", "run-1", "0.1", "2026-08-18T02:00:00Z")
        self.assertEqual(v.post_id, entry.post_id)
        self.assertEqual(v.query_family, entry.query_family)
        self.assertEqual(v.canonical_url, entry.canonical_url)

    def test_notes_explains_no_replacement_rule(self):
        v = unavailable_verdict(_sample_entry(), "AUDIT-1", "run-1", "0.1", "2026-08-18T02:00:00Z")
        self.assertIn("not replaced", v.notes)


if __name__ == "__main__":
    unittest.main()
