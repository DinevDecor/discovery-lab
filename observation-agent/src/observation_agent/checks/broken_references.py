"""Broken relative-reference detection.

Automates the exact `realpath -m` + `test -f` ritual this session has
performed by hand before every commit throughout its own history —
per DL-002/AGENT-001's own Part C finding, the single strongest
automation candidate found, precisely because it is already fully
mechanical.

Scope, stated honestly: only markdown link syntax `[text](path)` is
parsed — not bare inline-code paths, which are far more ambiguous
(a code span like `KO-NNNN.md` may be a pattern description, not a
literal reference). This narrower scope trades recall for precision:
every reference this check flags is unambiguous, at the cost of not
catching every reference a human would recognize as a path.
"""

from __future__ import annotations

import re

from ..config import RepoConfig
from ..models import Confidence, Evidence, Observation
from ..scanner import read_text, walk_files

_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
_SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")


def _is_checkable(target: str) -> bool:
    if target.startswith(_SKIP_PREFIXES):
        return False
    if "://" in target:
        return False
    # Strip a trailing anchor (path.md#section) before checking existence.
    return True


def check_broken_references(
    repo: RepoConfig,
    excluded_dirs: list[str],
    markdown_extensions: list[str],
    excluded_paths: list[str] | None = None,
) -> list[Observation]:
    observations: list[Observation] = []
    for path in walk_files(repo.path, excluded_dirs, markdown_extensions, excluded_paths):
        text = read_text(path)
        if text is None:
            continue
        rel = str(path.relative_to(repo.path))
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in _LINK_PATTERN.finditer(line):
                link_text, target = match.group(1), match.group(2).strip()
                if not _is_checkable(target):
                    continue
                target_path_part = target.split("#", 1)[0]
                if not target_path_part:
                    continue
                resolved = (path.parent / target_path_part).resolve()
                if not resolved.exists():
                    observations.append(
                        Observation(
                            event=f"Broken reference in {rel}: [{link_text}]({target})",
                            evidence=[
                                Evidence(
                                    repo=repo.name,
                                    file_path=rel,
                                    line_number=line_no,
                                    quoted_text=line.strip(),
                                )
                            ],
                            verification_method=(
                                "Relative path resolved against the citing "
                                "file's own directory and checked for "
                                "existence (equivalent to `realpath -m` + "
                                "`test -e`)"
                            ),
                            confidence=Confidence.MISMATCH,
                            possible_interpretation=(
                                "The target was renamed, moved, or deleted "
                                "after this link was written, or the link "
                                "was authored with an incorrect relative "
                                "path from the start"
                            ),
                            recommended_action=(
                                f"Correct or remove the link in {rel}:{line_no} "
                                f"— target `{target}` does not resolve to an "
                                "existing file."
                            ),
                            human_needed=True,
                            check_name="broken_references",
                        )
                    )
    return observations
