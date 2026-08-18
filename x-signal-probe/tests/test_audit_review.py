import _pathsetup  # noqa: F401
import inspect
import unittest

from x_signal_probe import audit_review


def _entry():
    return {
        "post_id": "42",
        "query_family": "manual_workaround",
        "query_id": "q05",
        "canonical_url": "https://x.com/i/status/42",
        "created_at": "2026-08-18T00:00:00Z",
        "retrieved_at": "2026-08-18T01:00:00Z",
    }


class RehydrateSelectedTests(unittest.TestCase):
    def test_calls_get_posts_fn_exactly_once_with_all_ids(self):
        calls = []

        def fake_get_posts(ids, token):
            calls.append(list(ids))
            return {"42": {"text": "t", "created_at": ""}}, []

        found, unavailable = audit_review.rehydrate_selected([_entry()], "tok", get_posts_fn=fake_get_posts)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], ["42"])
        self.assertIn("42", found)


class RecordVerdictTests(unittest.TestCase):
    def test_record_unavailable_sets_unavailable_fields(self):
        v = audit_review.record_unavailable(_entry(), "AUDIT-1", "run-1", "0.1")
        self.assertEqual(v.availability, "UNAVAILABLE")
        self.assertEqual(v.post_id, "42")

    def test_record_available_carries_rubric_answers(self):
        v = audit_review.record_available(
            _entry(), "AUDIT-1", "run-1", "0.1", "reviewer-x",
            "YES", "YES", "NO", "UNCLEAR", "YES", "short note",
        )
        self.assertEqual(v.availability, "AVAILABLE")
        self.assertEqual(v.a_genuine_problem_report, "YES")
        self.assertEqual(v.e_corroboration_worthy, "YES")
        self.assertEqual(v.notes, "short note")


class NoTextParameterTests(unittest.TestCase):
    """Structural proof that the audit-review boundary functions cannot
    be handed post text even by mistake - there is no parameter for it
    to flow through."""

    def test_record_available_signature_has_no_text_parameter(self):
        params = set(inspect.signature(audit_review.record_available).parameters)
        for forbidden in ("text", "post_text", "quote", "raw_text"):
            self.assertNotIn(forbidden, params)

    def test_record_unavailable_signature_has_no_text_parameter(self):
        params = set(inspect.signature(audit_review.record_unavailable).parameters)
        for forbidden in ("text", "post_text", "quote", "raw_text"):
            self.assertNotIn(forbidden, params)

    def test_rehydrate_selected_signature_has_no_text_parameter(self):
        params = set(inspect.signature(audit_review.rehydrate_selected).parameters)
        for forbidden in ("text", "post_text", "quote", "raw_text"):
            self.assertNotIn(forbidden, params)


if __name__ == "__main__":
    unittest.main()
