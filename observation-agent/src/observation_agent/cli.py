"""Entry point. Orchestrates: load config -> run checks per repo ->
diff against the previous run -> render report -> write report +
snapshot + execution log. The only write operations anywhere in this
module are: the report file, the snapshot file, and the execution log
— all three inside this package's own `reports/` directory. Nothing
outside `reports/` is ever opened for writing. See tests/test_safety.py.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .checks import (
    check_broken_references,
    check_orphan_files,
    check_registry_entries,
    check_stale_state,
    check_status_history_consistency,
)
from .config import AgentConfig, load_config
from .models import Observation
from .report import diff_against_previous, load_previous_snapshot, render_report, save_snapshot


def run_all_checks(config: AgentConfig) -> tuple[list[Observation], list[str], list[str], list[str]]:
    """Returns (observations, scanned_repo_names, skipped_repo_names, log_lines)."""
    observations: list[Observation] = []
    scanned: list[str] = []
    skipped: list[str] = []
    log: list[str] = []

    for repo in config.repos:
        repo_path = Path(repo.path)
        if not repo_path.exists():
            skipped.append(repo.name)
            log.append(f"SKIP {repo.name}: path {repo.path} does not exist or is not accessible")
            continue

        scanned.append(repo.name)
        log.append(f"SCAN {repo.name}: {repo.path}")

        for check_name, check_fn, extra_args in [
            ("broken_references", check_broken_references, (config.markdown_extensions,)),
            ("orphan_files", check_orphan_files, ()),
            ("registry_check", check_registry_entries, (config.markdown_extensions,)),
            ("stale_state", check_stale_state, (config.stale_threshold_days,)),
            ("status_history_consistency", check_status_history_consistency, ()),
        ]:
            start = time.monotonic()
            try:
                found = check_fn(repo, config.excluded_dirs, *extra_args, excluded_paths=config.excluded_paths)
            except Exception as exc:  # a check failing must not crash the whole run
                log.append(f"  ERROR in {check_name} for {repo.name}: {exc!r}")
                continue
            elapsed = time.monotonic() - start
            log.append(f"  {check_name}: {len(found)} observation(s) in {elapsed:.2f}s")
            observations.extend(found)

    return observations, scanned, skipped, log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="observation-agent")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "config.json"),
        help="Path to config.json",
    )
    parser.add_argument(
        "--reports-dir",
        default=str(Path(__file__).resolve().parents[2] / "reports"),
        help="Directory this agent's own outputs are written to (never any other directory)",
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)  # this agent's own directory only

    run_started = datetime.now(timezone.utc)
    observations, scanned, skipped, log_lines = run_all_checks(config)

    snapshot_path = reports_dir / "last_run_observations.json"
    previous = load_previous_snapshot(snapshot_path)
    new_obs, repeated_obs, resolved_keys = diff_against_previous(observations, previous)

    report_text = render_report(
        observations, new_obs, repeated_obs, resolved_keys, scanned, skipped
    )

    timestamp = run_started.strftime("%Y%m%dT%H%M%SZ")
    report_path = reports_dir / f"observation-report-{timestamp}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    save_snapshot(snapshot_path, observations)

    run_finished = datetime.now(timezone.utc)
    exec_log_path = reports_dir / f"execution-log-{timestamp}.md"
    with open(exec_log_path, "w", encoding="utf-8") as f:
        f.write(f"# Execution Log — {timestamp}\n\n")
        f.write(f"Started: {run_started.isoformat()}\n")
        f.write(f"Finished: {run_finished.isoformat()}\n")
        f.write(f"Duration: {(run_finished - run_started).total_seconds():.2f}s\n\n")
        f.write("## Steps\n\n")
        for line in log_lines:
            f.write(f"- {line}\n")
        f.write(f"\nReport written to: {report_path.name}\n")

    print(f"Scanned {len(scanned)} repositories, skipped {len(skipped)}.")
    print(f"{len(observations)} total observations ({len(new_obs)} new, "
          f"{len(repeated_obs)} repeated, {len(resolved_keys)} resolved).")
    print(f"Report: {report_path}")
    print(f"Execution log: {exec_log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
