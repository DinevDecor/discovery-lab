"""Task Sec 14: 'duplicate IDs are idempotent or rejected safely',
'T0 evidence cannot be mutated by resolution', 'Resolution references
existing prospective case' (the cross-reference check itself lives in
the CLI - see test_cli.py - because CaseLedger/ResolutionLedger are
deliberately two independent files with no read dependency on each
other at the storage layer; this file proves that independence itself)."""

import _pathsetup  # noqa: F401
import json
import os
import tempfile
import unittest

from prospective_ground_truth.identity import make_prospective_case_id, make_resolution_id
from prospective_ground_truth.ledger import CaseLedger, ResolutionLedger, derive_status, rebuild_snapshot
from prospective_ground_truth.models import (
    ExpectedResolution,
    ExpectedResolutionWindow,
    OUTCOME_EXPIRED_UNRESOLVED,
    OUTCOME_INVALIDATED,
    OUTCOME_POSITIVE,
    ProspectiveCase,
    RESOLVER_HUMAN,
    Resolution,
    T0EvidenceItem,
    T0Freeze,
)
from prospective_ground_truth.packet import compute_packet_sha256

DOMAIN = "permits"
PROPOSITION = "Will regulator X approve permit Y by 2026-09-15?"
T0_CUTOFF = "2026-08-15"
CASE_ID = make_prospective_case_id(DOMAIN, PROPOSITION, T0_CUTOFF)


def _case(**overrides):
    evidence = overrides.pop("evidence", [T0EvidenceItem(
        artifact_id="EV-1", citation="Official filing portal", source_url="https://example.gov/1",
        captured_at="2026-08-10", quote_or_summary="Application submitted.")])
    t0 = T0Freeze(t0_cutoff=T0_CUTOFF, evidence=evidence, packet_sha256=compute_packet_sha256(T0_CUTOFF, evidence))
    er = ExpectedResolution(resolution_question="Will regulator X approve permit Y?",
                             expected_resolution_window=ExpectedResolutionWindow(earliest="2026-09-01",
                                                                                  latest="2026-09-30"),
                             resolution_sources_expected=["regulator X official register"],
                             positive_condition="Regulator publishes approval.",
                             negative_condition="Regulator publishes refusal.",
                             ambiguous_condition="Deadline passes, no status available.")
    base = dict(prospective_case_id=CASE_ID, source_case_id=None, created_at="2026-08-15T00:00:00Z",
                domain=DOMAIN, proposition=PROPOSITION, decision_relevance="Gates construction start.",
                t0=t0, expected_resolution=er)
    base.update(overrides)
    return ProspectiveCase(**base)


def _resolution(outcome=OUTCOME_POSITIVE, resolved_at="2026-09-10", **overrides):
    base = dict(resolution_id=make_resolution_id(CASE_ID, outcome, resolved_at), prospective_case_id=CASE_ID,
                resolved_at=resolved_at, outcome=outcome, t1_evidence_artifact_ids=["EV-T1-1"],
                authoritative_source_type="regulator official publication",
                resolution_rationale="Regulator X published a decision.", resolver_type=RESOLVER_HUMAN,
                created_at=resolved_at + "T00:00:00Z")
    base.update(overrides)
    return Resolution(**base)


class _TmpDirTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cases_path = os.path.join(self._tmp.name, "cases.jsonl")
        self.resolutions_path = os.path.join(self._tmp.name, "resolutions.jsonl")

    def tearDown(self):
        self._tmp.cleanup()


class CaseLedgerIdempotencyTests(_TmpDirTestCase):
    def test_append_writes_one_line(self):
        ledger = CaseLedger(self.cases_path)
        self.assertTrue(ledger.append(_case()))
        with open(self.cases_path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)

    def test_duplicate_registration_is_idempotent_not_a_second_line(self):
        ledger = CaseLedger(self.cases_path)
        case = _case()
        self.assertTrue(ledger.append(case))
        self.assertFalse(ledger.append(case))
        with open(self.cases_path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)

    def test_known_ids_survive_reload_from_disk(self):
        ledger = CaseLedger(self.cases_path)
        case = _case()
        ledger.append(case)
        reopened = CaseLedger(self.cases_path)
        self.assertTrue(reopened.has(case.prospective_case_id))


class ResolutionLedgerIdempotencyTests(_TmpDirTestCase):
    def test_append_writes_one_line(self):
        ledger = ResolutionLedger(self.resolutions_path)
        self.assertTrue(ledger.append(_resolution()))
        with open(self.resolutions_path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)

    def test_duplicate_resolution_is_idempotent(self):
        ledger = ResolutionLedger(self.resolutions_path)
        r = _resolution()
        self.assertTrue(ledger.append(r))
        self.assertFalse(ledger.append(r))
        with open(self.resolutions_path, encoding="utf-8") as f:
            self.assertEqual(len([l for l in f if l.strip()]), 1)


class T0NeverMutatedByResolutionTests(_TmpDirTestCase):
    """Task Sec 5/14: appending a Resolution must not be able to touch a
    case's frozen T0 content, structurally - proven here by checking the
    case's raw ledger line is byte-identical before and after a
    resolution is appended (two independent files, two independent
    ledger objects)."""

    def test_case_ledger_file_is_untouched_by_resolving_the_case(self):
        case_ledger = CaseLedger(self.cases_path)
        case_ledger.append(_case())
        with open(self.cases_path, encoding="utf-8") as f:
            before = f.read()

        resolution_ledger = ResolutionLedger(self.resolutions_path)
        resolution_ledger.append(_resolution())

        with open(self.cases_path, encoding="utf-8") as f:
            after = f.read()
        self.assertEqual(before, after)

    def test_resolution_ledger_append_never_opens_the_cases_path(self):
        """Structural proof at the source level: ResolutionLedger.append
        never references the cases ledger path or filename anywhere in
        its own code."""
        import inspect

        from prospective_ground_truth.ledger import ResolutionLedger as RL
        source = inspect.getsource(RL.append)
        self.assertNotIn("cases_path", source)
        self.assertNotIn("cases.jsonl", source)


class DeriveStatusTests(unittest.TestCase):
    def _case_dict(self):
        return _case().to_dict()

    def test_no_resolution_before_window_is_open(self):
        self.assertEqual(derive_status(self._case_dict(), [], as_of_date="2026-08-20"), "OPEN")

    def test_no_resolution_after_window_opens_is_awaiting_outcome(self):
        self.assertEqual(derive_status(self._case_dict(), [], as_of_date="2026-09-05"), "AWAITING_OUTCOME")

    def test_positive_resolution_is_resolved(self):
        r = _resolution(outcome=OUTCOME_POSITIVE).to_dict()
        self.assertEqual(derive_status(self._case_dict(), [r]), "RESOLVED")

    def test_expired_unresolved_resolution_is_expired_unresolved_status(self):
        r = _resolution(outcome=OUTCOME_EXPIRED_UNRESOLVED, resolved_at="2026-09-30",
                         t1_evidence_artifact_ids=[], authoritative_source_type="",
                         resolution_rationale="Checked, nothing published.").to_dict()
        self.assertEqual(derive_status(self._case_dict(), [r]), "EXPIRED_UNRESOLVED")

    def test_invalidated_resolution_is_invalidated_status(self):
        r = _resolution(outcome=OUTCOME_INVALIDATED, resolved_at="2026-08-20",
                         t1_evidence_artifact_ids=[], authoritative_source_type="",
                         resolution_rationale="T0 evidence found defective.").to_dict()
        self.assertEqual(derive_status(self._case_dict(), [r]), "INVALIDATED")


class RebuildSnapshotTests(_TmpDirTestCase):
    def test_snapshot_never_mutates_source_entries(self):
        case_entries = [_case().to_dict()]
        resolution_entries = [_resolution().to_dict()]
        snapshot = rebuild_snapshot(case_entries, resolution_entries, as_of_date="2026-09-15")
        self.assertEqual(snapshot["cases"][0]["status"], "RESOLVED")
        # original entries passed in are untouched (no "status" key injected into the source dict)
        self.assertNotIn("status", case_entries[0])


if __name__ == "__main__":
    unittest.main()
