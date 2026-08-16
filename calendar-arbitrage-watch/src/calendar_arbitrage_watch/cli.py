"""CLI orchestration for Calendar Arbitrage Watch - the package's single
Coordinator, per the approved architecture review's role-collapse
decision (section 5): no separate Coordinator agent, just this
entrypoint, mirroring every other package's run_*.py + cli.py split.

`add`   validate a submission file -> append to the ledger -> run the
        adversarial gate -> apply the lifecycle transition -> append the
        POST-review record too (a lifecycle change is its own new ledger
        line, never a mutation of the specialist's own line) -> rebuild
        the snapshot -> render the daily report.
`report`  re-render the report from the current snapshot, add nothing.
`rebuild` rebuild the snapshot from the ledger only.

This module never opens a network connection and never calls a model
(enforced by tests/test_safety.py, same detector as every sibling
package).
"""

from __future__ import annotations

import datetime as dt
import sys
from dataclasses import replace
from typing import Any, Dict, List, Optional, Sequence

from . import intake, ledger, report
from .gate import review as gate_review
from .lifecycle import apply_review
from .models import CalendarAssessment

ANALYST_VERSION = "0.1.2"


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def _paths(root: str) -> Dict[str, str]:
    return {
        "events": f"{root}/data/calendar_events.jsonl",
        "snapshot": f"{root}/data/calendar_candidates.json",
        "reports": f"{root}/reports",
    }


def cmd_add(root: str, submission_paths: Sequence[str]) -> int:
    p = _paths(root)
    cal_ledger = ledger.CalendarLedger(p["events"])
    previous_snapshot = ledger.rebuild_snapshot(cal_ledger.all_entries())
    previous_current = previous_snapshot["current"]

    recorded_at = _utc_now_iso()
    exit_code = 0

    for path in submission_paths:
        try:
            submissions = intake.load_submissions(path)
        except intake.IntakeError as exc:
            print(f"REJECTED {path}: {exc}")
            exit_code = 1
            continue

        for raw in submissions:
            result = intake.validate_submission(raw)
            if not result.ok:
                print(f"REJECTED {path}::{raw.get('candidate_id', '?')}: {'; '.join(result.violations)}")
                exit_code = 1
                continue

            assessment: CalendarAssessment = result.assessment
            assessment.analyst_version = ANALYST_VERSION
            if not assessment.first_seen:
                assessment.first_seen = recorded_at
            assessment.last_updated = recorded_at

            written = cal_ledger.append(assessment, recorded_at)
            print(f"{'ADDED' if written else 'DUPLICATE'} {assessment.candidate_id} (specialist assessment)")

            decision = gate_review(assessment)
            new_state, reason = apply_review(assessment, decision)
            reviewed = replace(assessment, lifecycle_state=new_state, lifecycle_reason=reason,
                                last_updated=recorded_at)
            written2 = cal_ledger.append(reviewed, recorded_at)
            print(f"{'ADDED' if written2 else 'DUPLICATE'} {assessment.candidate_id} "
                  f"(review={decision.outcome}, state={new_state})")

    snapshot = ledger.rebuild_snapshot(cal_ledger.all_entries())
    ledger.persist_snapshot(p["snapshot"], snapshot)

    _render_and_write_report(p, previous_current, snapshot["current"])
    return exit_code


def cmd_report(root: str) -> int:
    p = _paths(root)
    cal_ledger = ledger.CalendarLedger(p["events"])
    snapshot = ledger.rebuild_snapshot(cal_ledger.all_entries())
    _render_and_write_report(p, snapshot["current"], snapshot["current"])
    return 0


def cmd_rebuild(root: str) -> int:
    p = _paths(root)
    cal_ledger = ledger.CalendarLedger(p["events"])
    snapshot = ledger.rebuild_snapshot(cal_ledger.all_entries())
    ledger.persist_snapshot(p["snapshot"], snapshot)
    print(f"rebuilt {p['snapshot']}: {len(snapshot['current'])} current, {len(snapshot['superseded'])} superseded")
    return 0


def _render_and_write_report(paths: Dict[str, str], previous_current: List[Dict[str, Any]],
                              new_current: List[Dict[str, Any]]) -> str:
    events = report.detect_material_events(previous_current, new_current)
    best_action = report.pick_best_next_action(new_current)
    open_findings_summary = []
    for record in new_current:
        for f in record.get("open_findings", []):
            open_findings_summary.append({**f, "candidate_id": record["candidate_id"]})
    text = report.render_report(_today_iso(), events, best_action, open_findings_summary)
    path = report.write_report(paths["reports"], _today_iso(), text)
    print(text)
    return path


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    import os

    # cli.py lives at <root>/src/calendar_arbitrage_watch/cli.py - three
    # dirname() calls back up to <root>.
    _default_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    parser = argparse.ArgumentParser(description="Calendar Arbitrage Watch")
    parser.add_argument("--root", default=_default_root,
                         help="package root (defaults to this file's package directory)")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="validate + append + review + report")
    add_p.add_argument("submission_paths", nargs="+")

    sub.add_parser("report", help="re-render the report only")
    sub.add_parser("rebuild", help="rebuild the snapshot only")

    args = parser.parse_args(argv)

    if args.command == "add":
        return cmd_add(args.root, args.submission_paths)
    if args.command == "report":
        return cmd_report(args.root)
    if args.command == "rebuild":
        return cmd_rebuild(args.root)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
