import _pathsetup  # noqa: F401
import unittest

from headquarters.inconsistency import Category, classify, classify_all
from headquarters.models import Confidence, Evidence, Finding


def _finding(category, is_opportunity=False) -> Finding:
    return Finding(
        finding_id="f1",
        category=category,
        title="title",
        description="description",
        confidence=Confidence.MISMATCH,
        evidence=[Evidence("repo", "detail")],
        affected=["repo"],
        is_opportunity=is_opportunity,
    )


class TestClassify(unittest.TestCase):
    def test_duplicate_adr_is_governance_issue(self):
        result = classify(_finding("duplicated_infrastructure"))
        self.assertEqual(result.category, Category.GOVERNANCE_ISSUE)

    def test_stale_adr_is_documentation_issue(self):
        result = classify(_finding("stale_specification"))
        self.assertEqual(result.category, Category.DOCUMENTATION_ISSUE)

    def test_registry_gap_is_governance_issue(self):
        result = classify(_finding("governance_inconsistency"))
        self.assertEqual(result.category, Category.GOVERNANCE_ISSUE)

    def test_decision_backlog_is_governance_issue(self):
        result = classify(_finding("decision_backlog"))
        self.assertEqual(result.category, Category.GOVERNANCE_ISSUE)

    def test_possibly_abandoned_is_unknown(self):
        result = classify(_finding("possibly_abandoned_initiative"))
        self.assertEqual(result.category, Category.UNKNOWN)

    def test_data_quality_check_is_data_quality_issue(self):
        result = classify(_finding("data_quality"))
        self.assertEqual(result.category, Category.DATA_QUALITY_ISSUE)

    def test_unmapped_category_falls_back_to_unknown_not_a_crash(self):
        result = classify(_finding("some_future_check_category"))
        self.assertEqual(result.category, Category.UNKNOWN)

    def test_every_inconsistency_carries_all_four_required_fields(self):
        result = classify(_finding("duplicated_infrastructure"))
        self.assertTrue(result.affected_artifact)
        self.assertTrue(result.observed_evidence)
        self.assertTrue(result.operational_impact)
        self.assertTrue(result.recommended_future_action)


class TestClassifyAll(unittest.TestCase):
    def test_opportunities_are_never_classified_as_inconsistencies(self):
        findings = [_finding("duplicated_infrastructure"), _finding("reusable_component", is_opportunity=True)]
        result = classify_all(findings)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].category, Category.GOVERNANCE_ISSUE)

    def test_empty_input_yields_empty_output(self):
        self.assertEqual(classify_all([]), [])


if __name__ == "__main__":
    unittest.main()
