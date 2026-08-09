"""Orchestration entry point for the external capture executor.

    run     fetch every panel item via its assigned method (DigiKey API,
            Mouser API, AutomationDirect probe+HTML, or a no-op
            HUMAN_FALLBACK_REQUIRED marker for McMaster-Carr/Grainger),
            write one C3 submission file per attempted item into
            capability-observatory/incoming/, then invoke the EXISTING,
            unmodified `python3 run_capability_observatory.py process` to
            validate/record/report -- this module never writes to
            capability-observatory/data/*.jsonl itself. Finally renders the
            executor health report.

No network call happens anywhere outside digikey.py / mouser.py /
automationdirect.py's RealTransport -- this module only orchestrates.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Tuple

from . import automationdirect, digikey, human_fallback, mouser
from .envelope import ExecutorSubmission
from .health import ProviderAttempt, build_health_report, classify_attempt, render_markdown
from .secrets import assert_submission_has_no_secret, known_secret_values
from .transport import RealTransport

EXECUTOR_VERSION = "automation:gh-actions-executor:v1"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C3_ROOT = os.path.join(REPO_ROOT, "capability-observatory")
EXECUTOR_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_panel(panel_path: str) -> Dict[str, Any]:
    with open(panel_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_submission(incoming_dir: str, submission: ExecutorSubmission) -> str:
    c3_dict = submission.to_c3_submission()
    assert_submission_has_no_secret(c3_dict, known_secret_values())
    filename = f"exec-{date.today().isoformat()}-{submission.panel_item_id}.json"
    path = os.path.join(incoming_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(c3_dict, fh, indent=2, sort_keys=True)
    return filename


def run_all_captures(panel: Dict[str, Any], incoming_dir: str, fetched_at: str) -> List[ProviderAttempt]:
    transport = RealTransport()
    attempts: List[ProviderAttempt] = []

    ad_probe = None

    for item in panel.get("items", []):
        if item.get("status") != "active":
            continue
        provider = item.get("provider", "")
        panel_item_id = item["panel_item_id"]

        if provider.startswith("provider_d_digikey"):
            submission = digikey.run(item, transport, fetched_at, EXECUTOR_VERSION)
            method = "api"
        elif provider.startswith("provider_e_mouser"):
            submission = mouser.run(item, transport, fetched_at, EXECUTOR_VERSION)
            method = "api"
        elif provider.startswith("provider_a_automationdirect"):
            if ad_probe is None:
                ad_probe = automationdirect.probe(transport)
            submission = automationdirect.run(item, ad_probe, transport, fetched_at, EXECUTOR_VERSION)
            method = "html"
        else:
            # provider_b_grainger, provider_c_mcmaster: no public self-serve
            # API found, HTML risk unverified against likely enterprise-
            # grade bot management (Slice 03 design doc, Section 4). Never
            # attempted here -- this is a deliberate no-op, not a failure.
            attempts.append(ProviderAttempt(
                provider=provider, panel_item_id=panel_item_id, capture_method="human",
                classification="HUMAN_FALLBACK_REQUIRED", outcome="not_attempted",
            ))
            continue

        filename = _write_submission(incoming_dir, submission)
        classification = classify_attempt(method, submission.outcome)
        attempts.append(ProviderAttempt(
            provider=provider, panel_item_id=panel_item_id, capture_method=method,
            classification=classification, outcome=submission.outcome, filename=filename,
        ))

    return attempts


def _run_c3_process() -> Dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "run_capability_observatory.py", "process"],
        cwd=C3_ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return {"error": "run_capability_observatory.py process failed",
                "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "could not parse process output as JSON", "stdout": result.stdout, "stderr": result.stderr}


def _reconcile_written_flags(attempts: List[ProviderAttempt], process_summary: Dict[str, Any]) -> None:
    """Exact, not a guess: run_capability_observatory.py process's own
    stdout lists exactly which submitted filenames it processed
    successfully (`processed_files`) versus rejected (`rejected`). Since
    this run named every submission file itself
    (exec-<date>-<panel_item_id>.json, written just above), matching by
    filename tells us precisely which attempts became Capture records --
    no re-reading of captures.jsonl needed. A processed file whose outcome
    is observation-producing (ok/unavailable) always produced exactly one
    Observation too, per capture_intake.record_capture's own logic, unless
    it was an idempotent resubmission of an already-known capture_id --
    not possible here since every filename in one run is freshly written."""
    processed = set(process_summary.get("processed_files", []))
    for attempt in attempts:
        if attempt.filename is None:
            continue
        attempt.capture_written = attempt.filename in processed
        attempt.observation_written = attempt.capture_written and attempt.outcome in ("ok", "unavailable")


def cmd_run(args: argparse.Namespace) -> int:
    panel_path = os.path.join(C3_ROOT, "config", "panel.json")
    incoming_dir = os.path.join(C3_ROOT, "incoming")
    os.makedirs(incoming_dir, exist_ok=True)

    panel = load_panel(panel_path)
    fetched_at = _utc_now_iso()

    attempts = run_all_captures(panel, incoming_dir, fetched_at)
    process_summary = _run_c3_process()
    _reconcile_written_flags(attempts, process_summary)

    report = build_health_report(attempts, process_summary)
    reports_dir = os.path.join(EXECUTOR_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    generated_at = _utc_now_iso()

    with open(os.path.join(reports_dir, "latest-executor-health.json"), "w", encoding="utf-8") as fh:
        json.dump({"generated_at": generated_at, **report}, fh, indent=2, sort_keys=True)
    with open(os.path.join(reports_dir, f"executor-health-{date.today().isoformat()}.md"), "w", encoding="utf-8") as fh:
        fh.write(render_markdown(report, generated_at))

    print(json.dumps({"generated_at": generated_at, **report}, indent=2, sort_keys=True))
    return 0 if "error" not in process_summary else 1


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(prog="capability-observatory-executor")
    sub = parser.add_subparsers(dest="command", required=True)
    p_run = sub.add_parser("run", help="fetch every panel item and ingest via existing C3 code")
    p_run.set_defaults(func=cmd_run)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
