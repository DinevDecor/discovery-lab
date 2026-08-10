import _pathsetup  # noqa: F401
import unittest

from business_candidate_analyst.config import load_rearchitecture_thresholds
from business_candidate_analyst.models import INFERRED, INSUFFICIENT_DATA, OBSERVED
from business_candidate_analyst.rearchitecture import dimensions as d


def obs(**kw):
    base = {"observation_id": "OBS-x", "source": "test", "url": "http://x", "process": "", "pain": "",
            "current_carrier": "", "failure_mode": "", "hidden_function_hint": "", "evidence_quote": ""}
    base.update(kw)
    return base


class DimensionTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_rearchitecture_thresholds()

    def test_existing_business_insufficient_when_empty(self):
        self.assertEqual(d.existing_business_or_jtbd([obs(process="")]).status, INSUFFICIENT_DATA)

    def test_existing_business_observed_when_present(self):
        r = d.existing_business_or_jtbd([obs(process="running a vending machine business")])
        self.assertEqual(r.status, OBSERVED)

    def test_historical_constraint_inferred_without_reason_language(self):
        r = d.historical_constraint([obs(hidden_function_hint="warehouse inventory buffer")], self.cfg)
        self.assertEqual(r.status, INFERRED)
        self.assertEqual(r.value, "buffer_inventory")

    def test_historical_constraint_observed_with_reason_language(self):
        r = d.historical_constraint(
            [obs(hidden_function_hint="warehouse inventory kept because supplier delivery was slow "
                                       "and unreliable")], self.cfg)
        self.assertEqual(r.status, OBSERVED)

    def test_historical_constraint_insufficient_when_no_pattern(self):
        r = d.historical_constraint([obs(hidden_function_hint="a giraffe crosses the savanna")], self.cfg)
        self.assertEqual(r.status, INSUFFICIENT_DATA)

    def test_weakened_still_binding_language_is_insufficient_not_weakened(self):
        r = d.evidence_constraint_weakened(
            [obs(pain="the batteries everyone suggests aren't free")], self.cfg)
        self.assertEqual(r.status, INSUFFICIENT_DATA)
        self.assertIn("STILL binding", r.note)

    def test_weakened_observed_requires_weakening_language_and_enabler(self):
        r = d.evidence_constraint_weakened(
            [obs(pain="prices have fallen thanks to cheaper compute")], self.cfg)
        self.assertEqual(r.status, OBSERVED)

    def test_weakened_inferred_when_change_language_but_no_enabler(self):
        r = d.evidence_constraint_weakened([obs(pain="this is now possible")], self.cfg)
        self.assertEqual(r.status, INFERRED)

    def test_legacy_structure_reuses_current_carrier_verbatim(self):
        r = d.legacy_structure([obs(current_carrier="manual branch visits")])
        self.assertEqual(r.status, OBSERVED)
        self.assertEqual(r.value, ["manual branch visits"])

    def test_proposed_rearchitecture_is_framing_only(self):
        r = d.proposed_rearchitecture(
            [obs(hidden_function_hint="warehouse inventory buffer", current_carrier="warehouse")], self.cfg)
        self.assertIn("FRAMING ONLY", r.note)

    def test_why_now_never_defaults_to_ai(self):
        r = d.why_now([obs(pain="no enabler language here at all")], self.cfg)
        self.assertEqual(r.status, INSUFFICIENT_DATA)
        self.assertIsNone(r.value)

    def test_why_now_cites_specific_enabler(self):
        r = d.why_now([obs(pain="digital payment infrastructure now exists")], self.cfg)
        self.assertEqual(r.status, OBSERVED)
        self.assertIn("digital_payments", r.value)

    def test_evidence_gaps_lists_insufficient_and_inferred_but_not_framing(self):
        fields = d.assess_all([obs(hidden_function_hint="warehouse inventory buffer",
                                    current_carrier="warehouse")], self.cfg)
        gaps = d.evidence_gaps(fields)
        self.assertTrue(any("historical_constraint" in g for g in gaps))
        self.assertFalse(any("proposed_rearchitecture" in g for g in gaps))

    def test_evidence_gaps_accepts_dict_shaped_fields_too(self):
        fields = d.assess_all([obs(hidden_function_hint="warehouse inventory buffer",
                                    current_carrier="warehouse")], self.cfg)
        as_dicts = {k: v.to_dict() for k, v in fields.items()}
        self.assertEqual(d.evidence_gaps(fields), d.evidence_gaps(as_dicts))

    def test_assess_all_covers_every_required_field(self):
        fields = d.assess_all([obs(process="p", hidden_function_hint="warehouse", current_carrier="c",
                                    pain="p", failure_mode="f")], self.cfg)
        expected = {"existing_business_or_jtbd", "historical_constraint", "evidence_constraint_existed",
                    "evidence_constraint_weakened", "legacy_structure", "proposed_rearchitecture",
                    "why_now", "potential_economic_effect"}
        self.assertEqual(set(fields.keys()), expected)


if __name__ == "__main__":
    unittest.main()
