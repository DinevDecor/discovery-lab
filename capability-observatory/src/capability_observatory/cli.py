"""Orchestration entry points. No network access anywhere in this module.

Subcommands:
    submit    validate + record ONE capture submission file
    process   validate + record every submission currently sitting in
              incoming/, then render the run summary (this is what the
              GitHub Actions workflow calls)
    report    render the run summary from whatever is already recorded,
              without processing any new submissions
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import date
from typing import Any, Dict, List, Tuple

from . import report
from .capture_intake import CaptureValidationError, record_capture
from .storage import AppendOnlyStore

DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _paths(root: str) -> Dict[str, str]:
    return {
        "panel": os.path.join(root, "config", "panel.json"),
        "captures": os.path.join(root, "data", "captures.jsonl"),
        "observations": os.path.join(root, "data", "observations.jsonl"),
        "identity_breaks": os.path.join(root, "data", "identity_breaks.jsonl"),
        "incoming": os.path.join(root, "incoming"),
        "processed": os.path.join(root, "incoming", "processed"),
        "rejected": os.path.join(root, "incoming", "rejected"),
        "reports": os.path.join(root, "reports"),
    }


def load_panel(panel_path: str) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    with open(panel_path, "r", encoding="utf-8") as fh:
        panel = json.load(fh)
    items = panel.get("items", [])
    ids = [item["panel_item_id"] for item in items]
    by_id = {item["panel_item_id"]: item for item in items}
    return ids, by_id


def _open_stores(paths: Dict[str, str]) -> Tuple[AppendOnlyStore, AppendOnlyStore, AppendOnlyStore]:
    captures = AppendOnlyStore(paths["captures"], id_field="capture_id")
    observations = AppendOnlyStore(paths["observations"], id_field="observation_id")
    identity_breaks = AppendOnlyStore(paths["identity_breaks"], id_field="identity_break_id")
    return captures, observations, identity_breaks


def cmd_submit(args: argparse.Namespace) -> int:
    paths = _paths(args.root)
    panel_ids, panel_by_id = load_panel(paths["panel"])
    captures, observations, identity_breaks = _open_stores(paths)

    with open(args.submission, "r", encoding="utf-8") as fh:
        submission = json.load(fh)

    panel_item = panel_by_id.get(submission.get("panel_item_id"))
    if panel_item is None:
        print(f"REJECTED {args.submission}: unknown panel_item_id {submission.get('panel_item_id')!r}")
        return 1

    try:
        result = record_capture(submission, panel_item, captures, observations, identity_breaks)
    except CaptureValidationError as exc:
        print(f"REJECTED {args.submission}: {exc}")
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


def _process_incoming(paths: Dict[str, str]) -> Dict[str, Any]:
    panel_ids, panel_by_id = load_panel(paths["panel"])
    captures, observations, identity_breaks = _open_stores(paths)

    os.makedirs(paths["incoming"], exist_ok=True)
    os.makedirs(paths["processed"], exist_ok=True)
    os.makedirs(paths["rejected"], exist_ok=True)

    submission_files = sorted(
        f for f in os.listdir(paths["incoming"])
        if f.endswith(".json") and os.path.isfile(os.path.join(paths["incoming"], f))
    )

    processed, rejected, results = [], [], []
    for filename in submission_files:
        src_path = os.path.join(paths["incoming"], filename)
        try:
            with open(src_path, "r", encoding="utf-8") as fh:
                submission = json.load(fh)
        except json.JSONDecodeError as exc:
            rejected.append({"file": filename, "error": f"invalid JSON: {exc}"})
            shutil.move(src_path, os.path.join(paths["rejected"], filename))
            continue

        panel_item = panel_by_id.get(submission.get("panel_item_id"))
        if panel_item is None:
            rejected.append({"file": filename, "error": f"unknown panel_item_id {submission.get('panel_item_id')!r}"})
            shutil.move(src_path, os.path.join(paths["rejected"], filename))
            continue

        try:
            result = record_capture(submission, panel_item, captures, observations, identity_breaks)
        except CaptureValidationError as exc:
            rejected.append({"file": filename, "error": str(exc)})
            shutil.move(src_path, os.path.join(paths["rejected"], filename))
            continue

        result["file"] = filename
        results.append(result)
        processed.append(filename)
        shutil.move(src_path, os.path.join(paths["processed"], filename))

    return {
        "panel_ids": panel_ids,
        "processed_files": processed,
        "rejected": rejected,
        "results": results,
    }


def _write_report(paths: Dict[str, str], panel_ids: List[str]) -> Dict[str, Any]:
    captures = AppendOnlyStore(paths["captures"], id_field="capture_id").read_all()
    observations = AppendOnlyStore(paths["observations"], id_field="observation_id").read_all()
    identity_breaks = AppendOnlyStore(paths["identity_breaks"], id_field="identity_break_id").read_all()

    summary = report.build_summary(panel_ids, captures, observations, identity_breaks)

    os.makedirs(paths["reports"], exist_ok=True)
    with open(os.path.join(paths["reports"], "latest-summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, sort_keys=True, ensure_ascii=False, indent=2)

    md_path = os.path.join(paths["reports"], f"weekly-{date.today().isoformat()}.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(report.render_markdown(summary))

    return summary


def cmd_process(args: argparse.Namespace) -> int:
    paths = _paths(args.root)
    intake_result = _process_incoming(paths)
    summary = _write_report(paths, intake_result["panel_ids"])

    print(json.dumps({
        "processed_files": intake_result["processed_files"],
        "rejected": intake_result["rejected"],
        "captures_written": sum(1 for r in intake_result["results"] if r["capture_written"]),
        "observations_written": sum(1 for r in intake_result["results"] if r["observation_written"]),
        "identity_breaks_written": sum(1 for r in intake_result["results"] if r["identity_break_written"]),
        "totals": summary["totals"],
        "stop_rules": summary["stop_rules"],
    }, sort_keys=True, indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    paths = _paths(args.root)
    panel_ids, _ = load_panel(paths["panel"])
    summary = _write_report(paths, panel_ids)
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(prog="capability-observatory")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="capability-observatory package root")
    sub = parser.add_subparsers(dest="command", required=True)

    p_submit = sub.add_parser("submit", help="validate and record one capture submission file")
    p_submit.add_argument("submission", help="path to a single submission JSON file")
    p_submit.set_defaults(func=cmd_submit)

    p_process = sub.add_parser("process", help="record every submission in incoming/ and render the report")
    p_process.set_defaults(func=cmd_process)

    p_report = sub.add_parser("report", help="render the report from already-recorded evidence")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
