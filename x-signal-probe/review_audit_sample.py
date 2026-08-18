"""CLI: local, human-interactive review of the frozen 20-post audit
sample.

*** Run this yourself, in your own terminal, with your own
X_BEARER_TOKEN - do not run this inside a hosted assistant session. ***
Rehydrated post text is held in this process's memory only, for one
review pass, and is never written to any file, log, or returned to any
calling tool - only the verdict/provenance record (AuditVerdict) is
ever persisted. Running this inside a hosted chat session would make
the post text part of that session's own transcript, a persistence
surface this design is specifically trying to avoid - see
x-signal-probe/audit/README.md.

Makes exactly one X API request (the ID-lookup endpoint, <=100 ids,
here <=20) - never search_recent, never a second lookup call, never a
retry with a smaller batch, never a fallback search for an unavailable
post.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from x_signal_probe import client as discovery_client  # noqa: E402  (only get_bearer_token - never .search_recent)
from x_signal_probe.audit_io import append_verdict_line  # noqa: E402
from x_signal_probe.audit_models import RUBRIC_ABCD_VALUES, RUBRIC_E_VALUES  # noqa: E402
from x_signal_probe.audit_review import (  # noqa: E402
    record_available,
    record_unavailable,
    rehydrate_selected,
)

ROOT = os.path.dirname(os.path.abspath(__file__))


def _prompt(question: str, allowed) -> str:
    while True:
        ans = input(f"{question} [{'/'.join(allowed)}]: ").strip().upper()
        if ans in allowed:
            return ans
        print(f"Please answer one of: {', '.join(allowed)}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sample", required=True, help="path to audit/run1-sample-*.json")
    p.add_argument("--run-id", default="32120712833")
    p.add_argument("--reviewer", default="")
    p.add_argument("--out-dir", default=os.path.join(ROOT, "audit"))
    args = p.parse_args()

    try:
        bearer_token = discovery_client.get_bearer_token()
    except discovery_client.MissingSecretError as e:
        print(json.dumps({"status": "MISSING_SECRET", "error": str(e)}))
        sys.exit(1)

    with open(args.sample, encoding="utf-8") as f:
        sample_payload = json.load(f)
    entries = sample_payload["selected"]
    audit_id = sample_payload.get("audit_id", "")
    algo_version = sample_payload.get("selection_algorithm_version", "")

    found, unavailable_ids = rehydrate_selected(entries, bearer_token)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join(args.out_dir, f"run1-verdicts-{stamp}.jsonl")

    for entry in entries:
        pid = entry["post_id"]
        if pid in unavailable_ids:
            verdict = record_unavailable(entry, audit_id, args.run_id, algo_version)
            append_verdict_line(out_path, verdict)
            print(f"[{pid}] UNAVAILABLE - recorded, not replaced")
            continue

        post = found[pid]
        print("\n" + "=" * 70)
        print(f"post_id: {pid}  family: {entry['query_family']}")
        print(post["text"])
        print("=" * 70)

        a = _prompt("A - genuine problem report?", RUBRIC_ABCD_VALUES[:3])
        b = _prompt("B - operational/economic consequence?", RUBRIC_ABCD_VALUES[:3])
        c = _prompt("C - noise?", RUBRIC_ABCD_VALUES[:3])
        d = _prompt("D - incremental vs Discovery Lab?", RUBRIC_ABCD_VALUES[:3])
        e = _prompt("E - corroboration worthy?", RUBRIC_E_VALUES[:2])
        notes = input("notes (your own words only - do not paste the post text): ").strip()

        verdict = record_available(entry, audit_id, args.run_id, algo_version, args.reviewer, a, b, c, d, e, notes)
        append_verdict_line(out_path, verdict)
        post = None  # drop the only local reference to rehydrated text

    print(json.dumps({"status": "OK", "verdicts_path": out_path, "unavailable": len(unavailable_ids)}))


if __name__ == "__main__":
    main()
