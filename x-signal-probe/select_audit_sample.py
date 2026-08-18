"""CLI: freeze the 20-post Run-1 Human Quality Audit sample from Run 1's
already-persisted probe-observations.jsonl (metadata only - that file
has no post text in it to begin with). Never calls the X API, never
touches config/queries.json.

Do not run this against real Run-1 data until a human explicitly says
SELECT AUDIT SAMPLE. See x-signal-probe/audit/README.md for the full
design this implements.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from x_signal_probe.audit_io import write_sample_file  # noqa: E402
from x_signal_probe.audit_models import to_dict  # noqa: E402
from x_signal_probe.audit_selection import (  # noqa: E402
    MAX_PER_FAMILY,
    SELECTION_ALGORITHM_VERSION,
    TARGET_SAMPLE_SIZE,
    compute_effective_cap,
    select_audit_sample,
)

ROOT = os.path.dirname(os.path.abspath(__file__))


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description="Freeze the Run-1 Human Quality Audit sample.")
    p.add_argument("--observations", default=os.path.join(ROOT, "data", "probe-observations.jsonl"))
    p.add_argument("--run-id", default="32120712833")
    p.add_argument("--out-dir", default=os.path.join(ROOT, "audit"))
    p.add_argument("--seed", default=None, help="defaults to sha256 of --observations file content")
    args = p.parse_args()

    with open(args.observations, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    candidates = [r for r in rows if r.get("classification") == "candidate_incremental"]

    seed = args.seed or _sha256_file(args.observations)
    sample = select_audit_sample(candidates, seed=seed)

    family_counts: dict[str, int] = {}
    for c in candidates:
        family_counts[c["query_family"]] = family_counts.get(c["query_family"], 0) + 1
    effective_cap = compute_effective_cap(family_counts, TARGET_SAMPLE_SIZE, MAX_PER_FAMILY)

    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join(args.out_dir, f"run1-sample-{stamp}.json")
    payload = {
        "audit_id": f"AUDIT-{stamp}",
        "run_id": args.run_id,
        "selection_algorithm_version": SELECTION_ALGORITHM_VERSION,
        "seed": seed,
        "target_sample_size": TARGET_SAMPLE_SIZE,
        "base_max_per_family": MAX_PER_FAMILY,
        "effective_max_per_family": effective_cap,
        "total_candidate_pool": len(candidates),
        "families_present": sorted(family_counts),
        "selection_timestamp": now.isoformat(),
        "selected": [to_dict(e) for e in sample],
    }
    write_sample_file(out_path, payload)
    print(json.dumps({"status": "OK", "selected": len(sample), "out_path": out_path}))


if __name__ == "__main__":
    main()
