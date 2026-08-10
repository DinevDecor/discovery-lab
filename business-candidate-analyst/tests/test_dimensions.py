import _pathsetup  # noqa: F401
import unittest

from business_candidate_analyst.config import load_thresholds
from business_candidate_analyst.models import EVIDENCED, INSUFFICIENT_DATA
from business_candidate_analyst import dimensions as d


def obs(**kw):
    base = {"observation_id": "OBS-x", "source": "test", "url": "http://x", "process": "", "pain": "",
            "current_carrier": "", "failure_mode": "", "hidden_function_hint": "", "evidence_quote": "",
            "confidence": 0.8}
    base.update(kw)
    return base


class DimensionTests(unittest.TestCase):
    def setUp(self):
        self.th = load_thresholds()

    def test_underlying_job_or_problem_insufficient_when_empty(self):
        r = d.underlying_job_or_problem([obs(hidden_function_hint="")])
        self.assertEqual(r.status, INSUFFICIENT_DATA)

    def test_underlying_job_or_problem_evidenced(self):
        r = d.underlying_job_or_problem([obs(hidden_function_hint="no visibility into cost")])
        self.assertEqual(r.status, EVIDENCED)
        self.assertEqual(r.evidence, ["OBS-x"])

    def test_pain_severity_severe_on_strong_marker(self):
        r = d.pain_severity([obs(pain="cannot recover the lost funds")], self.th)
        self.assertEqual((r.status, r.value), (EVIDENCED, "SEVERE"))

    def test_pain_severity_moderate_on_moderate_marker(self):
        r = d.pain_severity([obs(pain="this requires a tedious manual workaround")], self.th)
        self.assertEqual((r.status, r.value), (EVIDENCED, "MODERATE"))

    def test_pain_severity_low_when_only_plain_text(self):
        r = d.pain_severity([obs(pain="the button is a different color than expected")], self.th)
        self.assertEqual((r.status, r.value), (EVIDENCED, "LOW"))

    def test_pain_severity_insufficient_when_no_pain_text(self):
        r = d.pain_severity([obs(pain="")], self.th)
        self.assertEqual(r.status, INSUFFICIENT_DATA)

    def test_economic_consequence_requires_marker(self):
        self.assertEqual(d.economic_consequence([obs(pain="no relevant text")], self.th).status,
                          INSUFFICIENT_DATA)
        self.assertEqual(d.economic_consequence([obs(pain="the bill and budget overran")], self.th).status,
                          EVIDENCED)

    def test_frequency_requires_repetition_marker(self):
        self.assertEqual(d.frequency([obs(pain="a one-time event")], self.th).status, INSUFFICIENT_DATA)
        self.assertEqual(d.frequency([obs(pain="this happens again every reset")], self.th).status, EVIDENCED)

    def test_identifiable_buyer(self):
        self.assertEqual(d.identifiable_buyer([obs(process="developers face this")], self.th).status, EVIDENCED)
        self.assertEqual(d.identifiable_buyer([obs(process="a satellite passes overhead")], self.th).status,
                          INSUFFICIENT_DATA)

    def test_current_workaround(self):
        self.assertEqual(d.current_workaround([obs(current_carrier="")]).status, INSUFFICIENT_DATA)
        self.assertEqual(d.current_workaround([obs(current_carrier="a spreadsheet")]).status, EVIDENCED)

    def test_why_solutions_fail(self):
        self.assertEqual(d.why_solutions_fail([obs(failure_mode="")]).status, INSUFFICIENT_DATA)
        self.assertEqual(d.why_solutions_fail([obs(failure_mode="vendor cannot verify usage")]).status, EVIDENCED)

    def test_potential_product_function_is_framing_only(self):
        r = d.potential_product_function([obs(hidden_function_hint="a cost visibility layer")])
        self.assertEqual(r.status, EVIDENCED)
        self.assertIn("FRAMING ONLY", r.note)

    def test_willingness_to_pay_requires_money_already_spent(self):
        self.assertEqual(d.willingness_to_pay([obs(pain="inference is costly to run")], self.th).status,
                          INSUFFICIENT_DATA, "cost existing is not the same as money already committed")
        self.assertEqual(d.willingness_to_pay([obs(pain="I purchased credits and they vanished")], self.th).status,
                          EVIDENCED)

    def test_scalability_requires_multi_source_and_multi_vendor(self):
        single = [obs(source="hacker_news", process="openai users hit this")]
        self.assertEqual(d.scalability(single, self.th).status, INSUFFICIENT_DATA)
        multi = [
            obs(source="hacker_news", process="openai users hit this"),
            obs(source="lobsters", process="anthropic users hit this too"),
        ]
        self.assertEqual(d.scalability(multi, self.th).status, EVIDENCED)

    def test_independent_observation_count_flags_shared_urls(self):
        rows = [obs(observation_id="A", url="http://same"), obs(observation_id="B", url="http://same")]
        r = d.independent_observation_count(rows)
        self.assertEqual(r.value["observation_count"], 2)
        self.assertEqual(r.value["distinct_urls"], 1)
        self.assertIn("multiple extractions", r.note)

    def test_contradictory_evidence_none_observed_by_default(self):
        r = d.contradictory_evidence([obs(pain="a real problem")], self.th)
        self.assertEqual((r.status, r.value), (EVIDENCED, "none_observed"))

    def test_contradictory_evidence_flags_marker(self):
        r = d.contradictory_evidence([obs(pain="actually this works fine now")], self.th)
        self.assertEqual((r.status, r.value), (EVIDENCED, "contradiction_present"))

    def test_confidence_quality_bucketing(self):
        self.assertEqual(d.confidence_quality([obs(confidence=0.9)]).value["bucket"], "HIGH")
        self.assertEqual(d.confidence_quality([obs(confidence=0.6)]).value["bucket"], "MODERATE")
        self.assertEqual(d.confidence_quality([obs(confidence=0.2)]).value["bucket"], "LOW")

    def test_assess_all_covers_every_required_dimension(self):
        result = d.assess_all([obs(process="developers", current_carrier="manual review",
                                    failure_mode="vendor opaque", hidden_function_hint="no visibility")], self.th)
        expected = {
            "underlying_job_or_problem", "pain_severity", "economic_consequence", "frequency",
            "identifiable_buyer", "current_workaround", "why_solutions_fail", "potential_product_function",
            "willingness_to_pay", "scalability", "evidence_diversity", "independent_observation_count",
            "contradictory_evidence", "confidence_quality",
        }
        self.assertEqual(set(result.keys()), expected)


if __name__ == "__main__":
    unittest.main()
