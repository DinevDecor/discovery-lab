"""CI-only helper for EXEC-003. Reads the Observation Agent's own
already-produced report and execution log for the most recent run in
a given reports directory, and writes a short human-readable status
line to $GITHUB_STEP_SUMMARY (or stdout, outside CI).

Read-only with one narrow exception: this script opens
$GITHUB_STEP_SUMMARY in append mode, because that is how GitHub
Actions itself expects a step to publish a summary — it never opens
any other file for writing, and never touches any observed repository.
Kept outside src/observation_agent on purpose: this is workflow glue
around the agent, not a change to the agent itself.
"""

from __future__ import annotations

import glob
import os
import sys


def _latest(pattern: str) -> str | None:
    matches = sorted(glob.glob(pattern))
    return matches[-1] if matches else None


def build_summary(reports_dir: str) -> str:
    report_path = _latest(os.path.join(reports_dir, "observation-report-*.md"))
    log_path = _latest(os.path.join(reports_dir, "execution-log-*.md"))

    lines = ["# Observation Agent 001 — Run Summary", ""]

    if report_path is None:
        lines.append("STATUS: FAILURE — no report was produced.")
        return "\n".join(lines) + "\n"

    log_text = ""
    if log_path is not None:
        with open(log_path, encoding="utf-8") as f:
            log_text = f.read()

    if "ERROR in " in log_text:
        status = "PARTIAL — one or more checks errored; see the execution log artifact."
    elif "SKIP " in log_text:
        status = (
            "PARTIAL — one or more configured repositories were not "
            "accessible in this environment. Expected in CI (see "
            "README's CI Limitations section); see the execution log "
            "artifact for exactly which repositories were skipped."
        )
    else:
        status = "SUCCESS — all configured, accessible repositories were scanned cleanly."

    lines.append(f"STATUS: {status}")
    lines.append("")

    with open(report_path, encoding="utf-8") as f:
        report_text = f.read()

    in_confidence = False
    for line in report_text.splitlines():
        if line.strip() == "## Confidence":
            in_confidence = True
            lines.append(line)
            continue
        if in_confidence:
            if line.startswith("## "):
                break
            lines.append(line)

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    reports_dir = argv[0] if argv else "reports-ci"

    text = build_summary(reports_dir)

    summary_target = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_target:
        with open(summary_target, "a", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
