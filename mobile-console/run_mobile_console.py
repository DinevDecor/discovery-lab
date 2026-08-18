"""CLI entrypoint for the Mobile Machine Console: one role, `build`,
which reads every canonical ledger (read-only, via
`mobile_console.aggregate`) and writes the deterministic snapshot both
this package's own `data/snapshot.json` (for tests/inspection) and the
static site's `site/data.json` (what the PWA actually fetches at
runtime) consume.

No other role exists. This console has no write path back into any
ledger, no action button, no mutation of any kind - task instruction:
"Preserve the hard read-only boundary. No Stage 5, no actions, no
mutation buttons." `build` is regeneration of a read-only view, not a
system action.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from mobile_console.aggregate import build_snapshot  # noqa: E402

DEFAULT_SNAPSHOT_OUT = os.path.join(ROOT, "data", "snapshot.json")
DEFAULT_SITE_DATA_OUT = os.path.join(ROOT, "site", "data.json")


def cmd_build(args: argparse.Namespace) -> None:
    snapshot = build_snapshot()
    for out_path in (args.snapshot_out, args.site_data_out):
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps({
        "machine_status": snapshot["machine_status"],
        "opportunities_count": len(snapshot["opportunities"]),
        "pipeline_stages": len(snapshot["pipeline"]),
        "ground_truth_cases": len(snapshot["ground_truth"]["cases"]),
        "activity_entries": len(snapshot["activity"]),
        "snapshot_out": args.snapshot_out,
        "site_data_out": args.site_data_out,
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="role", required=True)

    p_build = sub.add_parser("build", help="regenerate the deterministic snapshot from canonical ledgers")
    p_build.add_argument("--snapshot-out", default=DEFAULT_SNAPSHOT_OUT)
    p_build.add_argument("--site-data-out", default=DEFAULT_SITE_DATA_OUT)
    p_build.set_defaults(func=cmd_build)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
