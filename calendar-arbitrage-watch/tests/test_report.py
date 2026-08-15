"""Daily brief: silence is the default (NO MATERIAL CALENDAR CHANGE), and
exactly the six categories named in the approved architecture review's
DAILY OUTPUT section are detected - never more, never fewer.
"""

import _pathsetup  # noqa: F401
import unittest

from calendar_arbitrage_watch import report
from calendar_arbitrage_watch.models import CalendarAssessment, WATCH, CHEAP_TEST, REJECTED, START_CLOCK_CANDIDATE


def _rec(candidate_id, state=WATCH, forecast_version=1, title="t"):
    a = CalendarAssessment(candidate_id=candidate_id, lifecycle_state=state, title=title)
    d = a.to_dict()
    d["shock_forecast"]["forecast_version"] = forecast_version
    return d


class MaterialEventsTests(unittest.TestCase):
    def test_no_previous_and_no_new_is_empty(self):
        events = report.detect_material_events([], [])
        self.assertTrue(events.is_empty())

    def test_new_candidate_is_a_new_signal(self):
        events = report.detect_material_events([], [_rec("c1")])
        self.assertEqual(len(events.new_signals), 1)
        self.assertFalse(events.is_empty())

    def test_promotion_is_detected(self):
        prev = [_rec("c1", state=WATCH)]
        new = [_rec("c1", state=CHEAP_TEST)]
        events = report.detect_material_events(prev, new)
        self.assertEqual(len(events.promotions), 1)

    def test_degradation_is_detected(self):
        prev = [_rec("c1", state=CHEAP_TEST)]
        new = [_rec("c1", state=WATCH)]
        events = report.detect_material_events(prev, new)
        self.assertEqual(len(events.degradations), 1)

    def test_rejection_is_a_dead_clock_not_a_degradation(self):
        prev = [_rec("c1", state=START_CLOCK_CANDIDATE)]
        new = [_rec("c1", state=REJECTED)]
        events = report.detect_material_events(prev, new)
        self.assertEqual(len(events.dead_clocks), 1)
        self.assertEqual(len(events.degradations), 0)

    def test_unchanged_state_and_unchanged_forecast_is_not_material(self):
        prev = [_rec("c1", state=WATCH, forecast_version=1)]
        new = [_rec("c1", state=WATCH, forecast_version=1)]
        events = report.detect_material_events(prev, new)
        self.assertTrue(events.is_empty())

    def test_new_forecast_version_with_unchanged_state_is_material_evidence_change(self):
        prev = [_rec("c1", state=WATCH, forecast_version=1)]
        new = [_rec("c1", state=WATCH, forecast_version=2)]
        events = report.detect_material_events(prev, new)
        self.assertEqual(len(events.material_evidence_changes), 1)

    def test_new_signals_capped_at_five_shown_in_report_text(self):
        new = [_rec(f"c{i}") for i in range(8)]
        events = report.detect_material_events([], new)
        self.assertEqual(len(events.new_signals), 8)  # all recorded internally
        text = report.render_report("2026-08-15", events, None, [])
        self.assertIn("5 of 8 shown", text)


class BestNextActionTests(unittest.TestCase):
    def test_none_when_nothing_waiting(self):
        self.assertIsNone(report.pick_best_next_action([_rec("c1", state=WATCH)]))

    def test_picks_the_candidate_at_a_max_automatic_state(self):
        new = [_rec("c1", state=WATCH), _rec("c2", state=START_CLOCK_CANDIDATE)]
        best = report.pick_best_next_action(new)
        self.assertEqual(best["candidate_id"], "c2")

    def test_only_one_recommendation_ever(self):
        new = [_rec("c1", state=START_CLOCK_CANDIDATE), _rec("c2", state=START_CLOCK_CANDIDATE)]
        best = report.pick_best_next_action(new)
        self.assertIsInstance(best, dict)  # a single record, never a list


class RenderReportTests(unittest.TestCase):
    def test_no_material_change_message(self):
        events = report.detect_material_events([], [])
        text = report.render_report("2026-08-15", events, None, [])
        self.assertIn("NO MATERIAL CALENDAR CHANGE", text)

    def test_open_findings_appear_when_present(self):
        events = report.detect_material_events([], [_rec("c1")])
        findings = [{"finding_id": "startability_gap", "candidate_id": "c1", "note": "diagnostic only"}]
        text = report.render_report("2026-08-15", events, None, findings)
        self.assertIn("startability_gap", text)
        self.assertIn("Open findings", text)


if __name__ == "__main__":
    unittest.main()
