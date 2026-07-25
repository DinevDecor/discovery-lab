"""Entry point. Orchestrates: load raw captures -> cluster -> gate ->
score -> upsert into the Signal Registry -> render briefs -> write
reports/. The only write operations anywhere in this module are the
three files in this package's own reports/ directory (signal-registry
.json, the daily brief, and the weekly brief) - never anywhere else.
See tests/test_safety.py.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from .brief import render_daily_brief, render_weekly_brief
from .capture import load_raw_captures
from .config import load_relevance_gate, load_source_registry
from .dedup import cluster
from .registry import build_signal, load_registry, save_registry, upsert

_PKG_ROOT = Path(__file__).resolve().parents[2]


def run_once(
    captures_path: str,
    source_registry_path: str,
    relevance_gate_path: str,
    reports_dir: str,
    run_timestamp: str | None = None,
) -> dict:
    """Pure orchestration, no argparse/print here so it's directly unit-
    testable. Returns a summary dict; also has the only side effects in
    this package (writing reports_dir's three files)."""
    run_timestamp = run_timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)

    # source_registry is loaded and validated even though this run
    # doesn't re-derive trust from it (the capture step already stamped
    # each RawCapture with its source_trust) - this is Required Test
    # "source validation": a raw capture citing a source name/URL not
    # present in the registry, or with a trust level the registry
    # disagrees with, is flagged rather than silently trusted.
    source_registry = load_source_registry(source_registry_path)
    relevance_config = load_relevance_gate(relevance_gate_path)

    captures, skip_reasons = load_raw_captures(captures_path)

    validation_warnings: list[str] = list(skip_reasons)
    valid_captures = []
    known_urls = {s.url for s in source_registry.sources}
    for c in captures:
        entry = source_registry.by_name(c.source_name)
        if entry is None and c.source_url not in known_urls:
            validation_warnings.append(
                f"{c.source_name!r} ({c.source_url}) is not in the Source Registry - "
                "kept, but its trust level is not independently confirmed"
            )
        elif entry is not None and entry.trust_level != c.source_trust:
            validation_warnings.append(
                f"{c.source_name!r} capture claims trust {c.source_trust!r} but the "
                f"Source Registry says {entry.trust_level!r} - Registry wins"
            )
            c.source_trust = entry.trust_level
        valid_captures.append(c)

    clusters = cluster(valid_captures)
    signals_this_run = [build_signal(members, relevance_config) for members in clusters]

    registry_path = reports_path / "signal-registry.json"
    registry = load_registry(registry_path)
    existing_keys = {r.key for r in registry}

    new_signals = []
    updated_signals = []
    for s in signals_this_run:
        is_new = s.key not in existing_keys
        registry = upsert(s, registry, run_timestamp)
        stored = next(r for r in registry if r.key == s.key)
        if is_new:
            new_signals.append(stored)
        else:
            updated_signals.append(stored)

    save_registry(registry_path, registry)

    daily_text = render_daily_brief(run_timestamp, new_signals, updated_signals)
    weekly_text = render_weekly_brief(run_timestamp, registry)

    stamp = run_timestamp.replace(":", "").replace("-", "")
    daily_path = reports_path / f"daily-ai-reality-brief-{stamp}.md"
    weekly_path = reports_path / f"weekly-ai-intelligence-brief-{stamp}.md"
    daily_path.write_text(daily_text, encoding="utf-8")
    weekly_path.write_text(weekly_text, encoding="utf-8")

    return {
        "run_timestamp": run_timestamp,
        "captures_loaded": len(captures),
        "captures_skipped": len(skip_reasons),
        "clusters": len(clusters),
        "new_signals": len(new_signals),
        "updated_signals": len(updated_signals),
        "registry_total": len(registry),
        "validation_warnings": validation_warnings,
        "registry_path": str(registry_path),
        "daily_brief_path": str(daily_path),
        "weekly_brief_path": str(weekly_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reality-sensor")
    parser.add_argument("--captures", required=True, help="Path to a raw-captures JSON file")
    parser.add_argument(
        "--source-registry",
        default=str(_PKG_ROOT / "config" / "source-registry.json"),
    )
    parser.add_argument(
        "--relevance-gate",
        default=str(_PKG_ROOT / "config" / "relevance-gate.json"),
    )
    parser.add_argument(
        "--reports-dir",
        default=str(_PKG_ROOT / "reports"),
        help="Directory this sensor's own outputs are written to (never any other directory)",
    )
    parser.add_argument(
        "--run-timestamp",
        default=None,
        help="Override the run timestamp (ISO-8601 UTC) - used only for reproducible tests",
    )
    args = parser.parse_args(argv)

    summary = run_once(
        captures_path=args.captures,
        source_registry_path=args.source_registry,
        relevance_gate_path=args.relevance_gate,
        reports_dir=args.reports_dir,
        run_timestamp=args.run_timestamp,
    )

    print(
        f"Loaded {summary['captures_loaded']} capture(s), "
        f"skipped {summary['captures_skipped']}."
    )
    print(
        f"{summary['clusters']} cluster(s) -> "
        f"{summary['new_signals']} new signal(s), "
        f"{summary['updated_signals']} updated signal(s). "
        f"Registry total: {summary['registry_total']}."
    )
    for w in summary["validation_warnings"]:
        print(f"WARNING: {w}")
    print(f"Registry: {summary['registry_path']}")
    print(f"Daily brief: {summary['daily_brief_path']}")
    print(f"Weekly brief: {summary['weekly_brief_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
