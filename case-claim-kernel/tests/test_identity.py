import _pathsetup  # noqa: F401
import unittest

from case_claim_kernel.identity import make_artifact_id, make_case_id, make_claim_id, stable_evidence_ids


class MakeCaseIdTests(unittest.TestCase):
    def test_deterministic_across_repeated_calls(self):
        a = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0001")
        b = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0001")
        self.assertEqual(a, b)

    def test_different_source_ids_produce_different_case_ids(self):
        a = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0001")
        b = make_case_id("constraint_archaeology_agents", "anomaly", "ANOM-0002")
        self.assertNotEqual(a, b)

    def test_different_source_systems_produce_different_case_ids(self):
        """Same literal id string in two different source systems must
        never collide - identity is scoped by (system, type, id), not by
        id alone."""
        a = make_case_id("constraint_archaeology_agents", "anomaly", "X-0001")
        b = make_case_id("business_candidate_analyst", "candidate", "X-0001")
        self.assertNotEqual(a, b)

    def test_case_id_has_stable_prefix(self):
        self.assertTrue(make_case_id("s", "t", "id").startswith("case:"))

    def test_case_id_ignores_content_not_passed_to_it(self):
        """There is no parameter here for status/dimensions/anything
        content-shaped - the function signature itself is the proof that
        identity cannot depend on content that changes between runs."""
        import inspect
        params = list(inspect.signature(make_case_id).parameters)
        self.assertEqual(params, ["source_system", "source_record_type", "source_record_id"])


class MakeClaimIdTests(unittest.TestCase):
    def test_deterministic_across_repeated_calls(self):
        case_id = make_case_id("s", "t", "id")
        a = make_claim_id(case_id, "willingness_to_pay")
        b = make_claim_id(case_id, "willingness_to_pay")
        self.assertEqual(a, b)

    def test_different_names_produce_different_claim_ids(self):
        case_id = make_case_id("s", "t", "id")
        a = make_claim_id(case_id, "willingness_to_pay")
        b = make_claim_id(case_id, "pain_severity")
        self.assertNotEqual(a, b)

    def test_same_name_under_different_cases_does_not_collide(self):
        case_a = make_case_id("s", "t", "id-a")
        case_b = make_case_id("s", "t", "id-b")
        self.assertNotEqual(make_claim_id(case_a, "pain_severity"), make_claim_id(case_b, "pain_severity"))

    def test_claim_id_has_stable_prefix(self):
        self.assertTrue(make_claim_id("case:abc", "x").startswith("claim:"))

    def test_claim_id_ignores_content_not_passed_to_it(self):
        """No status/value/evidence parameter - a Claim's identity must
        survive a later re-run that revises its content."""
        import inspect
        params = list(inspect.signature(make_claim_id).parameters)
        self.assertEqual(params, ["case_id", "name"])


class MakeArtifactIdTests(unittest.TestCase):
    def test_artifact_id_is_exactly_the_identity_id(self):
        self.assertEqual(make_artifact_id("case:abc123"), "case:abc123")
        self.assertEqual(make_artifact_id("claim:def456"), "claim:def456")


class StableEvidenceIdsTests(unittest.TestCase):
    def test_deduplicates_and_sorts(self):
        self.assertEqual(stable_evidence_ids(["b", "a", "b"]), ["a", "b"])

    def test_empty_stays_empty(self):
        self.assertEqual(stable_evidence_ids([]), [])

    def test_does_not_drop_or_rewrite_ids(self):
        ids = ["OBS-3", "OBS-1", "OBS-2"]
        self.assertEqual(set(stable_evidence_ids(ids)), set(ids))


if __name__ == "__main__":
    unittest.main()
