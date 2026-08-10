import _pathsetup  # noqa: F401
import unittest

from business_candidate_analyst.config import load_thresholds
from business_candidate_analyst.lifecycle import decide_state, meets_watch_bar
from business_candidate_analyst.models import DimensionResult, EVIDENCED, INSUFFICIENT_DATA


def dims(**overrides):
    base = {
        "identifiable_buyer": DimensionResult("identifiable_buyer", EVIDENCED, "api_consumer", ["o1"]),
        "current_workaround": DimensionResult("current_workaround", EVIDENCED, ["x"], ["o1"]),
        "why_solutions_fail": DimensionResult("why_solutions_fail", EVIDENCED, ["x"], ["o1"]),
        "economic_consequence": DimensionResult("economic_consequence", INSUFFICIENT_DATA, None, []),
        "willingness_to_pay": DimensionResult("willingness_to_pay", INSUFFICIENT_DATA, None, []),
        "contradictory_evidence": DimensionResult("contradictory_evidence", EVIDENCED, "none_observed", []),
        "scalability": DimensionResult("scalability", INSUFFICIENT_DATA, None, []),
        "pain_severity": DimensionResult("pain_severity", EVIDENCED, "LOW", ["o1"]),
    }
    base.update(overrides)
    return base


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.th = load_thresholds()

    def test_meets_watch_bar_true(self):
        ok, missing = meets_watch_bar(dims())
        self.assertTrue(ok)
        self.assertEqual(missing, [])

    def test_meets_watch_bar_false_when_buyer_missing(self):
        ok, missing = meets_watch_bar(dims(identifiable_buyer=DimensionResult(
            "identifiable_buyer", INSUFFICIENT_DATA, None, [])))
        self.assertFalse(ok)
        self.assertIn("identifiable_buyer", missing)

    def test_watch_only_when_bar_barely_met(self):
        d = decide_state(dims(), distinct_sources=1, ca_evaluations_for_group=[], thresholds=self.th)
        self.assertEqual(d["state"], "WATCH")

    def test_validating_requires_two_sources_and_economics(self):
        d = decide_state(dims(economic_consequence=DimensionResult(
            "economic_consequence", EVIDENCED, ["cost"], ["o1"])), distinct_sources=2,
            ca_evaluations_for_group=[], thresholds=self.th)
        self.assertEqual(d["state"], "VALIDATING")

    def test_stays_watch_if_only_sources_met_but_not_economics(self):
        d = decide_state(dims(), distinct_sources=2, ca_evaluations_for_group=[], thresholds=self.th)
        self.assertEqual(d["state"], "WATCH")
        self.assertIn("economic_consequence EVIDENCED", d["audit"]["VALIDATING"]["missing"])

    def test_investigate_requires_three_sources_willingness_and_no_contradiction(self):
        d = decide_state(dims(
            economic_consequence=DimensionResult("economic_consequence", EVIDENCED, ["cost"], ["o1"]),
            willingness_to_pay=DimensionResult("willingness_to_pay", EVIDENCED, ["purchased"], ["o1"]),
        ), distinct_sources=3, ca_evaluations_for_group=[], thresholds=self.th)
        self.assertEqual(d["state"], "INVESTIGATE")

    def test_investigate_blocked_by_contradiction(self):
        d = decide_state(dims(
            economic_consequence=DimensionResult("economic_consequence", EVIDENCED, ["cost"], ["o1"]),
            willingness_to_pay=DimensionResult("willingness_to_pay", EVIDENCED, ["purchased"], ["o1"]),
            contradictory_evidence=DimensionResult("contradictory_evidence", EVIDENCED, "contradiction_present", ["o1"]),
        ), distinct_sources=3, ca_evaluations_for_group=[], thresholds=self.th)
        self.assertEqual(d["state"], "VALIDATING")

    def test_promising_requires_all_four(self):
        d = decide_state(dims(
            economic_consequence=DimensionResult("economic_consequence", EVIDENCED, ["cost"], ["o1"]),
            willingness_to_pay=DimensionResult("willingness_to_pay", EVIDENCED, ["purchased"], ["o1"]),
            scalability=DimensionResult("scalability", EVIDENCED, "weak_signal_multi_platform", ["o1"]),
            pain_severity=DimensionResult("pain_severity", EVIDENCED, "SEVERE", ["o1"]),
        ), distinct_sources=3, ca_evaluations_for_group=[], thresholds=self.th)
        self.assertEqual(d["state"], "PROMISING")

    def test_promising_blocked_by_missing_scalability(self):
        d = decide_state(dims(
            economic_consequence=DimensionResult("economic_consequence", EVIDENCED, ["cost"], ["o1"]),
            willingness_to_pay=DimensionResult("willingness_to_pay", EVIDENCED, ["purchased"], ["o1"]),
            pain_severity=DimensionResult("pain_severity", EVIDENCED, "SEVERE", ["o1"]),
        ), distinct_sources=3, ca_evaluations_for_group=[], thresholds=self.th)
        self.assertEqual(d["state"], "INVESTIGATE")
        self.assertEqual(d["audit"]["PROMISING"]["missing"], ["scalability EVIDENCED"])

    def test_rejected_when_all_evaluated_anomalies_killed(self):
        d = decide_state(dims(), distinct_sources=3,
                          ca_evaluations_for_group=[{"anomaly_id": "A1", "action": "KILL"}],
                          thresholds=self.th)
        self.assertEqual(d["state"], "REJECTED")
        self.assertEqual(d["rejected_derived_from"], ["A1"])

    def test_not_rejected_when_only_some_evaluated_anomalies_killed(self):
        d = decide_state(dims(), distinct_sources=3,
                          ca_evaluations_for_group=[{"anomaly_id": "A1", "action": "KILL"},
                                                     {"anomaly_id": "A2", "action": "WATCH"}],
                          thresholds=self.th)
        self.assertNotEqual(d["state"], "REJECTED")

    def test_contradiction_alone_does_not_auto_reject(self):
        d = decide_state(dims(contradictory_evidence=DimensionResult(
            "contradictory_evidence", EVIDENCED, "contradiction_present", ["o1"])),
            distinct_sources=1, ca_evaluations_for_group=[], thresholds=self.th)
        self.assertNotEqual(d["state"], "REJECTED")


if __name__ == "__main__":
    unittest.main()
