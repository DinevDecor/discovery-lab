"""Data model for a single observation.

Field names and meaning follow AGENT-001's own Observation Model schema
exactly (../../docs/proposals/AGENT-001-observation-agent/
2-OBSERVATION-LOOP.md) — this module does not define a new schema, it
implements the one already specified there.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class Confidence:
    """Fixed vocabulary, per PROP-0001's own C1/C2/C3 rubric. Not an
    enum subclassed for extension — this set is closed by design,
    matching PROP-0001's "fixed criteria, not changed after evidence
    is seen"."""

    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass
class Evidence:
    repo: str
    file_path: str
    line_number: int | None
    quoted_text: str

    def citation(self) -> str:
        loc = f":{self.line_number}" if self.line_number is not None else ""
        return f"{self.repo}/{self.file_path}{loc} — \"{self.quoted_text}\""


@dataclass
class Observation:
    """One entry in the Observation Model. Every field required by
    AGENT-001's schema is present; nothing is optional except where the
    schema itself allows "none — informational only"."""

    event: str
    evidence: list[Evidence]
    verification_method: str
    confidence: str
    possible_interpretation: str
    recommended_action: str  # "none — informational only" if no action
    human_needed: bool
    check_name: str = ""  # which check produced this, for the Execution Log

    def evidence_citations(self) -> list[str]:
        return [e.citation() for e in self.evidence]
