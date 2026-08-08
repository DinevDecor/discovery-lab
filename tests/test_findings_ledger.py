"""
Offline tests for findings_ledger. No network, no model calls, no clock
dependence (recorded_at is injected where it matters).

Covers the ten required cases except #10 ("existing pipeline tests still
pass"), which cannot be run here because the repository is not reachable
from this environment. See the delivery note.
"""

import json
import os
import tempfile

try:
    import pytest
except ImportError:
    pytest = None

from findings_ledger import (
    Finding, FindingsLedger, FindingValidationError,
    build_anomaly, build_mechanism_profile,
    build_same_mechanism_decision, build_ca_evaluation,
    make_finding_id, utc_now_iso,
)

FIXED_TS = "2026-08-08T12:00:00Z"


def _ledger(tmpdir, name="findings.jsonl"):
    return FindingsLedger(os.path.join(tmpdir, name))


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def test_append_first_finding():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        f = build_anomaly(anomaly_id="an-1", observation_ids=["obs-1", "obs-2"],
                          payload={"summary": "x"}, analyst_version="0.3.0",
                          recorded_at=FIXED_TS)
        assert led.append(f) is True
        rows = _read(led.path)
        assert len(rows) == 1
        assert rows[0]["kind"] == "anomaly"
        assert rows[0]["origin"] == "generated"
        assert rows[0]["derived_from"] == ["obs-1", "obs-2"]
        assert rows[0]["method_version"] is None


def test_second_distinct_finding_appends():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        a = build_anomaly(anomaly_id="an-1", observation_ids=["obs-1"],
                          payload={}, analyst_version="0.3.0", recorded_at=FIXED_TS)
        b = build_anomaly(anomaly_id="an-2", observation_ids=["obs-2"],
                          payload={}, analyst_version="0.3.0", recorded_at=FIXED_TS)
        assert led.append(a) and led.append(b)
        assert len(_read(led.path)) == 2


def test_duplicate_finding_id_does_not_append():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        f = build_anomaly(anomaly_id="an-1", observation_ids=["obs-1"],
                          payload={}, analyst_version="0.3.0", recorded_at=FIXED_TS)
        assert led.append(f) is True
        assert led.append(f) is False
        assert len(_read(led.path)) == 1


def test_existing_contents_are_never_rewritten():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "findings.jsonl")
        sentinel = {"finding_id": "pre-existing:1", "kind": "anomaly",
                    "note": "written by an older writer"}
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(sentinel) + "\n")
        raw_before = open(path, encoding="utf-8").read()
        led = FindingsLedger(path)
        assert led.has("pre-existing:1")
        led.append(build_anomaly(anomaly_id="an-1", observation_ids=["obs-1"],
                                 payload={}, analyst_version="0.3.0",
                                 recorded_at=FIXED_TS))
        raw_after = open(path, encoding="utf-8").read()
        assert raw_after.startswith(raw_before)
        assert len(_read(path)) == 2


def test_missing_provenance_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        f = Finding(finding_id=make_finding_id("anomaly", {"anomaly_id": "an-x"}, []),
                    kind="anomaly", recorded_at=FIXED_TS, derived_from=[],
                    analyst="anomaly_clusterer", analyst_version="0.3.0",
                    method_version=None, payload={})
        try:
            led.append(f)
            raise AssertionError("expected FindingValidationError")
        except FindingValidationError as exc:
            assert "derived_from" in str(exc)
        assert not os.path.exists(led.path)

        f2 = Finding(finding_id=make_finding_id("anomaly", {"anomaly_id": "an-y"}, []),
                     kind="anomaly", recorded_at=FIXED_TS, derived_from=[],
                     analyst="anomaly_clusterer", analyst_version="0.3.0",
                     method_version=None,
                     payload={"provenance_note": "legacy record predates observation ids"})
        assert led.append(f2, allow_empty_provenance=True) is True

        f3 = Finding(finding_id=make_finding_id("anomaly", {"anomaly_id": "an-z"}, []),
                     kind="anomaly", recorded_at=FIXED_TS, derived_from=[],
                     analyst="anomaly_clusterer", analyst_version="0.3.0",
                     method_version=None, payload={})
        try:
            led.append(f3, allow_empty_provenance=True)
            raise AssertionError("expected FindingValidationError")
        except FindingValidationError as exc:
            assert "provenance_note" in str(exc)


def _decision(verdict, edge, pair=("an-1", "an-2")):
    return build_same_mechanism_decision(
        left_id=pair[0], right_id=pair[1], verdict=verdict, edge=edge,
        reasons=["failure_class differs: conflict vs absence"],
        counterfactuals=[{"repair_from": pair[0], "applied_to": pair[1],
                          "removes_failure": False, "reason": "does not transfer"}],
        short_circuited=True, gate_version="0.1.0",
        derived_from=[f"mechanism_profile:{pair[0]}", f"mechanism_profile:{pair[1]}"],
        analyst_version="0.1.0", recorded_at=FIXED_TS)


def test_related_distinct_is_persisted():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        assert led.append(_decision("different_mechanisms", "related_distinct")) is True
        row = _read(led.path)[0]
        assert row["payload"]["edge"] == "related_distinct"
        assert row["payload"]["short_circuited"] is True
        assert row["payload"]["gate_version"] == "0.1.0"
        assert row["payload"]["counterfactuals"][0]["removes_failure"] is False


def test_unresolved_is_persisted():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        assert led.append(_decision("insufficient_data", "unresolved")) is True
        assert _read(led.path)[0]["payload"]["edge"] == "unresolved"


def test_all_three_gate_outcomes_coexist():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        led.append(_decision("same_mechanism", "merged", ("a", "b")))
        led.append(_decision("different_mechanisms", "related_distinct", ("c", "d")))
        led.append(_decision("insufficient_data", "unresolved", ("e", "f")))
        edges = {r["payload"]["edge"] for r in _read(led.path)}
        assert edges == {"merged", "related_distinct", "unresolved"}


def test_ca_finding_carries_method_version():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        f = build_ca_evaluation(subject_id="an-1",
                                evidence_ids=["obs-1", "anomaly:an-1"],
                                payload={"mechanism_verdict": "fail",
                                         "capture_verdict": "fail",
                                         "classification": "reject"},
                                adapter_version="0.1.0", recorded_at=FIXED_TS)
        led.append(f)
        row = _read(led.path)[0]
        assert row["method_version"] == "0.5"
        assert row["analyst"] == "constraint_archaeology"
        assert row["analyst_version"] == "0.1.0"


def test_ca_finding_with_wrong_method_version_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        bad = Finding(finding_id="ca_evaluation:x", kind="ca_evaluation",
                      recorded_at=FIXED_TS, derived_from=["obs-1"],
                      analyst="constraint_archaeology", analyst_version="0.1.0",
                      method_version="0.6", payload={})
        try:
            led.append(bad)
            raise AssertionError("expected FindingValidationError")
        except FindingValidationError as exc:
            assert "0.5" in str(exc)


def test_retry_of_same_logical_run_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "findings.jsonl")
        def run(ts):
            led = FindingsLedger(path)
            batch = [
                build_anomaly(anomaly_id="an-1", observation_ids=["obs-1", "obs-2"],
                              payload={"summary": "x"}, analyst_version="0.3.0",
                              recorded_at=ts),
                _decision("different_mechanisms", "related_distinct"),
                build_ca_evaluation(subject_id="an-1", evidence_ids=["obs-1"],
                                    payload={"classification": "watch"},
                                    adapter_version="0.1.0", recorded_at=ts),
            ]
            return led.append_many(batch)
        assert run("2026-08-08T12:00:00Z") == 3
        assert run("2026-08-08T18:30:00Z") == 0
        assert len(_read(path)) == 3


def test_finding_id_ignores_recorded_at_but_separates_kinds():
    a = build_anomaly(anomaly_id="an-1", observation_ids=["obs-1"], payload={},
                      analyst_version="0.3.0", recorded_at="2026-01-01T00:00:00Z")
    b = build_anomaly(anomaly_id="an-1", observation_ids=["obs-1"], payload={},
                      analyst_version="0.3.0", recorded_at="2026-12-31T00:00:00Z")
    assert a.finding_id == b.finding_id
    same_inputs_other_kind = make_finding_id("mechanism_profile",
                                             {"anomaly_id": "an-1"}, ["obs-1"])
    assert same_inputs_other_kind != a.finding_id
    assert a.finding_id.startswith("anomaly:")


def test_pair_order_does_not_change_decision_id():
    d1 = _decision("different_mechanisms", "related_distinct", ("an-1", "an-2"))
    d2 = _decision("different_mechanisms", "related_distinct", ("an-2", "an-1"))
    assert d1.finding_id == d2.finding_id


def test_origin_must_be_generated():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        bad = Finding(finding_id="anomaly:x", kind="anomaly", recorded_at=FIXED_TS,
                      derived_from=["obs-1"], analyst="anomaly_clusterer",
                      analyst_version="0.3.0", method_version=None,
                      payload={}, origin="captured")
        try:
            led.append(bad)
            raise AssertionError("expected FindingValidationError")
        except FindingValidationError as exc:
            assert "generated" in str(exc)


def test_unknown_kind_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger(tmp)
        bad = Finding(finding_id="expectation:x", kind="expectation",
                      recorded_at=FIXED_TS, derived_from=["obs-1"],
                      analyst="whoever", analyst_version="0.1.0",
                      method_version=None, payload={})
        try:
            led.append(bad)
            raise AssertionError("expected FindingValidationError")
        except FindingValidationError as exc:
            assert "unknown kind" in str(exc)


def test_corrupt_line_is_skipped_not_repaired():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "findings.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("{not json}\n")
        before = open(path, encoding="utf-8").read()
        led = FindingsLedger(path)
        led.append(build_anomaly(anomaly_id="an-1", observation_ids=["obs-1"],
                                 payload={}, analyst_version="0.3.0",
                                 recorded_at=FIXED_TS))
        after = open(path, encoding="utf-8").read()
        assert after.startswith(before)


def _run_standalone():
    import traceback
    names = sorted(n for n, v in globals().items()
                   if n.startswith("test_") and callable(v))
    failed = 0
    for name in names:
        try:
            globals()[name]()
            print(f"PASS  {name}")
        except Exception:
            failed += 1
            print(f"FAIL  {name}")
            traceback.print_exc()
    print(f"\n{len(names) - failed}/{len(names)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if pytest is not None:
        raise SystemExit(pytest.main([__file__, "-q"]))
    raise SystemExit(_run_standalone())
