"""Wires the two daily pipelines in the required order: Constraint
Archaeology's daily scan must persist its own outputs successfully before
Business Candidate Analyst is allowed to read them. Never the reverse -
BCA is a strictly read-only downstream consumer (enforced by
evidence_reader.py + tests/test_safety.py) and must never run against a
CA snapshot that failed to complete.

Both stages are invoked as subprocesses (matching each package's own
run_*.py CLI entrypoint) rather than imported in-process. That keeps this
orchestrator from ever needing write access to either package's internals
- only their exit codes and, for BCA, the one-line JSON summary it prints
- and means a crash in either stage can never corrupt the other's
in-process state or partially-written files; each stage's own writes
(CA's data/*.json(l) and reports/, BCA's registry and reports/) are
already atomic-per-call the way each package writes them today.

Notification: this repo has no notification-delivery infrastructure
today, so per the operating contract (docs/operations/bca-daily-pipeline.md)
this orchestrator does not attempt to invent one. It persists two
machine-readable, append-free-to-overwrite artifacts for later surfacing
by whatever system reads them:

  reports/pipeline-status-<date>.json      this run's CA/BCA outcome
  business-candidate-analyst/reports/material-events-<date>.json
                                            written by BCA itself; lists
                                            only the lifecycle-material
                                            candidate events from this run

A pipeline failure (CA or BCA) is itself the sixth material-event
category from the operating contract; it is recorded in
pipeline-status-<date>.json and surfaced via a non-zero exit code, which
any wrapping scheduler already treats as "needs attention" without this
script inventing a second failure-signaling channel.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CA_CMD = [sys.executable, os.path.join(ROOT, "constraint-archaeology-agents", "run_daily.py")]
DEFAULT_BCA_CMD = [sys.executable, os.path.join(ROOT, "business-candidate-analyst", "run_business_candidate_analyst.py")]
DEFAULT_STATUS_DIR = os.path.join(ROOT, "reports")


def run_pipeline(ca_cmd: List[str], bca_cmd: List[str], status_dir: str,
                  now: Optional[dt.datetime] = None) -> Dict[str, Any]:
    """Runs `ca_cmd`; only on a zero exit code does it then run `bca_cmd`.
    Always persists a pipeline-status-<date>.json under `status_dir`, then
    returns the same dict. `ca_cmd`/`bca_cmd` are injectable specifically
    so tests can substitute deterministic, offline stand-ins for the real
    (network- and model-calling) CA scan and the real BCA run - this
    function's own logic (ordering, failure gating, status persistence)
    is what needs proving, not either subprocess's internal behavior,
    which each already has its own test suite for."""
    stamp = (now or dt.datetime.now(dt.timezone.utc)).date().isoformat()
    result: Dict[str, Any] = {"date": stamp}

    ca_proc = subprocess.run(ca_cmd, capture_output=True, text=True)
    result["ca"] = {
        "command": ca_cmd,
        "returncode": ca_proc.returncode,
        "stdout_tail": ca_proc.stdout[-2000:],
        "stderr_tail": ca_proc.stderr[-2000:],
    }

    if ca_proc.returncode != 0:
        result["status"] = "CA_FAILED"
        result["bca"] = None
        result["bca_skipped_reason"] = "Constraint Archaeology daily scan did not complete successfully"
        _persist_status(status_dir, stamp, result)
        return result

    bca_proc = subprocess.run(bca_cmd, capture_output=True, text=True)
    bca_summary = None
    if bca_proc.returncode == 0:
        try:
            bca_summary = json.loads(bca_proc.stdout.strip().splitlines()[-1])
        except Exception:
            bca_summary = None
    result["bca"] = {
        "command": bca_cmd,
        "returncode": bca_proc.returncode,
        "stdout_tail": bca_proc.stdout[-2000:],
        "stderr_tail": bca_proc.stderr[-2000:],
        "summary": bca_summary,
    }
    result["status"] = "OK" if bca_proc.returncode == 0 else "BCA_FAILED"

    _persist_status(status_dir, stamp, result)
    return result


def _persist_status(status_dir: str, stamp: str, result: Dict[str, Any]) -> None:
    os.makedirs(status_dir, exist_ok=True)
    path = os.path.join(status_dir, f"pipeline-status-{stamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
    result["status_path"] = path


def main() -> None:
    p = argparse.ArgumentParser(
        description="Daily orchestration: Constraint Archaeology scan, then, only on success, "
                     "Business Candidate Analyst.")
    p.add_argument("--status-dir", default=DEFAULT_STATUS_DIR)
    args = p.parse_args()

    result = run_pipeline(DEFAULT_CA_CMD, DEFAULT_BCA_CMD, args.status_dir)
    print(json.dumps(result, default=str))
    sys.exit(0 if result["status"] == "OK" else 1)


if __name__ == "__main__":
    main()
