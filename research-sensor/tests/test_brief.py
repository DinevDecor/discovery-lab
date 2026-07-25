import _pathsetup  # noqa: F401
import unittest

from research_sensor.brief import render_daily_brief, render_weekly_brief
from research_sensor.config import RelevanceGateConfig, RelevanceRule
from research_sensor.models import Domain, EvidenceLevel, Project, RawPaperCapture, SourceTrust
from research_sensor.registry import build_signal

_RELEVANCE = RelevanceGateConfig(rules=[RelevanceRule(project=Project.KOD, keywords=["provenance"])])


def _capture(**overrides):
    base = dict(
        title="Provenance Tracking",
        authors=["A. Researcher"],
        publication="arXiv",
        date="2026-07-10",
        source_name="arXiv cs.AI Recent",
        source_url="https://arxiv.org/abs/x",
        source_trust=SourceTrust.PRIMARY,
        evidence_level=EvidenceLevel.NOTABLE_LAB_PREPRINT,
        domain=Domain.KNOWLEDGE_SYSTEMS,
        raw_abstract="abstract",
        problem_addressed="provenance problem",
        main_contribution="a tracker",
        idea_keywords=["provenance"],
    )
    base.update(overrides)
    return RawPaperCapture(**base)


class TestDailyBrief(unittest.TestCase):
    def test_empty_run_produces_a_valid_no_signals_brief(self):
        text = render_daily_brief("2026-07-20T00:00:00Z", [], [])
        self.assertIn("No signals this run", text)

    def test_new_signal_appears_under_new_signals(self):
        signal = build_signal([_capture()], _RELEVANCE)
        signal.research_id = "RES-0001"
        signal.first_seen = signal.last_seen = "2026-07-20T00:00:00Z"
        text = render_daily_brief("2026-07-20T00:00:00Z", [signal], [])
        self.assertIn("RES-0001", text)
        self.assertIn("New Signals", text)
        self.assertIn("advisory only", text.lower())


class TestWeeklyBrief(unittest.TestCase):
    def test_empty_registry_produces_a_valid_no_signals_brief(self):
        text = render_weekly_brief("2026-07-20T00:00:00Z", [])
        self.assertIn("No signals active in this window", text)

    def test_stale_signal_outside_window_is_excluded(self):
        signal = build_signal([_capture()], _RELEVANCE)
        signal.research_id = "RES-0001"
        signal.first_seen = "2026-06-01T00:00:00Z"
        signal.last_seen = "2026-06-01T00:00:00Z"
        text = render_weekly_brief("2026-07-20T00:00:00Z", [signal])
        self.assertNotIn("RES-0001", text)

    def test_recent_signal_inside_window_is_included(self):
        signal = build_signal([_capture()], _RELEVANCE)
        signal.research_id = "RES-0001"
        signal.first_seen = "2026-07-19T00:00:00Z"
        signal.last_seen = "2026-07-19T00:00:00Z"
        text = render_weekly_brief("2026-07-20T00:00:00Z", [signal])
        self.assertIn("RES-0001", text)


if __name__ == "__main__":
    unittest.main()
