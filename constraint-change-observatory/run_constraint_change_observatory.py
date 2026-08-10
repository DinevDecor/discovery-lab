"""CLI for the Constraint Change Observatory. No network, no LLM, fully
deterministic - see CONTRACT.md.

Subcommands:
  add <file.json> [<file.json> ...]   validate and append records; rebuilds
                                        the snapshot and writes a dated report
  validate <file.json> ...             dry run - validate only, append nothing
  report                                re-render the report from current
                                        ledger state, adding nothing
  rebuild                               rebuild data/constraints.json from
                                        data/constraint_events.jsonl only
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from constraint_change_observatory.intake import intake_files, validate_file  # noqa: E402
from constraint_change_observatory.ledger import (  # noqa: E402
    ConstraintLedger, persist_snapshot, rebuild_snapshot,
)
from constraint_change_observatory.report import render  # noqa: E402


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _paths(root: str, data_dir: str, reports_dir: str):
    events_path = os.path.join(data_dir, "constraint_events.jsonl")
    snapshot_path = os.path.join(data_dir, "constraints.json")
    stamp = dt.date.today().isoformat()
    report_path = os.path.join(reports_dir, f"constraint-changes-{stamp}.md")
    return events_path, snapshot_path, report_path


def cmd_add(args) -> int:
    events_path, snapshot_path, report_path = _paths(args.root, args.data_dir, args.reports_dir)
    ledger = ConstraintLedger(events_path)
    now = utc_now_iso()
    results = intake_files(args.files, ledger, now)

    added_ids = [r.record_id for r in results if r.outcome == "added"]
    ok = True
    for r in results:
        if r.outcome == "rejected":
            ok = False
            print(f"REJECTED {r.record_id}:", file=sys.stderr)
            for v in r.violations:
                print(f"  - {v}", file=sys.stderr)
        else:
            print(f"{r.outcome.upper()} {r.record_id}")

    snapshot = rebuild_snapshot(ledger.all_entries())
    persist_snapshot(snapshot_path, snapshot)
    render(report_path, snapshot, added_ids, now)

    print(json.dumps({
        "added": len(added_ids), "duplicate": sum(1 for r in results if r.outcome == "duplicate"),
        "rejected": sum(1 for r in results if r.outcome == "rejected"),
        "current_total": len(snapshot["current"]), "report_path": report_path,
        "snapshot_path": snapshot_path, "events_path": events_path,
    }))
    return 0 if ok else 1


def cmd_validate(args) -> int:
    ok = True
    for path in args.files:
        for r in validate_file(path):
            if r.outcome == "rejected":
                ok = False
                print(f"REJECTED {r.record_id}:", file=sys.stderr)
                for v in r.violations:
                    print(f"  - {v}", file=sys.stderr)
            else:
                print(f"VALID {r.record_id}")
    return 0 if ok else 1


def cmd_report(args) -> int:
    events_path, snapshot_path, report_path = _paths(args.root, args.data_dir, args.reports_dir)
    ledger = ConstraintLedger(events_path)
    snapshot = rebuild_snapshot(ledger.all_entries())
    persist_snapshot(snapshot_path, snapshot)
    render(report_path, snapshot, [], utc_now_iso())
    print(json.dumps({"current_total": len(snapshot["current"]), "report_path": report_path}))
    return 0


def cmd_rebuild(args) -> int:
    events_path, snapshot_path, _ = _paths(args.root, args.data_dir, args.reports_dir)
    ledger = ConstraintLedger(events_path)
    snapshot = rebuild_snapshot(ledger.all_entries())
    persist_snapshot(snapshot_path, snapshot)
    print(json.dumps({"current_total": len(snapshot["current"]), "snapshot_path": snapshot_path}))
    return 0


def main() -> None:
    root = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description="Constraint Change Observatory - offline, deterministic.")
    p.add_argument("--data-dir", default=os.path.join(root, "data"))
    p.add_argument("--reports-dir", default=os.path.join(root, "reports"))
    sub = p.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="validate and append records from JSON file(s)")
    add_p.add_argument("files", nargs="+")
    add_p.set_defaults(func=cmd_add)

    val_p = sub.add_parser("validate", help="dry-run validate JSON file(s), append nothing")
    val_p.add_argument("files", nargs="+")
    val_p.set_defaults(func=cmd_validate)

    rep_p = sub.add_parser("report", help="re-render the report from current ledger state")
    rep_p.set_defaults(func=cmd_report)

    reb_p = sub.add_parser("rebuild", help="rebuild constraints.json from constraint_events.jsonl")
    reb_p.set_defaults(func=cmd_rebuild)

    args = p.parse_args()
    args.root = root
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
