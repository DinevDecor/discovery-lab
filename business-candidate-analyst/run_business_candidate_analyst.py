from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from business_candidate_analyst.analyst import run_analysis  # noqa: E402
from business_candidate_analyst.config import load_rearchitecture_thresholds  # noqa: E402
from business_candidate_analyst.rearchitecture.analyst import run_analysis as run_rearchitecture_analysis  # noqa: E402
from business_candidate_analyst.report import render  # noqa: E402


def main() -> None:
    root = os.path.dirname(os.path.abspath(__file__))
    default_ca_data = os.path.normpath(os.path.join(root, "..", "constraint-archaeology-agents", "data"))

    p = argparse.ArgumentParser(description="Read-only downstream analyst over Constraint Archaeology evidence.")
    p.add_argument("--ca-data-dir", default=default_ca_data,
                    help="Constraint Archaeology data directory (read-only). Default: %(default)s")
    p.add_argument("--data-dir", default=os.path.join(root, "data"),
                    help="This tool's own registry directory (write target, shared by both modes).")
    p.add_argument("--reports-dir", default=os.path.join(root, "reports"))
    p.add_argument("--skip-mode-b", action="store_true",
                    help="Run only Mode A (New Market Discovery). Mode B (Legacy Business Rearchitecture) "
                         "runs by default, reading the registry Mode A just updated.")
    args = p.parse_args()

    mode_a_result = run_analysis(args.ca_data_dir, args.data_dir)

    mode_b_result = None
    if not args.skip_mode_b:
        rearch_config = load_rearchitecture_thresholds()
        mode_b_result = run_rearchitecture_analysis(args.ca_data_dir, args.data_dir, rearch_config)

    stamp = dt.date.today().isoformat()
    report_path = os.path.join(args.reports_dir, f"business-candidates-{stamp}.md")
    render(report_path, mode_a_result, mode_b_result)

    summary = {
        "mode_a": {
            "anomalies_considered": mode_a_result["anomalies_considered"],
            "groups_formed": mode_a_result["groups_formed"],
            "events_appended": mode_a_result["events_appended"],
            "candidates_total": len(mode_a_result["candidates"]),
        },
        "report_path": report_path,
        "snapshot_path": mode_a_result["snapshot_path"],
        "events_path": mode_a_result["events_path"],
    }
    if mode_b_result is not None:
        summary["mode_b"] = {
            "anomalies_considered": mode_b_result["anomalies_considered"],
            "groups_formed": mode_b_result["groups_formed"],
            "events_appended": mode_b_result["events_appended"],
            "candidates_total": len(mode_b_result["candidates"]),
        }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
