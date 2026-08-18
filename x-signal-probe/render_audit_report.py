"""CLI: render the Human Quality Audit report from a finished verdicts
file. Reads only verdict/provenance records - never touches post text,
never re-contacts the X API."""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from x_signal_probe.audit_io import write_report_file  # noqa: E402
from x_signal_probe.audit_report import compute_report, render_markdown  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--verdicts", required=True)
    p.add_argument("--run-id", default="32120712833")
    p.add_argument("--out", default=os.path.join(ROOT, "audit", "run1-audit-report.md"))
    args = p.parse_args()

    with open(args.verdicts, encoding="utf-8") as f:
        verdicts = [json.loads(line) for line in f if line.strip()]
    metrics = compute_report(verdicts)
    write_report_file(args.out, render_markdown(metrics, args.run_id))
    print(json.dumps({"status": "OK", "decision": metrics.decision, "out": args.out}))


if __name__ == "__main__":
    main()
