"""Stale state-file detection.

Compares a state file's own declared date against the newest file
modification time found elsewhere in the same repository.

Honest limitation, stated here and repeated in every Observation this
check produces: filesystem mtimes are not always a reliable proxy for
true edit history — a shallow clone or fresh checkout can reset mtimes
to checkout time regardless of when content was actually authored
(DL-001 hit exactly this limitation checking `kod`, and used a
different method — reading `SPRINT-024.md`'s own content — instead).
This check is therefore INSUFFICIENT_EVIDENCE, not MISMATCH, whenever
it cannot corroborate the mtime signal against the state file's own
declared date using a second, independent source.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from ..config import RepoConfig
from ..models import Confidence, Evidence, Observation
from ..scanner import newest_mtime, read_text, walk_files

_DATE_PATTERNS = [
    re.compile(r"updated_at:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?"),
    re.compile(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})"),
    re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE),
]

_STATE_FILE_NAMES = {"STATE.md", "PROJECT_STATE.md"}


def _extract_date(text: str) -> str | None:
    for pattern in _DATE_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(1)
    return None


def check_stale_state(
    repo: RepoConfig,
    excluded_dirs: list[str],
    threshold_days: int,
    excluded_paths: list[str] | None = None,
) -> list[Observation]:
    observations: list[Observation] = []
    candidates = repo.state_file_candidates or list(_STATE_FILE_NAMES)
    all_files = walk_files(repo.path, excluded_dirs, excluded_paths=excluded_paths)

    for path in all_files:
        if path.name not in candidates:
            continue
        text = read_text(path)
        if text is None:
            continue
        declared = _extract_date(text)
        if declared is None:
            continue  # nothing to compare against — not a finding, just uncheckable here

        try:
            declared_dt = datetime.strptime(declared, "%Y-%m-%d")
        except ValueError:
            continue

        other_files = [p for p in all_files if p != path]
        newest = newest_mtime(other_files)
        rel = str(path.relative_to(repo.path))
        if newest is None:
            continue

        newest_dt = datetime.fromtimestamp(newest)
        gap = newest_dt - declared_dt
        if gap > timedelta(days=threshold_days):
            observations.append(
                Observation(
                    event=(
                        f"{rel} declares date {declared}, but other files "
                        f"in {repo.name} were modified as recently as "
                        f"{newest_dt.date()}"
                    ),
                    evidence=[
                        Evidence(
                            repo=repo.name,
                            file_path=rel,
                            line_number=None,
                            quoted_text=f"declared date: {declared}",
                        )
                    ],
                    verification_method=(
                        "Declared date compared against the newest "
                        "filesystem mtime elsewhere in the repository"
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    possible_interpretation=(
                        "Either the state file is genuinely stale, or "
                        "filesystem mtimes in this checkout do not reflect "
                        "true edit history (a known limitation — see "
                        "module docstring). This check alone cannot "
                        "distinguish the two."
                    ),
                    recommended_action=(
                        f"A human or a content-based check (not mtime "
                        f"alone) should confirm whether {rel} is actually "
                        "stale before treating this as a defect."
                    ),
                    human_needed=True,
                    check_name="stale_state",
                )
            )
    return observations
