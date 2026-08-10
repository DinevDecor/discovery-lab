"""Mode B lifecycle tests, including the two regression tests the task
explicitly requires:

  - a valid rearchitecture candidate can be generated with ZERO
    AI-related evidence (test_no_ai_bias_positive_case_reaches_validating);
  - a candidate whose ONLY justification is "AI could automate this" must
    NOT be sufficient to advance past WATCH
    (test_ai_only_justification_is_not_sufficient).
"""

import _pathsetup  # noqa: F401
import unittest

from business_candidate_analyst.config import load_rearchitecture_thresholds
from business_candidate_analyst.rearchitecture.dimensions import assess_all
from business_candidate_analyst.rearchitecture.lifecycle import decide_state, meets_watch_bar


def obs(**kw):
    base = {"observation_id": "OBS-x", "source": "test", "url": "http://x", "process": "", "pain": "",
            "current_carrier": "", "failure_mode": "", "hidden_function_hint": "", "evidence_quote": ""}
    base.update(kw)
    return base


class NoAIBiasTests(unittest.TestCase):
    """The task's explicitly required regression + negative tests."""

    def setUp(self):
        self.cfg = load_rearchitecture_thresholds()

    def test_no_ai_bias_positive_case_reaches_validating_with_zero_ai_evidence(self):
        observations = [obs(
            process="bank branch account opening",
            hidden_function_hint="customers had to visit a branch office because signature verification "
                                  "required physical presence",
            current_carrier="in-person branch visit with notarized signature",
            pain="customers had to visit a branch office because signature verification required "
                 "physical presence",
            failure_mode="no remote way to verify identity or signature existed",
        )]
        fields = assess_all(observations, self.cfg)
        # Confirm zero AI text anywhere in the fixture before asserting on it.
        for f in fields.values():
            self.assertNotIn("ai", str(f.value).lower().split())
        watch_ok, _ = meets_watch_bar(fields)
        self.assertTrue(watch_ok)

        # Give it explicit, non-AI weakening evidence (digital payments / regulation) and confirm it
        # can reach VALIDATING - proving the ladder is reachable without AI ever being mentioned.
        observations[0]["pain"] += (" digital payment infrastructure and new regulation now allow remote "
                                     "identity verification, so branch visits are increasingly optional")
        fields = assess_all(observations, self.cfg)
        decision = decide_state(fields, observations, distinct_sources=1, ca_evaluations_for_group=[],
                                 config=self.cfg)
        self.assertEqual(decision["state"], "VALIDATING")
        self.assertNotIn("ai", decision["reason"].lower().split())

    def test_ai_only_justification_is_not_sufficient(self):
        """Same historical-constraint strength as the positive case above,
        but the ONLY enabler evidence is an AI-automation claim. Must not
        reach VALIDATING, and the gap must say why."""
        observations = [obs(
            process="bank branch account opening",
            hidden_function_hint="customers had to visit a branch office because signature verification "
                                  "required physical presence",
            current_carrier="in-person branch visit with notarized signature",
            pain="customers had to visit a branch office because signature verification required physical "
                 "presence; AI could now automate this entire process",
            failure_mode="no remote way to verify identity or signature existed",
        )]
        fields = assess_all(observations, self.cfg)
        decision = decide_state(fields, observations, distinct_sources=1, ca_evaluations_for_group=[],
                                 config=self.cfg)
        self.assertNotEqual(decision["state"], "VALIDATING")
        self.assertEqual(decision["state"], "WATCH")
        self.assertTrue(any("no-AI-bias" in m for m in decision["audit"]["VALIDATING"]["missing"]))

    def test_ai_plus_one_real_enabler_is_sufficient(self):
        """Sanity check on the other side: AI is not disqualifying when it
        appears ALONGSIDE a real structural enabler - only "AI alone" is
        refused."""
        observations = [obs(
            process="bank branch account opening",
            hidden_function_hint="customers had to visit a branch office because signature verification "
                                  "required physical presence",
            current_carrier="in-person branch visit with notarized signature",
            pain="branch visits used to be required; new regulation now allows remote signing and AI could "
                 "also help automate parts of the review",
            failure_mode="no remote way to verify identity or signature existed",
        )]
        fields = assess_all(observations, self.cfg)
        decision = decide_state(fields, observations, distinct_sources=1, ca_evaluations_for_group=[],
                                 config=self.cfg)
        self.assertEqual(decision["state"], "VALIDATING")


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_rearchitecture_thresholds()

    def test_no_pattern_no_candidate(self):
        observations = [obs(process="a giraffe crosses the savanna")]
        fields = assess_all(observations, self.cfg)
        watch_ok, missing = meets_watch_bar(fields)
        self.assertFalse(watch_ok)

    def test_still_binding_evidence_caps_at_watch(self):
        observations = [obs(
            hidden_function_hint="curtailment substitutes for battery storage",
            current_carrier="grid operators discarding excess solar generation",
            pain="the batteries everyone suggests aren't free",
            failure_mode="battery storage remains cost-prohibitive",
        )]
        fields = assess_all(observations, self.cfg)
        decision = decide_state(fields, observations, distinct_sources=1, ca_evaluations_for_group=[],
                                 config=self.cfg)
        self.assertEqual(decision["state"], "WATCH")

    def test_rejected_via_ca_kill_evaluation(self):
        observations = [obs(
            hidden_function_hint="warehouse inventory kept because supplier delivery was slow and unreliable",
            current_carrier="warehouse buffer stock",
            pain="prices have fallen thanks to cheaper compute",
        )]
        fields = assess_all(observations, self.cfg)
        decision = decide_state(fields, observations, distinct_sources=1,
                                 ca_evaluations_for_group=[{"anomaly_id": "A1", "action": "KILL"}],
                                 config=self.cfg)
        self.assertEqual(decision["state"], "REJECTED")


if __name__ == "__main__":
    unittest.main()
