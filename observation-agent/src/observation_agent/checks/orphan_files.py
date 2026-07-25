"""Orphan/empty file detection.

Mechanical: a file is flagged if it is exactly 0 bytes. No judgment
about whether an empty file is "wrong" is made — Confidence is always
MATCH-for-the-observation-itself in the sense that "this file is
0 bytes" is not in dispute; the Recommended Action is phrased as a
question for a human, not a claim of defect (per AGENT-001's own
worked example for this exact finding type)."""

from __future__ import annotations

from ..config import RepoConfig
from ..models import Confidence, Evidence, Observation
from ..scanner import file_size, walk_files


def check_orphan_files(
    repo: RepoConfig, excluded_dirs: list[str], excluded_paths: list[str] | None = None
) -> list[Observation]:
    observations = []
    for path in walk_files(repo.path, excluded_dirs, excluded_paths=excluded_paths):
        size = file_size(path)
        if size == 0:
            rel = str(path.relative_to(repo.path))
            observations.append(
                Observation(
                    event=f"{rel} is a 0-byte file",
                    evidence=[
                        Evidence(
                            repo=repo.name,
                            file_path=rel,
                            line_number=None,
                            quoted_text="(file exists, 0 bytes)",
                        )
                    ],
                    verification_method="Direct file size check",
                    confidence=Confidence.MISMATCH,
                    possible_interpretation=(
                        "An orphaned placeholder, an incomplete artifact, "
                        "or a deliberately empty stub — not distinguishable "
                        "from file content alone"
                    ),
                    recommended_action=(
                        f"Populate or remove {rel}, at the repository's own "
                        "maintainers' discretion — flagged as orphan "
                        "content, not assumed to be a defect."
                    ),
                    human_needed=True,
                    check_name="orphan_files",
                )
            )
    return observations
