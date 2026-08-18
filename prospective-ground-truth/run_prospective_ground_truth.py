"""CLI entrypoint for the Prospective Ground-Truth Stream's three manual
roles: `register` (freeze T0 + pre-register resolution criteria in one
atomic step - task Sec 5/6, they cannot be split across two commands
without risking a case existing with unregistered criteria), `resolve`
(append a T1 Resolution, never touching the case's frozen T0 content),
and `report` (read-only: print the current derived-status snapshot).

No scheduler, no cron entry, no GitHub Actions workflow calls this file -
task Sec 9: "initial intake must remain manual." This script exists to be
run by a human, once per case, when there is a new case or a new outcome
to record - exactly the shape `constraint_change_observatory`'s own CLI
already established for the same reason.

No model client is imported anywhere in this file or anything it
imports - task Sec 8/15: this package cannot call a model even if someone
wanted it to.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from prospective_ground_truth.identity import make_prospective_case_id, make_resolution_id  # noqa: E402
from prospective_ground_truth.ledger import CaseLedger, ResolutionLedger, persist_snapshot, rebuild_snapshot  # noqa: E402
from prospective_ground_truth.models import (  # noqa: E402
    ExpectedResolution,
    ExpectedResolutionWindow,
    ProspectiveCase,
    Resolution,
    T0EvidenceItem,
    T0Freeze,
)
from prospective_ground_truth.packet import compute_packet_sha256  # noqa: E402
from prospective_ground_truth.validator import ValidationError  # noqa: E402

DEFAULT_CASES_LEDGER = os.path.join(ROOT, "data", "cases.jsonl")
DEFAULT_RESOLUTIONS_LEDGER = os.path.join(ROOT, "data", "resolutions.jsonl")
DEFAULT_SNAPSHOT = os.path.join(ROOT, "data", "cases.json")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cmd_register(args: argparse.Namespace) -> None:
    raw = _load_json(args.input)

    evidence = [T0EvidenceItem(
        artifact_id=e["artifact_id"], citation=e["citation"], source_url=e.get("source_url", ""),
        captured_at=e["captured_at"], quote_or_summary=e["quote_or_summary"],
    ) for e in raw["t0_evidence"]]
    t0_cutoff = raw["t0_cutoff"]
    packet_sha256 = compute_packet_sha256(t0_cutoff, evidence)
    t0 = T0Freeze(t0_cutoff=t0_cutoff, evidence=evidence, packet_sha256=packet_sha256)

    window_raw = raw["expected_resolution_window"]
    window = ExpectedResolutionWindow(earliest=window_raw["earliest"], latest=window_raw["latest"])
    expected_resolution = ExpectedResolution(
        resolution_question=raw["resolution_question"],
        expected_resolution_window=window,
        resolution_sources_expected=list(raw["resolution_sources_expected"]),
        positive_condition=raw["positive_condition"],
        negative_condition=raw["negative_condition"],
        ambiguous_condition=raw["ambiguous_condition"],
    )

    prospective_case_id = make_prospective_case_id(raw["domain"], raw["proposition"], t0_cutoff)
    case = ProspectiveCase(
        prospective_case_id=prospective_case_id,
        source_case_id=raw.get("source_case_id"),
        created_at=raw.get("created_at", utc_now_iso()),
        domain=raw["domain"],
        proposition=raw["proposition"],
        decision_relevance=raw["decision_relevance"],
        t0=t0,
        expected_resolution=expected_resolution,
    )

    ledger = CaseLedger(args.cases_ledger)
    try:
        written = ledger.append(case)
    except ValidationError as exc:
        raise SystemExit(f"registration refused: {exc}")

    _write_snapshot(args)
    print(json.dumps({
        "prospective_case_id": prospective_case_id,
        "t0_packet_sha256": packet_sha256,
        "written": written,
        "cases_ledger": args.cases_ledger,
    }, indent=2, sort_keys=True))


def cmd_resolve(args: argparse.Namespace) -> None:
    raw = _load_json(args.input)

    case_ledger = CaseLedger(args.cases_ledger)
    if not case_ledger.has(raw["prospective_case_id"]):
        raise SystemExit(f"resolution refused: prospective_case_id {raw['prospective_case_id']!r} "
                          f"is not present in {args.cases_ledger} - cannot resolve a case that was never registered")

    resolved_at = raw["resolved_at"]
    resolution_id = make_resolution_id(raw["prospective_case_id"], raw["outcome"], resolved_at)
    resolution = Resolution(
        resolution_id=resolution_id,
        prospective_case_id=raw["prospective_case_id"],
        resolved_at=resolved_at,
        outcome=raw["outcome"],
        t1_evidence_artifact_ids=list(raw.get("t1_evidence_artifact_ids", [])),
        authoritative_source_type=raw.get("authoritative_source_type", ""),
        resolution_rationale=raw["resolution_rationale"],
        resolver_type=raw["resolver_type"],
        created_at=raw.get("created_at", utc_now_iso()),
    )

    resolution_ledger = ResolutionLedger(args.resolutions_ledger)
    try:
        written = resolution_ledger.append(resolution)
    except ValidationError as exc:
        raise SystemExit(f"resolution refused: {exc}")

    _write_snapshot(args)
    print(json.dumps({
        "resolution_id": resolution_id,
        "prospective_case_id": raw["prospective_case_id"],
        "outcome": raw["outcome"],
        "written": written,
        "resolutions_ledger": args.resolutions_ledger,
    }, indent=2, sort_keys=True))


def cmd_report(args: argparse.Namespace) -> None:
    case_ledger = CaseLedger(args.cases_ledger)
    resolution_ledger = ResolutionLedger(args.resolutions_ledger)
    snapshot = rebuild_snapshot(case_ledger.all_entries(), resolution_ledger.all_entries(), args.as_of_date)
    print(json.dumps(snapshot, indent=2, sort_keys=True))


def _write_snapshot(args: argparse.Namespace) -> None:
    case_ledger = CaseLedger(args.cases_ledger)
    resolution_ledger = ResolutionLedger(getattr(args, "resolutions_ledger", DEFAULT_RESOLUTIONS_LEDGER))
    snapshot = rebuild_snapshot(case_ledger.all_entries(), resolution_ledger.all_entries())
    persist_snapshot(args.snapshot_out, snapshot)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="role", required=True)

    p_register = sub.add_parser("register", help="freeze T0 + pre-register resolution criteria for one new case")
    p_register.add_argument("--input", required=True, help="JSON file describing the case (see README)")
    p_register.add_argument("--cases-ledger", default=DEFAULT_CASES_LEDGER)
    p_register.add_argument("--resolutions-ledger", default=DEFAULT_RESOLUTIONS_LEDGER)
    p_register.add_argument("--snapshot-out", default=DEFAULT_SNAPSHOT)
    p_register.set_defaults(func=cmd_register)

    p_resolve = sub.add_parser("resolve", help="append a T1 Resolution for an existing case")
    p_resolve.add_argument("--input", required=True, help="JSON file describing the resolution (see README)")
    p_resolve.add_argument("--cases-ledger", default=DEFAULT_CASES_LEDGER)
    p_resolve.add_argument("--resolutions-ledger", default=DEFAULT_RESOLUTIONS_LEDGER)
    p_resolve.add_argument("--snapshot-out", default=DEFAULT_SNAPSHOT)
    p_resolve.set_defaults(func=cmd_resolve)

    p_report = sub.add_parser("report", help="read-only: print the current derived-status snapshot")
    p_report.add_argument("--cases-ledger", default=DEFAULT_CASES_LEDGER)
    p_report.add_argument("--resolutions-ledger", default=DEFAULT_RESOLUTIONS_LEDGER)
    p_report.add_argument("--as-of-date", default=None)
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
