from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from business_candidate_analyst.analyst import run_analysis  # noqa: E402
from business_candidate_analyst.report import render  # noqa: E402


def main() -> None:
    root = os.path.dirname(os.path.abspath(__file__))
    default_ca_data = os.path.normpath(os.path.join(root, "..", "constraint-archaeology-agents", "data"))

    p = argparse.ArgumentParser(description="Read-only downstream analyst over Constraint Archaeology evidence.")
    p.add_argument("--ca-data-dir", default=default_ca_data,
                    help="Constraint Archaeology data directory (read-only). Default: %(default)s")
    p.add_argument("--data-dir", default=os.path.join(root, "data"),
                    help="This tool's own registry directory (write target).")
    p.add_argument("--reports-dir", default=os.path.join(root, "reports"))
    args = p.parse_args()

    result = run_analysis(args.ca_data_dir, args.data_dir)
    stamp = dt.date.today().isoformat()
    report_path = os.path.join(args.reports_dir, f"business-candidates-{stamp}.md")
    render(report_path, result)

    print(json.dumps({
        "anomalies_considered": result["anomalies_considered"],
        "groups_formed": result["groups_formed"],
        "events_appended": result["events_appended"],
        "candidates_total": len(result["candidates"]),
        "snapshot_path": result["snapshot_path"],
        "events_path": result["events_path"],
        "report_path": report_path,
    }))


if __name__ == "__main__":
    main()
