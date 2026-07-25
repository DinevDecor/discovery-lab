"""STATUS.yaml vs. HISTORY.md consistency check.

Generalizes the exact defect `STRATEGIC-001` found and fixed by hand in
`AG-001`: a `STATUS.yaml` claiming `runs_completed: 0` sitting next to
a `HISTORY.md` that records a real run. This check looks for that
specific, narrow pattern anywhere a `STATUS.yaml` has a sibling
`HISTORY.md` — a small, simple regex parser, not a general YAML
parser (no third-party dependency needed for the two fields this check
actually reads).

LIMITATION (found running this check against the real `AG-001` and
`AG-002` roles): a "run entry" is only recognized when a `RUN-N`-shaped
token is the *primary subject* of a heading, immediately after the
date and dash (e.g. `## 2026-07-24 — RUN-0001`, `## 2026-07-24 —
PILOT-RUN-0002 ...`). This is deliberate precision, not laziness — an
earlier looser pattern (`##.*?RUN-\d+`, matching the token anywhere in
the heading) produced a real false positive against `AG-001`, where a
bug-fix entry's *explanatory prose* ("Bug fix: `STATUS.yaml` did not
reflect `RUN-0001`") was miscounted as a second run. The tightened
pattern still cannot recognize roles that name runs without a literal
"RUN-" token (e.g. `MIRROR-VERIFY-0001`) or headings that bundle
several run identifiers into one heading (e.g. `STRESS-RUN-0003,
-0004, -0005`) — both confirmed against the real `AG-002` role, whose
`HISTORY.md` uses both patterns. Recognizing those would require
semantic judgment about what counts as a "run," not mechanical
counting, so a declared/counted mismatch is reported as
`INSUFFICIENT_EVIDENCE`, not `MISMATCH` — consistent with how
`stale_state` and `registry_check` already handle proxies for
questions this check cannot fully answer on its own.
"""

from __future__ import annotations

import re

from ..config import RepoConfig
from ..models import Confidence, Evidence, Observation
from ..scanner import read_text, walk_files

_RUNS_COMPLETED = re.compile(r"^runs_completed:\s*(\d+)", re.MULTILINE)
_RUN_ENTRY = re.compile(
    r"^##\s*\d{4}-\d{2}-\d{2}\s*[—-]\s*\S*RUN-\d+\b",
    re.IGNORECASE | re.MULTILINE,
)


def check_status_history_consistency(
    repo: RepoConfig, excluded_dirs: list[str], excluded_paths: list[str] | None = None
) -> list[Observation]:
    observations: list[Observation] = []
    status_files = [
        p
        for p in walk_files(repo.path, excluded_dirs, excluded_paths=excluded_paths)
        if p.name == "STATUS.yaml"
    ]

    for status_path in status_files:
        history_path = status_path.parent / "HISTORY.md"
        if not history_path.exists():
            continue

        status_text = read_text(status_path)
        history_text = read_text(history_path)
        if status_text is None or history_text is None:
            continue

        m = _RUNS_COMPLETED.search(status_text)
        if m is None:
            continue
        declared_runs = int(m.group(1))
        actual_run_entries = len(_RUN_ENTRY.findall(history_text))

        if declared_runs != actual_run_entries:
            rel_status = str(status_path.relative_to(repo.path))
            rel_history = str(history_path.relative_to(repo.path))
            observations.append(
                Observation(
                    event=(
                        f"{rel_status} declares runs_completed={declared_runs}, "
                        f"but {rel_history} records {actual_run_entries} "
                        "run entr(y/ies)"
                    ),
                    evidence=[
                        Evidence(
                            repo=repo.name,
                            file_path=rel_status,
                            line_number=None,
                            quoted_text=f"runs_completed: {declared_runs}",
                        ),
                        Evidence(
                            repo=repo.name,
                            file_path=rel_history,
                            line_number=None,
                            quoted_text=f"{actual_run_entries} '## ... RUN-N' entries found",
                        ),
                    ],
                    verification_method=(
                        "Direct cross-reference between a STATUS.yaml "
                        "field and its sibling HISTORY.md's own "
                        "'## YYYY-MM-DD — RUN-N'-shaped headings"
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    possible_interpretation=(
                        "Either STATUS.yaml was not updated when a run "
                        "was recorded in HISTORY.md (a bookkeeping gap), "
                        "or HISTORY.md records real runs under a heading "
                        "convention this check's heuristic does not "
                        "recognize (no literal 'RUN-N' token as the "
                        "heading's primary subject, or several run IDs "
                        "bundled into one heading) — this check counts "
                        "headings mechanically and cannot distinguish "
                        "the two on its own"
                    ),
                    recommended_action=(
                        f"A human familiar with {repo.name}'s "
                        f"{rel_history} should confirm whether "
                        f"{declared_runs} is the correct count; if so, "
                        "either update HISTORY.md's heading convention "
                        f"or treat this as a false positive. If "
                        f"{actual_run_entries} is correct, update "
                        f"{rel_status}'s runs_completed field, or "
                        "correct HISTORY.md if it over-counts."
                    ),
                    human_needed=True,
                    check_name="status_history_consistency",
                )
            )
    return observations
