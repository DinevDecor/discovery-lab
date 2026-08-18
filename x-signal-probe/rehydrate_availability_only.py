"""CLI: single batched X API ID-lookup for the frozen 20-post audit
sample - emits ONLY availability + canonical_url + provenance fields,
never post text, to stdout or any file.

Companion to review_audit_sample.py for a review context where the
human reviewer opens canonical_url directly (e.g. reviewing from a
phone) instead of reading rehydrated text through this tool. See
audit/README.md and CONTRACT.md.

Makes exactly one X API request (the ID-lookup endpoint, <=100 ids,
here <=20) - never search_recent, never a second lookup call, never a
retry with a smaller batch, never a fallback search for an unavailable
post. Never alters the frozen sample file it reads.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from x_signal_probe import client as discovery_client  # noqa: E402  (only get_bearer_token - never .search_recent)
from x_signal_probe.audit_review import rehydrate_selected  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sample", required=True, help="path to the frozen audit/run1-sample-*.json (read-only)")
    args = p.parse_args()

    try:
        bearer_token = discovery_client.get_bearer_token()
    except discovery_client.MissingSecretError as e:
        print(json.dumps({"status": "MISSING_SECRET", "error": str(e)}))
        sys.exit(1)

    with open(args.sample, encoding="utf-8") as f:
        sample_payload = json.load(f)
    entries = sample_payload["selected"]

    found, unavailable_ids = rehydrate_selected(entries, bearer_token)

    results = []
    for entry in entries:
        pid = entry["post_id"]
        # `found[pid]["text"]` is deliberately never read anywhere below -
        # only dict membership (availability) is derived from `found` /
        # `unavailable_ids`. Nothing text-shaped is ever assigned to a
        # variable that reaches print() or a file.
        results.append(
            {
                "post_id": pid,
                "query_family": entry["query_family"],
                "query_id": entry["query_id"],
                "canonical_url": entry["canonical_url"],
                "availability": "UNAVAILABLE" if pid in unavailable_ids else "AVAILABLE",
            }
        )

    print(
        json.dumps(
            {
                "status": "OK",
                "sample_path": args.sample,
                "available": len(found),
                "unavailable": len(unavailable_ids),
                "results": results,
            }
        )
    )


if __name__ == "__main__":
    main()
