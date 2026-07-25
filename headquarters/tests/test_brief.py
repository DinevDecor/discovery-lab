import _pathsetup  # noqa: F401
import unittest

from headquarters.brief import render_brief
from headquarters.inconsistency import Category, Inconsistency
from headquarters.models import Evidence, HealthMetric, PortfolioEntry, Recommendation


def _health():
    return {
        "overall_health": HealthMetric("Overall Health", "71%", "mean of sub-scores"),
        "state_visibility": HealthMetric("State Visibility", "4/5", "formula"),
        "recommendation_backlog": HealthMetric("Recommendation Backlog", "6", "formula"),
        "decision_backlog": HealthMetric("Decision Backlog", "0", "formula"),
    }


def _portfolio():
    return [
        PortfolioEntry("a", "purpose", "ACTIVE", "N/A", "none", "2026-07-25", "LOW", "HIGH", "100%", [])
    ]


def _recommendation():
    return Recommendation(
        hq_id="HQ-0001",
        title="Fix the duplicate ADR",
        reason="Two files claim the same ADR ID.",
        evidence=[Evidence("discovery-lab", "ADR-0001-a.md")],
        reasoning="+3 confirmed",
        expected_impact="Removes ambiguity.",
        dependencies="None.",
        estimated_confidence="MISMATCH",
        estimated_risk="LOW",
        score=6,
        score_breakdown=["+3 confirmed"],
    )


def _inconsistency():
    return Inconsistency(
        category=Category.GOVERNANCE_ISSUE,
        category_rationale="ADR ID collision is a decision-record integrity problem.",
        affected_artifact="discovery-lab",
        observed_evidence=[Evidence("discovery-lab", "ADR-0001-a.md")],
        operational_impact="Ambiguous which decision ADR-0001 means.",
        recommended_future_action="A human should rename one of the files.",
        finding_id="duplicate-adr-discovery-lab-0001",
        title="discovery-lab: two files both claim ADR-0001",
    )


class TestRenderBrief(unittest.TestCase):
    def _render(self, **overrides):
        kwargs = dict(
            health=_health(),
            portfolio=_portfolio(),
            top_recommendation=_recommendation(),
            other_candidates=[],
            drift_findings=[],
            opportunity_findings=[],
            inconsistencies=[_inconsistency()],
            human_decisions_required=[],
            previous_snapshot=None,
            evaluation={"status": "INSUFFICIENT_EVIDENCE", "total_recommendations": 1},
            scanned_repos=["a"],
            skipped_repos=[],
        )
        kwargs.update(overrides)
        return render_brief(**kwargs)

    def test_contains_all_required_sections(self):
        text = self._render()
        for heading in [
            "## Overall Health",
            "## Projects",
            "## Most Important Recommendation",
            "## Critical Risks",
            "## Opportunities",
            "## Inconsistencies",
            "## Human Decisions Required",
            "## Trend",
        ]:
            self.assertIn(heading, text)

    def test_exactly_one_recommendation_shown_as_most_important(self):
        text = self._render()
        self.assertEqual(text.count("## Most Important Recommendation"), 1)
        self.assertIn("HQ-0001", text)

    def test_handles_no_recommendation_gracefully(self):
        text = self._render(top_recommendation=None)
        self.assertIn("INSUFFICIENT EVIDENCE", text)

    def test_never_claims_a_single_aggregate_across_projects(self):
        # Overall Health is its own explicit, documented metric — this
        # just guards against a second, undocumented number sneaking in.
        text = self._render()
        self.assertEqual(text.count("Overall Health"), 2)  # heading + trend line

    def test_inconsistency_shows_all_four_required_fields(self):
        text = self._render()
        self.assertIn("[Governance Issue]", text)
        self.assertIn("Affected artifact:", text)
        self.assertIn("Observed evidence:", text)
        self.assertIn("Operational impact:", text)
        self.assertIn("Recommended future action:", text)

    def test_no_inconsistencies_is_reported_explicitly(self):
        text = self._render(inconsistencies=[])
        self.assertIn("(none this run)", text)


if __name__ == "__main__":
    unittest.main()
