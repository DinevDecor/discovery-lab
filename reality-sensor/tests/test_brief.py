import _pathsetup  # noqa: F401
import unittest

from reality_sensor.brief import render_daily_brief, render_weekly_brief
from reality_sensor.config import RelevanceGateConfig, RelevanceRule
from reality_sensor.models import Category, Project, RawCapture, TrustLevel
from reality_sensor.registry import build_signal

_RELEVANCE = RelevanceGateConfig(rules=[RelevanceRule(project=Project.DISCOVERY_LAB, keywords=["mcp"])])


def _capture(**overrides):
    base = dict(
        source_name="MCP Docs",
        source_url="https://modelcontextprotocol.io/",
        source_trust=TrustLevel.PRIMARY,
        category=Category.AGENT_INFRASTRUCTURE,
        captured_at="2026-07-20T00:00:00Z",
        title="MCP 2.0 released",
        raw_text="MCP 2.0 adds streaming tool results.",
        affected_capability="MCP streaming tool results",
        capability_keywords=["mcp"],
    )
    base.update(overrides)
    return RawCapture(**base)


class TestDailyBrief(unittest.TestCase):
    def test_empty_run_produces_a_valid_no_signals_brief(self):
        text = render_daily_brief("2026-07-20T00:00:00Z", [], [])
        self.assertIn("No signals this run", text)

    def test_new_signal_appears_under_new_signals(self):
        signal = build_signal([_capture()], _RELEVANCE)
        signal.signal_id = "RS-0001"
        signal.first_seen = signal.last_seen = "2026-07-20T00:00:00Z"
        text = render_daily_brief("2026-07-20T00:00:00Z", [signal], [])
        self.assertIn("RS-0001", text)
        self.assertIn("New Signals", text)
        self.assertIn("advisory only", text.lower())


class TestWeeklyBrief(unittest.TestCase):
    def test_empty_registry_produces_a_valid_no_signals_brief(self):
        text = render_weekly_brief("2026-07-20T00:00:00Z", [])
        self.assertIn("No signals active in this window", text)

    def test_stale_signal_outside_window_is_excluded(self):
        signal = build_signal([_capture()], _RELEVANCE)
        signal.signal_id = "RS-0001"
        signal.first_seen = "2026-06-01T00:00:00Z"
        signal.last_seen = "2026-06-01T00:00:00Z"  # more than 7 days before the run
        text = render_weekly_brief("2026-07-20T00:00:00Z", [signal])
        self.assertNotIn("RS-0001", text)

    def test_recent_signal_inside_window_is_included(self):
        signal = build_signal([_capture()], _RELEVANCE)
        signal.signal_id = "RS-0001"
        signal.first_seen = "2026-07-19T00:00:00Z"
        signal.last_seen = "2026-07-19T00:00:00Z"
        text = render_weekly_brief("2026-07-20T00:00:00Z", [signal])
        self.assertIn("RS-0001", text)


if __name__ == "__main__":
    unittest.main()
