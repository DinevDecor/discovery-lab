"""Acceptance test for Stage 1. Loads the real, already-committed
`constraint-archaeology-agents/data/anomalies.json` and
`business-candidate-analyst/data/candidates.json` - not fixtures, not
synthetic data - and proves the seven Stage 1 requirements against them:

  1. a real CA anomaly receives a stable case_id
  2. a real BCA candidate receives a stable case_id
  3. existing source ids remain intact
  4. provenance back to the original artifact is preserved
  5. no historical artifact is rewritten (read-only open, byte-for-byte
     unchanged before/after)
  6. re-running identity assignment produces exactly the same ids
  7. no fuzzy/semantic identity inference (covered structurally in
     test_identity.py; reconfirmed here by asserting two DIFFERENT real
     anomalies never collide)
"""

import _pathsetup  # noqa: F401
import hashlib
import json
import os
import unittest

from case_claim_kernel.wrap import (
    find_by_id,
    load_bca_candidates,
    load_ca_anomalies,
    wrap_bca_candidate,
    wrap_ca_anomaly,
)
from case_claim_kernel.envelope import build_case_envelope, build_claim_envelope
from case_claim_kernel.identity import make_case_id

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CA_ANOMALIES_PATH = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
BCA_CANDIDATES_PATH = os.path.join(REPO_ROOT, "business-candidate-analyst", "data", "candidates.json")

# Real ids known to exist in the committed data at the time this test was
# written (business-candidate-analyst/data/candidates.json's BC-0001
# lists ANOM-0001 among its own anomaly_ids, so these two real records
# are already linked by the existing pipeline - not a coincidence chosen
# for convenience).
REAL_ANOMALY_ID = "ANOM-0001"
REAL_CANDIDATE_ID = "BC-0001"


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


@unittest.skipUnless(os.path.exists(CA_ANOMALIES_PATH), f"{CA_ANOMALIES_PATH} not present")
@unittest.skipUnless(os.path.exists(BCA_CANDIDATES_PATH), f"{BCA_CANDIDATES_PATH} not present")
class WrapRealDataTests(unittest.TestCase):
    def setUp(self):
        self.ca_hash_before = _sha256_file(CA_ANOMALIES_PATH)
        self.bca_hash_before = _sha256_file(BCA_CANDIDATES_PATH)
        self.anomalies = load_ca_anomalies(CA_ANOMALIES_PATH)
        self.candidates = load_bca_candidates(BCA_CANDIDATES_PATH)
        self.assertGreater(len(self.anomalies), 0, "real anomalies.json must be non-empty for this test")
        self.assertGreater(len(self.candidates), 0, "real candidates.json must be non-empty for this test")

    def tearDown(self):
        # Requirement 5: no historical artifact is rewritten. If either
        # source file changed while this test ran, something opened it in
        # a writing mode - that is a hard failure of Stage 1's central
        # invariant, not a flaky test.
        self.assertEqual(self.ca_hash_before, _sha256_file(CA_ANOMALIES_PATH),
                          "anomalies.json changed during the test run - it must stay read-only")
        self.assertEqual(self.bca_hash_before, _sha256_file(BCA_CANDIDATES_PATH),
                          "candidates.json changed during the test run - it must stay read-only")

    def _real_anomaly(self):
        anomaly = find_by_id(self.anomalies, "anomaly_id", REAL_ANOMALY_ID)
        if anomaly is None:
            anomaly = self.anomalies[0]
        return anomaly

    def _real_candidate(self):
        candidate = find_by_id(self.candidates, "candidate_id", REAL_CANDIDATE_ID)
        if candidate is None:
            candidate = self.candidates[0]
        return candidate

    # -- requirement 1: real CA anomaly receives a stable case_id --------
    def test_real_ca_anomaly_receives_stable_case_id(self):
        anomaly = self._real_anomaly()
        case, claims = wrap_ca_anomaly(anomaly)
        self.assertTrue(case.case_id.startswith("case:"))
        expected = make_case_id("constraint_archaeology_agents", "anomaly", anomaly["anomaly_id"])
        self.assertEqual(case.case_id, expected)

    # -- requirement 2: real BCA candidate receives a stable case_id -----
    def test_real_bca_candidate_receives_stable_case_id(self):
        candidate = self._real_candidate()
        case, claims = wrap_bca_candidate(candidate)
        self.assertTrue(case.case_id.startswith("case:"))
        expected = make_case_id("business_candidate_analyst", "candidate", candidate["candidate_id"])
        self.assertEqual(case.case_id, expected)
        # BC-0001's real dimensions (14 named fields) must all survive as
        # Claims - not summarized, not dropped.
        self.assertEqual(len(claims), len(candidate.get("dimensions", {})))

    # -- requirement 3: existing source ids remain intact ----------------
    def test_source_ids_remain_intact(self):
        anomaly = self._real_anomaly()
        case, _ = wrap_ca_anomaly(anomaly)
        self.assertEqual(case.source_record_id, anomaly["anomaly_id"])

        candidate = self._real_candidate()
        bca_case, claims = wrap_bca_candidate(candidate)
        self.assertEqual(bca_case.source_record_id, candidate["candidate_id"])
        real_observation_ids = set(candidate.get("observation_ids", []))
        self.assertEqual(set(bca_case.source_evidence_ids), real_observation_ids)
        for claim in claims:
            dim = candidate["dimensions"][claim.name]
            self.assertEqual(set(claim.evidence), set(dim.get("evidence", [])))

    # -- requirement 4: provenance back to the original artifact ---------
    def test_provenance_preserved_to_original_artifact(self):
        anomaly = self._real_anomaly()
        case, _ = wrap_ca_anomaly(anomaly)
        self.assertEqual(case.derived_from, [anomaly["anomaly_id"]])
        envelope = build_case_envelope(case)
        self.assertEqual(envelope.derived_from, [anomaly["anomaly_id"]])

        candidate = self._real_candidate()
        bca_case, claims = wrap_bca_candidate(candidate)
        for claim in claims:
            claim_envelope = build_claim_envelope(claim)
            if claim.evidence:
                self.assertEqual(set(claim_envelope.derived_from), set(claim.evidence))
            else:
                # Empty evidence is a real, valid outcome for some real
                # BC-0001 dimensions (e.g. contradictory_evidence) - the
                # envelope must carry a truthful note instead of a
                # fabricated derived_from.
                self.assertEqual(claim_envelope.derived_from, [])
                self.assertTrue(claim_envelope.payload.get("provenance_note"))

    # -- requirement 6: re-running produces exactly the same ids ---------
    def test_rerun_produces_identical_ids(self):
        anomaly = self._real_anomaly()
        case1, claims1 = wrap_ca_anomaly(anomaly)
        case2, claims2 = wrap_ca_anomaly(anomaly)
        self.assertEqual(case1.case_id, case2.case_id)
        self.assertEqual([c.claim_id for c in claims1], [c.claim_id for c in claims2])

        candidate = self._real_candidate()
        bca1, bca_claims1 = wrap_bca_candidate(candidate)
        bca2, bca_claims2 = wrap_bca_candidate(candidate)
        self.assertEqual(bca1.case_id, bca2.case_id)
        self.assertEqual(sorted(c.claim_id for c in bca_claims1), sorted(c.claim_id for c in bca_claims2))

        # Re-loading the file fresh from disk (simulating a real separate
        # day's run, not just calling the function twice on one in-memory
        # object) must produce the same id too.
        reloaded = load_bca_candidates(BCA_CANDIDATES_PATH)
        candidate_reloaded = find_by_id(reloaded, "candidate_id", candidate["candidate_id"])
        bca3, _ = wrap_bca_candidate(candidate_reloaded)
        self.assertEqual(bca1.case_id, bca3.case_id)

    # -- requirement 7: no fuzzy/semantic identity across real records ---
    def test_two_different_real_anomalies_never_collide(self):
        distinct = self.anomalies[:25]
        case_ids = [wrap_ca_anomaly(a)[0].case_id for a in distinct]
        self.assertEqual(len(case_ids), len(set(case_ids)),
                          "two different real anomaly_ids produced the same case_id")

    def test_two_different_real_candidates_never_collide(self):
        distinct = self.candidates[:25]
        case_ids = [wrap_bca_candidate(c)[0].case_id for c in distinct]
        self.assertEqual(len(case_ids), len(set(case_ids)),
                          "two different real candidate_ids produced the same case_id")

    def test_envelopes_are_json_serializable_and_re_parse_identically(self):
        candidate = self._real_candidate()
        case, claims = wrap_bca_candidate(candidate)
        case_env = build_case_envelope(case)
        raw = json.dumps(case_env.to_dict(), sort_keys=True, default=str)
        reparsed = json.loads(raw)
        self.assertEqual(reparsed["artifact_id"], case.case_id)
        self.assertEqual(reparsed["payload"]["source_record_id"], candidate["candidate_id"])


if __name__ == "__main__":
    unittest.main()
