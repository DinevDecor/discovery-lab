import _pathsetup  # noqa: F401
import unittest

from _factories import ev, make_record
from constraint_change_observatory.schema import (
    INFERRED, INSUFFICIENT_DATA, INVERTED, OBSERVED, SHIFTED, STILL_BINDING, WEAKENED,
    ChangeDriver, ClaimField, DeltaDimension, ReplacementConstraint,
)
from constraint_change_observatory.validator import ValidationError, validate, validate_or_raise


class RequiredFieldTests(unittest.TestCase):
    def test_missing_record_id_rejected(self):
        record = make_record(record_id="")
        self.assertTrue(any("record_id" in v for v in validate(record)))

    def test_missing_analyst_rejected(self):
        record = make_record(analyst="")
        self.assertTrue(any("analyst" in v for v in validate(record)))

    def test_wrong_protocol_version_rejected(self):
        record = make_record()
        record.protocol_version = "ccov0.2"
        self.assertTrue(any("protocol_version" in v for v in validate(record)))


class StateTaxonomyTests(unittest.TestCase):
    def test_unknown_state_rejected(self):
        record = make_record(current_constraint_state="MOSTLY_FINE_PROBABLY")
        self.assertTrue(any("current_constraint_state" in v for v in validate(record)))

    def test_unknown_evidence_status_rejected(self):
        record = make_record(historical_constraint=ClaimField("s", "PRETTY_SURE"))
        self.assertTrue(any("historical_constraint.evidence_status" in v for v in validate(record)))

    def test_unknown_magnitude_class_rejected(self):
        record = make_record(constraint_delta={"cost": DeltaDimension(1, 2, "USD", 2.0, "HUGE", [])})
        self.assertTrue(any("magnitude_class" in v for v in validate(record)))

    def test_all_five_states_are_individually_constructible(self):
        for state in (WEAKENED, STILL_BINDING, SHIFTED, INVERTED, INSUFFICIENT_DATA):
            kwargs = dict(current_constraint_state=state)
            if state in (WEAKENED, STILL_BINDING, SHIFTED, INVERTED):
                kwargs["current_evidence"] = [ev("Current source", "x", "n/a", "2026")]
            if state in (SHIFTED, INVERTED):
                kwargs["replacement_constraint"] = ReplacementConstraint("cost", "replacement", OBSERVED)
            record = make_record(**kwargs)
            self.assertEqual(validate(record), [], f"state {state} should be constructible as valid")


class ProvenanceTests(unittest.TestCase):
    def test_empty_provenance_with_evidence_rejected(self):
        record = make_record(provenance=[])
        self.assertTrue(any("provenance" in v for v in validate(record)))

    def test_empty_provenance_with_no_evidence_allowed(self):
        record = make_record(
            historical_constraint=ClaimField(None, INSUFFICIENT_DATA), historical_evidence=[],
            change_driver=ChangeDriver("", None, INSUFFICIENT_DATA), change_evidence=[],
            current_constraint_state=INSUFFICIENT_DATA, current_evidence=[], provenance=[],
        )
        self.assertEqual(validate(record), [])


class ObservedRequiresEvidenceTests(unittest.TestCase):
    def test_observed_historical_constraint_without_evidence_rejected(self):
        record = make_record(historical_constraint=ClaimField("s", OBSERVED), historical_evidence=[])
        self.assertTrue(any("historical_constraint is OBSERVED" in v for v in validate(record)))

    def test_inferred_historical_constraint_without_evidence_allowed(self):
        record = make_record(historical_constraint=ClaimField("plausible inference", INFERRED),
                              historical_evidence=[])
        self.assertEqual(validate(record), [])

    def test_observed_change_driver_without_change_evidence_rejected(self):
        record = make_record(change_driver=ChangeDriver("technological_improvement", "s", OBSERVED),
                              change_evidence=[])
        self.assertTrue(any("change_driver is OBSERVED" in v for v in validate(record)))

    def test_uncited_evidence_item_rejected(self):
        record = make_record(historical_evidence=[ev(citation="")])
        self.assertTrue(any("historical_constraint is OBSERVED" in v for v in validate(record)))


class TemporalOrderingTests(unittest.TestCase):
    def test_current_evidence_before_historical_evidence_rejected(self):
        record = make_record(
            historical_evidence=[ev("H", 1, "USD", "2020")],
            current_constraint_state=STILL_BINDING,
            current_evidence=[ev("C", 1, "n/a", "1990")],
        )
        self.assertTrue(any("THEN/NOW appear swapped" in v for v in validate(record)))

    def test_unparseable_dates_do_not_block_validation(self):
        record = make_record(
            historical_evidence=[ev("H", 1, "USD", "a long time ago")],
            current_constraint_state=STILL_BINDING,
            current_evidence=[ev("C", 1, "n/a", "recently")],
        )
        self.assertEqual(validate(record), [])

    def test_approximate_date_strings_parse_leniently(self):
        record = make_record(
            historical_evidence=[ev("H", 1, "USD", "2001")],
            change_evidence=[ev("Ch", 1, "USD", "2015 (late)")],
            current_constraint_state=STILL_BINDING,
            current_evidence=[ev("C", 1, "n/a", "~2021-2022")],
        )
        self.assertEqual(validate(record), [])


class ReplacementConstraintTests(unittest.TestCase):
    def test_inverted_without_replacement_rejected_even_with_unresolved_questions(self):
        record = make_record(
            current_constraint_state=INVERTED,
            current_evidence=[ev("C", "x", "n/a", "2026")],
            replacement_constraint=None,
            unresolved_questions=["what replaces this?"],
        )
        self.assertTrue(any("INVERTED requires" in v for v in validate(record)))

    def test_shifted_without_replacement_but_with_unresolved_question_allowed(self):
        record = make_record(
            current_constraint_state=SHIFTED,
            current_evidence=[ev("C", "x", "n/a", "2026")],
            replacement_constraint=None,
            unresolved_questions=["replacement constraint not yet identified in this research pass"],
        )
        self.assertEqual(validate(record), [])

    def test_replacement_constraint_observed_requires_current_evidence(self):
        record = make_record(
            current_constraint_state=SHIFTED,
            current_evidence=[],
            replacement_constraint=ReplacementConstraint("labor_cost", "s", OBSERVED),
            unresolved_questions=["x"],
        )
        violations = validate(record)
        self.assertTrue(any("current_evidence" in v for v in violations))


class QuantitativeDeltaTests(unittest.TestCase):
    def test_numeric_value_without_unit_rejected(self):
        record = make_record(constraint_delta={"cost": DeltaDimension(100, 10, "", None,
                                                                         "ORDER_OF_MAGNITUDE", [])})
        self.assertTrue(any("no unit" in v for v in validate(record)))

    def test_ratio_inconsistent_with_then_now_rejected(self):
        record = make_record(constraint_delta={"cost": DeltaDimension(100, 10, "USD", 0.5,
                                                                         "ORDER_OF_MAGNITUDE", [])})
        self.assertTrue(any("inconsistent" in v for v in validate(record)))

    def test_ratio_consistent_within_tolerance_accepted(self):
        record = make_record(constraint_delta={"cost": DeltaDimension(100, 10, "USD", 0.1,
                                                                         "ORDER_OF_MAGNITUDE", [])})
        self.assertEqual(validate(record), [])

    def test_zero_then_value_with_ratio_rejected(self):
        record = make_record(constraint_delta={"cost": DeltaDimension(0, 10, "USD", 1.0,
                                                                         "ORDER_OF_MAGNITUDE", [])})
        self.assertTrue(any("then_value=0" in v for v in validate(record)))

    def test_magnitude_class_without_support_rejected(self):
        record = make_record(constraint_delta={"cost": DeltaDimension(None, None, "n/a", None,
                                                                         "ORDER_OF_MAGNITUDE", [])})
        self.assertTrue(any("asserted without" in v for v in validate(record)))

    def test_direction_only_without_values_but_with_evidence_ids_allowed(self):
        record = make_record(constraint_delta={"skill": DeltaDimension(None, None, "n/a", None,
                                                                          "DIRECTION_ONLY", ["obs-1"])})
        self.assertEqual(validate(record), [])

    def test_qualitative_then_now_values_do_not_trigger_ratio_check(self):
        record = make_record(constraint_delta={"regulatory_burden": DeltaDimension(
            "prohibited", "permitted with cap", "n/a", None, "DIRECTION_ONLY", ["obs-1"])})
        self.assertEqual(validate(record), [])


class ValidateOrRaiseTests(unittest.TestCase):
    def test_raises_with_all_violations_listed(self):
        record = make_record(current_constraint_state=WEAKENED, current_evidence=[], record_id="")
        with self.assertRaises(ValidationError) as ctx:
            validate_or_raise(record)
        self.assertGreaterEqual(len(ctx.exception.violations), 2)

    def test_does_not_raise_for_valid_record(self):
        validate_or_raise(make_record())  # should not raise


if __name__ == "__main__":
    unittest.main()
