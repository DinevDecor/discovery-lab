import _pathsetup  # noqa: F401
import unittest

from _factories import ev, make_record
from constraint_change_observatory.schema import ConstraintChangeRecord, ReplacementConstraint


class SchemaRoundTripTests(unittest.TestCase):
    def test_to_dict_from_dict_round_trip(self):
        record = make_record(replacement_constraint=ReplacementConstraint("labor_cost", "stmt", "OBSERVED"))
        rebuilt = ConstraintChangeRecord.from_dict(record.to_dict())
        self.assertEqual(rebuilt.to_dict(), record.to_dict())

    def test_from_dict_tolerates_missing_optional_fields(self):
        minimal = {
            "record_id": "ccov-minimal",
            "constraint_family": "cost",
            "domain": "d",
            "constrained_activity": "a",
            "historical_constraint": {"statement": "s", "evidence_status": "OBSERVED"},
            "change_driver": {"category": "technological_improvement", "statement": "s", "evidence_status": "OBSERVED"},
            "current_constraint_state": "INSUFFICIENT_DATA",
        }
        record = ConstraintChangeRecord.from_dict(minimal)
        self.assertEqual(record.record_id, "ccov-minimal")
        self.assertEqual(record.historical_evidence, [])
        self.assertIsNone(record.replacement_constraint)

    def test_from_dict_ignores_unknown_keys(self):
        data = make_record().to_dict()
        data["some_future_field_not_in_schema_yet"] = "ignore me"
        data["historical_constraint"]["extra_commentary"] = "also ignore"
        record = ConstraintChangeRecord.from_dict(data)  # must not raise
        self.assertEqual(record.record_id, data["record_id"])

    def test_evidence_item_defaults(self):
        e = ev()
        self.assertEqual(e.deployment_context, "unknown")


if __name__ == "__main__":
    unittest.main()
