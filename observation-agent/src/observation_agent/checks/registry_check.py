"""Registry inconsistency detection — scoped honestly.

What this check can mechanically do: find markdown tables with a
"Status" column, and flag rows claiming an "ACTIVE"-shaped status with
no resolvable in-repository citation backing the claim.

What this check cannot do: confirm a registry claim is actually
contradicted by another document's content (e.g. `DL-001`'s
"Dinev Decor Systems: ACTIVE" vs. a separate investigation's
"INSUFFICIENT ACCESS" conclusion) — that requires reading and
semantically comparing two documents' meaning, not just their
structure. Every finding from this check is therefore
INSUFFICIENT_EVIDENCE, never MISMATCH — it surfaces candidates for a
human or a judgment-capable reviewer (an LLM-run pass, like `DL-001`
itself) to examine, consistent with `PROP-0001`'s own rule that an
uncheckable claim is recorded as uncertain, not guessed at.
"""

from __future__ import annotations

import re

from ..config import RepoConfig
from ..models import Confidence, Evidence, Observation
from ..scanner import read_text, walk_files

_TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")
_LINK_IN_ROW = re.compile(r"\[[^\]]*\]\([^)]+\)")
_ACTIVE_PATTERN = re.compile(r"\bACTIVE\b", re.IGNORECASE)


def check_registry_entries(
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
        lines = text.splitlines()

        header_idx = None
        for i, line in enumerate(lines):
            if _TABLE_ROW.match(line) and "status" in line.lower():
                header_idx = i
                break
        if header_idx is None:
            continue  # no registry-shaped table in this file

        rel = str(path.relative_to(repo.path))
        # Data rows start after the header and its `---` separator line.
        for line_no in range(header_idx + 2, len(lines)):
            line = lines[line_no]
            if not _TABLE_ROW.match(line):
                break
            if not _ACTIVE_PATTERN.search(line):
                continue
            has_citation = bool(_LINK_IN_ROW.search(line))
            if has_citation:
                continue  # a link is present; broken_references check covers whether it resolves

            subject = line.strip("| ").split("|")[0].strip()
            observations.append(
                Observation(
                    event=(
                        f"{rel}: row for '{subject}' claims an ACTIVE-shaped "
                        "status with no in-row citation"
                    ),
                    evidence=[
                        Evidence(
                            repo=repo.name,
                            file_path=rel,
                            line_number=line_no + 1,
                            quoted_text=line.strip(),
                        )
                    ],
                    verification_method=(
                        "Structural table parse only — this check cannot "
                        "read the claim's real-world truth, only whether "
                        "it cites supporting evidence"
                    ),
                    confidence=Confidence.INSUFFICIENT_EVIDENCE,
                    possible_interpretation=(
                        "The claim may be entirely correct and simply "
                        "uncited, or it may be stale/contradicted "
                        "elsewhere (as DL-001 found for a different "
                        "subject in this same file) — this check cannot "
                        "distinguish the two"
                    ),
                    recommended_action=(
                        f"A human or judgment-capable review should verify "
                        f"'{subject}' against citable evidence before "
                        "treating this row as current."
                    ),
                    human_needed=True,
                    check_name="registry_check",
                )
            )
    return observations
