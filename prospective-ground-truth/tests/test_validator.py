import _pathsetup  # noqa: F401
import unittest

from prospective_ground_truth.identity import make_prospective_case_id, make_resolution_id
from prospective_ground_truth.models import (
    ExpectedResolution,
    ExpectedResolutionWindow,
    OUTCOME_AMBIGUOUS,
    OUTCOME_EXPIRED_UNRESOLVED,
    OUTCOME_INVALIDATED,
    OUTCOME_NEGATIVE,
    OUTCOME_POSITIVE,
    ProspectiveCase,
    RESOLVER_HUMAN,
    Resolution,
    T0EvidenceItem,
    T0Freeze,
)
from prospective_ground_truth.packet import compute_packet_sha256
from prospective_ground_truth.validator import validate_prospective_case, validate_resolution

DOMAIN = "permits"
PROPOSITION = "Will regulator X approve permit Y by 2026-09-15?"
T0_CUTOFF = "2026-08-15"


def _evidence(captured_at="2026-08-10"):
    return [T0EvidenceItem(artifact_id="EV-1", citation="Official filing portal",
                            source_url="https://example.gov/case/1", captured_at=captured_at,
                            quote_or_summary="Application submitted, docket #1234.")]


def _case(**overrides):
    evidence = overrides.pop("evidence", _evidence())
    t0_cutoff = overrides.pop("t0_cutoff", T0_CUTOFF)
    window = overrides.pop("window", ExpectedResolutionWindow(earliest="2026-09-01", latest="2026-09-30"))
    conditions = dict(positive_condition="Regulator publishes approval.",
                       negative_condition="Regulator publishes refusal or deadline passes with no approval.",
                       ambiguous_condition="Deadline passes with no authoritative status available.")
    conditions.update({k: overrides.pop(k) for k in list(overrides) if k in conditions})
    t0 = T0Freeze(t0_cutoff=t0_cutoff, evidence=evidence, packet_sha256=compute_packet_sha256(t0_cutoff, evidence))
    er = ExpectedResolution(resolution_question="Will regulator X approve permit Y?",
                             expected_resolution_window=window,
                             resolution_sources_expected=["regulator X official register"],
                             **conditions)
    base = dict(
        prospective_case_id=make_prospective_case_id(DOMAIN, PROPOSITION, t0_cutoff),
        source_case_id=None, created_at="2026-08-15T00:00:00Z", domain=DOMAIN, proposition=PROPOSITION,
        decision_relevance="Determines whether the site can begin construction.", t0=t0, expected_resolution=er,
    )
    base.update(overrides)
    return ProspectiveCase(**base)


def _resolution(**overrides):
    base = dict(
        resolution_id=make_resolution_id(make_prospective_case_id(DOMAIN, PROPOSITION, T0_CUTOFF),
                                          OUTCOME_POSITIVE, "2026-09-10"),
        prospective_case_id=make_prospective_case_id(DOMAIN, PROPOSITION, T0_CUTOFF),
        resolved_at="2026-09-10", outcome=OUTCOME_POSITIVE, t1_evidence_artifact_ids=["EV-T1-1"],
        authoritative_source_type="regulator official publication",
        resolution_rationale="Regulator X published approval notice #5678 on 2026-09-10.",
        resolver_type=RESOLVER_HUMAN, created_at="2026-09-10T00:00:00Z",
    )
    base.update(overrides)
    return Resolution(**base)


class ValidCaseTests(unittest.TestCase):
    def test_well_formed_case_has_no_violations(self):
        self.assertEqual(validate_prospective_case(_case()), [])


class PostT0EvidenceRejectionTests(unittest.TestCase):
    """Task Sec 14: 'no post-T0 evidence enters frozen packet'."""

    def test_evidence_captured_after_t0_cutoff_is_rejected(self):
        evidence = _evidence(captured_at="2026-08-20")  # after T0_CUTOFF 2026-08-15
        violations = validate_prospective_case(_case(evidence=evidence))
        self.assertTrue(any("AFTER" in v and "t0_cutoff" in v for v in violations))

    def test_evidence_captured_exactly_on_t0_cutoff_is_allowed(self):
        evidence = _evidence(captured_at=T0_CUTOFF)
        violations = validate_prospective_case(_case(evidence=evidence))
        self.assertEqual(violations, [])

    def test_empty_evidence_list_is_rejected(self):
        violations = validate_prospective_case(_case(evidence=[]))
        self.assertTrue(any("evidence must be non-empty" in v for v in violations))


class PacketHashConsistencyTests(unittest.TestCase):
    def test_tampered_packet_hash_is_rejected(self):
        case = _case()
        tampered_t0 = T0Freeze(t0_cutoff=case.t0.t0_cutoff, evidence=case.t0.evidence, packet_sha256="0" * 64)
        tampered = ProspectiveCase(**{**case.__dict__, "t0": tampered_t0})
        violations = validate_prospective_case(tampered)
        self.assertTrue(any("does not match the recomputed hash" in v for v in violations))


class ResolutionCriteriaPreregisteredTests(unittest.TestCase):
    """Task Sec 6/14: 'resolution criteria exist before resolution' -
    enforced here as 'a case is not even valid, let alone registerable,
    without all three conditions stated'."""

    def test_blank_positive_condition_is_rejected(self):
        violations = validate_prospective_case(_case(positive_condition=""))
        self.assertTrue(any("positive_condition" in v for v in violations))

    def test_blank_negative_condition_is_rejected(self):
        violations = validate_prospective_case(_case(negative_condition="  "))
        self.assertTrue(any("negative_condition" in v for v in violations))

    def test_blank_ambiguous_condition_is_rejected(self):
        violations = validate_prospective_case(_case(ambiguous_condition=""))
        self.assertTrue(any("ambiguous_condition" in v for v in violations))

    def test_resolution_window_before_t0_cutoff_is_rejected(self):
        window = ExpectedResolutionWindow(earliest="2026-08-01", latest="2026-08-10")  # before T0_CUTOFF
        violations = validate_prospective_case(_case(window=window))
        self.assertTrue(any("before t0_cutoff" in v for v in violations))


class CaseIdentityConsistencyTests(unittest.TestCase):
    def test_mismatched_prospective_case_id_is_rejected(self):
        case = _case()
        tampered = ProspectiveCase(**{**case.__dict__, "prospective_case_id": "pgt-case:wrong"})
        violations = validate_prospective_case(tampered)
        self.assertTrue(any("does not match the deterministic id" in v for v in violations))


class ResolverTypeNeverBareModelTests(unittest.TestCase):
    """Task Sec 8: 'Models are never resolution evidence.'"""

    def test_human_resolver_is_valid(self):
        self.assertEqual(validate_resolution(_resolution(resolver_type=RESOLVER_HUMAN)), [])

    def test_model_assisted_human_confirmed_is_valid(self):
        self.assertEqual(validate_resolution(_resolution(resolver_type="model_assisted_human_confirmed")), [])

    def test_bare_model_resolver_type_is_rejected(self):
        violations = validate_resolution(_resolution(resolver_type="model"))
        self.assertTrue(any("resolver_type" in v for v in violations))

    def test_pattern_actually_rejects_something(self):
        for bogus in ("claude", "gpt", "automated", "ai", ""):
            violations = validate_resolution(_resolution(resolver_type=bogus))
            self.assertTrue(violations, f"{bogus!r} should have been rejected")


class OutcomesRequiringEvidenceTests(unittest.TestCase):
    def test_positive_without_t1_evidence_is_rejected(self):
        violations = validate_resolution(_resolution(outcome=OUTCOME_POSITIVE, t1_evidence_artifact_ids=[]))
        self.assertTrue(any("t1_evidence_artifact_id" in v for v in violations))

    def test_negative_without_authoritative_source_is_rejected(self):
        violations = validate_resolution(_resolution(outcome=OUTCOME_NEGATIVE, authoritative_source_type=""))
        self.assertTrue(any("authoritative_source_type" in v for v in violations))

    def test_ambiguous_without_t1_evidence_is_rejected(self):
        violations = validate_resolution(_resolution(
            outcome=OUTCOME_AMBIGUOUS,
            resolution_id=make_resolution_id(make_prospective_case_id(DOMAIN, PROPOSITION, T0_CUTOFF),
                                              OUTCOME_AMBIGUOUS, "2026-09-10"),
            t1_evidence_artifact_ids=[]))
        self.assertTrue(any("t1_evidence_artifact_id" in v for v in violations))


class ExpiredAndInvalidatedAreNotForcedFalsificationTests(unittest.TestCase):
    """Task Sec 7/14: 'EXPIRED_UNRESOLVED is not falsification' - proven
    here as: EXPIRED_UNRESOLVED and INVALIDATED do NOT require
    t1_evidence_artifact_ids/authoritative_source_type the way a real
    POSITIVE/NEGATIVE/AMBIGUOUS claim about reality does; they only
    require a rationale explaining the absence."""

    def test_expired_unresolved_does_not_require_t1_evidence(self):
        violations = validate_resolution(_resolution(
            outcome=OUTCOME_EXPIRED_UNRESOLVED,
            resolution_id=make_resolution_id(make_prospective_case_id(DOMAIN, PROPOSITION, T0_CUTOFF),
                                              OUTCOME_EXPIRED_UNRESOLVED, "2026-09-30"),
            resolved_at="2026-09-30", t1_evidence_artifact_ids=[], authoritative_source_type="",
            resolution_rationale="Window closed 2026-09-30; checked regulator X's register, no decision published."))
        self.assertEqual(violations, [])

    def test_invalidated_does_not_require_t1_evidence(self):
        violations = validate_resolution(_resolution(
            outcome=OUTCOME_INVALIDATED,
            resolution_id=make_resolution_id(make_prospective_case_id(DOMAIN, PROPOSITION, T0_CUTOFF),
                                              OUTCOME_INVALIDATED, "2026-08-20"),
            resolved_at="2026-08-20", t1_evidence_artifact_ids=[], authoritative_source_type="",
            resolution_rationale="T0 evidence artifact EV-1 was later found to be a duplicate of an unrelated docket."))
        self.assertEqual(violations, [])

    def test_expired_unresolved_still_requires_a_rationale(self):
        violations = validate_resolution(_resolution(
            outcome=OUTCOME_EXPIRED_UNRESOLVED,
            resolution_id=make_resolution_id(make_prospective_case_id(DOMAIN, PROPOSITION, T0_CUTOFF),
                                              OUTCOME_EXPIRED_UNRESOLVED, "2026-09-30"),
            resolved_at="2026-09-30", t1_evidence_artifact_ids=[], authoritative_source_type="",
            resolution_rationale=""))
        self.assertTrue(any("resolution_rationale" in v for v in violations))


class UnknownOutcomeRejectedTests(unittest.TestCase):
    def test_unknown_outcome_value_is_rejected(self):
        violations = validate_resolution(_resolution(outcome="MAYBE"))
        self.assertTrue(any("outcome" in v for v in violations))


if __name__ == "__main__":
    unittest.main()
