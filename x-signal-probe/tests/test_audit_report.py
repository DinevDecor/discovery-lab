import _pathsetup  # noqa: F401
import unittest

from x_signal_probe.audit_report import DENOMINATOR, compute_report, render_markdown


def _verdict(e="NO", availability="AVAILABLE", **overrides):
    base = {
        "availability": availability,
        "a_genuine_problem_report": "NO",
        "b_operational_economic_consequence": "NO",
        "c_noise": "NO",
        "d_incremental_vs_discovery_lab": "NO",
        "e_corroboration_worthy": e,
    }
    base.update(overrides)
    return base


class ThresholdTests(unittest.TestCase):
    def test_four_yes_is_fail(self):
        verdicts = [_verdict("YES") for _ in range(4)] + [_verdict("NO") for _ in range(16)]
        m = compute_report(verdicts)
        self.assertEqual(m.decision, "FAIL")

    def test_five_yes_is_iterate(self):
        verdicts = [_verdict("YES") for _ in range(5)] + [_verdict("NO") for _ in range(15)]
        m = compute_report(verdicts)
        self.assertEqual(m.decision, "INSUFFICIENT_DATA_ITERATE")

    def test_nine_yes_is_iterate(self):
        verdicts = [_verdict("YES") for _ in range(9)] + [_verdict("NO") for _ in range(11)]
        m = compute_report(verdicts)
        self.assertEqual(m.decision, "INSUFFICIENT_DATA_ITERATE")

    def test_ten_yes_is_pass_candidate(self):
        verdicts = [_verdict("YES") for _ in range(10)] + [_verdict("NO") for _ in range(10)]
        m = compute_report(verdicts)
        self.assertEqual(m.decision, "PASS_CANDIDATE")

    def test_zero_yes_is_fail(self):
        verdicts = [_verdict("NO") for _ in range(20)]
        m = compute_report(verdicts)
        self.assertEqual(m.decision, "FAIL")


class RateTests(unittest.TestCase):
    def test_denominator_fixed_at_20_even_with_unavailable(self):
        verdicts = (
            [_verdict("YES") for _ in range(10)]
            + [_verdict("UNAVAILABLE", availability="UNAVAILABLE") for _ in range(5)]
            + [_verdict("NO") for _ in range(5)]
        )
        m = compute_report(verdicts)
        self.assertEqual(m.total_selected, 20)
        self.assertEqual(m.unavailable, 5)
        self.assertEqual(m.e_yes, 10)
        self.assertEqual(m.corroboration_worthy_rate, 10 / DENOMINATOR)

    def test_unavailable_never_counted_as_yes(self):
        verdicts = [
            _verdict(
                "UNAVAILABLE",
                availability="UNAVAILABLE",
                a_genuine_problem_report="UNAVAILABLE",
                b_operational_economic_consequence="UNAVAILABLE",
                c_noise="UNAVAILABLE",
                d_incremental_vs_discovery_lab="UNAVAILABLE",
            )
            for _ in range(20)
        ]
        m = compute_report(verdicts)
        self.assertEqual(m.a_yes, 0)
        self.assertEqual(m.e_yes, 0)
        self.assertEqual(m.decision, "FAIL")

    def test_counts_and_rates_consistent(self):
        verdicts = [_verdict("YES") for _ in range(12)] + [_verdict("NO") for _ in range(8)]
        m = compute_report(verdicts)
        self.assertEqual(m.e_yes, 12)
        self.assertAlmostEqual(m.corroboration_worthy_rate, 0.6)


class RenderTests(unittest.TestCase):
    def test_render_contains_decision_and_no_text_placeholder(self):
        verdicts = [_verdict("YES") for _ in range(10)] + [_verdict("NO") for _ in range(10)]
        m = compute_report(verdicts)
        md = render_markdown(m, "32120712833")
        self.assertIn("PASS_CANDIDATE", md)
        self.assertIn("does not authorize", md)
        self.assertNotIn("canonical_url", md)  # aggregate report never lists individual posts


if __name__ == "__main__":
    unittest.main()
