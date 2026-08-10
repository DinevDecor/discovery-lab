import _pathsetup  # noqa: F401
import os
import shutil
import tempfile
import unittest

from _factories import ev, make_record
from constraint_change_observatory.ledger import ConstraintLedger, rebuild_snapshot
from constraint_change_observatory.report import render
from constraint_change_observatory.schema import (
    OBSERVED, SHIFTED, STILL_BINDING, DeltaDimension, ReplacementConstraint,
)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.report_path = os.path.join(self.tmp, "report.md")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _snapshot_with(self, *records):
        events_path = os.path.join(self.tmp, "events.jsonl")
        ledger = ConstraintLedger(events_path)
        for r in records:
            ledger.append(r, "2026-08-10T00:00:00Z")
        return rebuild_snapshot(ledger.all_entries())

    def test_report_contains_all_required_sections(self):
        snapshot = self._snapshot_with(make_record())
        render(self.report_path, snapshot, ["ccov-test-0001"], "2026-08-10T00:00:00Z")
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read()
        for heading in ("Newly added constraint changes", "Constraint states",
                         "Old bottleneck → new bottleneck transitions", "Strongest quantitative changes",
                         "Still-binding constraints", "INSUFFICIENT_DATA", "Unresolved questions",
                         "Possible conflicts"):
            self.assertIn(heading, text, f"missing section: {heading}")

    def test_report_contains_no_business_language(self):
        record = make_record(
            current_constraint_state=SHIFTED,
            current_evidence=[ev("C", "x", "n/a", "2026")],
            replacement_constraint=ReplacementConstraint("labor_cost", "installation now dominates", OBSERVED),
        )
        snapshot = self._snapshot_with(record)
        render(self.report_path, snapshot, [], "2026-08-10T00:00:00Z")
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read().lower()
        for banned in ("business opportunity", "startup", "market opportunity", "promising",
                        "recommend", "investment"):
            self.assertNotIn(banned, text, f"report must not contain business language: {banned!r}")

    def test_transitions_section_lists_shifted_with_replacement(self):
        record = make_record(
            current_constraint_state=SHIFTED,
            current_evidence=[ev("C", "x", "n/a", "2026")],
            replacement_constraint=ReplacementConstraint("labor_cost", "installation now dominates", OBSERVED),
        )
        snapshot = self._snapshot_with(record)
        render(self.report_path, snapshot, [], "2026-08-10T00:00:00Z")
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("labor_cost", text)
        self.assertIn("installation now dominates", text)

    def test_strongest_quantitative_changes_lists_order_of_magnitude_deltas(self):
        record = make_record(constraint_delta={
            "cost": DeltaDimension(100, 1, "USD", 0.01, "ORDER_OF_MAGNITUDE", []),
        })
        snapshot = self._snapshot_with(record)
        render(self.report_path, snapshot, [], "2026-08-10T00:00:00Z")
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("ccov-test-0001", text.split("Strongest quantitative changes")[1][:500])

    def test_still_binding_section_lists_record(self):
        record = make_record(current_constraint_state=STILL_BINDING,
                              current_evidence=[ev("Regulator", "still in force", "n/a", "2026")])
        snapshot = self._snapshot_with(record)
        render(self.report_path, snapshot, [], "2026-08-10T00:00:00Z")
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read()
        still_section = text.split("## Still-binding constraints")[1].split("## ")[0]
        self.assertIn("ccov-test-0001", still_section)

    def test_unresolved_questions_are_listed_per_record(self):
        record = make_record(unresolved_questions=["what about X?"])
        snapshot = self._snapshot_with(record)
        render(self.report_path, snapshot, [], "2026-08-10T00:00:00Z")
        with open(self.report_path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("what about X?", text)


if __name__ == "__main__":
    unittest.main()
