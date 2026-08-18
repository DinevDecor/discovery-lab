"""CLI entrypoint: wrap one real CA Anomaly and/or one real BCA Candidate
into Case/Claim envelopes and append them to this package's own ledger.

Read-only against CA/BCA data. Writes only to case-claim-kernel/data/.
See CONTRACT.md.

Usage:
    python3 run_case_claim_kernel.py --anomaly-id ANOM-0001 --candidate-id BC-0001
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(ROOT)
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from case_claim_kernel.envelope import build_case_envelope, build_claim_envelope  # noqa: E402
from case_claim_kernel.ledger import ArtifactLedger  # noqa: E402
from case_claim_kernel.wrap import (  # noqa: E402
    find_by_id,
    load_bca_candidates,
    load_ca_anomalies,
    wrap_bca_candidate,
    wrap_ca_anomaly,
)

DEFAULT_CA_ANOMALIES = os.path.join(REPO_ROOT, "constraint-archaeology-agents", "data", "anomalies.json")
DEFAULT_BCA_CANDIDATES = os.path.join(REPO_ROOT, "business-candidate-analyst", "data", "candidates.json")
DEFAULT_LEDGER_PATH = os.path.join(ROOT, "data", "artifacts.jsonl")


def run(anomaly_id: str = None, candidate_id: str = None,
        ca_anomalies_path: str = DEFAULT_CA_ANOMALIES,
        bca_candidates_path: str = DEFAULT_BCA_CANDIDATES,
        ledger_path: str = DEFAULT_LEDGER_PATH) -> dict:
    ledger = ArtifactLedger(ledger_path)
    result = {"cases_written": 0, "claims_written": 0, "cases_already_known": 0,
              "claims_already_known": 0, "wrapped": []}

    if anomaly_id:
        anomalies = load_ca_anomalies(ca_anomalies_path)
        anomaly = find_by_id(anomalies, "anomaly_id", anomaly_id)
        if anomaly is None:
            raise SystemExit(f"anomaly_id {anomaly_id!r} not found in {ca_anomalies_path}")
        case, claims = wrap_ca_anomaly(anomaly)
        case_env = build_case_envelope(case)
        written = ledger.append(case_env)
        result["cases_written" if written else "cases_already_known"] += 1
        for claim in claims:
            claim_env = build_claim_envelope(claim)
            written = ledger.append(claim_env)
            result["claims_written" if written else "claims_already_known"] += 1
        result["wrapped"].append({"source_record_id": anomaly_id, "case_id": case.case_id,
                                   "claim_count": len(claims)})

    if candidate_id:
        candidates = load_bca_candidates(bca_candidates_path)
        candidate = find_by_id(candidates, "candidate_id", candidate_id)
        if candidate is None:
            raise SystemExit(f"candidate_id {candidate_id!r} not found in {bca_candidates_path}")
        case, claims = wrap_bca_candidate(candidate)
        case_env = build_case_envelope(case)
        written = ledger.append(case_env)
        result["cases_written" if written else "cases_already_known"] += 1
        for claim in claims:
            claim_env = build_claim_envelope(claim)
            written = ledger.append(claim_env)
            result["claims_written" if written else "claims_already_known"] += 1
        result["wrapped"].append({"source_record_id": candidate_id, "case_id": case.case_id,
                                   "claim_count": len(claims)})

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anomaly-id", default=None, help="CA anomaly_id to wrap, e.g. ANOM-0001")
    parser.add_argument("--candidate-id", default=None, help="BCA candidate_id to wrap, e.g. BC-0001")
    parser.add_argument("--ca-anomalies-path", default=DEFAULT_CA_ANOMALIES)
    parser.add_argument("--bca-candidates-path", default=DEFAULT_BCA_CANDIDATES)
    parser.add_argument("--ledger-path", default=DEFAULT_LEDGER_PATH)
    args = parser.parse_args()

    if not args.anomaly_id and not args.candidate_id:
        parser.error("at least one of --anomaly-id / --candidate-id is required")

    result = run(
        anomaly_id=args.anomaly_id,
        candidate_id=args.candidate_id,
        ca_anomalies_path=args.ca_anomalies_path,
        bca_candidates_path=args.bca_candidates_path,
        ledger_path=args.ledger_path,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
