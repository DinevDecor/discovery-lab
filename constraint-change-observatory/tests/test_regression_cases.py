"""The nine regression cases explicitly required by the implementation
task, one test (or tight group) per numbered case. Each docstring quotes
the case as given so the mapping is auditable without cross-referencing
elsewhere.
"""

import _pathsetup  # noqa: F401
import os
import shutil
import tempfile
import unittest

from _factories import ev, make_record
from constraint_change_observatory.ledger import ConstraintLedger, rebuild_snapshot
from constraint_change_observatory.report import _find_conflicts
from constraint_change_observatory.schema import (
    INSUFFICIENT_DATA, INVERTED, OBSERVED, SHIFTED, STILL_BINDING, WEAKENED,
    ChangeDriver, ClaimField, DeltaDimension, ReplacementConstraint,
)
from constraint_change_observatory.validator import validate


class RegressionCaseTests(unittest.TestCase):
    def assertValid(self, record):
        v = validate(record)
        self.assertEqual(v, [], f"expected valid, got violations: {v}")

    def assertInvalid(self, record):
        v = validate(record)
        self.assertNotEqual(v, [], "expected violations, got none")
        return v

    # 1. new technology exists does NOT imply WEAKENED
    def test_case_1_new_technology_alone_does_not_imply_weakened(self):
        record = make_record(
            change_driver=ChangeDriver("technological_improvement", "a cheaper alternative now exists", OBSERVED),
            change_evidence=[ev("Change Source", 5, "USD", "2024")],
            current_constraint_state=WEAKENED,
            current_evidence=[],  # the whole point: nothing speaks to the ORIGINAL constraint's present state
        )
        violations = self.assertInvalid(record)
        self.assertTrue(any("current_evidence" in v for v in violations))

    # 2. 20x cost drop + binding regulation -> SHIFTED/STILL_BINDING, not WEAKENED
    def test_case_2_large_cost_delta_does_not_override_still_binding_regulation(self):
        record = make_record(
            constraint_delta={"cost": DeltaDimension(then_value=100, now_value=5, unit="USD", ratio=0.05,
                                                       magnitude_class="ORDER_OF_MAGNITUDE", evidence_ids=[])},
            current_constraint_state=STILL_BINDING,
            current_evidence=[ev("Regulator current rule text", "still in force", "n/a", "2026")],
        )
        self.assertValid(record)  # a 20x cost delta coexisting with STILL_BINDING is not a contradiction
        # Nothing here required (or would even let) the cost delta force the state to WEAKENED - the two
        # fields are independent, exactly design doc §9/§12.

    # 3. AI capability + legally required licensed human -> constraint remains binding
    def test_case_3_ai_change_driver_does_not_exempt_still_binding_from_current_evidence(self):
        valid = make_record(
            change_driver=ChangeDriver("ai", "an AI system can now perform the task technically", OBSERVED),
            change_evidence=[ev("AI capability report", "task automatable", "n/a", "2025")],
            current_constraint_state=STILL_BINDING,
            current_evidence=[ev("Licensing statute text", "licensed human required by law", "n/a", "2026")],
        )
        self.assertValid(valid)
        invalid = make_record(
            change_driver=ChangeDriver("ai", "an AI system can now perform the task technically", OBSERVED),
            change_evidence=[ev("AI capability report", "task automatable", "n/a", "2025")],
            current_constraint_state=STILL_BINDING,
            current_evidence=[],  # AI driver present, but no current evidence - must still be rejected
        )
        self.assertInvalid(invalid)

    # 4. cheap component + expensive installation -> replacement constraint captured
    def test_case_4_shifted_requires_replacement_constraint(self):
        valid = make_record(
            constraint_delta={"cost": DeltaDimension(100, 1, "USD", 0.01, "ORDER_OF_MAGNITUDE", [])},
            current_constraint_state=SHIFTED,
            current_evidence=[ev("Installation cost benchmark", "labor now dominant", "n/a", "2024")],
            replacement_constraint=ReplacementConstraint("labor_cost", "installation labor now dominates cost",
                                                           OBSERVED),
        )
        self.assertValid(valid)
        invalid = make_record(
            constraint_delta={"cost": DeltaDimension(100, 1, "USD", 0.01, "ORDER_OF_MAGNITUDE", [])},
            current_constraint_state=SHIFTED,
            current_evidence=[ev("Installation cost benchmark", "labor now dominant", "n/a", "2024")],
            replacement_constraint=None,
            unresolved_questions=[],
        )
        self.assertInvalid(invalid)

    # 5. lab-only capability -> not broadly WEAKENED
    def test_case_5_lab_only_evidence_cannot_support_broad_weakened(self):
        lab_only_evidence = [ev("Peer-reviewed lab demonstration", "works in controlled trial", "n/a", "2025",
                                  deployment_context="lab_only")]
        invalid = make_record(current_constraint_state=WEAKENED, current_evidence=lab_only_evidence)
        violations = self.assertInvalid(invalid)
        self.assertTrue(any("lab_only" in v for v in violations))
        # The same lab-only evidence CAN support an honest INSUFFICIENT_DATA record.
        valid = make_record(current_constraint_state=INSUFFICIENT_DATA, current_evidence=lab_only_evidence)
        self.assertValid(valid)

    # 6. cheaper but less reliable technology -> reliability preserved as constraint
    def test_case_6_reliability_dimension_survives_alongside_cost_improvement(self):
        record = make_record(
            constraint_delta={
                "cost": DeltaDimension(100, 5, "USD", 0.05, "ORDER_OF_MAGNITUDE", []),
                "reliability": DeltaDimension(None, None, "n/a", None, "INSUFFICIENT_DATA", ["obs-reliability"]),
            },
            current_constraint_state=SHIFTED,
            current_evidence=[ev("Field reliability report", "higher failure rate observed", "n/a", "2024")],
            replacement_constraint=ReplacementConstraint("reliability", "reliability, not cost, now binds", OBSERVED),
        )
        self.assertValid(record)
        self.assertIn("reliability", record.constraint_delta)
        self.assertIn("cost", record.constraint_delta)

    # 7. valid zero-AI constraint shift works normally
    def test_case_7_zero_ai_shift_validates_normally(self):
        record = make_record(
            historical_evidence=[ev("Old statute text", "restriction existed", "n/a", "1927")],
            change_driver=ChangeDriver("regulation_change", "a statute changed", OBSERVED),
            change_evidence=[ev("Statute text", "restriction removed", "n/a", "1994")],
            current_constraint_state=SHIFTED,
            current_evidence=[ev("Current regulator text", "a narrower rule now applies", "n/a", "2026")],
            replacement_constraint=ReplacementConstraint("regulation", "a narrower rule replaces the old one",
                                                           OBSERVED),
        )
        full_text = str(record.to_dict()).lower()
        self.assertNotIn("ai", full_text.split())  # crude but sufficient: no bare "ai" token anywhere
        self.assertValid(record)

    # 8. conflicting evidence remains auditable
    def test_case_8_conflicting_records_are_both_preserved_not_overwritten(self):
        tmp = tempfile.mkdtemp()
        try:
            events_path = os.path.join(tmp, "constraint_events.jsonl")
            ledger = ConstraintLedger(events_path)
            record_a = make_record(
                record_id="ccov-conflict-a", current_constraint_state=STILL_BINDING,
                current_evidence=[ev("Source A", "still binds", "n/a", "2026")],
            )
            record_b = make_record(
                record_id="ccov-conflict-b", current_constraint_state=WEAKENED,
                current_evidence=[ev("Source B", "clearly eased", "n/a", "2026")],
            )
            self.assertValid(record_a)
            self.assertValid(record_b)
            self.assertTrue(ledger.append(record_a, "2026-08-10T00:00:00Z"))
            self.assertTrue(ledger.append(record_b, "2026-08-10T00:01:00Z"))

            snapshot = rebuild_snapshot(ledger.all_entries())
            ids = {r["record_id"] for r in snapshot["current"]}
            self.assertIn("ccov-conflict-a", ids)
            self.assertIn("ccov-conflict-b", ids)  # neither overwrote the other

            conflicts = _find_conflicts(snapshot["current"])
            self.assertEqual(len(conflicts), 1)
            self.assertEqual({r["record_id"] for r in conflicts[0]}, {"ccov-conflict-a", "ccov-conflict-b"})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # 9. historical adaptation may remain INSUFFICIENT_DATA without invalidating the entire record
    def test_case_9_insufficient_historical_adaptation_does_not_invalidate_record(self):
        record = make_record(
            historical_adaptation=ClaimField(None, INSUFFICIENT_DATA),
            current_constraint_state=WEAKENED,
            current_evidence=[ev("Current source", "clearly weakened now", "n/a", "2026")],
        )
        self.assertValid(record)
        self.assertEqual(record.historical_adaptation.evidence_status, INSUFFICIENT_DATA)


if __name__ == "__main__":
    unittest.main()
