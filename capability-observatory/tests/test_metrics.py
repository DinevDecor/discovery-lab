import _pathsetup  # noqa: F401
import unittest

from capability_observatory import metrics

PANEL_20 = [f"C3-{i:03d}" for i in range(1, 21)]


def make_observation(panel_item_id, observed_at, price=100.0, availability="in_stock", lead_time_days=5):
    return {
        "panel_item_id": panel_item_id,
        "observed_at": observed_at,
        "recorded_at": observed_at,
        "price": price,
        "availability": availability,
        "lead_time_days": lead_time_days,
    }


def make_capture(panel_item_id, outcome, source="provider_a"):
    return {"panel_item_id": panel_item_id, "capture_outcome": outcome, "source": source}


class ObservabilityTests(unittest.TestCase):
    def test_counts_distinct_observed_panel_items(self):
        observations = [make_observation(pid, "2026-08-09T00:00:00Z") for pid in PANEL_20[:16]]
        result = metrics.observability(PANEL_20, observations)
        self.assertEqual(result["observed_count"], 16)
        self.assertTrue(result["meets_target"])

    def test_below_target_is_flagged(self):
        observations = [make_observation(pid, "2026-08-09T00:00:00Z") for pid in PANEL_20[:10]]
        result = metrics.observability(PANEL_20, observations)
        self.assertEqual(result["observed_count"], 10)
        self.assertFalse(result["meets_target"])
        self.assertEqual(len(result["unobserved_panel_item_ids"]), 10)

    def test_multiple_observations_for_one_item_count_once(self):
        observations = [
            make_observation("C3-001", "2026-08-09T00:00:00Z"),
            make_observation("C3-001", "2026-08-16T00:00:00Z"),
        ]
        result = metrics.observability(PANEL_20, observations)
        self.assertEqual(result["observed_count"], 1)


class CaptureSuccessTests(unittest.TestCase):
    def test_rate_is_ok_over_total(self):
        captures = [make_capture("C3-001", "ok")] * 12 + [make_capture("C3-002", "access_blocked")] * 8
        result = metrics.capture_success(captures)
        self.assertEqual(result["total_attempted"], 20)
        self.assertEqual(result["ok_count"], 12)
        self.assertAlmostEqual(result["rate"], 0.60)
        self.assertTrue(result["meets_target"])

    def test_below_threshold_is_flagged(self):
        captures = [make_capture("C3-001", "ok")] * 5 + [make_capture("C3-002", "access_blocked")] * 15
        result = metrics.capture_success(captures)
        self.assertFalse(result["meets_target"])

    def test_zero_attempts_does_not_crash_and_is_below_target(self):
        result = metrics.capture_success([])
        self.assertEqual(result["rate"], 0.0)
        self.assertFalse(result["meets_target"])


class ProviderParseFailureTests(unittest.TestCase):
    def test_rate_computed_per_provider(self):
        captures = (
            [make_capture("C3-001", "ok", source="provider_a")] * 8
            + [make_capture("C3-001", "parse_error", source="provider_a")] * 2
            + [make_capture("C3-010", "parse_error", source="provider_d")] * 3
            + [make_capture("C3-010", "ok", source="provider_d")] * 1
        )
        result = metrics.provider_parse_failure_rate(captures)
        self.assertAlmostEqual(result["per_provider"]["provider_a"]["rate"], 0.20)
        self.assertFalse(result["per_provider"]["provider_a"]["exceeds_alert_threshold"])
        self.assertAlmostEqual(result["per_provider"]["provider_d"]["rate"], 0.75)
        self.assertTrue(result["per_provider"]["provider_d"]["exceeds_alert_threshold"])
        self.assertIn("provider_d", result["providers_exceeding_threshold"])
        self.assertNotIn("provider_a", result["providers_exceeding_threshold"])


class IdentityBacklogTests(unittest.TestCase):
    def test_counts_distinct_items_not_break_events(self):
        breaks = [
            {"panel_item_id": "C3-001", "status": "UNRESOLVED"},
            {"panel_item_id": "C3-001", "status": "UNRESOLVED"},  # same item, second break
            {"panel_item_id": "C3-002", "status": "UNRESOLVED"},
        ]
        result = metrics.identity_backlog(breaks)
        self.assertEqual(result["unresolved_item_count"], 2)

    def test_trigger_fires_above_three(self):
        breaks = [{"panel_item_id": f"C3-{i:03d}", "status": "UNRESOLVED"} for i in range(1, 5)]
        result = metrics.identity_backlog(breaks)
        self.assertEqual(result["unresolved_item_count"], 4)
        self.assertTrue(result["exceeds_trigger"])

    def test_trigger_does_not_fire_at_exactly_three(self):
        breaks = [{"panel_item_id": f"C3-{i:03d}", "status": "UNRESOLVED"} for i in range(1, 4)]
        result = metrics.identity_backlog(breaks)
        self.assertEqual(result["unresolved_item_count"], 3)
        self.assertFalse(result["exceeds_trigger"])


class StateChangesTests(unittest.TestCase):
    def test_price_change_between_adjacent_observations_counts(self):
        observations = [
            make_observation("C3-001", "2026-08-09T00:00:00Z", price=100.0),
            make_observation("C3-001", "2026-08-16T00:00:00Z", price=110.0),
        ]
        result = metrics.state_changes(observations, [])
        self.assertEqual(result["raw_field_changes"], 1)

    def test_identical_repeated_observations_produce_no_changes(self):
        observations = [
            make_observation("C3-001", "2026-08-09T00:00:00Z"),
            make_observation("C3-001", "2026-08-16T00:00:00Z"),
        ]
        result = metrics.state_changes(observations, [])
        self.assertEqual(result["raw_field_changes"], 0)
        self.assertEqual(result["total_raw_state_changes"], 0)

    def test_identity_breaks_are_added_to_the_total(self):
        observations = [make_observation("C3-001", "2026-08-09T00:00:00Z")]
        breaks = [{"panel_item_id": "C3-001", "status": "UNRESOLVED"}]
        result = metrics.state_changes(observations, breaks)
        self.assertEqual(result["identity_breaks"], 1)
        self.assertEqual(result["total_raw_state_changes"], 1)


if __name__ == "__main__":
    unittest.main()
